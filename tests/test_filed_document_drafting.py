"""
Filed patient documents can be drafted from again.

A filed ``.deid.txt`` was approved and de-identified before it was written, so
drafting from it needs no re-detection and no privacy change. What it can never
regain is its identity map: that lives only in the session that produced it and
is never written to disk. So a draft made from a filed document keeps its
placeholders, and re-identification must stay shut off rather than silently
resolving half of them.

These tests pin both halves — that the document comes back usable, and that it
comes back unable to be re-identified.
"""

from __future__ import annotations

import pytest

from carescribe.core import batch

FILED_TEXT = (
    "Name: [PATIENT]   DOB: [DOB]\n"
    "Seen by: [PROVIDER_1] on [DATE_1]\n\n"
    "Presenting complaint: sore throat, three days, no fever.\n"
    "Plan: simple analgesia; safety-net advice given.\n"
)


@pytest.fixture()
def filed_doc() -> batch.Document:
    return batch.document_from_deidentified("visit.deid.txt", FILED_TEXT)


def test_the_text_comes_back_intact(filed_doc):
    assert filed_doc.redacted_text == FILED_TEXT
    assert filed_doc.name == "visit.deid.txt"


def test_it_is_already_approved_so_generation_accepts_it(filed_doc):
    """Generation refuses text a human has not approved. This text was
    approved before it was ever filed."""
    assert filed_doc.approved is True
    assert filed_doc.attested is True


def test_it_is_marked_analyzed_so_review_does_not_re_detect(filed_doc):
    assert filed_doc.analyzed is True


def test_it_carries_no_identity_map(filed_doc):
    """The map was never written to disk. Nothing can resolve these tokens."""
    assert filed_doc.phi_map == {}


def test_re_identification_stays_disabled_for_it(filed_doc):
    """The re-identify control is gated on phi_map, so an empty map disables
    it. A half-substituted document would be worse than a placeholdered one."""
    assert not filed_doc.phi_map


def test_no_original_text_is_invented(filed_doc):
    """raw_text is where a reviewer expects the source document. Filling it
    with the de-identified copy would misrepresent what was reviewed."""
    assert filed_doc.raw_text == ""
    assert filed_doc.source_bytes is None


def test_it_declares_no_entities(filed_doc):
    assert filed_doc.entities == []


def test_it_is_not_carrying_an_approved_path_from_a_past_session(filed_doc):
    """It has not been filed *again*; it is a fresh working copy."""
    assert filed_doc.approved_path == ""
    assert filed_doc.approved_docx_path == ""


def test_the_placeholders_survive_for_the_model_to_reproduce(filed_doc):
    for token in ("[PATIENT]", "[DOB]", "[PROVIDER_1]", "[DATE_1]"):
        assert token in filed_doc.redacted_text


def test_a_filed_document_round_trips_from_disk(tmp_path):
    """What the UI actually does: read the filed bytes, rebuild the document."""
    path = tmp_path / "visit.deid.txt"
    path.write_text(FILED_TEXT, encoding="utf-8")

    document = batch.document_from_deidentified(
        path.name, path.read_text(encoding="utf-8")
    )

    assert document.approved
    assert document.redacted_text == FILED_TEXT
    assert document.phi_map == {}
