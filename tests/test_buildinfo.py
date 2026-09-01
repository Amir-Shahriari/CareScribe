"""Tests for buildinfo module."""

import carescribe
from carescribe.core.buildinfo import build_info, APP_NAME


def test_build_info():
    """Test that build_info returns correct name and version."""
    info = build_info()
    assert info["name"] == APP_NAME
    assert info["version"] == carescribe.__version__
    assert set(info.keys()) == {"name", "version"}