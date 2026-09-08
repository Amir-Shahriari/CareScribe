"""
Regression tests for the sample-document field labels.

Four different labels name the same fictional patient across
``sample_documents/`` — "Patient:", "Client:", "Full name:", "Name:" and
"Worker:" — plus the WorkCover "Claim number:" field. Before these anchors
were added, only the first two redacted; the patient's name and claim number
rode out of four of the fifteen shipped documents when no spaCy model was
installed. All values here are fabricated (the sample documents are synthetic).
"""

from __future__ import annotations

from unittest import mock

from carescribe.core import deidentify as D


def deid_rules_only(text):
    """De-identify with no NER model — the supported no-spaCy machine."""
    with mock.patch.object(D, "get_analyzer", return_value=None):
        return D.deidentify(text).redacted_text


def test_worker_label_redacts_patient_name():
    """'Worker:' names the injured person on a WorkCover certificate."""
    out = deid_rules_only("Worker: Jordan Elliot Whitfield")
    assert "Jordan Elliot Whitfield" not in out


def test_full_name_label_redacts_patient_name():
    """'Full name:' is the intake-form spelling of the patient field."""
    out = deid_rules_only("Full name: Jordan Elliot Whitfield")
    assert "Jordan Elliot Whitfield" not in out


def test_name_label_redacts_patient_name():
    """A line-leading bare 'Name:' is a clinic letter's patient field."""
    out = deid_rules_only("Name: Jordan Elliot Whitfield")
    assert "Jordan Elliot Whitfield" not in out


def test_claim_number_label_redacts():
    """'Claim number:' is the insurer's case identifier for the patient."""
    out = deid_rules_only("Claim number: WC-2025-118342")
    assert "[MRN]" in out
    assert "WC-2025-118342" not in out


def test_claim_no_label_redacts():
    """'Claim No:' is the abbreviated spelling of the same field."""
    out = deid_rules_only("Claim No: WC-2025-118342")
    assert "[MRN]" in out
    assert "WC-2025-118342" not in out


def test_existing_patient_line_labels_still_redact():
    """'Patient:' and 'Client:' keep working after the label list grows."""
    assert "Jordan Elliot Whitfield" not in deid_rules_only(
        "Patient: Jordan Elliot Whitfield"
    )
    assert "Jordan Elliot Whitfield" not in deid_rules_only(
        "Client: Jordan Elliot Whitfield"
    )


def test_bare_name_does_not_eat_other_fields():
    """A bare 'Name' only anchors at line start, so other fields survive."""
    for line in (
        "Drug name: Sertraline",
        "Medication name: Quetiapine",
        "File name: report.docx",
        "Name: 50mg daily",
    ):
        assert deid_rules_only(line) == line


def test_bare_claim_is_not_an_anchor():
    """Bare 'claim' in prose is not an identifier label."""
    assert deid_rules_only("The claim was denied") == "The claim was denied"
    assert (
        deid_rules_only("Reference range: 135-145 mmol/L")
        == "Reference range: 135-145 mmol/L"
    )
