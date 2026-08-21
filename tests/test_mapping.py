"""
Mapping-layer checks: type normalisation, surface forms, and re-identification.

Re-identification is not used by the current stage's UI — nothing generates
text to restore yet — but the map is what makes the placeholders reversible for
the reviewer, and the fuzzy repair path is the reason a mangled placeholder is
never silently swapped for the wrong person.
"""

import pytest

from carescribe.core import mapping


# ==========================================================================
# Type normalisation
# ==========================================================================

@pytest.mark.parametrize(
    "raw,expected",
    [
        ("patient_name", "PATIENT_NAME"),
        ("Patient", "PATIENT_NAME"),
        ("PERSON", "PERSON"),
        ("name", "PERSON"),
        ("next of kin", "RELATIVE_NAME"),
        ("doctor", "PROVIDER_NAME"),
        ("clinician", "PROVIDER_NAME"),
        ("ORGANIZATION", "FACILITY"),
        ("hospital", "FACILITY"),
        ("date_time", "DATE"),
        ("date of birth", "DOB"),
        ("nhs_no", "NHS_NUMBER"),
        ("hospital number", "MRN"),
        ("postcode", "ADDRESS"),
        ("street_address", "ADDRESS"),
        # A bare place name is not a postal address. They were the same type
        # until a letterhead town ("Harrogate, North Yorkshire") needed to be
        # redactable without loosening the gate that preserves "visiting family
        # in Leeds".
        ("location", "LOCATION"),
        ("gpe", "LOCATION"),
        ("telephone", "PHONE"),
        ("something unheard of", "OTHER_ID"),
        (None, "OTHER_ID"),
        ("", "OTHER_ID"),
    ],
)
def test_normalise_type(raw, expected):
    assert mapping.normalise_type(raw) == expected


def test_every_stem_maps_a_real_type():
    for entity_type in mapping._PLACEHOLDER_STEMS:
        assert entity_type in mapping.ENTITY_TYPES


# ==========================================================================
# Placeholders
# ==========================================================================

def test_single_value_gets_a_bare_placeholder():
    result = mapping.assign_placeholders([{"type": "MRN", "value": "4471982"}])
    assert result[0]["placeholder"] == "[MRN]"


def test_multiple_values_get_numbered_placeholders():
    result = mapping.assign_placeholders(
        [{"type": "PROVIDER_NAME", "value": "A Smith"},
         {"type": "PROVIDER_NAME", "value": "B Jones"}]
    )
    assert [e["placeholder"] for e in result] == ["[CLINICIAN_1]", "[CLINICIAN_2]"]


def test_existing_placeholder_is_preserved():
    result = mapping.assign_placeholders(
        [{"type": "MRN", "value": "4471982", "placeholder": "[RECORD]"}]
    )
    assert result[0]["placeholder"] == "[RECORD]"


def test_dedupe_is_case_insensitive_and_keeps_first_casing():
    result = mapping.dedupe_entities(
        [{"type": "PERSON", "value": "Chen"}, {"type": "PERSON", "value": "CHEN"}]
    )
    assert [e["value"] for e in result] == ["Chen"]


def test_dedupe_drops_dangerously_short_values():
    result = mapping.dedupe_entities([{"type": "OTHER_ID", "value": "a"}])
    assert result == []


def test_dedupe_carries_the_keep_action():
    result = mapping.dedupe_entities(
        [{"type": "FACILITY", "value": "Riverside Clinic", "action": "Keep"}]
    )
    assert result[0]["action"] == mapping.KEEP


def test_dedupe_entities_keeps_confidence():
    entities = [{"type": "PERSON", "value": "Jo Bloggs", "confidence": "auto"}]
    result = mapping.dedupe_entities(entities)
    assert result[0]["confidence"] == "auto"


def test_dedupe_entities_defaults_missing_confidence_to_review():
    entities = [{"type": "PERSON", "value": "Jo Bloggs"}]
    result = mapping.dedupe_entities(entities)
    assert result[0]["confidence"] == "review"


def test_assign_placeholders_keeps_confidence():
    """assign_placeholders is analyze()'s last step — a silent drop here is permanent."""
    result = mapping.assign_placeholders(
        [{"type": "PERSON", "value": "Jo Bloggs", "confidence": "auto"}]
    )
    assert result[0]["confidence"] == "auto"


