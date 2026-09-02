# tests/test_backend_overrides.py
from __future__ import annotations

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
