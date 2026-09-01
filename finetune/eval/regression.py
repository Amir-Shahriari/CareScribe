"""
A regression set built from the repo's own corpus, not synthetic data.

`stress_corpus/` and `sample_documents/` are de-identified through the real
pipeline and handed to the model as-is. There are no `EncounterFacts` for
these, so only the fact-free gates are scored — placeholder integrity, residual
clean, and heading format for a fixed form — but that is enough to catch a
tuned model that has learned to mangle placeholders or drop a required section
on text shaped unlike the synthetic training notes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from finetune.assemble.deidentify_notes import deidentify_note
from finetune.assemble.validators import check_format, check_placeholders, check_residual
from finetune.datagen.schema import FormType
from finetune.eval.run_eval import Completer
from finetune.integrate.prompt_template import build_messages

_REPO = Path(__file__).resolve().parents[2]
_CORPUS_DIRS = ("stress_corpus", "sample_documents")


@dataclass(frozen=True)
class RegressionItem:
    name: str
    document: str
    known_placeholders: list[str]
    form: FormType = FormType.SOAP


def regression_items(limit: int | None = None) -> list[RegressionItem]:
    items: list[RegressionItem] = []
    for sub in _CORPUS_DIRS:
        d = _REPO / sub
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.txt")):
            raw = path.read_text(encoding="utf-8", errors="ignore")
            if len(raw.strip()) < 200:
                continue
            deid = deidentify_note(raw)
            items.append(
                RegressionItem(path.name, deid.placeholdered_text, deid.known_placeholders)
            )
    return items[:limit] if limit else items


def score_regression(model: Completer, items: list[RegressionItem]) -> dict[str, float]:
    if not items:
        return {}
    fmt = ph = res = 0
    for it in items:
        msgs = build_messages(it.form, it.document)
        draft = model.complete(msgs[0]["content"], msgs[1]["content"])
        fmt += int(check_format(draft, it.form)[0])
        ph += int(check_placeholders(draft, it.known_placeholders)[0])
        res += int(check_residual(draft)[0])
    n = len(items)
    return {
        "format": fmt / n,
        "placeholder_integrity": ph / n,
        "residual_clean": res / n,
        "n": n,
    }


def regressed(base: dict[str, float], tuned: dict[str, float]) -> list[str]:
    return [
        k
        for k in ("format", "placeholder_integrity", "residual_clean")
        if tuned.get(k, 0.0) < base.get(k, 0.0)
    ]


__all__ = ["RegressionItem", "regressed", "regression_items", "score_regression"]
