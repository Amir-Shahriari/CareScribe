"""The independent judge is actually reachable from a run, and stays blind.

`judge.py` existed but nothing called it, so no reported number had ever been
graded by anything except the rule grader that shares an artefact with the
target builder. These tests pin the wiring, not the judge's own parsing
(`test_judge.py` covers that).
"""

from __future__ import annotations

import inspect
from argparse import Namespace

import pytest

from finetune.eval import run_eval
from finetune.eval.metrics import DraftScore
from finetune.eval.report import build_report
from finetune.eval.run_eval import RunResult


class _Item:
    """Just enough EvalItem for `_judge_for`: a source note and nothing else."""

    def __init__(self, document: str) -> None:
        self.document = document


def _result(scores, drafts):
    return RunResult({"faithfulness": 1.0}, 1.0, len(drafts), scores, drafts)


def _score(faithfulness: float) -> DraftScore:
    return DraftScore(1.0, faithfulness, 1.0, 1.0)


@pytest.fixture
def args():
    return Namespace(judge=True, judge_model="test-judge")


def test_run_keeps_the_drafts_it_scored():
    """Without the drafts, nothing downstream can grade them a second way."""

    class _Model:
        def complete(self, system, user):
            return "**Subjective**\ndrafted"

    items = run_eval.make_eval_set(2, seed=7)
    if not items:
        pytest.skip("generator produced no eval items at this seed")
    result = run_eval.run(_Model(), items)
    assert len(result.drafts) == len(items)
    assert all(d == "**Subjective**\ndrafted" for d in result.drafts)


def test_judge_is_skipped_unless_asked(args):
    args.judge = False
    assert run_eval._judge_for(args, [], _result([], []), _result([], [])) is None


def test_disagreement_with_the_rule_grader_is_counted(args, monkeypatch):
    """A draft the rules passed and the judge rejected is the number we want."""
    replies = iter([
        '{"supported": false, "unsupported_claims": ["Troponin raised"]}',
        '{"supported": true, "unsupported_claims": []}',
    ] * 2)
    monkeypatch.setattr(
        "finetune.eval.judge.OllamaJudge.complete",
        lambda self, system, user: next(replies),
    )
    items = [_Item("note one"), _Item("note two")]
    scores = [_score(1.0), _score(1.0)]
    out = run_eval._judge_for(
        args, items, _result(scores, ["a", "b"]), _result(scores, ["a", "b"])
    )
    assert out["n"] == 2
    assert out["base"]["supported"] == 0.5
    assert out["base"]["rules_ok_judge_bad"] == 1
    assert out["base"]["unparsed"] == 0


def test_an_unparsable_reply_is_reported_not_scored(args, monkeypatch):
    monkeypatch.setattr(
        "finetune.eval.judge.OllamaJudge.complete",
        lambda self, system, user: "I could not decide.",
    )
    items = [_Item("note")]
    out = run_eval._judge_for(
        args, items, _result([_score(1.0)], ["a"]), _result([_score(1.0)], ["a"])
    )
    assert out["base"]["unparsed"] == 1
    assert out["base"]["supported"] is None


def test_the_judge_signature_cannot_accept_facts():
    """There must be no parameter through which they could be passed."""
    import finetune.eval.judge as judge_module

    assert "facts" not in inspect.signature(judge_module.judge_draft).parameters


def test_no_fact_value_reaches_what_the_judge_is_actually_sent(args, monkeypatch):
    """Capture the real prompt and look for the facts in it.

    An earlier version of this test grepped the source of `_judge_for` for the
    string "item.facts". That passes for any regression that reaches the facts
    by another spelling, and fails for a harmless rename — it checked how the
    code reads, not what it sends. This inspects the bytes that actually go to
    the judge.
    """
    sent = []
    monkeypatch.setattr(
        "finetune.eval.judge.OllamaJudge.complete",
        lambda self, system, user: sent.append(user)
        or '{"supported": true, "unsupported_claims": []}',
    )

    secret = "SUPERCALIFRAGILISTIC_FACT_MARKER"

    class _FactfulItem:
        """Every attribute except `document` carries the marker."""

        document = "Source note. Patient seen today."
        facts = {"impression": secret, "plan": secret}
        target = secret
        form = secret

    run_eval._judge_for(
        args, [_FactfulItem()],
        _result([_score(1.0)], ["draft"]), _result([_score(1.0)], ["draft"]),
    )

    assert sent, "the judge was never called"
    for prompt in sent:
        assert secret not in prompt
        assert "Source note." in prompt


def test_a_length_mismatch_is_refused_not_silently_truncated(args):
    """zip() would drop items and under-report the rate with no error."""
    items = [_Item("one"), _Item("two")]
    short = _result([_score(1.0)], ["only one draft"])
    with pytest.raises(ValueError, match="cannot align"):
        run_eval._judge_for(args, items, short, short)


def test_the_report_renders_a_judge_section():
    judge = {
        "model": "test-judge",
        "n": 2,
        "base": {"supported": 0.5, "rules_ok_judge_bad": 1, "unparsed": 0},
        "tuned": {"supported": 1.0, "rules_ok_judge_bad": 0, "unparsed": 0},
    }
    md, payload = build_report(
        _result([_score(1.0)], ["a"]), _result([_score(1.0)], ["a"]), judge=judge
    )
    assert "Independent judge" in md
    assert "test-judge" in md
    assert "the judge rejected" in md
    assert payload["judge"] == judge


def test_the_report_omits_the_section_when_no_judge_ran():
    md, payload = build_report(_result([_score(1.0)], ["a"]), _result([_score(1.0)], ["a"]))
    assert "Independent judge" not in md
    assert payload["judge"] is None


def test_the_report_keeps_the_two_models_apart_when_they_share_a_name():
    """Deriving the side from name equality collapsed both rows onto base.

    Nothing in `build_report`'s signature forbids equal display names, and
    comparing two checkpoints of the same model is exactly when you would pass
    them — and exactly when silently printing base's numbers twice would be
    read as "no difference".
    """
    judge = {
        "model": "test-judge",
        "n": 2,
        "base": {"supported": 0.1, "rules_ok_judge_bad": 9, "unparsed": 0},
        "tuned": {"supported": 0.9, "rules_ok_judge_bad": 1, "unparsed": 0},
    }
    md, _ = build_report(
        _result([_score(1.0)], ["a"]), _result([_score(1.0)], ["a"]),
        base_name="model", tuned_name="model", judge=judge,
    )
    assert "0.100" in md and "0.900" in md
    assert "9 drafts" in md and "1 drafts" in md
