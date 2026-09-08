"""
Tests for the widened ADDRESS_LINE qualifier list (task 063 finish).

Before the fix, a court report's ``Firm address:`` line was not recognised as
an address field, so the street number and name rode out intact while the
postcode was still caught by the structured postcode rule — the line looked
partly redacted while the address survived. These tests pin the widened
qualifier list (Firm, Practice, Clinic, ...) with the NER layer switched off,
so the guarantee is deterministic rather than something spaCy happens to fix.
"""

from unittest import mock

from carescribe.core import deidentify as D


def deid_rules_only(text):
    """De-identify with no NER model — the supported no-spaCy machine."""
    with mock.patch.object(D, "get_analyzer", return_value=None):
        return D.deidentify(text).redacted_text


def test_corpus_firm_address_line_is_redacted_whole():
    """The postcode was caught and the street was not, so the line read as redacted while the address rode out."""
    out = deid_rules_only("Firm address:           4 Chancery Row, Leeds, LS1 4BT")
    assert "4 Chancery Row" not in out
    assert "LS1 4BT" not in out


def test_practice_address_line_is_redacted():
    """'Practice address:' is now a recognised address field."""
    out = deid_rules_only("Practice address: 5 Green Lane, Otley, LS21 3HB")
    assert "5 Green Lane" not in out


def test_clinic_address_line_is_redacted():
    """'Clinic address:' is now a recognised address field."""
    out = deid_rules_only("Clinic address: 9 High Street, Leeds")
    assert "9 High Street" not in out


def test_existing_address_labels_still_work():
    """The labels that worked before the widening are not regressed."""
    for line in (
        "Address: 27 Rowena Parade, Richmond VIC 3121",
        "Home address: 14 Leeds Road, Harrogate, LS9 4TT",
        "Postal address: PO Box 42, Carlton VIC 3053",
        "Address line 1: 3 Mill Road",
    ):
        assert "Rowena Parade" not in deid_rules_only(line)
        assert "Leeds Road" not in deid_rules_only(line)
        assert "PO Box 42" not in deid_rules_only(line)
        assert "3 Mill Road" not in deid_rules_only(line)


def test_no_false_positive_without_a_colon():
    """Address words in prose are not fields and must come back unchanged."""
    for text in (
        "Email address is not recorded",
        "The address was confirmed by phone.",
    ):
        assert deid_rules_only(text) == text


def test_whole_letterhead_block():
    """A letterhead block: fields are redacted, but an unanchored name is NER's job."""
    block = (
        "Instructed solicitor:   Miriam Okwuosa\n"
        "Firm address:           4 Chancery Row, Leeds, LS1 4BT\n"
        "Direct dial:            01632 960 214"
    )
    out = deid_rules_only(block)
    assert "4 Chancery Row" not in out
    assert "01632 960 214" not in out
    # Deliberate boundary: a personal name with no label or title is NER's
    # job, not the rules layer's. Assert it so the test documents the line
    # rather than pretending it is fixed.
    assert "Miriam Okwuosa" in out
