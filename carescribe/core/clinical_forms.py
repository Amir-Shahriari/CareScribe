"""
Fill the three bundled APS clinical form templates from approved,
de-identified source documents.

Each template's fillable cells are discovered by walking its real table
structure (see docs/superpowers/specs/2026-08-13-clinical-forms-design.md),
not hand-transcribed, because merged cells make column indices unreliable
by eye. Generation asks the model for one delimited block of text per
discovered field; nothing here decides what counts as a field at
generation time — that was fixed when the spec was built from the asset.
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import docx

from . import mapping as _mapping  # PLACEHOLDER_RE, reused rather than reimplemented

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


class ClinicalFormError(RuntimeError):
    """Raised when a clinical form can't be built or filled."""


def slugify(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


@dataclass(frozen=True)
class FormField:
    key: str
    label: str
    table_index: int
    value_row_index: int
    value_col_index: int
    append_after_label: bool


@dataclass(frozen=True)
class HeaderField:
    key: str
    label: str
    table_index: int
    row_index: int
    col_index: int
    style: str  # "inline" (append to the label's own paragraph) or "append"
                # (new paragraph(s) after the label, same cell)


@dataclass(frozen=True)
class FormSpec:
    form_id: str
    title: str
    asset_path: Path
    header_fields: list[HeaderField]
    fields: list[FormField]


def _dedupe_row(row):
    """Deduplicate a row's cells by underlying XML element identity.

    python-docx reports a merged cell once per grid column it spans, so a
    naive ``row.cells`` walk sees the same cell 2-3 times. Comparing
    ``id(cell._tc)`` collapses those back into one logical cell per visual
    box, in left-to-right order.
    """
    seen: set[int] = set()
    cells = []
    for cell in row.cells:
        key = id(cell._tc)
        if key not in seen:
            seen.add(key)
            cells.append(cell)
    return cells


def _paragraph_texts(cell) -> list[str]:
    return [p.text for p in cell.paragraphs]


def _walk_table(table, table_index: int, start_row: int, header_seed: str = "") -> list[FormField]:
    fields: list[FormField] = []
    current_header = header_seed
    pending: tuple[int, str] | None = None  # (row_index, label_text)

    def make_key(label: str) -> str:
        return f"{slugify(current_header)}.{slugify(label)}" if current_header else slugify(label)

    for row_index in range(start_row, len(table.rows)):
        cells = _dedupe_row(table.rows[row_index])
        texts = [c.text.strip() for c in cells]
        full_blank = all(t == "" for t in texts)

        if pending is not None:
            _, label_text = pending
            pending = None
            if full_blank and len(cells) == 1:
                fields.append(FormField(
                    key=make_key(label_text), label=label_text,
                    table_index=table_index, value_row_index=row_index,
                    value_col_index=0, append_after_label=False,
                ))
                continue
            current_header = label_text
            # fall through — this row still needs its own classification

        if full_blank:
            continue

        if len(cells) == 1:
            paragraphs = _paragraph_texts(cells[0])
            label_text = paragraphs[0].strip()
            trailing = paragraphs[1:]
            trailing_blank = bool(trailing) and all(p.strip() == "" for p in trailing)
            if trailing_blank:
                fields.append(FormField(
                    key=make_key(label_text), label=label_text,
                    table_index=table_index, value_row_index=row_index,
                    value_col_index=0, append_after_label=True,
                ))
            elif len(paragraphs) == 1:
                pending = (row_index, label_text)
            else:
                current_header = label_text
            continue

        label_text = cells[0].text.strip()
        if label_text.lower().startswith("signature"):
            continue
        fields.append(FormField(
            key=make_key(label_text), label=label_text,
            table_index=table_index, value_row_index=row_index,
            value_col_index=1, append_after_label=False,
        ))

    return fields


def _treatment_review_spec() -> FormSpec:
    asset = TEMPLATES_DIR / "client_treatment_review.docx"
    doc = docx.Document(asset)
    (table,) = doc.tables
    fields = _walk_table(table, table_index=0, start_row=6)
    header_fields = [
        HeaderField("date", "Date", 0, 0, 0, "inline"),
        HeaderField("practitioner", "Practitioner", 0, 0, 1, "inline"),
        HeaderField("client_name", "Client name", 0, 1, 0, "inline"),
        HeaderField("client_dob", "Client DOB", 0, 1, 1, "inline"),
        HeaderField("session_number", "Session number", 0, 2, 0, "inline"),
        HeaderField("item_code", "Item code (if relevant)", 0, 2, 1, "inline"),
        HeaderField("reason_for_referral", "Reason for referral", 0, 4, 0, "append"),
    ]
    return FormSpec(
        form_id="client_treatment_review", title="Client Treatment Review",
        asset_path=asset, header_fields=header_fields, fields=fields,
    )


def _grid_fields(table, table_index: int, header_row: int, first_data_row: int,
                  last_data_row: int, section_header: str) -> list[FormField]:
    """The Biopsychosocial 'CLINICAL FORMULATION' table: a row-label ×
    column-label grid, not a single label/value pair per row."""
    header_cells = _dedupe_row(table.rows[header_row])
    column_labels = [c.text.strip() for c in header_cells[1:]]
    fields = []
    for row_index in range(first_data_row, last_data_row + 1):
        cells = _dedupe_row(table.rows[row_index])
        row_label = cells[0].text.strip()
        for col_offset, column_label in enumerate(column_labels, start=1):
            key = f"{slugify(section_header)}.{slugify(row_label)}.{slugify(column_label)}"
            fields.append(FormField(
                key=key, label=f"{row_label} – {column_label}",
                table_index=table_index, value_row_index=row_index,
                value_col_index=col_offset, append_after_label=False,
            ))
    return fields


def _session_notes_spec() -> FormSpec:
    asset = TEMPLATES_DIR / "client_session_notes.docx"
    doc = docx.Document(asset)
    (table,) = doc.tables
    fields = _walk_table(table, table_index=0, start_row=6)
    header_fields = [
        HeaderField("date", "Date", 0, 0, 0, "inline"),
        HeaderField("practitioner", "Practitioner", 0, 0, 1, "inline"),
        HeaderField("client_name", "Client name", 0, 1, 0, "inline"),
        HeaderField("client_dob", "Client DOB", 0, 1, 1, "inline"),
        HeaderField("session_number", "Session Number", 0, 2, 0, "inline"),
        HeaderField("item_code", "Item code (if relevant)", 0, 2, 1, "inline"),
        HeaderField("reason_for_referral", "Reason for referral", 0, 4, 0, "append"),
    ]
    return FormSpec(
        form_id="client_session_notes", title="Client Session Notes",
        asset_path=asset, header_fields=header_fields, fields=fields,
    )


def _biopsychosocial_spec() -> FormSpec:
    asset = TEMPLATES_DIR / "biopsychosocial_assessment.docx"
    doc = docx.Document(asset)
    table0, table1 = doc.tables
    fields = _walk_table(table0, table_index=0, start_row=5)
    fields += _grid_fields(
        table1, table_index=1, header_row=1, first_data_row=2, last_data_row=5,
        section_header="CLINICAL FORMULATION",
    )
    fields += _walk_table(table1, table_index=1, start_row=6)
    header_fields = [
        HeaderField("date", "Date", 0, 0, 0, "inline"),
        HeaderField("practitioner", "Practitioner", 0, 0, 1, "inline"),
        HeaderField("client_name", "Client Name", 0, 1, 0, "inline"),
        HeaderField("client_dob", "Client DOB", 0, 1, 1, "inline"),
        HeaderField("reason_for_referral", "Reason for referral", 0, 3, 0, "append"),
    ]
    return FormSpec(
        form_id="biopsychosocial_assessment", title="Biopsychosocial Assessment",
        asset_path=asset, header_fields=header_fields, fields=fields,
    )


_FORM_SPEC_BUILDERS = {
    "client_treatment_review": _treatment_review_spec,
}

_FORM_SPEC_BUILDERS["client_session_notes"] = _session_notes_spec
_FORM_SPEC_BUILDERS["biopsychosocial_assessment"] = _biopsychosocial_spec


@lru_cache(maxsize=None)
def get_form_spec(form_id: str) -> FormSpec:
    try:
        builder = _FORM_SPEC_BUILDERS[form_id]
    except KeyError:
        raise ClinicalFormError(f"Unknown clinical form '{form_id}'.") from None
    return builder()


def available_forms() -> list[tuple[str, str]]:
    """(form_id, title) pairs, in registration order — for the UI's selector."""
    return [(form_id, builder().title) for form_id, builder in _FORM_SPEC_BUILDERS.items()]


def _clear_cell(cell) -> None:
    """Remove every paragraph after the first, and every run in the first,
    leaving one empty paragraph ready to receive fresh text."""
    paragraphs = cell.paragraphs
    for extra in paragraphs[1:]:
        extra._element.getparent().remove(extra._element)
    for run in list(paragraphs[0].runs):
        run._element.getparent().remove(run._element)


def _fill_cell(cell, text: str) -> None:
    """Overwrite a dedicated value cell (label lives in a different cell)."""
    _clear_cell(cell)
    lines = (text or "Not documented").splitlines() or ["Not documented"]
    cell.paragraphs[0].add_run(lines[0])
    for line in lines[1:]:
        cell.add_paragraph(line)


def _fill_cell_after_label(cell, text: str) -> None:
    """Append text as new paragraphs after an existing label paragraph,
    which must survive untouched (used for own-cell fields and the
    'Reason for referral' header field)."""
    paragraphs = cell.paragraphs
    for extra in paragraphs[1:]:
        extra._element.getparent().remove(extra._element)
    for line in (text or "Not documented").splitlines() or ["Not documented"]:
        cell.add_paragraph(line)


def _fill_header_cell(cell, value: str) -> None:
    """Append a typed value inline, on the label's own paragraph and run —
    'Date: ' becomes 'Date: 12/08/2026'."""
    paragraph = cell.paragraphs[0]
    if paragraph.runs:
        paragraph.runs[-1].text = paragraph.runs[-1].text + value
    else:
        paragraph.add_run(value)


def fill_template(
    form_spec: FormSpec, field_values: dict[str, str], header_values: dict[str, str]
) -> bytes:
    """Fill a fresh in-memory copy of the template. Nothing touches disk."""
    doc = docx.Document(form_spec.asset_path)

    for header in form_spec.header_fields:
        value = (header_values.get(header.key) or "").strip()
        if not value:
            continue
        cell = _dedupe_row(doc.tables[header.table_index].rows[header.row_index])[header.col_index]
        if header.style == "inline":
            _fill_header_cell(cell, value)
        else:
            _fill_cell_after_label(cell, value)

    for field in form_spec.fields:
        cell = _dedupe_row(
            doc.tables[field.table_index].rows[field.value_row_index]
        )[field.value_col_index]
        text = field_values.get(field.key) or "Not documented"
        if field.append_after_label:
            _fill_cell_after_label(cell, text)
        else:
            _fill_cell(cell, text)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


_SYSTEM_PREAMBLE = """\
You are a clinical documentation assistant filling out a structured clinical \
form from de-identified source material. You produce a DRAFT that a \
clinician will review, correct, and sign.

The source text has already been de-identified. Names, numbers, dates and \
places have been replaced with bracketed placeholders such as [PATIENT], \
[CLINICIAN_1], [MRN] and [DATE_2].

Rules you must follow:

1. Use ONLY information present in the provided source text.
2. Do NOT invent facts, names, dates, dosages, values, or events.
3. Preserve every bracketed placeholder EXACTLY as written, character for \
character. Do not translate, expand, renumber, or replace them.
4. Write in plain clinical register, past tense, concisely.
5. For each field listed below, write the field's marker on its own line, \
then the field's content, then move to the next field. If the source has \
no information for a field, write exactly "Not documented" for that field \
rather than guessing or leaving it blank.
6. Do not add commentary, a greeting, or a sign-off. Output only the fields.

FIELDS TO COMPLETE, IN THIS EXACT ORDER — reproduce each marker exactly:

{field_list}
"""

_USER_TEMPLATE = """\
SOURCE TEXT (de-identified):
---
{document}
---

Write the content for every field listed in the system instructions, each \
under its own <<FIELD:key>> marker, in the exact order given.
"""


def build_prompt(form_spec: FormSpec, deidentified_text: str) -> tuple[str, str]:
    field_list = "\n".join(f"<<FIELD:{f.key}>> — {f.label}" for f in form_spec.fields)
    system = _SYSTEM_PREAMBLE.format(field_list=field_list)
    user = _USER_TEMPLATE.format(document=deidentified_text)
    return system, user


_FIELD_MARKER_RE = re.compile(r"<<FIELD:([a-z0-9_.]+)>>")


def parse_fields(form_spec: FormSpec, raw_output: str) -> dict[str, str]:
    """Turn the model's marker-delimited output into ``{field_key: text}``.

    Any field the model skipped defaults to "Not documented" — enforced
    here rather than trusted to the model. Unknown markers are ignored; on
    a duplicate marker for the same key, the first occurrence wins.
    """
    text = raw_output or ""
    matches = list(_FIELD_MARKER_RE.finditer(text))
    found: dict[str, str] = {}
    for index, match in enumerate(matches):
        key = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        if key not in found:
            found[key] = text[start:end].strip(" \n—-")

    return {
        field.key: found.get(field.key) or "Not documented"
        for field in form_spec.fields
    }


def combine_sources(
    sources: list[tuple[str, str, dict[str, str]]]
) -> tuple[str, dict[str, str]]:
    """Concatenate several documents' de-identified text into one source.

    ``sources`` is ``(name, redacted_text, phi_map)`` per contributing
    document. Every placeholder is prefixed with that document's position
    (``[PATIENT]`` -> ``[DOC1_PATIENT]``) so two documents that each define
    their own ``[PATIENT]`` never collide once merged — each keeps
    resolving to its own real value at re-identification time.
    """
    if not sources:
        raise ClinicalFormError("No source documents were selected.")

    parts = []
    merged: dict[str, str] = {}
    for index, (name, text, phi_map) in enumerate(sources, start=1):
        prefix = f"DOC{index}_"
        rewritten = _mapping.PLACEHOLDER_RE.sub(
            lambda m, p=prefix: f"[{p}{m.group(0)[1:]}", text or ""
        )
        parts.append(f"--- Source: {name} ---\n{rewritten}")
        for placeholder, value in (phi_map or {}).items():
            merged[f"[{prefix}{placeholder[1:]}"] = value

    return "\n\n".join(parts), merged
