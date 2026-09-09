"""Tests for ollama_client.generate() — the streaming parser and its error paths."""

import inspect
import json
import urllib.error

import pytest

from carescribe.core import ollama_client


class FakeResponse:
    def __init__(self, *, body=b"", lines=()):
        self._body, self._lines = body, list(lines)

    def __enter__(self): return self
    def __exit__(self, *exc): return False
    def read(self): return self._body
    def __iter__(self): return iter(self._lines)


@pytest.fixture
def wired(monkeypatch):
    """Daemon up with one model installed; records what generate() sends."""
    monkeypatch.setattr(ollama_client, "is_up", lambda: True)
    monkeypatch.setattr(ollama_client, "list_models", lambda: ["llama3.1:8b"])

    def fake(request, timeout=None):
        fake.request, fake.timeout = request, timeout
        if isinstance(fake.response, Exception):
            raise fake.response
        return fake.response

    fake.response = FakeResponse()
    monkeypatch.setattr(ollama_client.urllib.request, "urlopen", fake)
    return fake


def ndjson(*chunks):
    return [json.dumps(c).encode() + b"\n" for c in chunks]


def test_generate_is_a_generator_and_defers_the_network(wired):
    gen = ollama_client.generate("llama3.1:8b", "system", "prompt")
    assert inspect.isgenerator(gen)
    assert not hasattr(wired, "request")
    list(gen)
    assert wired.request is not None


def test_daemon_down_and_missing_model(wired, monkeypatch):
    monkeypatch.setattr(ollama_client, "is_up", lambda: False)
    with pytest.raises(ollama_client.OllamaError) as excinfo:
        list(ollama_client.generate("llama3.1:8b", "system", "prompt"))
    assert str(excinfo.value) == ollama_client.DAEMON_DOWN_MESSAGE

    monkeypatch.setattr(ollama_client, "is_up", lambda: True)
    with pytest.raises(ollama_client.OllamaError) as excinfo:
        list(ollama_client.generate("llama3.2:3b", "system", "prompt"))
    message = str(excinfo.value)
    assert "ollama pull" in message
    assert "llama3.2:3b" in message


def test_request_body(wired):
    wired.response = FakeResponse(lines=ndjson({"response": "a"}, {"done": True}))
    assert list(
        ollama_client.generate(
            "llama3.1:8b", "be brief", "draft this", temperature=0.7
        )
    ) == ["a"]

    body = json.loads(wired.request.data)
    assert body["model"] == "llama3.1:8b"
    assert body["system"] == "be brief"
    assert body["prompt"] == "draft this"
    assert body["think"] is False
    assert body["options"]["temperature"] == 0.7
    assert wired.timeout == ollama_client.GENERATE_TIMEOUT


def test_non_streaming(wired):
    wired.response = FakeResponse(body=json.dumps({"response": "hello"}).encode())
    assert list(
        ollama_client.generate("llama3.1:8b", "system", "prompt", stream=False)
    ) == ["hello"]

    # An empty response used to yield [] here. That reads downstream as a
    # finished-but-empty draft: app.py banked it as the generated note and
    # showed no error. An empty generation is a failure, so it now raises.
    wired.response = FakeResponse(body=json.dumps({"response": ""}).encode())
    with pytest.raises(ollama_client.OllamaError, match="no output"):
        list(ollama_client.generate("llama3.1:8b", "system", "prompt", stream=False))


def test_streaming_happy_path(wired):
    wired.response = FakeResponse(
        lines=ndjson({"response": "a"}, {"response": "b"}, {"done": True})
    )
    assert list(ollama_client.generate("llama3.1:8b", "system", "prompt")) == ["a", "b"]


def test_streaming_junk_is_skipped_not_fatal(wired):
    wired.response = FakeResponse(
        lines=(
            ndjson({"response": "a"})
            + [b"\n", b"not json\n"]
            + [json.dumps({"done": False}).encode() + b"\n"]
            + [json.dumps({"response": ""}).encode() + b"\n"]
            + ndjson({"response": "b"}, {"done": True})
        )
    )
    assert list(ollama_client.generate("llama3.1:8b", "system", "prompt")) == ["a", "b"]


def test_done_stops_and_error_fails(wired):
    wired.response = FakeResponse(
        lines=ndjson({"response": "a"}, {"done": True}, {"response": "b"})
    )
    assert list(ollama_client.generate("llama3.1:8b", "system", "prompt")) == ["a"]

    wired.response = FakeResponse(
        lines=ndjson({"response": "a"}, {"error": "boom"})
    )
    with pytest.raises(ollama_client.OllamaError, match="boom"):
        list(ollama_client.generate("llama3.1:8b", "system", "prompt"))

    wired.response = urllib.error.URLError("down")
    with pytest.raises(
        ollama_client.OllamaError, match="Could not reach the local Ollama server"
    ):
        list(ollama_client.generate("llama3.1:8b", "system", "prompt"))
