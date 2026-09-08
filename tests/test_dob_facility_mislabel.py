"""
Regression: a birth date whose label had no colon was redacted as a clinic.

When a birth date's label carried no colon ("DOB 01/01/1970"), the NER layer
returned one FACILITY span covering the label *and* the date, and that span
beat the correct DOB span on length. The reviewer then saw [CLINIC] where a
birth date was, and the "DOB" field label was deleted outright. These tests
lock the fix in — and guard the other direction, so a genuine hospital name
next to a date keeps its [CLINIC] placeholder.
"""

from __future__ import annotations

import pytest

from carescribe.core import deidentify


# ==========================================================================
# The regression: birth dates whose label has no colon (rows 1-6)
# ==========================================================================

BIRTH_DATE_CASES = [
    ("DOB 01/01/1970.", "DOB [DOB]."),
    ("Patient: John Smith, DOB 01/01/1970.", "Patient: [PATIENT], DOB [DOB]."),
    ("Born 01/01/1970.", "Born [DOB]."),
    ("Date of Birth 01/01/1970.", "Date of Birth [DOB]."),
    ("D.O.B. 01/01/1970.", "D.O.B. [DOB]."),
    ("DOB 01/01/1970 and seen on 05/05/2024.", "DOB [DOB] and seen on [DATE]."),
]


@pytest.mark.parametrize("text, expected", BIRTH_DATE_CASES)
def test_colonless_dob_label_redacts_to_a_dob_placeholder(text: str, expected: str) -> None:
    """The regression: the label survives and the date becomes [DOB]."""
    result = deidentify.deidentify(text)
    assert result.redacted_text == expected


@pytest.mark.parametrize("text, expected", BIRTH_DATE_CASES)
def test_colonless_dob_label_is_never_a_clinic(text: str, expected: str) -> None:
    """The thing that was broken: no birth-date case may yield a [CLINIC] span.

    Asserted explicitly, not just via the equality above — this is the defect.
    """
    result = deidentify.deidentify(text)
    assert "[CLINIC]" not in result.redacted_text


def test_phi_map_holds_the_date_alone_not_the_labelled_string() -> None:
    """The old FACILITY span captured "DOB 01/01/1970"; the map must hold only the date."""
    result = deidentify.deidentify("DOB 01/01/1970.")
    assert result.phi_map == {"[DOB]": "01/01/1970"}


def test_birth_date_and_appointment_date_stay_distinct_placeholders() -> None:
    """A DOB and a plain date in one sentence must not collapse into one placeholder."""
    result = deidentify.deidentify("DOB 01/01/1970 and seen on 05/05/2024.")
    assert result.redacted_text.count("[DOB]") == 1
    assert result.redacted_text.count("[DATE]") == 1
    assert result.phi_map["[DOB]"] == "01/01/1970"
    assert result.phi_map["[DATE]"] == "05/05/2024"


# ==========================================================================
# The guard against over-correcting: a genuine hospital (rows 7-8)
# ==========================================================================

HOSPITAL_GUARD_CASES = [
    ("Seen at St Mary's Hospital on 01/01/1970.", "Seen at [CLINIC] on [DATE]."),
    ("Seen at St Mary's Hospital last week.", "Seen at [CLINIC] last week."),
]


@pytest.mark.parametrize("text, expected", HOSPITAL_GUARD_CASES)
def test_hospital_name_keeps_its_clinic_placeholder(text: str, expected: str) -> None:
    """Guard: a fix that deleted every facility span would pass the rows above.

    A genuine hospital name must still redact to [CLINIC], with or without a
    date in the sentence.
    """
    result = deidentify.deidentify(text)
    assert result.redacted_text == expected
    assert "[CLINIC]" in result.redacted_text


def test_the_date_beside_a_hospital_is_still_a_date() -> None:
    """Guard: the appointment date next to the hospital stays [DATE], not [DOB]."""
    result = deidentify.deidentify("Seen at St Mary's Hospital on 01/01/1970.")
    assert "[DATE]" in result.redacted_text
    assert "[DOB]" not in result.redacted_text


# ==========================================================================
# Cross-cutting: no digit survives any of these outputs
# ==========================================================================


@pytest.mark.parametrize(
    "text, expected", BIRTH_DATE_CASES + HOSPITAL_GUARD_CASES
)
def test_no_digit_survives_in_any_case(text: str, expected: str) -> None:
    """De-identification guarantee: every date digit is gone from the output."""
    result = deidentify.deidentify(text)
    assert not any(c.isdigit() for c in result.redacted_text)
