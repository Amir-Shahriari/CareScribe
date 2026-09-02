"""
Batch input and approved-output handling.

The single module in CareScribe that writes to the filesystem, which is what
makes the privacy invariant checkable — the write paths can be enumerated by
reading one file. There are three, and all of them refuse PHI:

* :func:`write_approved` — the approved de-identified text.
* :func:`write_approved_docx` — the redacted Word document. Redaction runs
  entirely in memory: staging the original through a temp file would put the
  un-redacted document on disk, so it never happens.
* :func:`write_review_record` — the audit sidecar, which holds counts and types
  and no identifier value at all.

The first two re-run :func:`~carescribe.core.deidentify.residual_scan` over what
they are about to write and refuse if anything identifying survives.

Reading is separate and read-only — :func:`load_documents` pulls documents into
memory but never writes a copy of them anywhere.
"""

from __future__ import annotations

import io
import json
import os
import re
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path

from . import deidentify, docx_redact, ingest, mapping

# carescribe/core/batch.py -> carescribe/
_PACKAGE_ROOT = Path(__file__).resolve().parent.parent

def _default_output_dir() -> Path:
    """Where approved output lands.

    In a source checkout that is ``carescribe/output/deidentified``. In the
    packaged desktop app it is a per-user app-data directory, because the
    executable may sit somewhere unwritable (``C:\\Program Files``) or inside a
    signed ``.app`` bundle whose contents must not change. The launcher sets the
    environment variable; nothing else needs to know which case it is in.
    """
    override = (os.environ.get("CARESCRIBE_OUTPUT_DIR") or "").strip()
    if override:
        return Path(override)
    return _PACKAGE_ROOT / "output" / "deidentified"


OUTPUT_DIR = _default_output_dir()

# Approved files get this suffix so a de-identified copy is never mistaken for
# a source document sitting in the same folder.
APPROVED_SUFFIX = ".deid.txt"

# The Word equivalent. A redacted .docx keeps the original's tables, styles and
# headers, so a clinician gets back a document that still looks like the one
# they sent.
APPROVED_DOCX_SUFFIX = ".deid.docx"

# The audit sidecar. Counts and types only — never a value, never the mapping.
REVIEW_SUFFIX = ".review.json"


class BatchError(RuntimeError):
    """Raised for input-folder and output-write problems."""


@dataclass
class Document:
    """One document's state for the whole review pass.

    Everything here except :attr:`redacted_text` is PHI or PHI-derived and lives
    only in ``st.session_state``. Only :attr:`redacted_text` is ever written.
    """

    name: str
    raw_text: str
    # The original bytes, kept so an approved .docx can be redacted into a copy
    # of the real document rather than rebuilt from flattened text. PHI, and
    # like every other field here it lives only in session state.
    source_bytes: bytes | None = None
    has_text_boxes: bool = False
    text_boxes_acknowledged: bool = False
    # The reviewer has ticked "I have read the redacted preview and confirm it
    # is safe to release." Gates approval; recorded (as a bool, no PHI) in the
    # audit sidecar.
    attested: bool = False
    approved_docx_path: str = ""
    entities: list[dict] = field(default_factory=list)
    redacted_text: str = ""
    phi_map: dict[str, str] = field(default_factory=dict)  # placeholder -> original
    known_as: str | None = None
    analyzed: bool = False
    approved: bool = False
    approved_path: str = ""
    residual: list[str] = field(default_factory=list)
    dismissed: list[str] = field(default_factory=list)  # sweep findings reviewed and cleared
    error: str = ""


def safe_stem(name: str) -> str:
    """Reduce a filename to a safe output stem — no paths, no surprises."""
    stem = Path(str(name or "document")).stem.strip() or "document"
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._-")
    return stem or "document"


def approved_path(name: str) -> Path:
    """Where the approved de-identified text for ``name`` will be written."""
    return OUTPUT_DIR / f"{safe_stem(name)}{APPROVED_SUFFIX}"


def list_folder(folder: str | Path) -> list[Path]:
    """Return the supported documents in ``folder``, sorted by name.

    Non-recursive on purpose: a reviewer points at one batch, not a tree they
    might not have looked inside.
    """
    path = Path(str(folder)).expanduser()
    if not path.exists():
        raise BatchError(f"No such folder: {path}")
    if not path.is_dir():
        raise BatchError(f"Not a folder: {path}")

    found = [
        child
        for child in sorted(path.iterdir(), key=lambda p: p.name.lower())
        if child.is_file()
        and child.suffix.lower().lstrip(".") in ingest.SUPPORTED_EXTENSIONS
        and not child.name.endswith(APPROVED_SUFFIX)
    ]
    if not found:
        raise BatchError(
            f"{path} contains no {', '.join(ingest.SUPPORTED_EXTENSIONS)} files."
        )
    return found


