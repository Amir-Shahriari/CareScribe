"""Filling a template: header values land inline or as a new paragraph
depending on style, field values land in their mapped cell, and the
document's structure (table/row counts, section headers, signature row)
survives untouched.
"""

import io

import docx
import pytest

from carescribe.core import clinical_forms


def test_fill_template_writes_header_and_field_values():
    spec = clinical_forms.get_form_spec("client_session_notes")
    header_values = {
        "date": "12/08/2026", "practitioner": "A. Nguyen",
        "client_name": "J. Smith", "client_dob": "01/01/1990",
        "session_number": "4", "item_code": "80010",
        "reason_for_referral": "Ongoing anxiety management.",
    }
    field_values = {f.key: f"Generated text for {f.key}." for f in spec.fields}

    output = clinical_forms.fill_template(spec, field_values, header_values)
    doc = docx.Document(io.BytesIO(output))

    row0 = clinical_forms._dedupe_row(doc.tables[0].rows[0])
    assert row0[0].text == "Date: 12/08/2026"
    assert row0[1].text == "Practitioner: A. Nguyen"

    reason_cell = clinical_forms._dedupe_row(doc.tables[0].rows[4])[0]
    assert "Reason for referral:" in reason_cell.paragraphs[0].text
    assert "Ongoing anxiety management." in reason_cell.text

    sample_field = spec.fields[0]
    value_cell = clinical_forms._dedupe_row(
        doc.tables[sample_field.table_index].rows[sample_field.value_row_index]
    )[sample_field.value_col_index]
    assert f"Generated text for {sample_field.key}." in value_cell.text


def test_fill_template_preserves_structure():
    spec = clinical_forms.get_form_spec("client_session_notes")
    field_values = {f.key: "x" for f in spec.fields}
    output = clinical_forms.fill_template(spec, field_values, {})
    original = docx.Document(spec.asset_path)
    filled = docx.Document(io.BytesIO(output))

    assert len(filled.tables) == len(original.tables)
    assert len(filled.tables[0].rows) == len(original.tables[0].rows)
    # Section header untouched.
    assert filled.tables[0].rows[6].cells[0].text == "SESSION SUMMARY"
    # Signature row untouched (still blank).
    sig_row = clinical_forms._dedupe_row(filled.tables[0].rows[18])
    assert sig_row[0].text == "Signature:"


def test_fill_template_defaults_missing_field_to_not_documented():
    spec = clinical_forms.get_form_spec("client_session_notes")
    output = clinical_forms.fill_template(spec, {}, {})
    doc = docx.Document(io.BytesIO(output))
    sample_field = spec.fields[0]
    value_cell = clinical_forms._dedupe_row(
        doc.tables[sample_field.table_index].rows[sample_field.value_row_index]
    )[sample_field.value_col_index]
    assert value_cell.text.strip() == "Not documented"
