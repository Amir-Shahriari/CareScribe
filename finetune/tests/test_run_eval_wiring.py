"""main() reads the held-out split, and reports overlap and confabulation."""

import random
import types

from finetune.assemble.pairs import make_pair, write_jsonl
from finetune.datagen.sampler import expand
from finetune.datagen.schema import FormType
from finetune.datagen.vignettes import VIGNETTES
from finetune.eval.run_eval import _confabulation_for, _overlap_for, load_eval_items


def _write_split(tmp_path, name, target):
    facts = expand(VIGNETTES[0], random.Random(0))
    pair = make_pair(
        facts, FormType.SOAP, "Name: [PATIENT]", target, known_placeholders=["[PATIENT]"]
    )
    path = tmp_path / f"{name}.jsonl"
    write_jsonl([pair], path)
    return path


def _args(**kw):
    base = dict(resample=False, test_jsonl="", train_jsonl="", gap_probes=0)
    base.update(kw)
    return types.SimpleNamespace(**base)


def test_messages_pair_gives_a_system_and_user_string(tmp_path):
    item = load_eval_items(_write_split(tmp_path, "test", "**S**\nx"))[0]
    system, user = item.messages_pair()
    assert isinstance(system, str) and isinstance(user, str)
    assert "[PATIENT]" in user


def test_overlap_finds_the_sibling_train_split(tmp_path):
    _write_split(tmp_path, "train", "**S**\nidentical body text here")
    test_path = _write_split(tmp_path, "test", "**S**\nidentical body text here")
    items = load_eval_items(test_path)
    report = _overlap_for(_args(test_jsonl=str(test_path)), items)
    assert report is not None
    assert report["n_above_0_6"] == 1


def test_overlap_is_absent_when_there_is_no_train_split(tmp_path):
    test_path = _write_split(tmp_path, "test", "**S**\nx")
    items = load_eval_items(test_path)
    assert _overlap_for(_args(test_jsonl=str(test_path)), items) is None


def test_overlap_is_skipped_when_resampling(tmp_path):
    """A resampled set has no committed train split to compare against."""
    _write_split(tmp_path, "train", "**S**\nx")
    test_path = _write_split(tmp_path, "test", "**S**\nx")
    items = load_eval_items(test_path)
    assert _overlap_for(_args(test_jsonl=str(test_path), resample=True), items) is None


def test_confabulation_is_absent_when_probes_are_disabled():
    assert _confabulation_for(_args(gap_probes=0), None, None) is None


def test_confabulation_scores_both_models():
    """Writing "Not documented." never confabulates; inventing content does.

    Both fakes answer under the headings each probe actually gaps, looked up
    from the probe itself. An earlier version hardcoded `**Follow-up**`, which
    stopped measuring anything the moment new vignettes changed what
    `make_gap_probes(3, seed=2000)` draws: neither model wrote under a gapped
    heading at all, so both scored 0.0 and the test failed for the wrong reason.
    """
    from finetune.eval.gap_probe import gapped_headings, make_gap_probes

    probes = make_gap_probes(3, seed=2000)
    assert probes, "no gap probes generated"
    assert all(gapped_headings(p.target) for p in probes)

    def _model(body):
        def complete(_self, system, user):
            probe = next(p for p in probes if p.messages_pair()[1] == user)
            return "\n".join(
                f"**{heading}**\n{body}\n" for heading in gapped_headings(probe.target)
            )

        return type("Fake", (), {"complete": complete})()

    result = _confabulation_for(
        _args(gap_probes=3), _model("Not documented."), _model("Review in six weeks.")
    )
    assert result["n"] == 3
    assert result["base"] == 0.0
    assert result["tuned"] > 0.0