def _source_bytes(source) -> bytes | None:
    """The raw bytes behind an upload or a path, without copying it to disk."""
    if hasattr(source, "getvalue"):
        return source.getvalue()
    if hasattr(source, "read"):
        if hasattr(source, "seek"):
            source.seek(0)
        data = source.read()
        if hasattr(source, "seek"):
            source.seek(0)
        return data
    path = Path(str(source))
    return path.read_bytes() if path.is_file() else None


def load_documents(sources: list) -> tuple[dict[str, Document], list[str]]:
    """Extract text from uploads or paths. Returns ``(documents, errors)``.

    One unreadable file does not sink the batch — it is reported and the rest
    are loaded.
    """
    documents: dict[str, Document] = {}
    errors: list[str] = []

    for source in sources:
        name = getattr(source, "name", None) or Path(str(source)).name
        try:
            text = ingest.extract_text(source)
        except ingest.IngestError as exc:
            errors.append(f"{name}: {exc}")
            continue
        if name in documents:
            errors.append(f"{name}: duplicate filename in this batch — skipped.")
            continue

        # Keep the original bytes for a .docx so the approved redaction can be
        # applied to a copy of the real file, preserving its tables and styles,
        # instead of being rebuilt from flattened text.
        source_bytes = None
        if name.lower().endswith(".docx"):
            try:
                source_bytes = _source_bytes(source)
            except Exception:  # noqa: BLE001 — text still works without it
                source_bytes = None

        documents[name] = Document(
            name=name,
            raw_text=text,
            source_bytes=source_bytes,
            has_text_boxes=document_has_text_boxes(source_bytes),
        )

    return documents, errors


def analyze_document(document: Document) -> Document:
    """Run the de-identification layers over one document, in place."""
    try:
        result = deidentify.deidentify(document.raw_text)
    except deidentify.DeidentificationError as exc:
        document.error = str(exc)
        document.analyzed = True
        return document

    document.entities = result.entities
    document.redacted_text = result.redacted_text
    document.phi_map = result.phi_map
    document.known_as = result.known_as
    document.analyzed = True
    document.error = ""
    document.approved = False
    return document


def sweep(deidentified_text: str, acknowledged: list[str] | tuple[str, ...] = ()) -> list[str]:
    """Findings from the safety sweep, minus the ones the reviewer has cleared.

    A place name the pipeline deliberately preserved ("Leeds", "Bolton") will
    be flagged by the PERSON check — spaCy labels towns as people as readily as
    it labels them places. Without a way to clear such a finding the reviewer's
    only route past the gate would be to over-redact it, which is exactly the
    failure the precision rules exist to avoid. Clearing is per-string and per
    document, and is never persisted.
    """
    cleared = {value.casefold() for value in acknowledged}
    return [
        value
        for value in deidentify.residual_scan(deidentified_text)
        if value.casefold() not in cleared
    ]


