"""Shared pytest fixtures.

The spaCy model load costs several seconds, so the pipeline runs once per
session and every test reads the same result.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from carescribe.core import deidentify  # noqa: E402
from tests.fixtures import DISCHARGE_SUMMARY  # noqa: E402


@pytest.fixture(scope="session")
def raw_text() -> str:
    return DISCHARGE_SUMMARY


@pytest.fixture(scope="session")
def deid(raw_text):
    """The full pipeline's output for the fixture document."""
    return deidentify.deidentify(raw_text)


@pytest.fixture(scope="session")
def redacted(deid) -> str:
    return deid.redacted_text


@pytest.fixture(scope="session")
def ner_available() -> bool:
    """True when a spaCy model loaded — layer 2 tests skip without one."""
    return deidentify.get_analyzer() is not None
