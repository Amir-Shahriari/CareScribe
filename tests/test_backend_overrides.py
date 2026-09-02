# tests/test_backend_overrides.py
from __future__ import annotations

import pytest

from carescribe.core import backends
from carescribe.core.carenotes import OllamaBackend


def test_ollama_backend_default_temperature_is_zero():
    assert OllamaBackend("llama3.1:8b").temperature == 0.0


def test_select_backend_honours_explicit_ollama_model(monkeypatch):
    monkeypatch.setattr(backends.ollama_client, "is_up", lambda: True)
    monkeypatch.setattr(
        backends.ollama_client, "list_models", lambda: ["qwen2.5:32b", "llama3.1:8b"]
    )
    kind, backend, label = backends.select_backend(prefer="ollama", model="qwen2.5:32b")
    assert kind == backends.BACKEND_OLLAMA
    assert backend.model == "qwen2.5:32b"
    assert "qwen2.5:32b" in label


def test_select_backend_falls_back_when_requested_model_not_installed(monkeypatch):
    monkeypatch.setattr(backends.ollama_client, "is_up", lambda: True)
    monkeypatch.setattr(backends.ollama_client, "list_models", lambda: ["llama3.1:8b"])
    _, backend, _ = backends.select_backend(prefer="ollama", model="not-installed:1b")
    assert backend.model == "llama3.1:8b"


def test_select_backend_threads_temperature_override_to_ollama(monkeypatch):
    monkeypatch.setattr(backends.ollama_client, "is_up", lambda: True)
    monkeypatch.setattr(backends.ollama_client, "list_models", lambda: ["llama3.1:8b"])
    _, backend, _ = backends.select_backend(prefer="ollama", temperature=0.5)
    assert backend.temperature == 0.5


def test_select_backend_threads_temperature_override_to_local_gguf(monkeypatch):
    monkeypatch.setattr(backends.ollama_client, "is_up", lambda: False)
    monkeypatch.setattr(backends.LocalGGUFBackend, "available", staticmethod(lambda: True))
    monkeypatch.setattr(
        backends.desktop, "find_local_model", lambda: __import__("pathlib").Path("model.gguf")
    )
    _, backend, _ = backends.select_backend(prefer="local", temperature=0.7)
    assert backend.temperature == 0.7


def test_select_backend_with_no_overrides_still_works(monkeypatch):
    """The default (no prefer/model/temperature) path is unchanged."""
    monkeypatch.setattr(backends.ollama_client, "is_up", lambda: True)
    monkeypatch.setattr(backends.ollama_client, "list_models", lambda: ["llama3.1:8b"])
    kind, backend, _ = backends.select_backend()
    assert kind == backends.BACKEND_OLLAMA
    assert backend.temperature == 0.0


# --------------------------------------------------------------------------
# Truncation detection — a completion cut off by max_tokens (or by the
# context window filling up) must never come back as if it were a complete
# draft. llama-cpp-python signals this via finish_reason == "length" on both
# the non-streaming completion dict and the final streamed chunk; a fake
# model stands in for the real one so these run without a GGUF file.
# --------------------------------------------------------------------------

class _FakeModel:
    """Stands in for ``llama_cpp.Llama``: only ``create_chat_completion`` is
    ever called on it by ``LocalGGUFBackend.generate()``."""

    def __init__(self, completion):
        self._completion = completion

    def create_chat_completion(self, **kwargs):
        return self._completion


def _backend_with_fake_model(monkeypatch, completion) -> backends.LocalGGUFBackend:
    backend = backends.LocalGGUFBackend()
    monkeypatch.setattr(backend, "_llama", lambda: _FakeModel(completion))
    return backend


def test_local_gguf_non_streaming_raises_when_cut_off_by_token_limit(monkeypatch):
    """A completion dict with finish_reason 'length' must not be handed back
    as a finished draft — this is the exact shape of the biopsychosocial-
    assessment bug (7 of 62 fields, no exception, no signal)."""
    completion = {
        "choices": [
            {
                "message": {"content": "<<FIELD:a>> some content\n<<FIELD:b"},
                "finish_reason": "length",
            }
        ]
    }
    backend = _backend_with_fake_model(monkeypatch, completion)
    with pytest.raises(backends.BackendError, match="cut off by the token limit"):
        list(backend.generate("system", "prompt", stream=False))


def test_local_gguf_non_streaming_returns_content_on_natural_stop(monkeypatch):
    """The happy path must keep working: finish_reason 'stop' yields the text
    with no error."""
    completion = {
        "choices": [
            {
                "message": {"content": "<<FIELD:a>> some content"},
                "finish_reason": "stop",
            }
        ]
    }
    backend = _backend_with_fake_model(monkeypatch, completion)
    assert list(backend.generate("system", "prompt", stream=False)) == [
        "<<FIELD:a>> some content"
    ]


def test_local_gguf_streaming_raises_when_cut_off_by_token_limit(monkeypatch):
    """The streaming path gets finish_reason only on its final, contentless
    chunk (llama-cpp-python's own shape) — it must still be caught there."""
    chunks = [
        {"choices": [{"delta": {"role": "assistant"}, "finish_reason": None}]},
        {"choices": [{"delta": {"content": "<<FIELD:a>> some"}, "finish_reason": None}]},
        {"choices": [{"delta": {"content": " content\n<<FIELD:b"}, "finish_reason": None}]},
        {"choices": [{"delta": {}, "finish_reason": "length"}]},
    ]
    backend = _backend_with_fake_model(monkeypatch, iter(chunks))
    collected: list[str] = []
    with pytest.raises(backends.BackendError, match="cut off by the token limit"):
        for piece in backend.generate("system", "prompt", stream=True):
            collected.append(piece)
    # The truncated text was still streamed as it arrived — the error fires
    # only once it is clear no more is coming.
    assert "".join(collected) == "<<FIELD:a>> some content\n<<FIELD:b"


def test_local_gguf_streaming_completes_on_natural_stop(monkeypatch):
    chunks = [
        {"choices": [{"delta": {"role": "assistant"}, "finish_reason": None}]},
        {"choices": [{"delta": {"content": "<<FIELD:a>> done"}, "finish_reason": None}]},
        {"choices": [{"delta": {}, "finish_reason": "stop"}]},
    ]
    backend = _backend_with_fake_model(monkeypatch, iter(chunks))
    collected = list(backend.generate("system", "prompt", stream=True))
    assert "".join(collected) == "<<FIELD:a>> done"
