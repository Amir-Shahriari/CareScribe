from unittest import mock

from carescribe.core import deidentify as D


def deid_rules_only(text):
    """De-identify with no NER model — the supported no-spaCy machine."""
    with mock.patch.object(D, "get_analyzer", return_value=None):
        return D.deidentify(text).redacted_text


def test_bracketed_value_in_prose():
    """The claim number is reached when the value itself is bracketed."""
    out = deid_rules_only(
        "New Certificate of Capacity issued for the WorkCover claim "
        "(WC-2025-118342), modified duties."
    )
    assert "WC-2025-118342" not in out
    assert "[MRN]" in out


def test_gloss_before_the_value_still_works():
    """"Hospital No (MRN): 4471982" must be unaffected by the new separator."""
    assert "4471982" not in deid_rules_only("Hospital No (MRN): 4471982")


def test_plain_labelled_values_still_work():
    """The ordinary label forms are unchanged."""
    assert "WC-2025-118342" not in deid_rules_only("Claim number: WC-2025-118342")
    assert "4471982" not in deid_rules_only("UR No: 4471982")
    assert "RAD-2025-77120" not in deid_rules_only("Accession number: RAD-2025-77120")
    assert "CPC-4471" not in deid_rules_only("Clinic file: CPC-4471")


def test_prose_without_a_value_is_untouched():
    """A label with no digit-shaped value still takes nothing."""
    for line in ("The claim was denied.", "Her claim remains open."):
        assert deid_rules_only(line) == line


def test_lab_reference_range_is_not_an_identifier():
    """Reference ranges must survive; redacting them destroys clinical meaning."""
    line = "Reference range: 135-145 mmol/L"
    assert deid_rules_only(line) == line
