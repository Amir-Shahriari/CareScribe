"""Display helpers for the patient browser.

Everything here is a plain function over plain data: given the same input it
returns the same output, and nothing touches the store, the filesystem, or
Streamlit. That is what makes the browser testable without a running session --
the Streamlit rendering in ``app.py`` is a thin shell over these.
"""

from __future__ import annotations

from datetime import datetime, timezone

from carescribe.core.patients import FiledDocument, Patient

# The stored ``kind`` values are terse and mean nothing to a clinician.
KIND_LABELS = {
    "text": "Text",
    "word": "Word document",
    "audit": "Review record",
}

# Order the kinds are shown in. A kind not listed here sorts after these, by
# name, so a store that grows a new suffix still renders.
_KIND_ORDER = ["word", "text", "audit"]


def normalise_query(query: str) -> str:
    """Collapse whitespace and strip the ends. Never raises."""
    return " ".join(str(query or "").split())


def filter_patients(patients: list[Patient], query: str) -> list[Patient]:
    """Roster entries whose display name contains ``query``.

    Case-insensitive, matches anywhere in the name, and preserves the caller's
    ordering -- the roster arrives already sorted. An empty or whitespace-only
    query returns everything. Always a new list; the input is never mutated.
    """
    needle = normalise_query(query).casefold()
    if not needle:
        return list(patients)
    return [p for p in patients if needle in normalise_query(p.display_name).casefold()]


def human_size(size_bytes: int) -> str:
    """``1023`` -> "1023 B"; ``1024`` -> "1.0 KB"; ``1048576`` -> "1.0 MB"."""
    try:
        size = float(size_bytes)
    except (TypeError, ValueError):
        return "unknown size"
    if size < 0:
        return "unknown size"
    if size < 1024:
        return f"{int(size)} B"
    for unit in ("KB", "MB", "GB", "TB"):
        size /= 1024.0
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}"
    return f"{size:.1f} TB"  # pragma: no cover - unreachable, loop returns first


def format_modified(iso_timestamp: str) -> str:
    """ISO-8601 UTC -> "2026-09-07 18:41 UTC".

    Returns the input unchanged if it does not parse. A display helper must
    never raise on data that has been sitting on disk since an older version.
    """
    raw = str(iso_timestamp or "")
    try:
        parsed = datetime.fromisoformat(raw)
    except (TypeError, ValueError):
        return raw
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def group_documents_by_kind(
    documents: list[FiledDocument],
) -> dict[str, list[FiledDocument]]:
    """Bucket by ``kind``, dropping nothing and preserving input order.

    Keys are the raw stored kind, not the label -- an unknown kind still gets a
    bucket rather than disappearing.
    """
    grouped: dict[str, list[FiledDocument]] = {}
    for document in documents:
        grouped.setdefault(document.kind, []).append(document)
    return grouped


def kind_label(kind: str) -> str:
    """The clinician-facing name for a stored kind."""
    return KIND_LABELS.get(kind, str(kind or "Other").capitalize())


def ordered_kinds(grouped: dict[str, list[FiledDocument]]) -> list[str]:
    """Kinds present in ``grouped``, in display order."""
    known = [k for k in _KIND_ORDER if k in grouped]
    rest = sorted(k for k in grouped if k not in _KIND_ORDER)
    return known + rest


def document_label(document: FiledDocument) -> str:
    """One display line for a filed artefact."""
    return (
        f"{document.name}"
        f"  ·  {human_size(document.size_bytes)}"
        f"  ·  {format_modified(document.modified_at)}"
    )


def patient_summary(patient: Patient, document_count: int) -> str:
    """One display line for a roster row."""
    if document_count <= 0:
        tail = "no documents"
    elif document_count == 1:
        tail = "1 document"
    else:
        tail = f"{document_count} documents"
    return f"{patient.display_name}  ·  {tail}"


__all__ = [
    "KIND_LABELS",
    "document_label",
    "filter_patients",
    "format_modified",
    "group_documents_by_kind",
    "human_size",
    "kind_label",
    "normalise_query",
    "ordered_kinds",
    "patient_summary",
]
