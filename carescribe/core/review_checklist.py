"""
The adaptive reviewer checklist.

A checklist only works if it is short enough to read. A fixed ten-point list
gets ticked without being read, which is worse than no list at all — it
manufactures evidence of a review that did not happen. So this builds only the
items a given document actually earns: a plain note gets two, a document with a
table, relatives and a text box gets those and no more.

The heavy lifting is the highlighter in :mod:`.review_flags`. The checklist
states the affirmations a reviewer is making; the highlighter is what points at
the specific spans.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import review_flags

# A document with more than a handful of tabular rows is a form, and form values
# are where a label and its value get separated.
_TABLE_ROW = re.compile(r"^[^\n:]{1,40}:[ \t]+\S|^\s*\S.*\|.*\S\s*$", re.MULTILINE)
_LETTERHEAD_LINES = 6


@dataclass(frozen=True)
class ChecklistItem:
    """One affirmation the reviewer must make before approval unlocks."""

    key: str
    label: str
    # True when the system can confirm the item itself; the reviewer still has
    # to tick it, but a False value means it cannot yet be ticked truthfully.
    auto_satisfied: bool = True
    hint: str = ""


@dataclass
class DocFeatures:
    """What a document contains, which decides what it must be checked for."""

    has_table: bool = False
    has_header_footer: bool = False
    has_textbox: bool = False
    has_relatives: bool = False
    has_dates: bool = False
    has_ids: bool = False
    n_candidate_flags: int = 0
    flags_outstanding: int = 0
    extras: dict = field(default_factory=dict)


def describe(
    document,
    flags: list | None = None,
    dismissed: list[str] | tuple[str, ...] = (),
) -> DocFeatures:
    """Derive the feature set from a loaded, analysed document."""
    raw = getattr(document, "raw_text", "") or ""
    redacted = getattr(document, "redacted_text", "") or ""
    entities = getattr(document, "entities", []) or []

    if flags is None:
        flags = review_flags.candidate_residuals(redacted)
    remaining = review_flags.outstanding(list(flags), dismissed)

    types = {str(e.get("type", "")) for e in entities}
    lines = raw.splitlines()

    return DocFeatures(
        has_table=len(_TABLE_ROW.findall(raw)) >= 3,
        # A letterhead and a sign-off block, which only exist as distinct things
        # if the document is long enough for the two regions not to overlap. A
        # three-line note trivially has "content in its first and last lines",
        # and asking a reviewer to check its header is the kind of item that
        # teaches them the list is noise.
        has_header_footer=(
            len(lines) > _LETTERHEAD_LINES * 2
            and any(line.strip() for line in lines[:_LETTERHEAD_LINES])
            and any(line.strip() for line in lines[-_LETTERHEAD_LINES:])
        ),
        has_textbox=bool(getattr(document, "has_text_boxes", False)),
        has_relatives="RELATIVE_NAME" in types,
        has_dates=bool({"DATE", "DOB"} & types),
        has_ids=bool({"MRN", "NHS_NUMBER", "CPA_NO", "OTHER_ID"} & types),
        n_candidate_flags=len(flags),
        flags_outstanding=len(remaining),
    )


def build_checklist(doc_features: DocFeatures) -> list[ChecklistItem]:
    """The affirmations this document requires — and only those."""
    features = doc_features
    items: list[ChecklistItem] = [
        ChecklistItem(
            key="read_full",
            label="I have read the full redacted text, not just the fields.",
        )
    ]

    outstanding = features.flags_outstanding
    items.append(
        ChecklistItem(
            key="flags_cleared",
            label="Every remaining highlighted span has been checked "
            "(redacted or dismissed).",
            auto_satisfied=outstanding == 0,
            hint=(
                ""
                if outstanding == 0
                else f"{outstanding} highlighted span(s) still need a decision."
            ),
        )
    )

    if features.has_table:
        items.append(
            ChecklistItem(
                key="table_cells",
                label="I checked every table cell value, including IDs split "
                "from their labels.",
            )
        )
    if features.has_header_footer:
        items.append(
            ChecklistItem(
                key="header_footer",
                label="I checked the header and footer (clinic, location, "
                "'typed by' staff).",
            )
        )
    if features.has_relatives:
        items.append(
            ChecklistItem(
                key="relatives",
                label="Each relative is a distinct person and the patient is "
                "not mislabelled as one.",
            )
        )
    if features.has_textbox:
        items.append(
            ChecklistItem(
                key="textboxes",
                label="Text boxes / shapes are reviewed manually — "
                "auto-redaction does not reach them.",
                hint="This is the same acknowledgement the Word output requires.",
            )
        )
    if features.has_dates:
        items.append(
            ChecklistItem(
                key="dates",
                label="Appointment, admission and contact dates are redacted "
                "where identifying.",
            )
        )
    return items


def blocking_reason(
    items: list[ChecklistItem],
    ticked: set[str] | dict,
    residual: list[str],
    flags_outstanding: int,
) -> str:
    """Why Approve is disabled, in one short line. Empty string means it isn't."""
    if residual:
        return f"The safety sweep found {len(residual)} finding(s) to resolve."
    if flags_outstanding:
        return (
            f"{flags_outstanding} highlighted span(s) still need to be "
            "redacted or dismissed."
        )
    missing = [item for item in items if item.key not in set(ticked)]
    if missing:
        return f"{len(missing)} of {len(items)} checklist item(s) not yet confirmed."
    return ""


__all__ = [
    "ChecklistItem",
    "DocFeatures",
    "blocking_reason",
    "build_checklist",
    "describe",
]
