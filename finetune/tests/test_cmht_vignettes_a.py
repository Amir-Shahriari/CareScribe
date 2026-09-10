"""The two community mental health skeletons added by task 090 sample cleanly."""

from __future__ import annotations

import random

import pytest

from finetune.assemble.build_target import build_target
from finetune.assemble.validators import validate
from finetune.datagen.sampler import expand
from finetune.datagen.schema import FormType
from finetune.datagen.vignettes import VIGNETTES

NEW_IDS = ("cmht_anxiety_new", "cmht_ptsd_assessment")


def _vignette(vignette_id):
    return next(v for v in VIGNETTES if v.id == vignette_id)


def test_both_vignettes_are_registered():
    ids = [v.id for v in VIGNETTES]
    for vignette_id in NEW_IDS:
        assert vignette_id in ids


def test_vignette_ids_stay_unique():
    ids = [v.id for v in VIGNETTES]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("vignette_id", NEW_IDS)
def test_gappable_names_real_fields(vignette_id):
    vignette = _vignette(vignette_id)
    assert vignette.gappable
    for field in vignette.gappable:
        assert hasattr(vignette, field), field


@pytest.mark.parametrize("vignette_id", NEW_IDS)
def test_expands_without_gaps(vignette_id):
    for seed in range(5):
        facts = expand(_vignette(vignette_id), random.Random(seed))
        assert facts.presenting_complaint
        assert not facts.documented_gaps


@pytest.mark.parametrize("vignette_id", NEW_IDS)
def test_every_gappable_field_can_be_blanked(vignette_id):
    vignette = _vignette(vignette_id)
    seen = set()
    for seed in range(12):
        facts = expand(vignette, random.Random(seed), gap_probability=1.0)
        seen.update(facts.documented_gaps or [])
    assert seen == set(vignette.gappable)


@pytest.mark.parametrize("vignette_id", NEW_IDS)
def test_target_validates_for_every_form(vignette_id):
    for seed in range(3):
        facts = expand(_vignette(vignette_id), random.Random(seed))
        for form in FormType:
            if form is FormType.UPLOADED_TEMPLATE:
                continue
            report = validate(build_target(facts, form), facts, form)
            assert report.format_ok and report.faithful_ok
            assert report.placeholder_ok and report.residual_ok
