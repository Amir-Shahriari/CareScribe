"""Tests for the model_setup guard helpers: _verify, _free_bytes, clear_partial_download."""

import shutil
from pathlib import Path
from unittest import mock

import pytest

from carescribe.core import model_setup
from carescribe.core.model_setup import ModelSetupError


@pytest.fixture
def small_threshold(monkeypatch):
    """Shrink the plausible-size floor so tests write bytes, not gigabytes."""
    monkeypatch.setattr(model_setup, "MIN_PLAUSIBLE_BYTES", 8)


def _write_model_file(path: Path, payload: bytes) -> Path:
    path.write_bytes(payload)
    return path


def test_verify_accepts_a_valid_file(tmp_path, small_threshold):
    """A file with the GGUF magic and a plausible size passes verification."""
    path = _write_model_file(tmp_path / "model.gguf", b"GGUF" + b"\x00" * 20)
    assert model_setup._verify(path, expected=0) is None


def test_verify_refuses_a_missing_file(tmp_path, small_threshold):
    """A download that never produced a file must be refused, not retried blindly."""
    with pytest.raises(ModelSetupError) as excinfo:
        model_setup._verify(tmp_path / "missing.gguf", expected=0)
    assert "did not produce a file" in str(excinfo.value)


def test_verify_refuses_a_file_under_the_size_floor(tmp_path, small_threshold):
    """A file below the plausibility floor is treated as a truncated download."""
    path = _write_model_file(tmp_path / "model.gguf", b"GGUF")
    with pytest.raises(ModelSetupError) as excinfo:
        model_setup._verify(path, expected=0)
    assert "stopped early" in str(excinfo.value)


def test_verify_refuses_a_file_short_of_expected(tmp_path, small_threshold):
    """A file smaller than the declared total is a partial download, not a model."""
    path = _write_model_file(tmp_path / "model.gguf", b"GGUF" + b"\x00" * 20)
    with pytest.raises(ModelSetupError) as excinfo:
        model_setup._verify(path, expected=1000)
    assert "stopped early" in str(excinfo.value)


def test_verify_accepts_98_percent_of_expected(tmp_path, small_threshold):
    """The 2% tolerance is deliberate, so a trivially-off content-length does not reject a good download."""
    path = _write_model_file(tmp_path / "model.gguf", b"GGUF" + b"\x00" * 96)
    assert len(path.read_bytes()) == 100
    model_setup._verify(path, expected=100)


def test_verify_refuses_wrong_magic_bytes(tmp_path, small_threshold):
    """A captive-portal login page saved as the model must be refused outright."""
    path = _write_model_file(
        tmp_path / "model.gguf", b"<!DOCTYPE html>...." + b"\x00" * 20
    )
    with pytest.raises(ModelSetupError) as excinfo:
        model_setup._verify(path, expected=0)
    assert "not a valid model" in str(excinfo.value)


def test_free_bytes_returns_real_free_space(tmp_path):
    """The free-space check must report what the OS says, so disk checks are honest."""
    with mock.patch.object(
        model_setup.shutil, "disk_usage", return_value=mock.Mock(free=12345)
    ) as disk_usage:
        assert model_setup._free_bytes(tmp_path) == 12345
    disk_usage.assert_called_once_with(tmp_path)


def test_free_bytes_returns_zero_when_os_call_raises(tmp_path):
    """An unreadable disk must not crash setup, it must just decline to promise space."""
    with mock.patch.object(
        model_setup.shutil, "disk_usage", side_effect=OSError("unreadable")
    ):
        assert model_setup._free_bytes(tmp_path) == 0


def test_clear_partial_download_removes_part_file_and_tolerates_absence(tmp_path):
    """Clearing a partial download removes only the .part file and is safe to re-run."""
    with mock.patch.object(
        model_setup.desktop, "models_dir", return_value=tmp_path
    ):
        final_file = tmp_path / "Qwen2.5-3B-Instruct-Q4_K_M.gguf"
        final_file.write_bytes(b"GGUF" + b"\x00" * 20)
        part_file = tmp_path / "Qwen2.5-3B-Instruct-Q4_K_M.gguf.part"
        part_file.write_bytes(b"GGUF" + b"\x00" * 5)

        model_setup.clear_partial_download()

        assert not part_file.exists()
        assert final_file.exists()

        model_setup.clear_partial_download()
        assert not part_file.exists()
