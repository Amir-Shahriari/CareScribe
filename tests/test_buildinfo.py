"""Tests for buildinfo module."""

import carescribe
from carescribe.core.buildinfo import build_info, user_agent, APP_NAME


def test_build_info():
    """Test that build_info returns correct name and version."""
    info = build_info()
    assert info["name"] == APP_NAME
    assert info["version"] == carescribe.__version__
    assert set(info.keys()) == {"name", "version"}


def test_user_agent():
    """Test that user_agent returns correct format."""
    assert user_agent() == f"{APP_NAME}/{carescribe.__version__}"