def test_dedupe_entities_worst_case_wins_across_duplicates():
    """If ANY occurrence of a value was low-confidence, the whole entity is."""
    entities = [
        {"type": "PERSON", "value": "Jo Bloggs", "confidence": "auto"},
        {"type": "PERSON", "value": "jo bloggs", "confidence": "review"},
    ]
    result = mapping.dedupe_entities(entities)
    assert len(result) == 1
    assert result[0]["confidence"] == "review"


# ==========================================================================
# Surface forms and the Keep action
# ==========================================================================

def test_surface_forms_reports_collisions():
    entities = [
        {"type": "PATIENT_NAME", "value": "Margaret Chen", "placeholder": "[PATIENT]"},
        {"type": "RELATIVE_NAME", "value": "David Chen", "placeholder": "[RELATIVE]"},
    ]
    expanded = mapping.surface_forms(entities)
    assert expanded.ambiguous  # both people claim "Chen"
    assert "chen" in expanded.forms  # ...and it is still redacted


def test_kept_rows_contribute_no_surface_forms():
    entities = [
        {"type": "FACILITY", "value": "Riverside Clinic",
         "placeholder": "[CLINIC]", "action": "Keep"},
    ]
    assert mapping.surface_forms(entities).forms == {}


def test_kept_rows_are_absent_from_the_map():
    entities = [
        {"type": "MRN", "value": "4471982", "placeholder": "[MRN]", "action": "Keep"},
        {"type": "NHS_NUMBER", "value": "943 476 5919", "placeholder": "[NHS_NO]"},
    ]
    assert mapping.build_map(entities) == {"[NHS_NO]": "943 476 5919"}


def test_find_known_as():
    assert mapping.find_known_as('Known as: "Peggy"') == "Peggy"
    assert mapping.find_known_as("Preferred name: Bill") == "Bill"
    assert mapping.find_known_as("No alias here.") is None


def test_residual_values_reports_what_did_not_replace():
    entities = [{"type": "PERSON", "value": "Chen", "placeholder": "[P]"}]
    assert mapping.residual_values("Chen was seen.", entities) == ["Chen"]
    assert mapping.residual_values("[P] was seen.", entities) == []


# ==========================================================================
# Re-identification
# ==========================================================================

MAP = {"[PATIENT_1]": "Margaret Chen", "[MRN_1]": "4471982", "[CLINIC_1]": "St. Aidan's"}


def test_round_trip():
    redacted = "[PATIENT_1] attended [CLINIC_1] (record [MRN_1])."
    assert mapping.reidentify(redacted, MAP) == (
        "Margaret Chen attended St. Aidan's (record 4471982)."
    )


def test_mangled_placeholder_is_repaired():
    result = mapping.reidentify_detailed("[MATIENT_1] attended.", MAP)
    assert result.text == "Margaret Chen attended."
    assert result.corrected == [("[MATIENT_1]", "[PATIENT_1]")]


def test_ambiguous_placeholder_is_refused_not_guessed():
    """Guessing between [MRN_1] and [MRN_2] would attach the wrong identity."""
    ambiguous = {"[MRN_1]": "111", "[MRN_2]": "222"}
    assert mapping.resolve_placeholder("[MRN_3]", ambiguous) is None


def test_invented_placeholder_is_left_alone():
    result = mapping.reidentify_detailed("[GHOST_9] appeared.", MAP)
    assert result.text == "[GHOST_9] appeared."
    assert result.unresolved == ["[GHOST_9]"]


@pytest.mark.parametrize("junk", ["[", "]", "[]", "[[[", "[_]", "[123]", "[a]", ""])
def test_reidentify_never_crashes(junk):
    mapping.reidentify(f"text {junk} more", MAP)


def test_empty_map_is_a_no_op():
    assert mapping.reidentify("[PATIENT_1]", {}) == "[PATIENT_1]"


def test_non_regex_placeholder_still_substitutes():
    assert mapping.reidentify("[Pt] here", {"[Pt]": "Margaret Chen"}) == "Margaret Chen here"


def test_edit_distance_caps_out():
    assert mapping._edit_distance("[MRN_1]", "[MRN_1]") == 0
    assert mapping._edit_distance("abc", "xyzqrstuv") > 2
