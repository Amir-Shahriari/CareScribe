"""vignette_id must survive expand() onto EncounterFacts."""

import random

from finetune.datagen.sampler import expand, sample_encounters
from finetune.datagen.vignettes import VIGNETTES


def test_expand_records_the_source_vignette_id():
    vignette = VIGNETTES[0]
    facts = expand(vignette, random.Random(0))
    assert facts.vignette_id == vignette.id


def test_the_id_is_never_blank_for_a_real_vignette():
    facts = expand(VIGNETTES[0], random.Random(0))
    assert facts.vignette_id != ""


def test_every_sampled_encounter_carries_an_id():
    for facts in sample_encounters(8, seed=3):
        assert facts.vignette_id


def test_ids_come_from_the_known_vignette_set():
    known = {v.id for v in VIGNETTES}
    for facts in sample_encounters(8, seed=4):
        assert facts.vignette_id in known


def test_the_field_defaults_to_empty_when_not_supplied():
    from finetune.datagen.schema import Demographics, EncounterFacts, EncounterType

    facts = EncounterFacts(
        specialty="cardiology",
        encounter_type=EncounterType.NEW,
        demographics=Demographics(age_band="65-74", sex="female"),
        presenting_complaint="chest pain",
    )
    assert facts.vignette_id == ""


def test_documented_gaps_may_not_name_the_id_field():
    """vignette_id is not clinical content, so it is not gappable."""
    import pytest
    from finetune.datagen.schema import Demographics, EncounterFacts, EncounterType

    with pytest.raises(Exception):
        EncounterFacts(
            specialty="cardiology",
            encounter_type=EncounterType.NEW,
            demographics=Demographics(age_band="65-74", sex="female"),
            presenting_complaint="chest pain",
            documented_gaps=["vignette_id"],
        )
