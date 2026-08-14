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

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import docx

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
