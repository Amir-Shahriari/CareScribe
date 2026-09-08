"""The Ollama client's loopback pin, ``is_up()`` and ``list_models()``.

The security-relevant property under test: the client is hard-wired to
``http://127.0.0.1:11434`` and **never reads ``OLLAMA_HOST``**, so no
environment variable can turn a local-only tool into one that ships clinical
text to another machine. Every request these tests record is inspected, and
none of them opens a real socket — ``urlopen`` is swapped for a recorder.
"""

import json
import urllib.error

import pytest

from carescribe.core import ollama_client


class FakeResponse:
    def __init__(self, *, status=200, body=b""):
        self.status, self._body = status, body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self._body


@pytest.fixture
def urlopen(monkeypatch):
    """Swap urlopen for a recorder. Set `fake.response` in each test."""
    def fake(request, timeout=None):
        fake.calls.append(request)
        if isinstance(fake.response, Exception):
            raise fake.response
        return fake.response

    fake.calls, fake.response = [], FakeResponse()
    monkeypatch.setattr(ollama_client.urllib.request, "urlopen", fake)
    return fake


def tags(*models):
    return json.dumps({"models": [{"name": m} for m in models]}).encode()


def test_base_url_is_pinned_loopback():
    assert ollama_client.BASE_URL == "http://127.0.0.1:11434"


def test_ollama_host_env_var_is_ignored_on_purpose(urlopen, monkeypatch):
    """The loopback pin must survive a hostile ``OLLAMA_HOST``.

    ``OLLAMA_HOST`` is the documented way to point an Ollama client at another
    machine — a variable set for an unrelated reason would quietly turn this
    local-only tool into one that ships clinical text off the box. This test
    MUST FAIL LOUDLY if anyone ever reads that variable to build a URL: every
    request the client makes has to go to 127.0.0.1:11434 regardless.
    """
    monkeypatch.setenv("OLLAMA_HOST", "10.0.0.5:11434")

    ollama_client.is_up()
    ollama_client.list_models()

    assert urlopen.calls
    for request in urlopen.calls:
        assert request.full_url.startswith("http://127.0.0.1:11434")


def test_is_up_reflects_http_status(urlopen):
    urlopen.response = FakeResponse(status=200)
    assert ollama_client.is_up() is True

    urlopen.response = FakeResponse(status=404)
    assert ollama_client.is_up() is False


@pytest.mark.parametrize(
    "error",
    [
        urllib.error.URLError("down"),
        TimeoutError(),
        Exception("boom"),
    ],
)
def test_is_up_never_raises(urlopen, error):
    urlopen.response = error
    assert ollama_client.is_up() is False


def test_list_models_shapes_names_and_sorts(urlopen):
    payload = {
        "models": [
            {"name": "llama3.1:8b"},
            {"model": "qwen2.5:7b"},
            {"description": "no name or model key at all"},
            {"name": "  mistral:7b  "},
        ]
    }
    urlopen.response = FakeResponse(body=json.dumps(payload).encode())

    assert ollama_client.list_models() == ["llama3.1:8b", "mistral:7b", "qwen2.5:7b"]


def test_list_models_returns_empty_list_never_raises(urlopen):
    # Malformed JSON body.
    urlopen.response = FakeResponse(body=b"not json at all")
    assert ollama_client.list_models() == []

    # Well-formed JSON with no "models" key.
    urlopen.response = FakeResponse(body=json.dumps({"error": "nope"}).encode())
    assert ollama_client.list_models() == []

    # urlopen itself raising.
    urlopen.response = urllib.error.URLError("connection refused")
    assert ollama_client.list_models() == []
