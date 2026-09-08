"""Tests for model_setup.download_model — the app's one non-loopback socket."""

import io
import urllib.error
from unittest import mock

import pytest

from carescribe.core import model_setup
from carescribe.core.model_setup import ModelSetupError, Progress

PAYLOAD = b"GGUF" + b"\x00" * 60


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """Models dir in tmp_path, with a size floor tests can actually reach."""
    monkeypatch.setattr(model_setup, "MIN_PLAUSIBLE_BYTES", 8)
    monkeypatch.setattr(model_setup.desktop, "MODEL_APPROX_BYTES", len(PAYLOAD))
    monkeypatch.setattr(model_setup.desktop, "models_dir", lambda: tmp_path)
    monkeypatch.setattr(model_setup, "_free_bytes", lambda _p: 10**12)
    return tmp_path


class FakeResponse(io.BytesIO):
    """urlopen's return: a context manager with headers and a status."""

    def __init__(self, data, status=200, headers=None):
        super().__init__(data)
        self.status = status
        self.headers = headers or {"Content-Length": str(len(data))}

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


def _partial_path(sandbox):
    destination = model_setup.model_destination()
    return destination.with_suffix(destination.suffix + ".part")


def test_clean_download_writes_file_and_returns_path(sandbox):
    """A fresh download writes the model and leaves no .part behind."""
    with mock.patch.object(
        model_setup.urllib.request, "urlopen", return_value=FakeResponse(PAYLOAD)
    ):
        result = model_setup.download_model()
    assert result == sandbox / model_setup.desktop.DEFAULT_MODEL_FILENAME
    assert result.is_file()
    assert result.read_bytes() == PAYLOAD
    assert not _partial_path(sandbox).exists()


def test_progress_reported_and_ends_done(sandbox):
    """on_progress receives Progress objects and finishes with 'Done'."""
    events = []
    with mock.patch.object(
        model_setup.urllib.request, "urlopen", return_value=FakeResponse(PAYLOAD)
    ):
        model_setup.download_model(on_progress=events.append)
    assert events
    assert all(isinstance(event, Progress) for event in events)
    assert events[-1].message == "Done"


def test_user_agent_sent_and_no_range_when_fresh(sandbox):
    """A fresh request carries the User-Agent and no Range header."""
    with mock.patch.object(
        model_setup.urllib.request, "urlopen", return_value=FakeResponse(PAYLOAD)
    ) as urlopen:
        model_setup.download_model()
    request = urlopen.call_args[0][0]
    assert request.get_header("User-agent") == model_setup.USER_AGENT
    assert request.get_header("Range") is None


def test_partial_file_resumes_with_range_and_appends(sandbox):
    """An existing .part resumes via Range and appends to what is there."""
    _partial_path(sandbox).write_bytes(PAYLOAD[:20])
    remainder = PAYLOAD[20:]
    with mock.patch.object(
        model_setup.urllib.request,
        "urlopen",
        return_value=FakeResponse(
            remainder, status=206, headers={"Content-Length": str(len(remainder))}
        ),
    ) as urlopen:
        result = model_setup.download_model()
    request = urlopen.call_args[0][0]
    assert request.get_header("Range") == "bytes=20-"
    assert result.read_bytes() == PAYLOAD


def test_http_416_restarts_download(sandbox):
    """A 416 discards the .part and retries once from the beginning."""
    _partial_path(sandbox).write_bytes(PAYLOAD[:20])
    with mock.patch.object(
        model_setup.urllib.request,
        "urlopen",
        side_effect=[
            urllib.error.HTTPError(
                url="u", code=416, msg="Range Not Satisfiable", hdrs=None, fp=None
            ),
            FakeResponse(PAYLOAD),
        ],
    ) as urlopen:
        result = model_setup.download_model()
    assert result.read_bytes() == PAYLOAD
    assert urlopen.call_count == 2


def test_http_and_url_errors_become_model_setup_error(sandbox):
    """A 403 and an unreachable server both surface as ModelSetupError."""
    with mock.patch.object(
        model_setup.urllib.request,
        "urlopen",
        side_effect=urllib.error.HTTPError(
            url="u", code=403, msg="Forbidden", hdrs=None, fp=None
        ),
    ):
        with pytest.raises(ModelSetupError, match="refused by the server"):
            model_setup.download_model()
    with mock.patch.object(
        model_setup.urllib.request,
        "urlopen",
        side_effect=urllib.error.URLError("no route"),
    ):
        with pytest.raises(ModelSetupError, match="Could not reach"):
            model_setup.download_model()


def test_low_disk_space_refuses_before_any_request(sandbox, monkeypatch):
    """With no room, the download fails before a socket is ever opened."""
    monkeypatch.setattr(model_setup, "_free_bytes", lambda _p: 1)
    with mock.patch.object(
        model_setup.urllib.request, "urlopen", mock.Mock()
    ) as urlopen:
        with pytest.raises(ModelSetupError, match="Not enough disk space"):
            model_setup.download_model()
    assert urlopen.call_count == 0
