"""
EVAL_REPORT.md + eval_report.json from a base-vs-tuned comparison.

The report is the artefact a model card points at and a reviewer reads before a
ship. It states the ship gate verdict plainly at the top.
"""

from __future__ import annotations

import json
from pathlib import Path

from finetune.eval.metrics import TARGET_METRICS
from finetune.eval.run_eval import RunResult, compare


def _row(name: str, base: dict, tuned: dict, key: str) -> str:
    b = base.get(key)
    t = tuned.get(key)
    if b is None or t is None:
        return f"| {name} | – | – | – |"
    d = t - b
    arrow = "▲" if d > 0 else ("▼" if d < 0 else "–")
    return f"| {name} | {b:.3f} | {t:.3f} | {arrow} {d:+.3f} |"


def build_report(
    base: RunResult,
    tuned: RunResult,
    *,
    base_name: str = "base",
    tuned_name: str = "tuned",
) -> tuple[str, dict]:
    verdict = compare(base, tuned)
    ship = verdict["ship"]

    lines = [
        "# Evaluation report",
        "",
        f"**Ship gate: {'PASS' if ship else 'FAIL'}**",
        "",
        f"- eval items: {base.n}",
        f"- median seconds/draft: {base_name} {base.median_seconds:.2f}s, "
        f"{tuned_name} {tuned.median_seconds:.2f}s "
        f"(ratio {verdict['latency_ratio']}, ceiling {1.15})",
        f"- regressions: {', '.join(verdict['regressions']) or 'none'}",
        "",
        "| metric | " + base_name + " | " + tuned_name + " | Δ |",
        "|---|---|---|---|",
    ]
    for m in TARGET_METRICS:
        lines.append(_row(m, base.metrics, tuned.metrics, m))
    if "style_match" in base.metrics or "style_match" in tuned.metrics:
        lines.append(_row("style_match", base.metrics, tuned.metrics, "style_match"))
    lines.append("")
    lines.append(
        "Ship gate: tuned ≥ base on every metric above the style row, no "
        "regression on the regression set, and latency ratio ≤ 1.15."
    )

    payload = {
        "ship": ship,
        "verdict": verdict,
        "base": {"metrics": base.metrics, "median_seconds": base.median_seconds},
        "tuned": {"metrics": tuned.metrics, "median_seconds": tuned.median_seconds},
    }
    return "\n".join(lines) + "\n", payload


def write_report(base: RunResult, tuned: RunResult, out_dir: str | Path, **kw) -> bool:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    md, payload = build_report(base, tuned, **kw)
    (out_dir / "EVAL_REPORT.md").write_text(md, encoding="utf-8")
    (out_dir / "eval_report.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
    )
    return payload["ship"]


__all__ = ["build_report", "write_report"]
