"""
The four target metrics, scored per draft and reducible to a mean.

Format, faithfulness, placeholder integrity and residual-clean are the same
four gates `assemble.validators` uses to keep a training pair — reused here so
"the model got better" is measured against exactly the bar the data was held
to. Each is 1.0 (pass) or 0.0 (fail) for a single draft; a run reports the
mean over its drafts.

`style_match` is only scored for styled examples: section-order agreement plus
lexical overlap with the target, a dependency-free stand-in for the embedding
cosine the design allows.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from finetune.assemble.validators import validate
from finetune.datagen.schema import EncounterFacts, FormType

_HEADING_RE = re.compile(r"\*\*\s*(.+?)\s*\*\*")


@dataclass(frozen=True)
class DraftScore:
    format: float
    faithfulness: float
    placeholder_integrity: float
    residual_clean: float
    style_match: float | None = None

    def as_dict(self) -> dict[str, float | None]:
        return {
            "format": self.format,
            "faithfulness": self.faithfulness,
            "placeholder_integrity": self.placeholder_integrity,
            "residual_clean": self.residual_clean,
            "style_match": self.style_match,
        }


def _headings(text: str) -> list[str]:
    return [m.group(1) for m in _HEADING_RE.finditer(text)]


def _order_agreement(a: list[str], b: list[str]) -> float:
    """Fraction of ``a``'s headings that appear in ``b`` in the same relative order."""
    common = [h for h in a if h in b]
    if not common:
        return 0.0
    b_order = [h for h in b if h in common]
    hits = sum(1 for x, y in zip(common, b_order) if x == y)
    return hits / len(common)


def _lexical_overlap(a: str, b: str) -> float | None:
    ta = set(re.findall(r"[a-z]{3,}", a.lower()))
    tb = set(re.findall(r"[a-z]{3,}", b.lower()))
    if not ta or not tb:
        return None
    return len(ta & tb) / len(ta | tb)


def style_match(output: str, target: str) -> float:
    """0..1 — heading-order agreement and lexical overlap, evenly weighted.

    Falls back to order-only when there are no comparable content words, and is
    exactly 1.0 for identical text.
    """
    if output == target:
        return 1.0
    order = _order_agreement(_headings(target), _headings(output))
    lex = _lexical_overlap(output, target)
    if lex is None:
        return round(order, 4)
    return round(0.5 * order + 0.5 * lex, 4)


def score_draft(
    output: str,
    facts: EncounterFacts,
    form: FormType,
    *,
    known_placeholders=(),
    acknowledged=(),
    style_target: str | None = None,
) -> DraftScore:
    report = validate(
        output,
        facts,
        form,
        known_placeholders=known_placeholders,
        acknowledged=acknowledged,
    )
    return DraftScore(
        format=float(report.format_ok),
        faithfulness=float(report.faithful_ok),
        placeholder_integrity=float(report.placeholder_ok),
        residual_clean=float(report.residual_ok),
        style_match=None if style_target is None else style_match(output, style_target),
    )


def aggregate(scores: list[DraftScore]) -> dict[str, float]:
    """Mean of each metric over ``scores`` (style_match over styled drafts only)."""
    if not scores:
        return {}
    n = len(scores)
    styled = [s.style_match for s in scores if s.style_match is not None]
    out = {
        "format": sum(s.format for s in scores) / n,
        "faithfulness": sum(s.faithfulness for s in scores) / n,
        "placeholder_integrity": sum(s.placeholder_integrity for s in scores) / n,
        "residual_clean": sum(s.residual_clean for s in scores) / n,
        "n": n,
    }
    if styled:
        out["style_match"] = sum(styled) / len(styled)
    return out


# The four metrics that gate a ship, in the order the report shows them.
TARGET_METRICS = ("format", "faithfulness", "placeholder_integrity", "residual_clean")


__all__ = [
    "TARGET_METRICS",
    "DraftScore",
    "aggregate",
    "score_draft",
    "style_match",
]
