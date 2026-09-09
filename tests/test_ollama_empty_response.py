"""An empty or errored Ollama response must raise, not yield an empty draft.

The streaming path already raises on an error chunk. The non-streaming path
did not look at ``error`` at all, and yielded nothing when the model produced
no tokens -- which the caller banks as a finished draft.
"""

from __future__ import annotations

import io
import json

import pytest

from carescribe.core import ollama_client


class _Response(io.BytesIO):
    """Enough of an HTTP response for ``generate`` to read once."""

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _patch(monkeypatch, payload: dict):
    monkeypatch.setattr(
        ollama_client,
        "_request",
        lambda *a, **k: _Response(json.dumps(payload).encode("utf-8")),
    )


def _run(monkeypatch, payload):
    _patch(monkeypatch, payload)
    return "".join(ollama_client.generate("m", "sys", "prompt", stream=False))


def test_a_normal_response_is_returned(monkeypatch):
    assert _run(monkeypatch, {"response": "Hello."}) == "Hello."


def test_an_empty_response_raises(monkeypatch):
    with pytest.raises(ollama_client.OllamaError, match="no output"):
        _run(monkeypatch, {"response": ""})


def test_a_missing_response_field_raises(monkeypatch):
    with pytest.raises(ollama_client.OllamaError, match="no output"):
        _run(monkeypatch, {})


def test_an_error_field_raises_with_the_servers_message(monkeypatch):
    with pytest.raises(ollama_client.OllamaError, match="model not found"):
        _run(monkeypatch, {"error": "model not found"})


def test_an_error_beats_an_empty_response(monkeypatch):
    """The server's own explanation is more useful than our generic one."""
    with pytest.raises(ollama_client.OllamaError, match="context length"):
        _run(monkeypatch, {"error": "context length exceeded", "response": ""})


def test_whitespace_only_output_is_still_output(monkeypatch):
    """Only a genuinely empty string is a failure; whitespace is the model's."""
    assert _run(monkeypatch, {"response": " "}) == " "
