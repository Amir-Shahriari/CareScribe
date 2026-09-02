"""EncounterFacts is the ground truth, so its guarantees are tested first."""

from __future__ import annotations

import pytest

from finetune.datagen.schema import (
    FIELD_NAMES,
    Demographics,
    EncounterFacts,
    EncounterType,
    Finding,
    FormType,
    Medication,
    PlanItem,
)


def _full_facts(**overrides) -> EncounterFacts:
    base = dict(
        specialty="respiratory",
        encounter_type=EncounterType.FOLLOW_UP,
        demographics=Demographics(age_band="40-49", sex="F", occupation="teacher"),
        presenting_complaint="worsening exertional breathlessness over 3 weeks",
        history=[],
        pmh=["asthma"],
        meds=[Medication(name="salbutamol", dose="100mcg", route="inhaled", frequency="PRN")],
        allergies=["penicillin"],
        examination=[Finding(system="respiratory", finding="wheeze", value="bilateral")],
        investigations=[],
        impression=["poorly controlled asthma"],
        plan=[PlanItem(action="step up inhaled steroid", detail="beclometasone 200mcg BD")],
        follow_up="4 weeks",
        documented_gaps=[],
    )
    base.update(overrides)
    return EncounterFacts(**base)


def test_full_instance_round_trips():
    facts = _full_facts()
    again = EncounterFacts.model_validate(facts.model_dump())
    assert again == facts


def test_extra_keys_are_forbidden():
    with pytest.raises(Exception):
        EncounterFacts(
            specialty="gp",
            encounter_type="new",
            demographics=Demographics(age_band="20-29", sex="M"),
            presenting_complaint="cough",
            unexpected_field="boom",
        )


def test_field_names_matches_the_model():
    assert FIELD_NAMES == frozenset(EncounterFacts.model_fields)
    assert "presenting_complaint" in FIELD_NAMES


@pytest.mark.parametrize("bad", ["NHS 4857773456", "John Smith", "ID 12345"])
def test_demographics_rejects_identifier_shapes(bad):
    with pytest.raises(Exception):
        Demographics(age_band="30-39", sex="F", occupation=bad)


def test_demographics_allows_ordinary_occupations():
    for ok in ("teacher", "bus driver", "retired", "software engineer"):
        Demographics(age_band="30-39", sex="F", occupation=ok)


def test_documented_gap_must_be_an_empty_real_field():
    # empty field named as a gap: fine
    _full_facts(meds=[], documented_gaps=["meds"])
    # populated field named as a gap: rejected
    with pytest.raises(Exception):
        _full_facts(meds=[Medication(name="aspirin")], documented_gaps=["meds"])
    # unknown field name: rejected
    with pytest.raises(Exception):
        _full_facts(documented_gaps=["not_a_field"])
    # real field that may not be gapped: rejected
    with pytest.raises(Exception):
        _full_facts(presenting_complaint="cough", documented_gaps=["presenting_complaint"])


def test_form_type_and_encounter_type_are_string_enums():
    assert FormType.SOAP == "soap"
    assert EncounterType.CRISIS == "crisis"
    assert {t.value for t in FormType} == {
        "soap",
        "care_plan",
        "progress_note",
        "handover",
        "uploaded_template",
    }
