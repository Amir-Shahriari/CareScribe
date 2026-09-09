"""vignette_id reaches pair metadata, and stays out of the facts number-set."""

import random

from finetune.assemble.pairs import make_pair
from finetune.assemble.validators import _numbers_in_facts
from finetune.datagen.sampler import expand
from finetune.datagen.schema import FormType
from finetune.datagen.vignettes import VIGNETTES


def _facts():
    return expand(VIGNETTES[0], random.Random(0))


def test_make_pair_records_the_vignette_id():
    facts = _facts()
    pair = make_pair(facts, FormType.SOAP, "doc [PATIENT]", "**Subjective**\nx")
    assert pair.meta["vignette_id"] == facts.vignette_id


def test_the_recorded_id_is_a_real_vignette():
    facts = _facts()
    pair = make_pair(facts, FormType.SOAP, "doc [PATIENT]", "**Subjective**\nx")
    assert pair.meta["vignette_id"] in {v.id for v in VIGNETTES}


def test_the_id_survives_the_json_line():
    import json

    facts = _facts()
    pair = make_pair(facts, FormType.SOAP, "doc [PATIENT]", "**Subjective**\nx")
    assert json.loads(pair.to_json_line())["meta"]["vignette_id"] == facts.vignette_id


def test_existing_meta_keys_are_untouched():
    facts = _facts()
    pair = make_pair(facts, FormType.SOAP, "doc [PATIENT]", "**Subjective**\nx")
    for key in ("form_type", "specialty", "encounter_type", "styled",
                "polished", "documented_gaps"):
        assert key in pair.meta


def test_digits_in_the_vignette_id_are_not_supported_numbers():
    """A skeleton named cardio_hf_02 must not make "02" a stateable number."""
    facts = _facts().model_copy(update={"vignette_id": "cardio_hf_0299"})
    assert "0299" not in _numbers_in_facts(facts)


def test_real_clinical_numbers_are_still_collected():
    facts = _facts()
    numbers = _numbers_in_facts(facts)
    assert isinstance(numbers, set)
    # the vignette's own content supplies at least one number (a dose, a value)
    assert numbers
