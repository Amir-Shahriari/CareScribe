"""The eval harness: scoring, aggregation, the ship gate, the report."""

from __future__ import annotations

from finetune.datagen.schema import FormType
from finetune.eval.metrics import aggregate, score_draft, style_match
from finetune.eval.regression import regressed, regression_items, score_regression
from finetune.eval.report import build_report
from finetune.eval.run_eval import (
    CallableCompleter,
    RunResult,
    compare,
    make_eval_set,
    run,
)

EVAL = make_eval_set(24, seed=4242)


def test_eval_set_is_non_trivial_and_well_formed():
    assert len(EVAL) >= 15
    for item in EVAL:
        assert "[" in item.document
        assert item.target.strip()


def _perfect(system, user):
    # echo the reference scaffold back — a "model" that always nails it
    return _TARGET_BY_DOC[user]


_TARGET_BY_DOC = {}
for _it in EVAL:
    _msgs = _it.messages()
    _TARGET_BY_DOC[_msgs[1]["content"]] = _it.target


def test_a_perfect_model_scores_one_on_every_gate():
    result = run(CallableCompleter(_perfect), EVAL)
    for metric in ("format", "faithfulness", "placeholder_integrity", "residual_clean"):
        assert result.metrics[metric] == 1.0


def test_a_broken_model_scores_below_perfect():
    def broken(system, user):
        return "Here is your note.\n\nBP was 999/999. [WARD_9] noted."

    result = run(CallableCompleter(broken), EVAL)
    assert result.metrics["format"] < 1.0
    assert result.metrics["faithfulness"] < 1.0


def test_compare_ship_gate():
    good = run(CallableCompleter(_perfect), EVAL)

    def worse(system, user):
        return _TARGET_BY_DOC[user].replace("**", "")  # drop heading markers

    bad = run(CallableCompleter(worse), EVAL)
    verdict_up = compare(base=bad, tuned=good)
    assert verdict_up["ship"] is True
    assert verdict_up["regressions"] == []

    verdict_down = compare(base=good, tuned=bad)
    assert verdict_down["ship"] is False
    assert "format" in verdict_down["regressions"]


def test_style_match_is_one_for_identical_text():
    t = "**A**\n- x\n\n**B**\n- y"
    assert style_match(t, t) == 1.0
    assert style_match("**B**\n- y\n\n**A**\n- x", t) < 1.0


def test_report_renders_and_states_the_verdict():
    good = run(CallableCompleter(_perfect), EVAL)
    md, payload = build_report(good, good)
    assert "Ship gate:" in md
    assert payload["ship"] is True
    assert "| format |" in md


def test_regression_set_loads_and_scores():
    items = regression_items(limit=4)
    assert items
    result = score_regression(CallableCompleter(_perfect_regression), items)
    assert result["placeholder_integrity"] == 1.0
    assert regressed(result, result) == []


def _perfect_regression(system, user):
    # a plausible SOAP skeleton that keeps placeholders and adds no identifiers
    return (
        "**S — Subjective**\n- as documented\n\n"
        "**O — Objective**\n- as documented\n\n"
        "**A — Assessment**\n- as documented\n\n"
        "**P — Plan**\n- as documented"
    )
