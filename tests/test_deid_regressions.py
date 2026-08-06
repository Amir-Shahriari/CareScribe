"""
Regression suite for the five leaks found on a second, non-fixture document.

Each test here corresponds to a confirmed bug. They are deliberately written
against the *deterministic* layer where the guarantee should be deterministic:
a leak that only stays closed because spaCy happened to tag something is not a
guarantee, and document #2 is what proved it — the same initial+surname form
that NER catches in one context sails through in another.

Everything in this file is fabricated. Names are invented, the NHS number is a
format-valid fake, phone numbers use Ofcom's 01632 960xxx drama range.
"""

import pytest

from carescribe.core import deidentify, mapping


# ==========================================================================
# BUG 1 — MRN in a labelled field
# ==========================================================================

def _mrn_values(text: str) -> set[str]:
    return {
        text[s.start : s.end]
        for s in deidentify.structured_spans(text)
        if s.entity_type == "MRN"
    }


@pytest.mark.parametrize(
    "line, expected",
    [
        ("Hospital No (MRN): 4471982", "4471982"),
        ("Case No. 990214", "990214"),
        ("MRN 5567013", "5567013"),
        ("Record No: 33-201-45", "33-201-45"),
        ("Hospital Number: 82911", "82911"),
        ("Unit No: 4471982", "4471982"),
        ("Patient ID: 7781234", "7781234"),
        ("Record Number # 5567013", "5567013"),
        ("MRN:4471982", "4471982"),
    ],
)
def test_labelled_record_number_is_detected(line, expected):
    """The label shapes document #2 actually used, including the parenthetical."""
    assert expected in _mrn_values(line)


@pytest.mark.parametrize(
    "line",
    [
        "Aspirin 75mg once daily",
        "The patient is age 68 today.",
        "Reviewed again in 2026.",
        "PHQ-9 18 at assessment.",
        "Platelets were 4471982 at review.",
        "Weight 82911 grams was recorded.",
    ],
)
def test_bare_numbers_are_not_record_numbers(line):
    """Context-anchoring is the whole point — a bare digit run is a lab value."""
    assert _mrn_values(line) == set()


def test_labelled_record_number_redacts_to_mrn_placeholder():
    result = deidentify.deidentify("Hospital No (MRN): 4471982\nSeen in clinic.\n")
    assert "4471982" not in result.redacted_text
    assert "[MRN]" in result.redacted_text


# ==========================================================================
# BUG 2 — header location leaked
# ==========================================================================

HEADER_DOC = """RIVERSIDE COMMUNITY MENTAL HEALTH TEAM
Harrogate, North Yorkshire

Patient: Ngozi Okafor

She travelled in from Leeds to attend the appointment.
"""


def test_header_town_and_county_are_redacted():
    result = deidentify.deidentify(HEADER_DOC)
    assert "Harrogate, North Yorkshire" not in result.redacted_text
    assert "[LOCATION" in result.redacted_text


def test_place_of_care_in_prose_still_survives():
    """The precision guard that keeps clinical context intact."""
    result = deidentify.deidentify(HEADER_DOC)
    assert "from Leeds to attend" in result.redacted_text


def test_header_location_is_found_by_the_deterministic_layer():
    spans = deidentify.structured_spans(HEADER_DOC)
    found = {HEADER_DOC[s.start : s.end] for s in spans if s.entity_type == "LOCATION"}
    assert "Harrogate, North Yorkshire" in found


def test_clinical_prose_line_with_a_comma_is_not_a_location():
    """A two-part capitalised phrase mid-document is not a letterhead."""
    text = "History\n\nECG showed ST depression, Anterior leads were involved.\n"
    spans = deidentify.structured_spans(text)
    assert not any(s.entity_type == "LOCATION" for s in spans)


# ==========================================================================
# BUG 3 — staff names as initial + surname
# ==========================================================================

STAFF_DOC = """Ward round notes.

Present: R. Ellis (OT), S. Nowak (CPN), J. O'Connor.
Care coordinator: A. Whitfield.
Reviewed by Dr R. Patel on the ward.

Bloods showed normal T3/T4 and no growth of S. aureus.
Typed by A. Whitfield.
"""


@pytest.mark.parametrize(
    "name", ["A. Whitfield", "J. O'Connor", "R. Ellis", "S. Nowak", "R. Patel"]
)
def test_initial_plus_surname_is_detected_without_ner(name):
    """Layer 1 must carry this on its own — NER catching it is luck, not a guarantee."""
    spans = deidentify.structured_spans(STAFF_DOC)
    found = {STAFF_DOC[s.start : s.end] for s in spans if s.entity_type == "PROVIDER_NAME"}
    assert name in found


@pytest.mark.parametrize(
    "name", ["A. Whitfield", "J. O'Connor", "R. Ellis", "S. Nowak", "R. Patel"]
)
def test_staff_initial_surname_redacts_to_a_clinician_placeholder(name):
    result = deidentify.deidentify(STAFF_DOC)
    assert name not in result.redacted_text
    placeholders = {
        e["placeholder"] for e in result.entities if e["type"] == "PROVIDER_NAME"
    }
    assert placeholders
    assert all(p.startswith("[CLINICIAN") for p in placeholders)


@pytest.mark.parametrize("clinical", ["T3/T4", "S. aureus"])
def test_clinical_shorthand_is_not_a_staff_name(clinical):
    result = deidentify.deidentify(STAFF_DOC)
    assert clinical in result.redacted_text


