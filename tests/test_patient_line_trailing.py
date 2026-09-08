"""PATIENT_LINE must keep matching when DOB, Medicare or address details
follow the name -- the old "$" anchor only matched a bare "Label: Name".
"""

from unittest import mock

from carescribe.core import deidentify as D


def deid_rules_only(text):
    """De-identify with no NER model -- the supported no-spaCy machine."""
    with mock.patch.object(D, "get_analyzer", return_value=None):
        return D.deidentify(text).redacted_text


def test_bare_name_does_not_eat_other_fields():
    """A bare "Name" label must not swallow other fields' values."""
    for line in (
        "Drug name: Sertraline",
        "File name: report.docx",
        "Name: 50mg daily",
    ):
        assert deid_rules_only(line) == line


def test_case_conference_line():
    """This exact line appears in sample_documents/07_case_conference_note.docx and the name leaked."""
    text = "Client: Jordan Elliot Whitfield (DOB 12/04/1985, Medicare 2934 5671 0)"
    assert "Jordan Elliot Whitfield" not in deid_rules_only(text)


def test_pipe_delimited_gp_line():
    """This exact line appears in sample_documents/13_gp_progress_note.docx and the name leaked."""
    text = "Patient: Jordan Elliot Whitfield  |  DOB 12/04/1985  |  Medicare 2934 5671 0"
    assert "Jordan Elliot Whitfield" not in deid_rules_only(text)


def test_trailing_age():
    """A trailing comma-separated age after the name still redacts."""
    text = "Patient: Ngozi Okafor, 42"
    assert "Ngozi Okafor" not in deid_rules_only(text)


def test_worker_line_with_claim_number():
    """A WorkCover "Worker" line followed by the claim number still redacts the name."""
    text = "Worker: Jordan Elliot Whitfield - claim WC-2025-118342"
    assert "Jordan Elliot Whitfield" not in deid_rules_only(text)


def test_bare_shapes_still_work():
    """The bare "Label: Name" shapes that always worked still redact, unchanged."""
    for text in (
        "Client: Jordan Elliot Whitfield",
        "Full name: Jordan Elliot Whitfield",
        "Patient: Jordan Elliot Whitfield",
    ):
        assert "Jordan Elliot Whitfield" not in deid_rules_only(text)
