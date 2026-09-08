"""Regression tests: IHI and passport numbers were never anchored by the rules.

With no spaCy model installed the regex layer is the only defense, and these
two identifiers sailed through it untouched.
"""

from unittest import mock

from carescribe.core import deidentify as D


def deid_rules_only(text):
    """De-identify with no NER model — the supported no-spaCy machine."""
    with mock.patch.object(D, "get_analyzer", return_value=None):
        return D.deidentify(text).redacted_text


def test_ihi_with_spaces():
    """A spaced IHI is fully replaced, leaving no digit groups behind."""
    out = deid_rules_only("IHI: 8003 6080 0000 1234")
    assert "[MRN]" in out
    assert "8003" not in out
    assert "6080" not in out
    assert "1234" not in out
    assert "[MRN]" in deid_rules_only("Medicare: 2123 45678 1")


def test_ihi_spelled_out_with_hyphens():
    """Hyphen separators and the spelled-out label are handled."""
    out = deid_rules_only("Individual Healthcare Identifier: 8003-6080-0000-1234")
    assert "[MRN]" in out
    assert "8003" not in out
    assert "6080" not in out
    assert "1234" not in out


def test_ihi_bare_digits():
    """An unseparated IHI with no colon is still anchored."""
    out = deid_rules_only("IHI 8003608000001234")
    assert "[MRN]" in out
    assert "8003" not in out
    assert "6080" not in out
    assert "1234" not in out


def test_passport_no():
    """A passport number is redacted via the Passport label."""
    out = deid_rules_only("Passport No: PA1234567")
    assert "[MRN]" in out
    assert "PA1234567" not in out
    assert "[MRN]" in deid_rules_only("DVA File Number: NX123456")


def test_passport_bare_label():
    """Bare "Passport:" with no No/Number word still anchors."""
    out = deid_rules_only("Passport: 123456789")
    assert "[MRN]" in out
    assert "123456789" not in out


def test_no_false_positives():
    """Lab ranges and doses are left untouched — none is an identifier."""
    out = deid_rules_only("Reference range: 135-145 mmol/L")
    assert out == "Reference range: 135-145 mmol/L"
    out = deid_rules_only("Dose 8003 units")
    assert out == "Dose 8003 units"
