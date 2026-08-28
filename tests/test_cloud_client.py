"""The optional cloud generation transport — stdlib HTTP, two wire formats,
key read from the environment at call time. Cloud stays off by default; these
tests configure it explicitly and never touch the network (``urlopen`` is
stubbed).
"""

import io
import json
import urllib.error

import pytest

from carescribe.core import backends, cloud_client


class _FakeResponse:
    def __init__(self, lines=(), body=b""):
        self._lines = [l if isinstance(l, bytes) else l.encode() for l in lines]
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def __iter__(self):
        return iter(self._lines)

    def read(self):
        return self._body


@pytest.fixture(autouse=True)
def _clean_cloud_env(monkeypatch):
    for name in (
        cloud_client.PROVIDER_ENV, cloud_client.API_KEY_ENV,
        cloud_client.BASE_URL_ENV, cloud_client.MODEL_ENV,
    ):
        monkeypatch.delenv(name, raising=False)


def _capture(monkeypatch, response):
    captured = {}

    def fake_urlopen(request, timeout=None):
        captured["url"] = request.full_url
        captured["headers"] = {k.lower(): v for k, v in request.header_items()}
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return response

    monkeypatch.setattr(cloud_client.urllib.request, "urlopen", fake_urlopen)
    return captured


def test_anthropic_stream_yields_text_deltas_with_the_right_request(monkeypatch):
    monkeypatch.setenv(cloud_client.API_KEY_ENV, "test-key")
    lines = [
        "event: content_block_delta",
        'data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"Hello "}}',
        'data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"world"}}',
        'data: {"type":"message_stop"}',
    ]
    captured = _capture(monkeypatch, _FakeResponse(lines))

    out = "".join(cloud_client.stream_generation("anthropic", "SYS", "PROMPT"))

    assert out == "Hello world"
    assert captured["url"] == "https://api.anthropic.com/v1/messages"
    assert captured["headers"]["x-api-key"] == "test-key"
    assert captured["headers"]["anthropic-version"] == cloud_client.ANTHROPIC_VERSION
    assert captured["body"]["stream"] is True
    assert captured["body"]["system"] == "SYS"
    assert captured["body"]["messages"] == [{"role": "user", "content": "PROMPT"}]
    assert captured["body"]["model"] == "claude-opus-5"


def test_openai_stream_honours_base_url_and_model_override(monkeypatch):
    monkeypatch.setenv(cloud_client.API_KEY_ENV, "k")
    monkeypatch.setenv(cloud_client.BASE_URL_ENV, "https://gw.clinic.example/v1")
    monkeypatch.setenv(cloud_client.MODEL_ENV, "clinic-local-70b")
    lines = [
        'data: {"choices":[{"delta":{"content":"Hi"}}]}',
        'data: {"choices":[{"delta":{"content":" there"}}]}',
        "data: [DONE]",
    ]
    captured = _capture(monkeypatch, _FakeResponse(lines))

    out = "".join(cloud_client.stream_generation("openai", "SYS", "P"))

    assert out == "Hi there"
    assert captured["url"] == "https://gw.clinic.example/v1/chat/completions"
    assert captured["headers"]["authorization"] == "Bearer k"
    assert captured["body"]["model"] == "clinic-local-70b"
    assert captured["body"]["messages"][0] == {"role": "system", "content": "SYS"}


def test_openai_requires_an_explicit_model(monkeypatch):
    monkeypatch.setenv(cloud_client.API_KEY_ENV, "k")
    monkeypatch.setattr(
        cloud_client.urllib.request, "urlopen",
        lambda *a, **k: pytest.fail("must not POST without a model"),
    )
    with pytest.raises(cloud_client.CloudError):
        list(cloud_client.stream_generation("openai", "s", "p"))


def test_a_missing_key_raises_before_any_request(monkeypatch):
    monkeypatch.setattr(
        cloud_client.urllib.request, "urlopen",
        lambda *a, **k: pytest.fail("must not POST without a key"),
    )
    with pytest.raises(cloud_client.CloudError):
        list(cloud_client.stream_generation("anthropic", "s", "p"))


def test_an_unknown_provider_points_at_the_openai_escape_hatch(monkeypatch):
    monkeypatch.setenv(cloud_client.API_KEY_ENV, "k")
    with pytest.raises(cloud_client.CloudError) as excinfo:
        list(cloud_client.stream_generation("azure", "s", "p"))
    assert "openai" in str(excinfo.value).lower()


def test_an_http_error_becomes_a_cloud_error(monkeypatch):
    monkeypatch.setenv(cloud_client.API_KEY_ENV, "k")

    def boom(request, timeout=None):
        raise urllib.error.HTTPError(
            request.full_url, 401, "Unauthorized", {}, io.BytesIO(b'{"error":"bad key"}')
        )

    monkeypatch.setattr(cloud_client.urllib.request, "urlopen", boom)
    with pytest.raises(cloud_client.CloudError) as excinfo:
        list(cloud_client.stream_generation("anthropic", "s", "p"))
    assert "401" in str(excinfo.value)


def test_an_error_event_mid_stream_becomes_a_cloud_error(monkeypatch):
    monkeypatch.setenv(cloud_client.API_KEY_ENV, "k")
    lines = [
        'data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"partial"}}',
        'data: {"type":"error","error":{"message":"overloaded"}}',
    ]
    _capture(monkeypatch, _FakeResponse(lines))
    with pytest.raises(cloud_client.CloudError) as excinfo:
        list(cloud_client.stream_generation("anthropic", "s", "p"))
    assert "overloaded" in str(excinfo.value)


# --- CloudBackend wiring ---------------------------------------------------

def test_cloud_backend_streams_via_the_transport(monkeypatch):
    monkeypatch.setenv(backends.CLOUD_PROVIDER_ENV, "anthropic")
    monkeypatch.setenv(backends.CLOUD_API_KEY_ENV, "k")
    monkeypatch.setattr(
        cloud_client, "stream_generation",
        lambda provider, system, prompt, stream=True: iter(["draft ", "text"]),
    )
    backend = backends.CloudBackend()
    assert "".join(backend.generate("sys", "prompt")) == "draft text"


def test_cloud_backend_translates_transport_errors_to_backend_error(monkeypatch):
    monkeypatch.setenv(backends.CLOUD_PROVIDER_ENV, "anthropic")
    monkeypatch.setenv(backends.CLOUD_API_KEY_ENV, "k")

    def boom(*a, **k):
        raise cloud_client.CloudError("provider is down")

    monkeypatch.setattr(cloud_client, "stream_generation", boom)
    backend = backends.CloudBackend()
    with pytest.raises(backends.BackendError) as excinfo:
        list(backend.generate("s", "p"))
    assert "provider is down" in str(excinfo.value)


def test_the_cloud_client_source_stores_no_key(monkeypatch):
    from pathlib import Path

    source = Path(cloud_client.__file__).read_text(encoding="utf-8")
    assert "sk-" not in source
    assert "self.key" not in source and "self.api_key" not in source
    assert cloud_client.API_KEY_ENV in source
