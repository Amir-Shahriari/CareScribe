from unittest import mock

from carescribe.core import deidentify as D


def deid_rules_only(text):
    """De-identify with no NER model — the supported no-spaCy machine."""
    with mock.patch.object(D, "get_analyzer", return_value=None):
        return D.deidentify(text).redacted_text


def test_date_of_death_label_redacts_date():
    """'Date of death' is an anchored date and must be redacted, not leaked."""
    out = deid_rules_only("Date of death: 12 March 2026")
    assert "[DATE]" in out
    assert "March" not in out
    assert "2026" not in out


def test_dod_label_redacts_date():
    """'DOD:' is a death-of-date anchor and must not leave the date standing."""
    out = deid_rules_only("DOD: 12/03/2026")
    assert "[DATE]" in out
    assert "12/03/2026" not in out


def test_deceased_label_redacts_date():
    """'Deceased:' is a death anchor and must not leave the date standing."""
    out = deid_rules_only("Deceased: 12/03/2026")
    assert "[DATE]" in out
    assert "12/03/2026" not in out


def test_died_on_redacts_date():
    """'died on' anchors the date that follows it as identity."""
    out = deid_rules_only("His mother died on 3 April 2026")
    assert "3 April 2026" not in out


def test_dob_is_still_a_birth_date():
    """D.O.D / D.O.B collision guard: 'DOB:' still yields [DOB], never [DATE]."""
    out = deid_rules_only("DOB: 12 March 1970")
    assert "[DOB]" in out
    assert "[DATE]" not in out


def test_admission_date_still_behaves():
    """'Date of admission' was already anchored; this must be unchanged."""
    out = deid_rules_only("Date of admission: 12 March 2026")
    assert "[DATE]" in out


def test_no_false_positive_on_clinical_prose():
    """Death labels without a date leave ordinary clinical prose untouched."""
    for text in (
        "Mortality risk was discussed with the family.",
        "The patient died peacefully; no date recorded.",
    ):
        assert deid_rules_only(text) == text
