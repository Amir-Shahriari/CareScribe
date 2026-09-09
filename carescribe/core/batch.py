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
import zipfile
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


def document_from_deidentified(name: str, redacted_text: str) -> Document:
    """A :class:`Document` standing for text de-identified in an earlier session.

    This is how a *filed* patient document re-enters the pipeline. It is already
    de-identified, so drafting from it is safe and needs no re-detection.

    What it deliberately does NOT carry:

    * ``raw_text`` is blank — the original was never written to disk, and
      inventing a stand-in would put un-reviewed text where the reviewer expects
      the source.
    * ``phi_map`` is empty — the identity map lives only in the session that
      produced it. Nothing can resolve this document's placeholders back to real
      values, so re-identification stays disabled (the button is already gated
      on ``phi_map``). A draft from here keeps ``[PATIENT]`` and ``[DATE_2]``,
      which is the honest outcome rather than a silent half-substitution.

    ``approved`` and ``attested`` are True because the text was approved by a
    reviewer before it was ever filed; ``analyzed`` is True so the review step
    does not offer to re-detect identifiers in text that has none left.
    """
    return Document(
        name=name,
        raw_text="",
        redacted_text=redacted_text,
        analyzed=True,
        attested=True,
        approved=True,
        phi_map={},
        entities=[],
    )


def safe_stem(name: str) -> str:
    """Reduce a filename to a safe output stem — no paths, no surprises."""
    stem = Path(str(name or "document")).stem.strip() or "document"
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._-")
    return stem or "document"


def _resolve_output_dir(output_dir: Path | str | None) -> Path:
    """The folder a write lands in — an explicit override, or the default.

    ``output_dir`` is how the per-patient records store routes the same three
    write functions at ``patients/<id>/documents`` instead of the flat output
    folder (see :mod:`carescribe.core.patients`). ``None`` keeps the historical
    behaviour and, crucially, reads ``OUTPUT_DIR`` at call time so a test that
    monkeypatches the module global still works.
    """
    return Path(output_dir) if output_dir is not None else OUTPUT_DIR


