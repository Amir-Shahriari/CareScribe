"""The judge grades against the source note, never against EncounterFacts."""

import inspect
import pathlib

from finetune.eval.judge import JudgeVerdict, judge_draft


def _canned(payload):
    return lambda system, user: payload


def test_a_clean_draft_is_supported():
    v = judge_draft(
        "Chest pain. BP 140/90.",
        "**Objective**\nBP 140/90.",
        complete=_canned('{"supported": true, "unsupported_claims": []}'),
    )
    assert v.supported is True
    assert v.unsupported_claims == []


def test_an_invented_claim_is_caught():
    v = judge_draft(
        "Chest pain. BP 140/90.",
        "**Objective**\nBP 140/90. Troponin raised.",
        complete=_canned(
            '{"supported": false, "unsupported_claims": ["Troponin raised"]}'
        ),
    )
    assert v.supported is False
    assert "Troponin raised" in v.unsupported_claims


def test_json_wrapped_in_prose_is_still_parsed():
    v = judge_draft(
        "x", "y", complete=_canned('Sure! {"supported": true, '
                                   '"unsupported_claims": []} Hope that helps.')
    )
    assert v.supported is True


def test_unparseable_output_is_not_silently_a_pass():
    v = judge_draft("x", "y", complete=_canned("I think it looks fine, mostly."))
    assert v.supported is None
    assert v.raw == "I think it looks fine, mostly."


def test_a_non_boolean_supported_value_is_treated_as_unparsed():
    v = judge_draft("x", "y", complete=_canned('{"supported": "yes"}'))
    assert v.supported is None


def test_the_judge_is_never_handed_the_facts():
    """Its whole value is that it cannot see the scaffold's source of truth."""
    params = inspect.signature(judge_draft).parameters
    assert "facts" not in params
    assert set(params) == {"source", "draft", "complete"}


def test_carescribe_never_imports_the_judge():
    """The judge opens a socket. It must stay outside the app's import graph."""
    root = pathlib.Path(__file__).resolve().parents[2] / "carescribe"
    offenders = []
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "eval.judge" in text or "eval import judge" in text:
            offenders.append(str(path))
    assert offenders == []
