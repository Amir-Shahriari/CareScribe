"""
Generation must hand the clinician the finished document, not the model's
working. A reasoning-capable model emits a planning monologue — sometimes
wrapped in ``<think>…</think>``, sometimes as bare prose terminated by a lone
``</think>``, sometimes (truncated) an unclosed ``<think>``. None of it belongs
in the draft.

Everything here is fabricated; no live model runs.
"""

import pytest

from carescribe.core import carenotes, ollama_client

NOTE = (
    "Patient details: [PATIENT], [MRN]\n\n"
    "S - Subjective\n[PATIENT] reported low mood for [not documented] weeks.\n\n"
    "A - Assessment\nRecurrent depressive disorder.\n"
)


# ----------------------------------------------------------------------------
# strip_reasoning — the whole-text scrub
# ----------------------------------------------------------------------------

def test_a_wellformed_think_block_is_removed():
    raw = f"<think>The user wants a SOAP note. Let me plan.</think>\n\n{NOTE}"
    assert carenotes.strip_reasoning(raw) == NOTE


def test_a_bare_closing_tag_takes_everything_before_it():
    raw = (
        "The user wants a SOAP-structured care note based on the referral. "
        "Let's analyze the source text. Wait, check the rules.\n</think>\n"
        + NOTE
    )
    assert carenotes.strip_reasoning(raw) == NOTE


def test_an_unclosed_think_block_is_dropped_from_the_tag_on():
    raw = f"{NOTE}<think>and now I second-guess myself and rewrite it all"
    assert carenotes.strip_reasoning(raw) == NOTE


def test_multiple_think_blocks_all_go():
    raw = f"<think>plan</think>{NOTE}<think>hmm, revise tense</think>"
    assert carenotes.strip_reasoning(raw).strip() == NOTE.strip()


def test_case_and_whitespace_variants_of_the_tag():
    raw = f"< Think >noodling</ THINK >{NOTE}"
    assert carenotes.strip_reasoning(raw) == NOTE


def test_reasoning_tagged_reasoning_is_also_removed():
    raw = f"<reasoning>step by step</reasoning>\n{NOTE}"
    assert carenotes.strip_reasoning(raw) == NOTE


def test_text_with_no_reasoning_is_untouched_apart_from_leading_space():
    assert carenotes.strip_reasoning(NOTE) == NOTE
    assert carenotes.strip_reasoning(f"   \n{NOTE}") == NOTE


def test_strip_reasoning_is_idempotent():
    raw = f"<think>plan</think>\n{NOTE}"
    once = carenotes.strip_reasoning(raw)
    assert carenotes.strip_reasoning(once) == once


def test_strip_reasoning_tolerates_empty():
    assert carenotes.strip_reasoning("") == ""
    assert carenotes.strip_reasoning(None) is None


# ----------------------------------------------------------------------------
# _without_reasoning — the streaming filter
# ----------------------------------------------------------------------------

def _drain(chunks):
    return "".join(carenotes._without_reasoning(chunks))


def test_stream_with_a_think_block_yields_only_the_answer():
    chunks = ["<think>plan", " more plan</think>", "\n\n", "S - Subjective\n", "text"]
    assert _drain(chunks) == "S - Subjective\ntext"


def test_stream_with_a_bare_closing_tag_yields_only_the_answer():
    chunks = ["The user wants ", "a note. Let's plan.\n", "</think>\n", "S - Subjective"]
    assert _drain(chunks) == "S - Subjective"


def test_stream_close_tag_split_across_chunks():
    chunks = ["reason reason", " <", "/think", ">", "answer body"]
    assert _drain(chunks) == "answer body"


def test_stream_with_no_reasoning_passes_through_unchanged():
    chunks = ["S - Subjective\n", "[PATIENT] reported ", "low mood.\n"]
    assert _drain(chunks) == "S - Subjective\n[PATIENT] reported low mood.\n"


def test_stream_releases_a_long_answer_that_never_carries_a_tag():
    body = "word " * 2000  # well over the internal flush threshold
    assert _drain([body]) == body


def test_stream_filtered_output_matches_strip_reasoning():
    raw = f"<think>a lot of planning here</think>\n{NOTE}"
    assert _drain([raw]) == carenotes.strip_reasoning(raw)


# ----------------------------------------------------------------------------
# wiring — generate_document and generate_care_note drop reasoning
# ----------------------------------------------------------------------------

class ReasoningBackend:
    """A backend that prefixes its answer with a planning monologue."""

    def __init__(self, answer: str = "Draft body.", *, tag: bool = True):
        self.answer = answer
        self.tag = tag
        self.prompt = ""
        self.system = ""

    def generate(self, system, prompt, stream=True, *, grammar=None):
        self.system, self.prompt = system, prompt
        if self.tag:
            yield "<think>Let me work through this"
            yield " step by step.</think>\n\n"
        else:
            yield "The user wants a note. Let's plan it.\n</think>\n"
        for piece in self.answer.split(" "):
            yield piece + " "


def test_generate_document_streams_no_reasoning():
    backend = ReasoningBackend(NOTE)
    out = "".join(
        carenotes.generate_document("De-identified [PATIENT] text.", "SOAP care note", backend)
    )
    assert "<think>" not in out and "</think>" not in out
    assert "Let me work through this" not in out
    assert out.strip() == NOTE.strip()


def test_generate_document_handles_the_bare_closing_tag_variant():
    backend = ReasoningBackend(NOTE, tag=False)
    out = "".join(
        carenotes.generate_document("De-identified [PATIENT] text.", "SOAP care note", backend)
    )
    assert "</think>" not in out
    assert "Let's plan it" not in out
    assert out.strip() == NOTE.strip()


def test_generate_care_note_returns_a_clean_banner_draft():
    backend = ReasoningBackend(NOTE)
    note = carenotes.generate_care_note(
        "De-identified [PATIENT] text.", "SOAP care note", backend=backend
    )
    assert note.startswith("> **DRAFT")
    assert "<think>" not in note and "</think>" not in note
    assert "work through this" not in note


def test_refine_document_also_strips_reasoning():
    backend = ReasoningBackend("Revised body.")
    out = "".join(
        carenotes.refine_document(
            "De-identified [PATIENT] text.", "Old draft.", "tighten the plan", backend
        )
    )
    assert "<think>" not in out and "</think>" not in out
    assert out.strip() == "Revised body."


# ----------------------------------------------------------------------------
# ollama_client — thinking is disabled at the request
# ----------------------------------------------------------------------------

def test_ollama_generate_payload_disables_thinking(monkeypatch):
    captured = {}

    class _Resp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            import json

            return json.dumps({"response": "ok", "done": True}).encode()

    def fake_request(path, payload=None, timeout=0):
        captured["path"] = path
        captured["payload"] = payload
        return _Resp()

    monkeypatch.setattr(ollama_client, "is_up", lambda: True)
    monkeypatch.setattr(ollama_client, "list_models", lambda: ["m"])
    monkeypatch.setattr(ollama_client, "_request", fake_request)

    list(ollama_client.generate("m", "sys", "prompt", stream=False))

    assert captured["path"] == "/api/generate"
    assert captured["payload"]["think"] is False
