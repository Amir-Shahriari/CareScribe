"""
Corpus-driven regression net.

Every document in ``stress_corpus/`` is run through the full pipeline and
checked against ``answer_key.json``: every ``must_redact`` string has to be gone
from the output, every ``must_preserve`` string has to still be there. One test
per string, so a failure names the exact leak rather than "document 3 failed".

Comparison normalises whitespace on both sides. Without that, a name the
document split across a line break ("Aiden\\nBraithwaite") would not match its
answer-key spelling and a real leak could pass unnoticed.

The corpus is data, not code: drop in another document plus its answer-key
entry and it is covered from the next run onward, no test changes needed.
"""

import json
import re
from pathlib import Path

import pytest

from carescribe.core import deidentify

CORPUS = Path(__file__).resolve().parent.parent / "stress_corpus"
ANSWER_KEY = CORPUS / "answer_key.json"

pytestmark = pytest.mark.skipif(
    not ANSWER_KEY.exists(), reason="stress_corpus/answer_key.json is not present"
)


def _normalise(text: str) -> str:
    """Collapse every whitespace run to one space, so line breaks stop mattering."""
    return re.sub(r"\s+", " ", text)


def _documents() -> list[dict]:
    if not ANSWER_KEY.exists():
        return []
    return json.loads(ANSWER_KEY.read_text(encoding="utf-8"))["documents"]


DOCUMENTS = _documents()

# One de-identification pass per document, shared by every assertion against it.
_CACHE: dict[str, str] = {}


def _redacted(name: str) -> str:
    if name not in _CACHE:
        text = (CORPUS / name).read_text(encoding="utf-8")
        _CACHE[name] = deidentify.deidentify(text).redacted_text
    return _CACHE[name]


def _redact_cases() -> list[tuple[str, str]]:
    return [(d["file"], value) for d in DOCUMENTS for value in d["must_redact"]]


def _preserve_cases() -> list[tuple[str, str]]:
    return [(d["file"], value) for d in DOCUMENTS for value in d["must_preserve"]]


def test_the_corpus_and_its_answer_key_agree():
    """A document listed in the key but missing on disk would silently pass."""
    assert DOCUMENTS, "answer_key.json lists no documents"
    for document in DOCUMENTS:
        assert (CORPUS / document["file"]).exists(), document["file"]
        assert document["must_redact"], f"{document['file']} asserts no leaks"
        assert document["must_preserve"], f"{document['file']} asserts no preservation"


@pytest.mark.parametrize(
    "document, value", _redact_cases(), ids=lambda v: str(v).replace(" ", "_")[:40]
)
def test_identifier_does_not_survive(document, value):
    assert _normalise(value) not in _normalise(_redacted(document))


@pytest.mark.parametrize(
    "document, value", _preserve_cases(), ids=lambda v: str(v).replace(" ", "_")[:40]
)
def test_clinical_content_is_preserved(document, value):
    assert _normalise(value) in _normalise(_redacted(document))


@pytest.mark.parametrize("document", [d["file"] for d in DOCUMENTS])
def test_the_safety_sweep_finds_no_structured_identifier(document):
    """Whatever the sweep still flags must not be a structured identifier.

    A surviving place name is expected and is the reviewer's call to dismiss —
    a surviving NHS number, phone, email or record number is not.
    """
    findings = deidentify.residual_scan(_redacted(document))
    structured = [
        f
        for f in findings
        if re.search(r"\d{4}", f) or "@" in f
    ]
    assert structured == [], structured
