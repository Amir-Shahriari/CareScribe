"""
End-to-end: sampled encounters -> validated SFT pairs + manifest.

    python -m finetune.assemble.build_dataset --n 200 --out data/dryrun

The full round trip per encounter:

    sample facts -> render messy note -> inject fake identifiers
        -> REAL CareScribe de-identify -> build deterministic target
        -> validate (4 gates) -> keep or discard

Discards are expected — the design generates ~1.7x and drops failures. The
`template` identifier/render path has no external dependency, so this runs in
CI and as the M1 dry run.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Callable

from finetune.assemble.build_target import build_target
from finetune.assemble.deidentify_notes import deidentify_note, leaked_values
from finetune.assemble.manifest import build_manifest, write_manifest
from finetune.assemble.pairs import make_pair, stratified_split, write_jsonl
from finetune.assemble.validators import validate
from finetune.datagen.render_note import render
from finetune.datagen.sampler import sample_encounters
from finetune.datagen.schema import EncounterFacts, FormType

_DEFAULT_FORMS = (
    FormType.SOAP,
    FormType.PROGRESS_NOTE,
    FormType.HANDOVER,
    FormType.CARE_PLAN,
)

InjectFn = Callable[[str, int], "tuple[str, list[str]]"]


def _fallback_inject(text: str, seed: int) -> tuple[str, list[str]]:
    """Fill ``[[TOKEN]]`` slots with simple fake values.

    Used only until ``finetune.datagen.identifiers.inject`` exists; the real one
    is Faker-backed with valid NHS check digits. Returns (text, values).
    """
    rng = random.Random(seed)
    first = rng.choice(["Alex", "Sam", "Jordan", "Priya", "Wei", "Tomas", "Amara"])
    last = rng.choice(["Doyle", "Okafor", "Nasser", "Brandt", "Ilic", "Mercer"])
    subs = {
        "[[NAME]]": f"{first} {last}",
        "[[PROVIDER]]": "Dr " + rng.choice(["H. Bolt", "P. Ngu", "R. Vale"]),
        "[[DOB]]": f"{rng.randint(1,28):02d}/{rng.randint(1,12):02d}/{rng.randint(1945,2010)}",
        "[[DATE]]": f"{rng.randint(1,28):02d}/{rng.randint(1,12):02d}/2026",
        "[[NHS]]": f"{rng.randint(400,699)} {rng.randint(100,999)} {rng.randint(1000,9999)}",
        "[[MRN]]": f"{rng.randint(100000,999999)}",
    }
    import re

    values: list[str] = []
    for token, value in subs.items():
        pattern = re.compile(re.escape(token), re.IGNORECASE)
        if pattern.search(text):
            text = pattern.sub(value.replace("\\", "\\\\"), text)
            values.append(value)
    return text, values


def _resolve_inject(inject_fn: InjectFn | None) -> InjectFn:
    if inject_fn is not None:
        return inject_fn
    try:
        from finetune.datagen.identifiers import inject as real_inject
    except Exception:  # noqa: BLE001
        return _fallback_inject

    def _adapt(text: str, seed: int) -> tuple[str, list[str]]:
        out, placed = real_inject(text, seed=seed)
        return out, [p.value for p in placed]

    return _adapt


_TEMPLATE_FORM_IDS = ("client_session_notes", "client_treatment_review")


def _template_specs():
    from carescribe.core import clinical_forms

    return [clinical_forms.get_form_spec(fid) for fid in _TEMPLATE_FORM_IDS]


def build(
    n: int,
    *,
    seed: int = 0,
    forms: tuple[FormType, ...] = _DEFAULT_FORMS,
    gap_probability: float = 0.25,
    template_fraction: float = 0.25,
    inject_fn: InjectFn | None = None,
) -> dict:
    """Return ``{"pairs": [...], "kept": k, "dropped": d, "reasons": {...}}``.

    ``template_fraction`` of the pairs target an uploaded clinic template
    (``<<FIELD:key>>`` markers) instead of a built-in note type, so the model
    also learns that format and its "Not documented" discipline."""
    from finetune.assemble.pairs import make_template_pair

    inject = _resolve_inject(inject_fn)
    specs = _template_specs()
    pairs = []
    dropped = 0
    reasons: dict[str, int] = {}

    for i, facts in enumerate(
        sample_encounters(n, seed=seed, gap_probability=gap_probability)
    ):
        note = render(facts, seed=seed + i)
        identified, values = inject(note, seed + i)
        deid = deidentify_note(identified)

        missed = leaked_values(deid, values)
        if missed:
            dropped += 1
            reasons["identifier_leaked_through_deid"] = (
                reasons.get("identifier_leaked_through_deid", 0) + 1
            )
            continue

        _stride = max(1, round(1 / template_fraction)) if template_fraction > 0 else 0
        as_template = bool(specs) and _stride and (i % _stride == 0)
        if as_template:
            spec = specs[i % len(specs)]
            form = FormType.UPLOADED_TEMPLATE
            target = build_target(facts, form, form_spec=spec)
            report = validate(
                target, facts, form,
                known_placeholders=deid.known_placeholders, form_spec=spec,
            )
        else:
            spec = None
            form = forms[i % len(forms)]
            target = build_target(facts, form)
            report = validate(
                target, facts, form, known_placeholders=deid.known_placeholders
            )

        if not report.ok:
            dropped += 1
            key = report.problems[0].split(":")[0] if report.problems else "unknown"
            reasons[key] = reasons.get(key, 0) + 1
            continue

        if as_template:
            pairs.append(make_template_pair(facts, spec, deid.placeholdered_text, target))
        else:
            pairs.append(make_pair(facts, form, deid.placeholdered_text, target))

    return {"pairs": pairs, "kept": len(pairs), "dropped": dropped, "reasons": reasons}


def _load_datagen_config(path: Path) -> dict:
    try:
        import yaml

        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001 — config is optional
        return {}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=None, help="override config count")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--gap-probability", type=float, default=None)
    ap.add_argument("--config", type=Path, default=Path("finetune/config/datagen.yaml"))
    ap.add_argument("--out", type=Path, default=Path("finetune/data/dryrun"))
    args = ap.parse_args(argv)

    cfg = _load_datagen_config(args.config)
    n = args.n if args.n is not None else int(
        (cfg.get("counts", {}) or {}).get("total", 200)
    )
    seed = args.seed if args.seed is not None else int(
        (cfg.get("rng", {}) or {}).get("seed", 0)
    )
    gap = args.gap_probability if args.gap_probability is not None else float(
        (cfg.get("quality", {}) or {}).get("gap_probability", 0.25)
    )

    result = build(n, seed=seed, gap_probability=gap)
    splits = stratified_split(result["pairs"], seed=seed)
    for name, group in splits.items():
        write_jsonl(group, args.out / f"{name}.jsonl")
    manifest = build_manifest(
        splits, generator_backend="template", generator_model=None, seed=seed
    )
    write_manifest(manifest, args.out / "dataset_manifest.json")

    print(
        f"kept {result['kept']} / dropped {result['dropped']}  ({n} sampled)\n"
        f"reasons: {json.dumps(result['reasons'])}\n"
        f"splits: {manifest['counts']}\n"
        f"-> {args.out}/"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
