"""
Regression: an unlabelled letterhead street address leaks in the clear.

Found by a cockpit QA pass on ``sample_documents/`` (no answer key there).

The letterhead line in ``06_risk_assessment.docx`` and
``07_case_conference_note.docx`` is::

    Northgate Psychology Clinic, 8 Derby Street, Pascoe Vale VIC 3044  |  Ph: ...

It carries no ``Address:`` label and is not the bare ``Town, County`` shape the
``HEADER_LOCATION`` rule catches, so before the fix:

* doc07 kept ``8 Derby Street`` verbatim in ``redacted_text``;
* doc06 kept the house number ``8`` and the postcode ``3044`` (the street name
  was only removed because NER happened to mislabel it as an organisation);
* ``residual_scan`` flagged none of it.

A street address and postcode are geographic identifiers (HIPAA Safe Harbor:
all geographic subdivisions smaller than a state; UK GDPR equivalent). A
letterhead address must be taken whole, the way a labelled ``Address:`` line
already is — *without* starting to redact street names that appear in ordinary
clinical prose.

Fabricated label lines follow the style of tests/test_deid_regressions.py.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from carescribe.core import deidentify, ingest

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_documents"
AFFECTED_DOCS = ["06_risk_assessment.docx", "07_case_conference_note.docx"]


def _letterhead_line(redacted: str) -> str:
    """The de-identified form of the address/phone letterhead line."""
    for line in redacted.splitlines():
        if "Ph:" in line or "Fax:" in line or "3044" in line or "Derby" in line:
            return line
    return ""


@pytest.mark.parametrize("doc_name", AFFECTED_DOCS)
def test_the_sample_letterhead_address_is_fully_redacted(doc_name: str) -> None:
    path = SAMPLE_DIR / doc_name
    if not path.exists():
        pytest.skip(f"{doc_name} not present")
    raw = ingest.extract_text(str(path))
    assert "Derby Street" in raw, f"{doc_name} no longer has the expected address — update this test"

    redacted = deidentify.deidentify(raw).redacted_text
    assert "Derby" not in redacted, (doc_name, "street name survived", _letterhead_line(redacted))
    assert "8 Derby" not in redacted, (doc_name, "house number + street survived")
    line = _letterhead_line(redacted)
    assert "3044" not in line, (doc_name, "postcode survived on the letterhead line", line)
    assert deidentify.residual_scan(redacted) == [], (doc_name, deidentify.residual_scan(redacted))


@pytest.mark.parametrize(
    "line",
    [
        "8 Derby Street, Pascoe Vale VIC 3044",
        "Northgate Psychology Clinic, 8 Derby Street, Pascoe Vale VIC 3044  |  Ph: (03) 5551 3320",
    ],
)
def test_a_letterhead_street_address_line_is_taken_whole(line: str) -> None:
    redacted = deidentify.deidentify(line).redacted_text
    for leaked in ("8 Derby Street", "Derby Street", "Derby", "3044", "Pascoe Vale"):
        assert leaked not in redacted, (line, leaked, redacted)


@pytest.mark.parametrize(
    "line",
    [
        "She was seen after walking down Derby Street to the clinic.",
        "He mentioned a fall on the high street last week.",
        "Repaired the 3044 error code on the infusion pump.",
        "The patient scored 8 on the assessment and lives locally.",
    ],
)
def test_street_words_in_prose_are_not_over_redacted(line: str) -> None:
    """The new letterhead rule must not fire on a street word in a sentence."""
    redacted = deidentify.deidentify(line).redacted_text
    assert redacted == line, redacted
