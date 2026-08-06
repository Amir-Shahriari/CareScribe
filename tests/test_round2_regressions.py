"""
Regression suite for the round-2 leaks (A1-A9).

The corpus tests in ``test_stress_corpus.py`` prove these end to end on whole
documents. These pin the individual mechanisms, so a failure says which rule
broke rather than which document.

Everything here is fabricated.
"""

import pytest

from carescribe.core import deidentify, mapping


# ==========================================================================
# A1 — a full name broken by a line wrap
# ==========================================================================

WRAPPED = (
    "The referral concerns Oluwaseun\n"
    "Adeyinka, who was seen at the day unit. Oluwaseun remains on the caseload.\n"
)


@pytest.mark.parametrize("newline", ["\n", "\r\n"], ids=["lf", "crlf"])
def test_a_name_split_by_a_line_break_is_one_person(newline):
    """The dangerous direction: this used to fail open, leaking the whole name."""
    text = WRAPPED.replace("\n", newline)
    result = deidentify.deidentify(text)
    assert "Adeyinka" not in result.redacted_text
    assert "Oluwaseun" not in result.redacted_text


@pytest.mark.parametrize("newline", ["\n", "\r\n"], ids=["lf", "crlf"])
def test_the_wrapped_name_is_a_single_entity(newline):
    text = WRAPPED.replace("\n", newline)
    people = [
        e for e in deidentify.deidentify(text).entities
        if e["type"] in mapping.PERSON_TYPES
    ]
    assert len(people) == 1, [e["value"] for e in people]
    assert people[0]["value"] == "Oluwaseun Adeyinka"


def test_lf_and_crlf_wrapped_documents_agree():
    lf = deidentify.deidentify(WRAPPED).redacted_text
    crlf = deidentify.deidentify(WRAPPED.replace("\n", "\r\n")).redacted_text
    assert crlf.replace("\r\n", "\n") == lf


def test_a_field_value_does_not_run_into_the_next_line():
    """"Brother: David Chen\\nWei Chen" was one span covering two people."""
    text = "Brother:  David Chen\nWei Chen attended for review.\n"
    values = {e["value"] for e in deidentify.deidentify(text).entities}
    assert "David Chen Wei Chen" not in values


# ==========================================================================
# A2 — identity over-merge and patient/relative typing
# ==========================================================================

FAMILY = """Patient:        Wei Chen
Sister:         Mei Chen
Brother:        David Chen

Wei Chen attended with Mei Chen. David Chen joined by telephone.
"""


def test_the_patient_is_typed_as_the_patient():
    entities = deidentify.deidentify(FAMILY).entities
    patients = [e for e in entities if e["type"] == "PATIENT_NAME"]
    assert [e["value"] for e in patients] == ["Wei Chen"]
    assert patients[0]["placeholder"] == "[PATIENT]"


def test_two_relatives_sharing_a_surname_stay_distinct():
    entities = deidentify.deidentify(FAMILY).entities
    relatives = {
        e["value"]: e["placeholder"]
        for e in entities
        if e["type"] == "RELATIVE_NAME"
    }
    assert set(relatives) == {"Mei Chen", "David Chen"}
    assert len(set(relatives.values())) == 2


def test_a_patient_label_outranks_a_kinship_heading():
    """A sibling listed above must not drag the patient into being a relative."""
    text = "NEXT OF KIN\n  Mei Chen (sister)\n\nPatient: Wei Chen\n"
    types = {e["value"]: e["type"] for e in deidentify.deidentify(text).entities}
    assert types.get("Wei Chen") == "PATIENT_NAME"


@pytest.mark.parametrize(
    "a, b",
    [("Wei Chen", "Mei Chen"), ("Priya Venkataraman", "Rajesh Venkataraman"),
     ("Margaret Chen", "David Chen")],
)
def test_a_shared_surname_is_not_a_shared_identity(a, b):
    assert mapping.canonical_person_key(a) != mapping.canonical_person_key(b)


def test_one_person_keeps_one_identity_key():
    key = mapping.canonical_person_key("Margaret Elizabeth Chen")
    assert mapping.canonical_person_key("Margaret Chen") == key
    assert mapping.canonical_person_key("Mrs Margaret Chen") == key


def test_an_initial_can_stand_in_for_a_given_name():
    assert mapping.keys_are_compatible(
        mapping.canonical_person_key("W. Chen"),
        mapping.canonical_person_key("Wei Chen"),
    )
    assert not mapping.keys_are_compatible(
        mapping.canonical_person_key("Wei Chen"),
        mapping.canonical_person_key("Mei Chen"),
    )


# ==========================================================================
# A3 — protected clinical and legal terms
# ==========================================================================

PROTECTED_DOC = """Patient: Ngozi Okafor

She remains subject to Section 3 of the Mental Health Act. The Section 117
aftercare plan was agreed. HoNOS was 18, PHQ-9 was 12 and GAD-7 was 9. The
diagnosis is EUPD. An ECG was normal, eGFR 88, BMI 24, T3/T4 in range.
She is managed under the Care Programme Approach.
"""


