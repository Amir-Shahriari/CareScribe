from unittest import mock

from carescribe.core import deidentify as D


def deid_rules_only(text):
    """De-identify with no NER model — the supported no-spaCy machine."""
    with mock.patch.object(D, "get_analyzer", return_value=None):
        return D.deidentify(text).redacted_text


def test_subject_lines_are_not_names():
    """Subject-line "Re:" values pass through unchanged."""
    for text in [
        "Re: Referral for medication review",
        "Re: Medication Review",
        "Re: Discharge Summary",
        "Re: Follow-up appointment",
        "Re: Results",
        "Re: Treatment Plan",
        "Re: Progress Notes",
    ]:
        assert deid_rules_only(text) == text


def test_re_line_with_title():
    """"Re: Mr Jonathan Blake" redacts the name."""
    out = deid_rules_only("Dear Dr Wilson,\n\nRe: Mr Jonathan Blake\n\nHe was admitted.")
    assert "Jonathan Blake" not in out


def test_re_line_without_title():
    """"Re: Jonathan Blake" with no title still redacts the name."""
    out = deid_rules_only("Dear Dr Wilson,\n\nRe: Jonathan Blake\n\nHe was admitted.")
    assert "Jonathan Blake" not in out


def test_re_line_uppercase_label():
    """The corpus line "RE: Ngozi Okafor" redacts the name."""
    out = deid_rules_only("Dear Dr Wilson,\n\nRE: Ngozi Okafor\n\nShe was admitted.")
    assert "Ngozi Okafor" not in out


def test_re_line_apostrophe_surname():
    """An apostrophe surname, "O'Brien", is redacted."""
    out = deid_rules_only("Dear Dr Wilson,\n\nRe: Mr O'Brien\n\nHe was admitted.")
    assert "O'Brien" not in out


def test_re_line_hyphenated_forename():
    """A hyphenated forename, "Jean-Luc Bonnet", is redacted."""
    out = deid_rules_only("Dear Dr Wilson,\n\nRe: Jean-Luc Bonnet\n\nHe was admitted.")
    assert "Jean-Luc Bonnet" not in out


def test_existing_labels_still_work():
    """"Patient:" and "Client name:" lines keep redacting."""
    out = deid_rules_only("Patient: Jonathan Blake")
    assert "Jonathan Blake" not in out
    out = deid_rules_only("Client name: Aisha Rahman")
    assert "Aisha Rahman" not in out


def test_full_letterhead():
    """A full letterhead's name, UR number and email are all redacted."""
    out = deid_rules_only(
        "Dear Dr Wilson,\n\n"
        "Re: Mr Jonathan Blake\n"
        "UR No: 4471982\n"
        "Email: j.blake70@fastmail.com.au\n\n"
        "He was admitted last week."
    )
    assert "Jonathan Blake" not in out
    assert "4471982" not in out
    assert "j.blake70@fastmail.com.au" not in out
