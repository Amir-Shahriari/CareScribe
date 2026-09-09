"""
Adversarial probes for the "Not documented." behaviour.

Every probe is an encounter in which fields the form asks about were
deliberately removed. The metric is the *confabulation rate*: how often a draft
asserts content under a heading whose backing facts were taken away. That is the
failure that matters clinically, and none of the four v1 metrics measured it.

The gapped headings are read off the **target**, not from a hand-maintained
field-to-heading map. The target is rendered from the same gapped facts, so it
already writes "Not documented." in exactly the right places — and a map would
have to track wording the forms actually use (SOAP's heading is ``S — Subjective``,
not ``Subjective``), which is a standing source of silent drift.
"""

from __future__ import annotations

import re
from typing import Sequence

from finetune.assemble.build_target import build_target
from finetune.assemble.deidentify_notes import deidentify_note, leaked_values
from finetune.datagen.render_note import render
from finetune.datagen.sampler import sample_encounters
from finetune.datagen.schema import FormType
from finetune.eval.run_eval import _DEFAULT_FORMS, EvalItem

NOT_DOCUMENTED = "not documented"

_SECTION_RE = re.compile(r"\*\*\s*(.+?)\s*\*\*\s*\n(.*?)(?=\n\*\*|\Z)", re.DOTALL)


def _norm(heading: str) -> str:
    """Compare headings without tripping on case or spacing."""
    return " ".join(heading.split()).casefold()


def sections(text: str) -> dict[str, str]:
    """``{normalised heading: body}`` for a bold-headed form."""
    return {_norm(m.group(1)): m.group(2) for m in _SECTION_RE.finditer(text)}


def gapped_headings(target: str) -> list[str]:
    """Headings the target answers with "Not documented."."""
    return [
        heading
        for heading, body in sections(target).items()
        if NOT_DOCUMENTED in body.casefold()
    ]


def make_gap_probes(
    n: int,
    *,
    seed: int = 2000,
    forms: tuple[FormType, ...] = _DEFAULT_FORMS,
) -> list[EvalItem]:
    """``n`` eval items whose target admits at least one undocumented field.

    ``gap_probability=1.0`` blanks every gappable field a vignette allows, so
    the probes are deliberately harsher than the training distribution.
    """
    from finetune.datagen.identifiers import inject

    items: list[EvalItem] = []
    drawn = 0
    for facts in sample_encounters(n * 5, seed=seed, gap_probability=1.0):
        if len(items) >= n:
            break
        if not facts.documented_gaps:
            continue
        form = forms[drawn % len(forms)]
        drawn += 1
        target = build_target(facts, form)
        if not gapped_headings(target):
            # This form does not surface any of the blanked fields; it cannot
            # probe confabulation, so it is not a probe.
            continue
        identified, placed = inject(render(facts, seed=seed + drawn), seed=seed + drawn)
        deid = deidentify_note(identified)
        if leaked_values(deid, [p.value for p in placed]):
            continue
        items.append(
            EvalItem(
                facts=facts,
                form=form,
                document=deid.placeholdered_text,
                known_placeholders=deid.known_placeholders,
                target=target,
            )
        )
    return items


def confabulated(item: EvalItem, draft: str) -> bool:
    """True when the draft asserts content the source does not document.

    A heading the draft omits entirely is a *format* failure, not a
    confabulation, and is left to the format metric.
    """
    draft_sections = sections(draft)
    for heading in gapped_headings(item.target):
        body = draft_sections.get(heading)
        if body is None:
            continue
        stripped = body.strip()
        if stripped and NOT_DOCUMENTED not in stripped.casefold():
            return True
    return False


def confabulation_rate(
    items: Sequence[EvalItem], drafts: Sequence[str]
) -> float | None:
    """Fraction of probes that invented content. ``None`` when uncomputable."""
    if not items or not drafts:
        return None
    pairs = list(zip(items, drafts))
    if not pairs:
        return None
    return sum(confabulated(i, d) for i, d in pairs) / len(pairs)


__all__ = [
    "NOT_DOCUMENTED",
    "confabulated",
    "confabulation_rate",
    "gapped_headings",
    "make_gap_probes",
    "sections",
]
