"""A written pair must carry enough to rebuild an eval item from disk."""

import json
import random

from finetune.assemble.pairs import make_pair
from finetune.datagen.sampler import expand
from finetune.datagen.schema import EncounterFacts, FormType
from finetune.datagen.vignettes import VIGNETTES

DOC = "Name: [PATIENT]\nSeen: [DATE]"


def _made():
    facts = expand(VIGNETTES[0], random.Random(0))
    pair = make_pair(
        facts,
        FormType.SOAP,
        DOC,
        "**Subjective**\nx",
        known_placeholders=["[PATIENT]", "[DATE]"],
    )
    return facts, pair


def test_meta_carries_the_raw_document():
    _, pair = _made()
    assert pair.meta["document"] == DOC


def test_meta_carries_the_known_placeholders():
    _, pair = _made()
    assert pair.meta["known_placeholders"] == ["[PATIENT]", "[DATE]"]


def test_placeholders_default_to_empty_when_not_given():
    facts = expand(VIGNETTES[0], random.Random(0))
    pair = make_pair(facts, FormType.SOAP, DOC, "**Subjective**\nx")
    assert pair.meta["known_placeholders"] == []


def test_facts_survive_a_json_round_trip():
    facts, pair = _made()
    revived = EncounterFacts(**json.loads(pair.to_json_line())["meta"]["facts"])
    assert revived.presenting_complaint == facts.presenting_complaint
    assert revived.vignette_id == facts.vignette_id
    assert revived.documented_gaps == facts.documented_gaps


def test_the_whole_pair_is_json_serialisable():
    _, pair = _made()
    payload = json.loads(pair.to_json_line())
    assert payload["messages"][-1]["content"] == "**Subjective**\nx"
    assert payload["meta"]["document"] == DOC


def test_earlier_meta_keys_are_untouched():
    _, pair = _made()
    for key in ("form_type", "specialty", "encounter_type", "styled",
                "polished", "documented_gaps", "vignette_id"):
        assert key in pair.meta
