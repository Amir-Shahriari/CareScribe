"""
The four target metrics, scored per draft and reducible to a mean.

Format, faithfulness, placeholder integrity and residual-clean are the same
four gates `assemble.validators` uses to keep a training pair — reused here so
"the model got better" is measured against exactly the bar the data was held
to. Each is 1.0 (pass) or 0.0 (fail) for a single draft; a run reports the
mean over its drafts.

`style_match` was withdrawn (v2 design, D3). It was reported over a corpus in
which no pair was styled — every stratum in the v1 manifest is `styled=False`,
because `datagen/vignettes/styles/` was never created — so it scored a dimension
that never varied. Worse, `run_eval` passed the deterministic target as the
style reference for *every* item, so the number measured how closely a draft
reproduced the scaffold: the same self-marking as D2, under another name. It
returns when styled pairs actually exist.
"""

from __future__ import annotations

from dataclasses import dataclass

from finetune.assemble.validators import validate
from finetune.datagen.schema import EncounterFacts, FormType


@dataclass(frozen=True)
class DraftScore:
    format: float
    faithfulness: float
    placeholder_integrity: float
    residual_clean: float

    def as_dict(self) -> dict[str, float]:
        return {
            "format": self.format,
            "faithfulness": self.faithfulness,
            "placeholder_integrity": self.placeholder_integrity,
            "residual_clean": self.residual_clean,
        }


def score_draft(
    output: str,
    facts: EncounterFacts,
    form: FormType,
    *,
    known_placeholders=(),
    acknowledged=(),
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
    )


def aggregate(scores: list[DraftScore]) -> dict[str, float]:
    """Mean of each metric over ``scores``."""
    if not scores:
        return {}
    n = len(scores)
    return {
        "format": sum(s.format for s in scores) / n,
        "faithfulness": sum(s.faithfulness for s in scores) / n,
        "placeholder_integrity": sum(s.placeholder_integrity for s in scores) / n,
        "residual_clean": sum(s.residual_clean for s in scores) / n,
        "n": n,
    }


# The four metrics that gate a ship, in the order the report shows them.
TARGET_METRICS = ("format", "faithfulness", "placeholder_integrity", "residual_clean")


__all__ = [
    "TARGET_METRICS",
    "DraftScore",
    "aggregate",
    "score_draft",
]