def write_approved(
    name: str,
    deidentified_text: str,
    *,
    acknowledged: list[str] | tuple[str, ...] = (),
) -> Path:
    """Write approved de-identified text to the output folder.

    Re-runs the safety sweep and refuses the write if anything identifying
    survives. The UI checks first and shows the findings; this check exists so
    the guarantee does not depend on the UI having done so.

    ``acknowledged`` lists findings the reviewer has explicitly looked at and
    cleared. It carries no PHI — every string in it is one the reviewer read in
    the *de-identified* text. The identity mapping is not a parameter here and
    no caller can make it one: the only thing that reaches disk is the text
    passed in.
    """
    if not deidentified_text or not deidentified_text.strip():
        raise BatchError("There is no de-identified text to write.")

    residual = sweep(deidentified_text, acknowledged)
    if residual:
        raise BatchError(
            "Refusing to write: the text still contains what look like "
            "identifiers — " + ", ".join(repr(value) for value in residual[:10])
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    destination = approved_path(name)
    destination.write_text(deidentified_text, encoding="utf-8")
    return destination


def approved_map(entities, known_as: str | None = None) -> dict[str, str]:
    """The reviewer-approved ``{literal: placeholder}`` map for the Word pass.

    This is built from the *approved* entity table — everything the reviewer
    added, minus everything they set to Keep — and expanded into every surface
    form of each identity (full name, first name, title+surname, initials,
    alias). Detection is deliberately not re-run: the Word file has to match
    what the human signed off, and a second detection pass could differ from the
    text they previewed.

    Longest literal first, so a shorter form can never consume part of a longer
    one during replacement.
    """
    expanded = mapping.surface_forms(list(entities), known_as)
    literals: dict[str, str] = {}
    for placeholder, forms in expanded.by_placeholder.items():
        for form in forms:
            form = form.strip()
            if len(form) >= mapping.MIN_VALUE_LENGTH:
                literals.setdefault(form, placeholder)
    return dict(sorted(literals.items(), key=lambda kv: len(kv[0]), reverse=True))


def review_record_path(name: str) -> Path:
    """Where the review audit sidecar for ``name`` will be written."""
    return OUTPUT_DIR / (safe_stem(name) + REVIEW_SUFFIX)


def write_review_record(
    name: str,
    *,
    entities,
    flags_shown: int,
    flags_redacted: int,
    flags_dismissed: int,
    attested: bool = False,
) -> Path:
    """Write the no-PHI audit sidecar for one approved document.

    Evidence that a consistent review happened, and nothing more. It records
    *counts* and *types*: how many redacted identifiers were auto-resolved by
    confidence tiering versus actually reviewed by the practitioner, how many
    highlighted residual spans were shown and what became of them, how many
    placeholders of each type the document ended up with, and whether the
    reviewer ticked the read-and-confirmed attestation.

    It deliberately holds no identifier value, no placeholder-to-value mapping,
    and no document text. There is no parameter through which one could reach
    it — the entity values are counted here and discarded, never written.
    """
    tally: dict[str, int] = {}
    auto_redacted = 0
    reviewed_redacted = 0
    for entity in entities or []:
        entity_type = str(entity.get("type", "") or "OTHER_ID")
        if mapping.normalise_action(entity.get("action")) != mapping.REDACT:
            continue
        tally[entity_type] = tally.get(entity_type, 0) + 1
        if str(entity.get("confidence", "review")) == "auto":
            auto_redacted += 1
        else:
            reviewed_redacted += 1

    record = {
        "document": Path(name).name,
        "reviewed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "identifiers_auto_redacted": auto_redacted,
        "identifiers_reviewed_by_practitioner": reviewed_redacted,
        "candidate_flags": {
            "shown": int(flags_shown),
            "redacted": int(flags_redacted),
            "dismissed": int(flags_dismissed),
        },
        "placeholders_by_type": dict(sorted(tally.items())),
        "reviewer_attested": bool(attested),
        "contains_phi": False,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    destination = review_record_path(name)
    destination.write_text(
        json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return destination


def approved_docx_path(name: str) -> Path:
    """Where the approved redacted .docx for ``name`` will be written."""
    return OUTPUT_DIR / (safe_stem(name) + APPROVED_DOCX_SUFFIX)


def write_approved_docx(
    name: str,
    source_bytes: bytes,
    replacements: dict[str, str],
    *,
    acknowledged: list[str] | tuple[str, ...] = (),
) -> Path:
    """Redact the original .docx into the output folder, structure preserved.

    The same bar as the text path: the written file is re-scanned through
    :func:`sweep` and deleted again if anything identifying survives. A
    placeholder mangled inside a run, or a value the approved map did not cover,
    must not ride out inside the document.

    Only the redacted document reaches disk. The mapping is an argument, never
    an output.
    """
    if not source_bytes:
        raise BatchError("The original document is no longer in memory — reload it.")
    if not replacements:
        raise BatchError("There is nothing approved to redact.")

    # Everything happens in memory. Staging the original through a temp file
    # would put the un-redacted document on disk — briefly, in the system temp
    # directory, and not at all if the process died mid-way — which would break
    # the invariant that the only thing this app ever writes is de-identified.
    staged = io.BytesIO()
    try:
        docx_redact.apply_redactions(io.BytesIO(source_bytes), staged, replacements)
    except Exception as exc:  # noqa: BLE001 — any failure must not write
        raise BatchError(f"The document could not be redacted: {exc}") from exc

    # Scan the finished document the same way it was read in, so the sweep sees
    # a details table as "label: value" exactly as detection did. Normalise
    # line endings the same way extract_text() does — this is a direct call
    # to the extractor, not extract_text() itself, so it does not get that
    # normalisation for free; without it, a raw \r left in a run's text (real
    # XML content, not a paragraph break) can hide an identifier from the
    # \n-anchored patterns this scan relies on.
    scan_text = ingest.normalise_line_endings(ingest._extract_docx(staged.getvalue()))
    residual = sweep(scan_text, acknowledged)
    if residual:
        raise BatchError(
            "Refusing to write the Word file: it still contains what look "
            "like identifiers — "
            + ", ".join(repr(value) for value in residual[:10])
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    destination = approved_docx_path(name)
    destination.write_bytes(staged.getvalue())
    return destination


def document_has_text_boxes(source_bytes: bytes | None) -> bool:
    """True if a .docx holds text this redaction pass cannot reach."""
    if not source_bytes:
        return False
    try:
        return docx_redact.has_unreachable_text(io.BytesIO(source_bytes))
    except Exception:  # noqa: BLE001 — an unreadable probe is not a warning
        return False


__all__ = [
    "APPROVED_DOCX_SUFFIX",
    "REVIEW_SUFFIX",
    "review_record_path",
    "write_review_record",
    "APPROVED_SUFFIX",
    "OUTPUT_DIR",
    "approved_docx_path",
    "approved_map",
    "document_has_text_boxes",
    "write_approved_docx",
    "BatchError",
    "Document",
    "analyze_document",
    "approved_path",
    "list_folder",
    "load_documents",
    "safe_stem",
    "sweep",
    "write_approved",
]
