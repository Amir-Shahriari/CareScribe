"""Tests for model_setup.pull_ollama_model() — the streaming pull generator.

``pull_ollama_model`` is a *generator*: nothing in its body — not even the
daemon check — runs until it is iterated. Every test below consumes it with
``list(...)``; a bare call would assert nothing.

No test opens a real socket: ``is_up`` and ``urlopen`` are patched.
"""

import io
import json
from unittest import mock

import pytest

from carescribe.core import model_setup
from carescribe.core.model_setup import ModelSetupError, Progress


class FakeResponse(io.BytesIO):
    """Stands in for urlopen's return: a context manager yielding byte lines."""

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


def ndjson(*lines: str) -> FakeResponse:
    return FakeResponse("\n".join(lines).encode("utf-8"))


@mock.patch.object(model_setup.urllib.request, "urlopen")
@mock.patch.object(model_setup.ollama_client, "is_up", return_value=False)
def test_daemon_down_raises_before_any_request(is_up, urlopen):
    """A down daemon fails fast with its message and never touches urlopen."""
    with pytest.raises(ModelSetupError) as excinfo:
        list(model_setup.pull_ollama_model())
    assert str(excinfo.value) == model_setup.ollama_client.DAEMON_DOWN_MESSAGE
    urlopen.assert_not_called()


@mock.patch.object(
    model_setup.urllib.request,
    "urlopen",
    return_value=ndjson(
        '{"status":"pulling","completed":10,"total":100}',
        '{"status":"pulling","completed":50,"total":100}',
        '{"status":"success","completed":100,"total":100}',
    ),
)
@mock.patch.object(model_setup.ollama_client, "is_up", return_value=True)
def test_progress_lines_are_yielded_in_order(is_up, urlopen):
    """Each NDJSON line becomes one Progress, in order, with the sent model."""
    steps = list(model_setup.pull_ollama_model("qwen3:4b"))
    assert steps == [
        Progress(10, 100, "pulling"),
        Progress(50, 100, "pulling"),
        Progress(100, 100, "success"),
    ]

    request = urlopen.call_args[0][0]
    assert json.loads(request.data) == {"model": "qwen3:4b", "stream": True}


@mock.patch.object(
    model_setup.urllib.request,
    "urlopen",
    return_value=ndjson(
        '{"status":"pulling","completed":10,"total":100}',
        '{"status":"pulling","completed":50,"total":100}',
        '{"status":"success","completed":100,"total":100}',
    ),
)
@mock.patch.object(model_setup.ollama_client, "is_up", return_value=True)
def test_fraction_is_computed_as_the_progress_bar_needs_it(is_up, urlopen):
    """fraction tracks downloaded/total: 10%, then half, then done."""
    fractions = [p.fraction for p in model_setup.pull_ollama_model()]
    assert fractions == [0.1, 0.5, 1.0]


@mock.patch.object(
    model_setup.urllib.request,
    "urlopen",
    return_value=ndjson("", "  ", '{"status":"ok","completed":1,"total":2}'),
)
@mock.patch.object(model_setup.ollama_client, "is_up", return_value=True)
def test_blank_lines_are_skipped(is_up, urlopen):
    """Empty or whitespace-only lines yield nothing."""
    assert list(model_setup.pull_ollama_model()) == [Progress(1, 2, "ok")]


@mock.patch.object(
    model_setup.urllib.request,
    "urlopen",
    return_value=ndjson("not json at all", '{"status":"ok","completed":1,"total":2}'),
)
@mock.patch.object(model_setup.ollama_client, "is_up", return_value=True)
def test_malformed_json_line_is_skipped_not_fatal(is_up, urlopen):
    """A daemon writing a partial line must not abort a 5 GB pull."""
    assert list(model_setup.pull_ollama_model()) == [Progress(1, 2, "ok")]


@mock.patch.object(
    model_setup.urllib.request,
    "urlopen",
    return_value=ndjson('{"error":"model not found"}'),
)
@mock.patch.object(model_setup.ollama_client, "is_up", return_value=True)
def test_error_field_raises_with_the_daemons_words(is_up, urlopen):
    """An error chunk surfaces verbatim as ModelSetupError."""
    with pytest.raises(ModelSetupError, match="model not found"):
        list(model_setup.pull_ollama_model())


@mock.patch.object(
    model_setup.urllib.request,
    "urlopen",
    side_effect=model_setup.urllib.error.URLError("connection refused"),
)
@mock.patch.object(model_setup.ollama_client, "is_up", return_value=True)
def test_urlerror_becomes_model_setup_error(is_up, urlopen):
    """A refused connection is reported as Ollama's fault, cause chained."""
    with pytest.raises(ModelSetupError, match="Ollama refused the download") as excinfo:
        list(model_setup.pull_ollama_model())
    assert isinstance(excinfo.value.__cause__, model_setup.urllib.error.URLError)
