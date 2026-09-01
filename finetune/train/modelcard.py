"""
MODEL_CARD.md from the training config, the dataset manifest, and the eval
report — the artefact CareScribe surfaces in its About box so a reviewer can
check what trained the model that drafts their notes.

Pure: no torch, no I/O beyond the file write.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


def render_card(
    *,
    base_model: str,
    base_licence: str,
    lora: dict,
    manifest: dict,
    eval_payload: dict,
    known_limitations: list[str] | None = None,
    built: str | None = None,
) -> str:
    built = built or date.today().isoformat()
    ship = eval_payload.get("ship")
    verdict = eval_payload.get("verdict", {})
    base_m = eval_payload.get("base", {}).get("metrics", {})
    tuned_m = eval_payload.get("tuned", {}).get("metrics", {})

    lines = [
        "# CareScribe clinical drafting model — model card",
        "",
        f"- **Base model:** {base_model}",
        f"- **Licence:** {base_licence}",
        f"- **Method:** QLoRA SFT (r={lora.get('r')}, alpha={lora.get('alpha')}, "
        f"dropout={lora.get('dropout')}, targets={', '.join(lora.get('target_modules', []))})",
        f"- **Built:** {built}",
        f"- **carescribe commit:** {manifest.get('carescribe_sha', 'unknown')}",
        "",
        "## Training data",
        "",
        f"- 100% synthetic. Generator: {manifest.get('generator_backend')}"
        + (f" / {manifest.get('generator_model')}" if manifest.get("generator_model") else ""),
        f"- Seed: {manifest.get('seed')}",
        f"- Pairs: {manifest.get('total')} "
        f"({json.dumps(manifest.get('counts', {}))})",
        f"- Dataset SHA-256: `{manifest.get('content_sha256', '')}`",
        "",
        "## Evaluation",
        "",
        f"**Ship gate: {'PASS' if ship else 'FAIL'}**  "
        f"(latency ratio {verdict.get('latency_ratio', '–')}, "
        f"regressions: {', '.join(verdict.get('regressions', [])) or 'none'})",
        "",
        "| metric | base | tuned |",
        "|---|---|---|",
    ]
    for m in ("format", "faithfulness", "placeholder_integrity", "residual_clean"):
        b = base_m.get(m)
        t = tuned_m.get(m)
        lines.append(
            f"| {m} | {b:.3f} | {t:.3f} |" if b is not None and t is not None
            else f"| {m} | – | – |"
        )

    lines += ["", "## Known limitations", ""]
    for lim in known_limitations or [
        "Trained only on synthetic encounters — real-note performance is unverified.",
        "Specialty coverage limited to the vignette set (GP, mental health, "
        "cardiology, respiratory, elderly care).",
        "Not a clinical decision tool; every draft requires clinician review.",
    ]:
        lines.append(f"- {lim}")
    return "\n".join(lines) + "\n"


def write_card(out_path: str | Path, **kw) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_card(**kw), encoding="utf-8")
    return out_path


def _load(p: str | Path) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))


__all__ = ["render_card", "write_card"]
