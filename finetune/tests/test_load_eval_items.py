"""Eval reads the committed held-out split; it does not re-sample."""

import json
import random

import pytest

from finetune.assemble.pairs import make_pair, write_jsonl
from finetune.datagen.sampler import expand
from finetune.datagen.schema import FormType
from finetune.datagen.vignettes import VIGNETTES
from finetune.eval.run_eval import load_eval_items

DOC = "Name: [PATIENT]\nSeen: [DATE]"
TARGET = "**Subjective**\nx"


def _written(tmp_path):
    facts = expand(VIGNETTES[0], random.Random(0))
    pair = make_pair(
        facts, FormType.SOAP, DOC, TARGET, known_placeholders=["[PATIENT]", "[DATE]"]
    )
    path = tmp_path / "test.jsonl"
    write_jsonl([pair], path)
    return facts, path


def test_one_item_is_rebuilt_from_the_file(tmp_path):
    _, path = _written(tmp_path)
    assert len(load_eval_items(path)) == 1


def test_the_document_and_form_survive(tmp_path):
    _, path = _written(tmp_path)
    item = load_eval_items(path)[0]
    assert item.document == DOC
    assert item.form is FormType.SOAP


def test_the_placeholders_and_target_survive(tmp_path):
    _, path = _written(tmp_path)
    item = load_eval_items(path)[0]
    assert item.known_placeholders == ["[PATIENT]", "[DATE]"]
    assert item.target == TARGET


def test_the_facts_survive(tmp_path):
    facts, path = _written(tmp_path)
    item = load_eval_items(path)[0]
    assert item.facts.vignette_id == facts.vignette_id
    assert item.facts.presenting_complaint == facts.presenting_complaint


def test_blank_lines_are_skipped(tmp_path):
    _, path = _written(tmp_path)
    path.write_text(path.read_text(encoding="utf-8") + "\n\n", encoding="utf-8")
    assert len(load_eval_items(path)) == 1


def test_a_pair_written_before_task_079_is_rejected_loudly(tmp_path):
    """An old jsonl lacks document/facts. Fail, don't silently eval on nothing."""
    path = tmp_path / "old.jsonl"
    path.write_text(
        json.dumps({"messages": [{"role": "assistant", "content": "x"}],
                    "meta": {"form_type": "soap"}}) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="document"):
        load_eval_items(path)
