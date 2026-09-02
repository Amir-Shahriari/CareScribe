"""
Regression: an Australian Medicare number left in the clear.

Found by a cockpit QA pass on ``sample_documents/`` (which, unlike
``stress_corpus/``, has no answer key, so nothing asserted this).

``06_risk_assessment.docx`` and ``07_case_conference_note.docx`` both carry
``Medicare 2934 5671 0`` / ``Medicare number: 2934 5671 0``. Before the fix:

* the 9-digit number was not detected by any layer and survived into
  ``redacted_text``;
* ``residual_scan`` did not flag it either, so the approval safety-net would
  not have blocked a write — a reviewer clicking through files a document
  containing a live government patient identifier;
* the label word "Medicare" was misclassified as an organisation.

A Medicare number is a direct patient identifier (HIPAA Safe Harbor category
"medical record / health-plan beneficiary numbers"; UK GDPR special-category
equivalent). It must be redacted like an MRN, and the residual sweep must
catch it if it ever slips through.

Everything here uses the real shipped sample documents plus fabricated label
lines in the style of tests/test_deid_regressions.py.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from carescribe.core import deidentify, ingest

MEDICARE_NUMBER = "2934 5671 0"
SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_documents"
AFFECTED_DOCS = ["06_risk_assessment.docx", "07_case_conference_note.docx"]


def _mrn_values(text: str) -> set[str]:
    return {
        text[s.start : s.end]
        for s in deidentify.structured_spans(text)
        if s.entity_type == "MRN"
    }


@pytest.mark.parametrize(
    "line",
    [
        "Medicare number: 2934 5671 0",
        "Medicare No: 2934 5671 0",
        "Medicare 2934 5671 0",
        "Client: Jane Roe (DOB 12/04/1985, Medicare 2934 5671 0)",
        "Medicare Card No: 2934 56710 1",
    ],
)
def test_a_medicare_labelled_number_is_detected_as_a_record_number(line: str) -> None:
    """The number after a Medicare label is taken, like any other MRN."""
    hits = _mrn_values(line)
    assert any(h.replace(" ", "").startswith("2934") for h in hits), (line, hits)


@pytest.mark.parametrize(
    "line",
    [
        "The patient is eligible for Medicare funded sessions.",
        "Medicare rebate was discussed at the review.",
        "Aspirin 75mg once daily",
        "Seen again after 5 or 6 days.",
    ],
)
def test_the_medicare_label_does_not_over_capture(line: str) -> None:
    """A Medicare mention with no number attached is not a record-number hit."""
    assert _mrn_values(line) == set()


def test_residual_scan_catches_a_leaked_medicare_number() -> None:
    """Safety-net: if a Medicare number ever reaches redacted text, approval blocks."""
    leaked = "Assessment complete. Medicare 2934 5671 0 on file. Plan agreed."
    findings = deidentify.residual_scan(leaked)
    assert any("2934" in f for f in findings), findings


@pytest.mark.parametrize("doc_name", AFFECTED_DOCS)
def test_the_sample_document_medicare_number_does_not_survive(doc_name: str) -> None:
    path = SAMPLE_DIR / doc_name
    if not path.exists():
        pytest.skip(f"{doc_name} not present")
    raw = ingest.extract_text(str(path))
    assert MEDICARE_NUMBER.replace(" ", "") in raw.replace(" ", ""), (
        f"{doc_name} no longer contains the expected Medicare number — update this test"
    )
    result = deidentify.deidentify(raw)
    collapsed = result.redacted_text.replace(" ", "")
    assert "293456710" not in collapsed, (
        doc_name,
        "Medicare number survived de-identification",
    )
    assert deidentify.residual_scan(result.redacted_text) == [] or all(
        "2934" not in f for f in deidentify.residual_scan(result.redacted_text)
    )
