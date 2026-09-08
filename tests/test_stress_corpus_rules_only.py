"""The stress corpus run with the analyzer forced off.

This is the same corpus and the same answer key as ``test_stress_corpus.py``,
de-identified a second time with ``get_analyzer()`` patched to ``None`` — the
supported state of a machine with no spaCy model, where the structured rules
are all that stand between a document and a leak. That second pass matters
because a hole in the regex layer is invisible to any test that runs with the
model loaded: NER catches what the rules miss, the green suite hides the gap.
"""

import json
import re
from pathlib import Path
from unittest import mock

import pytest

from carescribe.core import deidentify

CORPUS = Path(__file__).resolve().parent.parent / "stress_corpus"
ANSWER_KEY = CORPUS / "answer_key.json"

pytestmark = pytest.mark.skipif(
    not ANSWER_KEY.exists(), reason="stress_corpus/answer_key.json is not present"
)


def normalise(text: str) -> str:
    """Collapse every whitespace run to one space, so line breaks stop mattering."""
    return re.sub(r"\s+", " ", text)


def _documents() -> list[dict]:
    if not ANSWER_KEY.exists():
        return []
    return json.loads(ANSWER_KEY.read_text(encoding="utf-8"))["documents"]


DOCUMENTS = _documents()

# Values that survive with no NER model, by design. Each is an unanchored name
# in prose -- no label, no fixed vocabulary, nothing a regex can key on without
# redacting every capitalised word it sees. All are caught when spaCy is loaded;
# test_stress_corpus.py covers that path.
#
# This list should only ever shrink. If a fix makes one of these redact, delete
# it from here -- a stale entry quietly widens what the gate permits.
KNOWN_NER_ONLY = {
    "doc08_wrapped_referral.txt": {
        # A forename and surname split across a line break mid-sentence.
        "Oluwaseun Adeyinka", "Oluwaseun", "Adeyinka",
    },
    "doc14_family_therapy_notes.txt": {
        # Bare first names of family members in therapy narrative.
        "Carla", "Bruno", "Noah",
    },
    "doc17_email_correspondence_thread.txt": {
        # A patient named at the tail of an email subject line, after a dash.
        # A rule for that shape also matches "Clinic list - Monday" and
        # "Ward round - Ashdown Ward", so it was deliberately not written.
        "Wilfred Openshaw",
    },
    "doc18_court_report.txt": {
        # A solicitor and their firm. "Solicitors" is not in ORG_DESCRIPTORS
        # because that vocabulary feeds FACILITY_PATTERN -- adding it would type
        # a law firm as [CLINIC].
        "Miriam Okwuosa", "Fentiman Bright Solicitors",
    },
}

# One rules-only pass per document, shared by every test that reads it.
_CACHE: dict[str, str] = {}


def rules_only(name: str) -> str:
    """De-identify one corpus document with the analyzer forced off, once."""
    if name not in _CACHE:
        text = (CORPUS / name).read_text(encoding="utf-8")
        with mock.patch.object(deidentify, "get_analyzer", return_value=None):
            _CACHE[name] = deidentify.deidentify(text).redacted_text
    return _CACHE[name]


@pytest.mark.parametrize("document", DOCUMENTS, ids=lambda d: d["file"])
def test_no_unexpected_leak_without_a_model(document):
    """No must_redact value may survive the rules alone, beyond the allowlist.

    The check is a subset, not equality: a fix that removes a leak must not
    fail this test, only a new one does. The allowlist is the honest boundary
    of the regex layer — unanchored names in prose, which are NER's job.
    """
    file = document["file"]
    leaked = {
        value
        for value in document["must_redact"]
        if normalise(value) in normalise(rules_only(file))
    }
    unexpected = leaked - KNOWN_NER_ONLY.get(file, set())
    assert not unexpected, f"{file}: {sorted(unexpected)} leaked with no NER model"


@pytest.mark.parametrize("document", DOCUMENTS, ids=lambda d: d["file"])
def test_no_over_redaction_without_a_model(document):
    """Every must_preserve value must still be present with the rules alone.

    Over-redaction destroys clinical meaning, and a widened rule is exactly
    where it appears. There is no allowlist for this: it must hold for every
    document.
    """
    file = document["file"]
    lost = [
        value
        for value in document["must_preserve"]
        if normalise(value) not in normalise(rules_only(file))
    ]
    assert not lost, f"{file}: {sorted(lost)} over-redacted with no NER model"


def test_allowlist_has_no_stale_entries():
    """Every allowlisted value must in fact still leak rules-only.

    This is what stops KNOWN_NER_ONLY rotting: when a future fix makes one of
    these redact, this test fails and tells you to delete the entry. A stale
    entry quietly widens what the leak gate permits, so the list only ever
    shrinks.
    """
    for file, allowed in KNOWN_NER_ONLY.items():
        redacted = normalise(rules_only(file))
        gone = sorted(value for value in allowed if normalise(value) not in redacted)
        assert not gone, (
            f"{file}: {gone} no longer leak rules-only — a fix has landed. "
            "Delete them from KNOWN_NER_ONLY rather than weakening this gate."
        )
