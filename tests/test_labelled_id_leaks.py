"""
Regression: two more labelled patient/clinician record numbers left in the clear.

Found by a cockpit QA pass on ``sample_documents/`` (no answer key there).

* ``05_discharge_summary.docx``:  ``UR number: MCDH-410287`` — the Australian
  hospital Unit Record number, the local equivalent of "Hospital No", survived
  verbatim. Its ``MCDH-`` facility prefix also meant the record-number value
  pattern (``[A-Z]{0,3}...``) could not have captured it even with the label.
* ``01_gp_referral_letter.docx``:  ``Provider No. 2481726A`` — the treating
  GP's Australian provider identifier (same class as a GMC/NMC number),
  survived; the trailing check letter ``A`` fell outside the value pattern.

``residual_scan`` flagged neither, so the approval safety-net would not have
blocked a write. Both are the same shape of gap as the Medicare number
(tests/test_medicare_number_leak.py): a labelled identifier with no entry in
``_MRN_LABELS`` and a value shape the capture group did not cover.

Fabricated label lines follow the style of tests/test_deid_regressions.py.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from carescribe.core import deidentify, ingest

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_documents"


def _mrn_values(text: str) -> set[str]:
    return {
        text[s.start : s.end]
        for s in deidentify.structured_spans(text)
        if s.entity_type == "MRN"
    }


@pytest.mark.parametrize(
    "line, needle",
    [
        ("UR number: MCDH-410287", "410287"),
        ("UR No: 410287", "410287"),
        ("UR Number MCDH-410287", "410287"),
        ("Provider No. 2481726A", "2481726"),
        ("Provider Number 2481726A", "2481726"),
        ("Referred by Dr Ng (Provider No 2481726A).", "2481726"),
    ],
)
def test_a_labelled_ur_or_provider_number_is_detected(line: str, needle: str) -> None:
    hits = _mrn_values(line)
    assert any(needle in h.replace(" ", "") for h in hits), (line, hits)


@pytest.mark.parametrize(
    "line",
    [
        "Provider of choice was the local crisis team.",
        "The care provider network was reviewed.",
        "UR was elevated; recheck bloods in a week.",
        "Seen again in 2026 for review.",
        "Weight 92 kg, BP 128/84.",
    ],
)
def test_bare_provider_or_ur_is_not_over_captured(line: str) -> None:
    assert _mrn_values(line) == set()


@pytest.mark.parametrize(
    "doc_name, identifier",
    [
        ("05_discharge_summary.docx", "MCDH-410287"),
        ("01_gp_referral_letter.docx", "2481726A"),
    ],
)
def test_the_sample_document_labelled_id_does_not_survive(doc_name: str, identifier: str) -> None:
    path = SAMPLE_DIR / doc_name
    if not path.exists():
        pytest.skip(f"{doc_name} not present")
    raw = ingest.extract_text(str(path))
    assert identifier in raw, f"{doc_name} no longer contains {identifier} — update this test"
    redacted = deidentify.deidentify(raw).redacted_text
    assert identifier not in redacted, (doc_name, f"{identifier} survived de-identification")
    assert deidentify.residual_scan(redacted) == [], (doc_name, deidentify.residual_scan(redacted))


def test_existing_labelled_record_numbers_still_detected() -> None:
    """Guard against the widened value pattern breaking the shapes it already caught."""
    for line, expected in [
        ("MRN 5567013", "5567013"),
        ("Hospital No (MRN): 4471982", "4471982"),
        ("Record No: 33-201-45", "33-201-45"),
        ("Patient ID: 7781234", "7781234"),
    ]:
        assert expected in _mrn_values(line), (line, _mrn_values(line))
