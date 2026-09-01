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


def build(
    n: int,
    *,
    seed: int = 0,
    forms: tuple[FormType, ...] = _DEFAULT_FORMS,
    gap_probability: float = 0.25,
    inject_fn: InjectFn | None = None,
) -> dict:
    """Return ``{"pairs": [...], "kept": k, "dropped": d, "reasons": {...}}``."""
    inject = _resolve_inject(inject_fn)
    pairs = []
    dropped = 0
    reasons: dict[str, int] = {}

    for i, facts in enumerate(
        sample_encounters(n, seed=seed, gap_probability=gap_probability)
    ):
        form = forms[i % len(forms)]
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

        target = build_target(facts, form)
        report = validate(
            target, facts, form, known_placeholders=deid.known_placeholders
        )
        if not report.ok:
            dropped += 1
            key = report.problems[0].split(":")[0] if report.problems else "unknown"
            reasons[key] = reasons.get(key, 0) + 1
            continue

        pairs.append(make_pair(facts, form, deid.placeholdered_text, target))

    return {"pairs": pairs, "kept": len(pairs), "dropped": dropped, "reasons": reasons}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--gap-probability", type=float, default=0.25)
    ap.add_argument("--out", type=Path, default=Path("data/dryrun"))
    args = ap.parse_args(argv)

    result = build(args.n, seed=args.seed, gap_probability=args.gap_probability)
    splits = stratified_split(result["pairs"], seed=args.seed)
    for name, group in splits.items():
        write_jsonl(group, args.out / f"{name}.jsonl")
    manifest = build_manifest(
        splits, generator_backend="template", generator_model=None, seed=args.seed
    )
    write_manifest(manifest, args.out / "dataset_manifest.json")

    print(
        f"kept {result['kept']} / dropped {result['dropped']}  "
        f"({args.n} sampled)\n"
        f"reasons: {json.dumps(result['reasons'])}\n"
        f"splits: {manifest['counts']}\n"
        f"-> {args.out}/"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