def test_initials_followed_by_a_section_word_are_not_a_name():
    """"M.E.C.\\nFollow-up" must not become the name "M.E.C. Follow"."""
    text = "Referred to as M.E.C.\nFollow-up in six weeks.\n"
    spans = deidentify.structured_spans(text)
    values = {text[s.start : s.end] for s in spans}
    assert not any("Follow" in v for v in values)


# ==========================================================================
# BUG 4 — same identity, two placeholders
# ==========================================================================

IDENTITY_DOC = """Patient:   Mohammed Al-Rashid
Known as:  "Mo"
NHS No:    943 476 5919

Mr Al-Rashid was seen in clinic. Mohammed reported poor sleep, and M.A.R.
was noted to be low in mood. Mo declined a referral.
"""


def test_one_person_collapses_to_one_placeholder():
    result = deidentify.deidentify(IDENTITY_DOC)
    people = [e for e in result.entities if e["type"] in mapping.PERSON_TYPES]
    assert len(people) == 1, [e["value"] for e in people]
    assert people[0]["placeholder"] == "[PATIENT]"


@pytest.mark.parametrize(
    "form", ["Mohammed Al-Rashid", "Mr Al-Rashid", "Mohammed", "M.A.R.", "Mo"]
)
def test_every_surface_form_of_one_person_maps_to_the_same_placeholder(form):
    result = deidentify.deidentify(IDENTITY_DOC)
    assert form not in result.redacted_text
    assert "[PATIENT]" in result.redacted_text


def test_hyphenated_surname_contributes_both_initials():
    variants = mapping.expand_name_variants("Mohammed Al-Rashid")
    assert "M.A.R." in variants


TWO_RELATIVES_DOC = """Patient: Ngozi Okafor

NEXT OF KIN
  Yusuf Okafor (son) is the main contact.
  Amara Okafor (daughter) also visits.

The ward rang Yusuf Okafor about discharge, and Amara Okafor attended.
"""


def test_two_relatives_get_two_placeholders():
    result = deidentify.deidentify(TWO_RELATIVES_DOC)
    relatives = {
        e["placeholder"] for e in result.entities if e["type"] == "RELATIVE_NAME"
    }
    assert len(relatives) == 2, relatives


SHARED_SURNAME_DOC = """Patient: Margaret Chen was admitted overnight.

Dr David Chen reviewed the angiogram and countersigned the summary.
"""


def test_a_clinician_and_a_patient_sharing_a_surname_stay_separate():
    result = deidentify.deidentify(SHARED_SURNAME_DOC)
    people = [e for e in result.entities if e["type"] in mapping.PERSON_TYPES]
    placeholders = {e["placeholder"] for e in people}
    assert len(placeholders) == 2, [(e["value"], e["placeholder"]) for e in people]


def test_canonical_key_separates_two_people_with_one_surname():
    assert mapping.canonical_person_key("Margaret Chen") != mapping.canonical_person_key(
        "David Chen"
    )


def test_canonical_key_unifies_the_forms_of_one_person():
    key = mapping.canonical_person_key("Margaret Elizabeth Chen")
    assert mapping.canonical_person_key("Margaret Chen") == key
    assert mapping.canonical_person_key("Mrs Margaret Chen") == key


# ==========================================================================
# BUG 5 — labelled date field vs prose
# ==========================================================================

DATE_DOC = """Date of Birth:  3 April 1971
Admission date: 2 June 2026
Discharge date: 14 June 2026
Date typed:     20 June 2026
Next review:    5 August 2026
Appointment:    12/09/2026

He was admitted on 2 June 2026 after a three-day history of low mood.
Aspirin 75mg twice daily was continued throughout.
"""


@pytest.mark.parametrize(
    "value",
    ["3 April 1971", "2 June 2026", "14 June 2026", "20 June 2026", "5 August 2026",
     "12/09/2026"],
)
def test_labelled_date_fields_are_always_redacted(value):
    """Regardless of REDACT_INPROSE_DATES, which stays False by default."""
    assert not deidentify.REDACT_INPROSE_DATES
    result = deidentify.deidentify(DATE_DOC)
    assert value not in result.redacted_text


def test_a_date_in_a_field_and_in_prose_shares_one_placeholder():
    result = deidentify.deidentify(DATE_DOC)
    admission = [e for e in result.entities if e["value"] == "2 June 2026"]
    assert len(admission) == 1
    placeholder = admission[0]["placeholder"]
    assert result.redacted_text.count(placeholder) == 2


def test_a_date_entity_never_spans_a_line_break():
    """"14 June 2026\\nDate" swallowed the next line's label and mangled the text."""
    result = deidentify.deidentify(DATE_DOC)
    for entity in result.entities:
        assert "\n" not in entity["value"], entity


def test_the_line_after_a_date_field_is_not_damaged():
    result = deidentify.deidentify(DATE_DOC)
    assert "Date typed:" in result.redacted_text
    assert "Next review:" in result.redacted_text


@pytest.mark.parametrize(
    "clinical", ["twice daily", "three-day history", "Aspirin 75mg"]
)
def test_durations_and_frequencies_are_never_dates(clinical):
    result = deidentify.deidentify(DATE_DOC)
    assert clinical in result.redacted_text
