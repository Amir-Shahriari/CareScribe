from unittest import mock

from carescribe.core import deidentify as D


def deid_rules_only(text):
    """De-identify with no NER model — the supported no-spaCy machine."""
    with mock.patch.object(D, "get_analyzer", return_value=None):
        return D.deidentify(text).redacted_text


def test_no_false_positives():
    """Strings that merely look date-ish stay untouched."""
    for text in (
        "increase to 1.2-Mar-5 mg",
        "32-Mar-2026",
        "15-Mar-26",
        "Vitamin B12-Mar-2026",
    ):
        assert deid_rules_only(text) == text


def test_hyphen_month_date_redacted():
    """"15-Mar-2026" after a date label is redacted."""
    out = deid_rules_only("Next review: 15-Mar-2026")
    assert "[DATE]" in out
    assert "15-Mar-2026" not in out


def test_hyphen_month_date_all_caps():
    """An ALL-CAPS export form is caught too."""
    out = deid_rules_only("Next review: 15-MAR-2026")
    assert "[DATE]" in out
    assert "15-MAR-2026" not in out


def test_dob_hyphen_month_date():
    """A hyphen-month DOB is redacted."""
    out = deid_rules_only("DOB: 01-Jan-1970")
    assert "01-Jan-1970" not in out


def test_slash_separated_month_name():
    """Slash separators work the same as hyphens."""
    out = deid_rules_only("Next review: 15/Mar/2026")
    assert "[DATE]" in out
    assert "15/Mar/2026" not in out


def test_corpus_line_trio():
    """These three were inconsistent — the middle one leaked."""
    out = deid_rules_only(
        "Visit date:         15/03/2026\n"
        "Next review:        15-Mar-2026\n"
        "Date typed:         15th March 2026\n"
    )
    assert "15/03/2026" not in out
    assert "15-Mar-2026" not in out
    assert "15th March 2026" not in out


def test_other_date_formats_still_work():
    """The pre-existing date formats still redact."""
    for text in (
        "Visit date: 2026-03-15",
        "Visit date: 15.03.2026",
        "Visit date: 15 Mar 2026",
        "Visit date: 15/03/2026",
    ):
        out = deid_rules_only(text)
        assert "[DATE]" in out, text