@pytest.mark.parametrize(
    "term",
    ["Mental Health Act", "Section 3", "Section 117", "HoNOS", "PHQ-9", "GAD-7",
     "EUPD", "ECG", "eGFR", "BMI", "T3/T4", "Care Programme Approach"],
)
def test_protected_terms_survive(term):
    assert term in deidentify.deidentify(PROTECTED_DOC).redacted_text


def test_the_allow_list_is_an_editable_file():
    assert deidentify.PROTECTED_TERMS_PATH.exists()
    assert "Mental Health Act" in deidentify.load_protected_terms()


def test_a_guessed_span_that_swallowed_a_protected_term_is_dropped():
    text = "MENTAL HEALTH ACT ASSESSMENT RECORD\n\nPatient: Ngozi Okafor\n"
    assert "MENTAL HEALTH ACT" in deidentify.deidentify(text).redacted_text


# ==========================================================================
# A4 — ward names
# ==========================================================================

@pytest.mark.parametrize("ward", ["Cedar Ward", "Ashdown Ward"])
def test_ward_names_are_redacted(ward):
    text = f"Ward: {ward}\n\nHe was reviewed on the ward this morning.\n"
    result = deidentify.deidentify(text)
    assert ward not in result.redacted_text
    assert "[WARD]" in result.redacted_text


def test_the_bare_word_ward_in_prose_survives():
    text = "Ward: Cedar Ward\n\nHe was reviewed on the ward this morning.\n"
    assert "on the ward this morning" in deidentify.deidentify(text).redacted_text


# ==========================================================================
# A5 / A6 — case numbers and CPA identifiers
# ==========================================================================

@pytest.mark.parametrize(
    "line, value",
    [("Case No.: 990214", "990214"), ("Case No. 990214", "990214"),
     ("Case Number: 990214", "990214"), ("Case No: LS-668209", "LS-668209")],
)
def test_case_numbers_are_detected(line, value):
    found = {
        line[s.start : s.end]
        for s in deidentify.structured_spans(line)
        if s.entity_type == "MRN"
    }
    assert value in found


def test_a_bare_number_without_a_case_label_is_left_alone():
    text = "The platelet count was 990214 at review.\n"
    assert "990214" in deidentify.deidentify(text).redacted_text


def test_a_cpa_number_is_redacted_but_the_word_cpa_survives():
    text = "CPA number: CPA-4471-B\n\nShe is managed under CPA arrangements.\n"
    result = deidentify.deidentify(text)
    assert "CPA-4471-B" not in result.redacted_text
    assert "under CPA arrangements" in result.redacted_text


# ==========================================================================
# A7 — an organisation split across a line break
# ==========================================================================

@pytest.mark.parametrize("newline", ["\n", "\r\n"], ids=["lf", "crlf"])
def test_an_organisation_split_across_a_break_is_redacted(newline):
    text = ("The registration is held at Kirkstall Lane" + newline +
            "Surgery, who hold the notes." + newline)
    assert "Kirkstall Lane" not in deidentify.deidentify(text).redacted_text


def test_a_letterhead_is_not_joined_to_the_town_below_it():
    """Flattening the break made one span of the org and the next line's town."""
    text = ("RIVERSIDE COMMUNITY MENTAL HEALTH TEAM\nHarrogate, North Yorkshire\n"
            "\nPatient: Ngozi Okafor\n")
    result = deidentify.deidentify(text)
    assert "Harrogate, North Yorkshire" not in result.redacted_text
    assert "[LOCATION" in result.redacted_text


# ==========================================================================
# A8 — initials
# ==========================================================================

@pytest.mark.parametrize("form", ["M.A.R.", "M.A.R", "MAR"])
def test_initials_forms_are_generated(form):
    assert form in mapping.expand_name_variants("Mariam Aisha Rahman")


def test_initials_collapse_onto_the_patient_placeholder():
    text = ("Patient: Mariam Aisha Rahman\n\n"
            "Earlier correspondence refers to her as M.A.R. throughout.\n")
    result = deidentify.deidentify(text)
    assert "M.A.R." not in result.redacted_text
    assert "[PATIENT]" in result.redacted_text


# ==========================================================================
# A9 — appointment and contact dates
# ==========================================================================

CONTACT_DOC = """The team called at 3 August 2026 and spoke to him at home. He was
seen again on 4 August 2026. A further visit was arranged for 6 August 2026
at 14:30.

He reported a four-week history of low mood. Olanzapine 10mg at night and
Diazepam 2mg twice daily were continued for three months.
"""


@pytest.mark.parametrize(
    "value", ["3 August 2026", "4 August 2026", "6 August 2026", "14:30"]
)
def test_contact_dates_are_redacted_with_the_flag_off(value):
    assert not deidentify.REDACT_INPROSE_DATES
    assert value not in deidentify.deidentify(CONTACT_DOC).redacted_text


@pytest.mark.parametrize(
    "value",
    ["four-week history", "at night", "twice daily", "three months", "Olanzapine 10mg"],
)
def test_durations_and_frequencies_are_untouched(value):
    assert value in deidentify.deidentify(CONTACT_DOC).redacted_text


def test_a_clinical_date_with_no_contact_anchor_still_survives():
    text = "Angiography on 06/06/2026 demonstrated a 90% stenosis of the LAD.\n"
    assert "06/06/2026" in deidentify.deidentify(text).redacted_text
