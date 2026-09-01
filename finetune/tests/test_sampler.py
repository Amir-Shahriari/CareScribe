"""The sampler must be deterministic, valid, and honest about gaps."""

from __future__ import annotations

import random

import pytest

from finetune.datagen.sampler import expand, sample_encounters
from finetune.datagen.schema import EncounterFacts
from finetune.datagen.vignettes import SPECIALTIES, VIGNETTES


def test_vignette_library_is_broad_and_unique():
    ids = [v.id for v in VIGNETTES]
    assert len(ids) == len(set(ids))
    assert len(VIGNETTES) >= 8
    # domains the user asked for
    assert "general practice" in SPECIALTIES
    assert "community mental health" in SPECIALTIES
    assert len(SPECIALTIES) >= 5


@pytest.mark.parametrize("vignette", VIGNETTES, ids=lambda v: v.id)
def test_every_vignette_expands_to_valid_facts(vignette):
    rng = random.Random(1234)
    for _ in range(5):
        facts = expand(vignette, rng, gap_probability=0.5)
        assert isinstance(facts, EncounterFacts)
        assert facts.specialty == vignette.specialty
        # gaps only ever name fields the vignette allows, and they are empty
        for name in facts.documented_gaps:
            assert name in vignette.gappable
            assert getattr(facts, name) in (None, [], "")


def test_sampling_is_deterministic_for_a_seed():
    a = [f.model_dump() for f in sample_encounters(30, seed=7)]
    b = [f.model_dump() for f in sample_encounters(30, seed=7)]
    c = [f.model_dump() for f in sample_encounters(30, seed=8)]
    assert a == b
    assert a != c


def test_gap_probability_zero_produces_no_gaps():
    facts = list(sample_encounters(40, seed=3, gap_probability=0.0))
    assert all(f.documented_gaps == [] for f in facts)


def test_gap_probability_one_gaps_everything_gappable():
    # pick a vignette that has gappable fields
    vignette = next(v for v in VIGNETTES if v.gappable)
    facts = expand(vignette, random.Random(0), gap_probability=1.0)
    assert set(facts.documented_gaps) == set(vignette.gappable)


def test_specialty_weight_of_zero_excludes_a_domain():
    weights = {s: 0.0 for s in SPECIALTIES if s != "cardiology"}
    facts = list(sample_encounters(25, seed=2, specialty_weights=weights))
    assert {f.specialty for f in facts} == {"cardiology"}