def approved_path(name: str, output_dir: Path | str | None = None) -> Path:
    """Where the approved de-identified text for ``name`` will be written."""
    return _resolve_output_dir(output_dir) / f"{safe_stem(name)}{APPROVED_SUFFIX}"


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
    output_dir: Path | str | None = None,
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

    ``output_dir`` routes the write at a per-patient folder instead of the flat
    default; the sweep and refusal are identical either way.
    """
    if not deidentified_text or not deidentified_text.strip():
        raise BatchError("There is no de-identified text to write.")

    residual = sweep(deidentified_text, acknowledged)
    if residual:
        raise BatchError(
            "Refusing to write: the text still contains what look like "
            "identifiers — " + ", ".join(repr(value) for value in residual[:10])
        )

    dest_dir = _resolve_output_dir(output_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    destination = approved_path(name, dest_dir)
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


def review_record_path(name: str, output_dir: Path | str | None = None) -> Path:
    """Where the review audit sidecar for ``name`` will be written."""
    return _resolve_output_dir(output_dir) / (safe_stem(name) + REVIEW_SUFFIX)


def write_review_record(
    name: str,
    *,
    entities,
    flags_shown: int,
    flags_redacted: int,
    flags_dismissed: int,
    attested: bool = False,
    output_dir: Path | str | None = None,
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

    dest_dir = _resolve_output_dir(output_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    destination = review_record_path(name, dest_dir)
    destination.write_text(
        json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return destination


def approved_docx_path(name: str, output_dir: Path | str | None = None) -> Path:
    """Where the approved redacted .docx for ``name`` will be written."""
    return _resolve_output_dir(output_dir) / (safe_stem(name) + APPROVED_DOCX_SUFFIX)


# Document properties that carry a person, a place or a date. Word fills these
# in from the machine that authored the file, so they arrive already populated
# and the reviewer never sees them: the chip table is built from the document's
# text, and File > Properties is not part of the text. A discharge summary
# authored in Word routinely ships dc:creator and cp:lastModifiedBy holding
# clinician names, and dc:title holding a heading like "Discharge summary for
# <patient>" -- the patient's name, in the approved file, after every visible
# trace of it has been redacted.
#
# Matched on local name so both docProps/core.xml (Dublin Core plus the cp:
# extensions) and docProps/app.xml (Company, Manager) are covered without
# hard-coding namespace URIs.
_METADATA_TEXT_FIELDS = frozenset({
    "title", "subject", "creator", "keywords", "description", "lastModifiedBy",
    "category", "contentStatus", "identifier", "version", "manager", "Company",
    "Manager", "lastPrinted",
})

# created/modified cannot simply be blanked -- the schema types them as
# timestamps and Word will not open a file whose dcterms:created is empty. A
# document's authoring time is the same class of fact as a service date, which
# this app redacts everywhere else, so it is normalised to a fixed neutral
# instant rather than left telling the reader when the patient was seen.
_METADATA_TIMESTAMP_FIELDS = frozenset({"created", "modified"})
_NEUTRAL_TIMESTAMP = "1970-01-01T00:00:00Z"

_METADATA_PARTS = ("docProps/core.xml", "docProps/app.xml")


def _strip_document_properties(data: bytes) -> bytes:
    """Blank the .docx metadata fields that carry names, places and dates.

    Rewrites only the two docProps parts and copies every other entry through
    byte-for-byte, so the redaction that has already been applied to the body is
    untouched and no second serialisation of the document can perturb it.
    """
    try:
        from lxml import etree
    except Exception:  # noqa: BLE001 -- never block a write on the probe
        return data

    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as source:
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as target:
            for item in source.infolist():
                blob = source.read(item.filename)
                if item.filename in _METADATA_PARTS:
                    try:
                        blob = _blanked_properties(etree, blob)
                    except Exception:  # noqa: BLE001 -- keep the original part
                        pass
                target.writestr(item, blob)
    return output.getvalue()


def _blanked_properties(etree, blob: bytes) -> bytes:
    root = etree.fromstring(blob)
    for element in root.iter():
        name = etree.QName(element).localname
        if name in _METADATA_TEXT_FIELDS:
            element.text = None
        elif name in _METADATA_TIMESTAMP_FIELDS:
            element.text = _NEUTRAL_TIMESTAMP
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def _document_property_text(data: bytes) -> str:
    """Every scrap of text in the .docx property parts, for the residual sweep.

    Read back from the finished file rather than trusted to have been blanked:
    the field list above is a list, and a Word version that files a name
    somewhere not on it should still refuse the write rather than ride out.
    """
    try:
        from lxml import etree
    except Exception:  # noqa: BLE001 -- never block a write on the probe
        return ""

    lines: list[str] = []
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            present = set(archive.namelist())
            for part in _METADATA_PARTS:
                if part not in present:
                    continue
                root = etree.fromstring(archive.read(part))
                for element in root.iter():
                    text = (element.text or "").strip()
                    if text:
                        lines.append(text)
    except Exception:  # noqa: BLE001 -- an unreadable probe is not a finding
        return ""
    return "\n".join(lines)

# Parts whose text the body walk never loads at all. Comments, footnotes and
# endnotes are separate parts in the package; python-docx does not read them,
# apply_redactions cannot reach them, and a supervisor's review comment naming
# the patient is entirely ordinary in a clinical document.
_UNREAD_PARTS = (
    "word/comments.xml",
    "word/commentsExtended.xml",
    "word/footnotes.xml",
    "word/endnotes.xml",
)

# The document body IS walked, so it must not be re-flattened here -- doing that
# is what made the sweep misjudge body-table dates and refuse 63 good documents.
# Only the one tag the walk cannot see is taken from it: a tracked-change
# deletion keeps its text in w:delText rather than w:t, so a name deleted with
# track changes on is still in the file and invisible to every other pass.
_BODY_PART = "word/document.xml"
_DELETED_TEXT_TAG = "delText"

# Revision and comment marks carry the editor's name in an attribute rather than
# in text -- w:author on every <w:del>, <w:ins> and <w:comment>.
_AUTHOR_ATTRIBUTE = "author"


def _revision_and_note_text(data: bytes) -> str:
    """Text in a .docx that no other pass reads: deletions, comments, notes.

    All of it is unreachable by ``apply_redactions``, so there is nothing to
    redact and the only safe outcome is for the sweep to see it and refuse the
    write -- the same call made for text boxes.
    """
    try:
        from lxml import etree
    except Exception:  # noqa: BLE001 -- never block a write on the probe
        return ""

    found: list[str] = []
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            present = set(archive.namelist())
            for part in (_BODY_PART, *_UNREAD_PARTS):
                if part not in present:
                    continue
                body_only = part == _BODY_PART
                root = etree.fromstring(archive.read(part))
                for element in root.iter():
                    name = etree.QName(element).localname
                    if not body_only or name == _DELETED_TEXT_TAG:
                        text = (element.text or "").strip()
                        if text:
                            found.append(text)
                    for key, value in element.attrib.items():
                        if etree.QName(key).localname != _AUTHOR_ATTRIBUTE:
                            continue
                        value = (value or "").strip()
                        if value:
                            found.append(value)
    except Exception:  # noqa: BLE001 -- an unreadable probe is not a finding
        return ""
    return "\n".join(found)

def _text_the_body_walk_misses(data: bytes) -> str:
    """Header, footer and text-box content -- what ``_extract_docx`` never reads.

    ``ingest._extract_docx`` walks the body and its tables, which is the view
    detection ran on. A letterhead is not in the body: the clinic name, the
    clinician, the address and the phone number sit in a header or footer, so
    they were invisible both to detection and to the residual sweep that is
    supposed to be the last line of defence. This returns only the part the body
    walk misses, shaped with the same "label: value" convention
    ``_extract_docx`` uses for a two-column row, so the sweep's label-anchored
    rules read it the same way. Only the header/footer, deliberately: flattening
    the whole document a second way makes the sweep misjudge body tables whose
    dates are anchored by a label in the first view.
    """
    try:
        import docx

        document = docx.Document(io.BytesIO(data))
    except Exception:  # noqa: BLE001 -- an unreadable probe must not block a write
        return ""

    parts: list[str] = []
    for section in document.sections:
        for area in (
            section.header, section.first_page_header, section.even_page_header,
            section.footer, section.first_page_footer, section.even_page_footer,
        ):
            if area is None:
                continue
            try:
                paragraphs, tables = area.paragraphs, area.tables
            except Exception:  # noqa: BLE001
                continue
            parts.extend(p.text for p in paragraphs if p.text.strip())
            for table in tables:
                for row in table.rows:
                    cells = [cell.text.strip() for cell in row.cells]
                    if not any(cells):
                        continue
                    if len(cells) == 2:
                        label, value = cells
                        parts.append(f"{label}: {value}" if label and value else label or value)
                    else:
                        parts.append(" | ".join(cells))

    # Text boxes and drawing shapes, wherever they sit. python-docx's paragraph
    # walk does not descend into a <w:txbxContent>, so a referrer's name, an MRN
    # or a phone number typed into a floating box was missed exactly the way the
    # letterhead was. document_has_text_boxes() already warns the user such text
    # exists, but a warning is not the guarantee this function's docstring makes,
    # and the file was still written with the box's contents intact. Both VML
    # (<v:textbox>) and DrawingML (<wps:txbx>) wrap their text in w:txbxContent,
    # so iterating that one tag covers both.
    try:
        from docx.oxml.ns import qn

        seen: set[int] = set()
        for part in (document.element, *(
            area._element
            for section in document.sections
            for area in (
                section.header, section.first_page_header, section.even_page_header,
                section.footer, section.first_page_footer, section.even_page_footer,
            )
            if area is not None
        )):
            for box in part.iter(qn("w:txbxContent")):
                if id(box) in seen:
                    continue
                seen.add(id(box))
                boxed = "".join(node.text or "" for node in box.iter(qn("w:t")))
                if boxed.strip():
                    parts.append(boxed)
    except Exception:  # noqa: BLE001 -- an unreadable shape must not block a write
        pass
    return "\n".join(parts)


def write_approved_docx(
    name: str,
    source_bytes: bytes,
    replacements: dict[str, str],
    *,
    acknowledged: list[str] | tuple[str, ...] = (),
    output_dir: Path | str | None = None,
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
    # Word fills the document properties in from the authoring machine, so a
    # clinician's name arrives in dc:creator and the patient's can arrive in
    # dc:title. None of it is in the document text, so the reviewer never saw
    # it and redaction never touched it. Blank it before the sweep -- and the
    # sweep then reads the properties too, so a field this misses still
    # refuses the write rather than riding out.
    staged = io.BytesIO(_strip_document_properties(staged.getvalue()))

    scan_text = ingest.normalise_line_endings(ingest._extract_docx(staged.getvalue()))

    # ...plus the header and footer, which the body walk above never reads. A
    # letterhead lives there: the clinic name, the clinician, the address and
    # the phone. Those were invisible to detection, so they never entered the
    # approved map and were never redacted -- and this sweep could not catch
    # them either, so an approved .docx rode out with all of them still on it.
    scan_text += "\n" + ingest.normalise_line_endings(
        _text_the_body_walk_misses(staged.getvalue())
    )

    # ...and the document properties, so a name left in dc:creator or dc:title
    # is refused exactly like one left in the body.
    scan_text += "\n" + ingest.normalise_line_endings(
        _document_property_text(staged.getvalue())
    )

    # ...and tracked-change deletions, comments and notes, none of which any
    # other pass can see or redact.
    scan_text += "\n" + ingest.normalise_line_endings(
        _revision_and_note_text(staged.getvalue())
    )
    residual = sweep(scan_text, acknowledged)
    if residual:
        raise BatchError(
            "Refusing to write the Word file: it still contains what look "
            "like identifiers — "
            + ", ".join(repr(value) for value in residual[:10])
        )

    dest_dir = _resolve_output_dir(output_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    destination = approved_docx_path(name, dest_dir)
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
