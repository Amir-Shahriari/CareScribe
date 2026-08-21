"""
Unifies the two things a reviewer might still need to act on in one
document's redacted text into one clickable, ordered list.

The two sources are different in kind. A low-confidence *entity* was already
found and already redacted (confidence tiering just isn't sure about it) —
the reviewer is confirming or correcting a placeholder that is already safe.
A *residual* candidate (:mod:`.review_flags`) is the opposite: raw text the
layers missed entirely, still sitting un-redacted in what is nominally
"redacted" text. Both need a human decision; this module is only the part
that merges them into one span list so the UI has a single thing to render.

Kept separate from :mod:`.review_flags` on purpose: that module's job is the
permissive text-pattern sweep itself, one thing done well. This module's job
is purely the merge.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import mapping, review_flags

KIND_ENTITY = "entity"
KIND_RESIDUAL = "residual"


@dataclass(frozen=True)
class ReviewSpan:
    """One clickable span in a document's redacted text."""

    id: str
    char_start: int
    char_end: int
    kind: str  # KIND_ENTITY or KIND_RESIDUAL
    text: str  # the placeholder ("[PATIENT_2]") for an entity span,
    # the raw candidate text for a residual span
    why: str
    entity_type: str = ""  # set for KIND_ENTITY only
    flag_kind: str = ""  # set for KIND_RESIDUAL only — review_flags.KIND_*


def _entity_spans(
    redacted_text: str, entities: list[dict], confirmed: set[str]
) -> list[ReviewSpan]:
    """Placeholder occurrences for low-confidence, not-yet-confirmed entities."""
    spans: list[ReviewSpan] = []
    for entity in entities:
        if mapping.normalise_action(entity.get("action")) != mapping.REDACT:
            continue
        if str(entity.get("confidence") or "review") != "review":
            continue
        value_key = str(entity.get("value", "")).strip().casefold()
        if not value_key or value_key in confirmed:
            continue
        placeholder = str(entity.get("placeholder", "") or "")
        if not placeholder:
            continue
        entity_type = str(entity.get("type", "OTHER_ID"))
        start = 0
        while True:
            found = redacted_text.find(placeholder, start)
            if found == -1:
                break
            spans.append(
                ReviewSpan(
                    id=f"entity:{value_key}",
                    char_start=found,
                    char_end=found + len(placeholder),
                    kind=KIND_ENTITY,
                    text=placeholder,
                    why=f"detected as {entity_type} by a single layer — worth a second look",
                    entity_type=entity_type,
                )
            )
            start = found + len(placeholder)
    return spans


def _residual_spans(
    redacted_text: str, dismissed: list[str] | tuple[str, ...]
) -> list[ReviewSpan]:
    flags = review_flags.outstanding(
        review_flags.candidate_residuals(redacted_text), dismissed
    )
    return [
        ReviewSpan(
            id=f"residual:{flag.key}",
            char_start=flag.char_start,
            char_end=flag.char_end,
            kind=KIND_RESIDUAL,
            text=flag.text,
            why=flag.why,
            flag_kind=flag.kind,
        )
        for flag in flags
    ]


def review_spans(
    redacted_text: str,
    entities: list[dict],
    confirmed: set[str],
    dismissed: list[str] | tuple[str, ...] = (),
) -> list[ReviewSpan]:
    """Every clickable span in ``redacted_text``, in reading order.

    ``confirmed`` is the set of (casefolded) entity values the reviewer has
    already clicked "Confirm" on for this document. ``dismissed`` is the
    existing per-document dismissed-residual-flag list
    (:func:`carescribe.app.flag_dismissals`), unchanged from today.
    """
    spans = _entity_spans(redacted_text, entities, confirmed)
    spans.extend(_residual_spans(redacted_text, dismissed))
    spans.sort(key=lambda span: span.char_start)
    return spans


__all__ = ["KIND_ENTITY", "KIND_RESIDUAL", "ReviewSpan", "review_spans"]
