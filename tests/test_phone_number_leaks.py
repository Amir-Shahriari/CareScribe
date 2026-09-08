from unittest import mock

from carescribe.core import deidentify as D


def deid_rules_only(text):
    """De-identify with no NER model — the supported no-spaCy machine."""
    with mock.patch.object(D, "get_analyzer", return_value=None):
        return D.deidentify(text).redacted_text


def test_no_false_positives_on_clinical_values():
    """Lab values, doses and dates are not phone numbers and pass through.

    "Seen on" is a _DATE_ANCHORS label, so that one line's date is redacted
    [DATE] by the pre-existing date layer — what is being protected here is
    that the phone pattern leaves all five alone.
    """
    for text in [
        "Sodium 135-145 mmol/L",
        "BP 120/80",
        "Metformin 500 mg BD",
        "Seen on 12/03/2026",
        "INR 2.4",
    ]:
        out = deid_rules_only(text)
        assert "[PHONE]" not in out
        assert "[NHS_NO]" not in out
    for text in [
        "Sodium 135-145 mmol/L",
        "BP 120/80",
        "Metformin 500 mg BD",
        "INR 2.4",
    ]:
        assert deid_rules_only(text) == text


def test_international_australian_number():
    """+61 with spaced groups is caught, digits fully gone."""
    out = deid_rules_only("Contact: +61 412 345 678")
    assert "[PHONE]" in out
    assert "+61" not in out
    assert "345" not in out


def test_international_uk_number():
    """+44 with spaced groups is caught, digits fully gone."""
    out = deid_rules_only("Tel: +44 20 7946 0958")
    assert "[PHONE]" in out
    assert "7946" not in out


def test_compact_international_number():
    """A +61 number with no spaces is caught."""
    out = deid_rules_only("Mobile: +61412345678")
    assert "[PHONE]" in out
    assert "61412345678" not in out


def test_bracketed_area_code():
    """A bracketed "(03)" area code is caught with its brackets."""
    out = deid_rules_only("Phone: (03) 9876 5432")
    assert "[PHONE]" in out
    assert "9876" not in out
    assert "(03)" not in out


def test_two_digit_area_code():
    """A two-digit area code with no brackets is caught."""
    out = deid_rules_only("Fax: 03 9876 5433")
    assert "[PHONE]" in out
    assert "5433" not in out


def test_international_with_trunk_zero():
    """The "+44 (0)20" trunk-zero form is caught."""
    out = deid_rules_only("Contact: +44 (0)20 7946 0958")
    assert "[PHONE]" in out


def test_us_number_not_mislabeled_as_nhs():
    """A US phone number used to be typed as an NHS number."""
    out = deid_rules_only("Contact number: +1 617 555 0142")
    assert "[PHONE]" in out
    assert "[NHS_NO]" not in out


def test_uk_trunk_number_still_works():
    """The original UK trunk shape, "0412 345 678", keeps working."""
    out = deid_rules_only("Ph: 0412 345 678")
    assert "[PHONE]" in out
