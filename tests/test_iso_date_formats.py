"""
Regression tests for the ISO / dotted / compact date fix.

A de-identification leak was fixed in the rules layer: year-first (ISO), dotted
and compact date forms were invisible to it, so a birth date written 1970-02-01
sailed straight through whenever no spaCy model was installed. This file locks
that fix down in both modes — with the real analyzer and with none installed —
because a leak that only stays closed when spaCy happens to be present is not
a guarantee.

The clinical entities in here are fabricated; the dates are format-valid fakes.
"""

import pytest

from carescribe.core import deidentify


@pytest.fixture(params=["with-ner", "rules-only"])
def deid(request, monkeypatch):
    """The pipeline with the real analyzer, and with none installed.

    A machine with no spaCy model falls back to the rules layer alone, and that
    is exactly where the ISO date used to sail straight through, so every case
    here has to hold in both modes.
    """
    if request.param == "rules-only":
        monkeypatch.setattr(deidentify, "get_analyzer", lambda *a, **k: None)
    return deidentify.deidentify


# ==========================================================================
# Labelled birth dates — every common format must redact to [DOB]
# ==========================================================================


@pytest.mark.parametrize(
    "text, expected",
    [
        ("DOB: 1970-02-01", "DOB: [DOB]"),
        ("DOB: 1970/02/01", "DOB: [DOB]"),
        ("DOB: 01.02.1970", "DOB: [DOB]"),
        ("DOB: 19700201", "DOB: [DOB]"),
        ("Date of birth: 1970-02-01", "Date of birth: [DOB]"),
    ],
)
def test_labelled_birth_date_redacts_to_dob_placeholder(text, expected, deid):
    """The birth label decides the placeholder, whatever the date format."""
    result = deid(text)
    assert result.redacted_text == expected
    assert not any(c.isdigit() for c in result.redacted_text)


def test_iso_birth_date_maps_to_original_text(deid):
    """The placeholder maps back to the exact date as typed."""
    result = deid("DOB: 1970-02-01")
    assert result.phi_map["[DOB]"] == "1970-02-01"


# ==========================================================================
# Labelled non-birth dates — [DATE], ISO date and full timestamp
# ==========================================================================


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Admitted: 2024-03-05", "Admitted: [DATE]"),
        ("Admitted: 2024-03-05T14:30:00", "Admitted: [DATE]"),
    ],
)
def test_labelled_date_redacts_to_date_placeholder(text, expected, deid):
    """A labelled event date redacts as [DATE] in both ISO forms."""
    result = deid(text)
    assert result.redacted_text == expected
    assert not any(c.isdigit() for c in result.redacted_text)


def test_full_timestamp_loses_its_time_half_too(deid):
    """The whole timestamp goes, not just the date half."""
    result = deid("Admitted: 2024-03-05T14:30:00")
    assert "14:30" not in result.redacted_text


# ==========================================================================
# Deliberate non-dates — must come back completely unchanged
# ==========================================================================


@pytest.mark.parametrize(
    "text",
    [
        # A dose is not a dotted date.
        "Increase to 1.2.5 mg",
        # 8 digits with no date label is not a date.
        "Reference 19700201 in the archive",
        # Unlabelled prose date — deliberate policy.
        "Bloods taken 2024-03-05 showed anaemia.",
        # A clinical measurement is never a date.
        "BP 120/80",
    ],
)
def test_non_dates_pass_through_unchanged(text, deid):
    assert deid(text).redacted_text == text
