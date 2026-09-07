"""
Answer-key regression net for ``sample_documents/``.

Unlike ``stress_corpus/`` these shipped documents had no per-string answer key,
which is why several labelled identifiers (Medicare number, hospital UR number,
provider number, letterhead street address) leaked undetected until a cockpit
QA pass. This file is the missing net: every sample document is about the same
fictional patient, so the identifiers are known and finite. Each must be absent
from ``redacted_text`` and the residual sweep must be clean.

All values here are fabricated (the sample documents are synthetic).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from carescribe.core import deidentify, ingest

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_documents"

# identifier -> the sample docs (by numeric prefix) that contain it in the source
PATIENT_IDENTIFIERS: dict[str, tuple[str, ...]] = {
    "Jordan Elliot Whitfield": (
        "01", "02", "03", "04", "05", "06", "07",
        "08", "09", "10", "11", "12", "13", "14", "15",
    ),
    "12/04/1985": (
        "01", "02", "04", "05", "06", "07",
        "08", "09", "10", "11", "12", "13", "14", "15",
    ),
    "2934 5671 0": ("01", "05", "06", "07", "08", "10", "13", "14"),  # Medicare number
    "45 Kestrel Ave": ("01", "05", "08", "12", "13"),  # patient home address
    "0412 887 234": ("01", "12"),                      # patient mobile
    "0433 990 214": ("01", "06", "10"),                # relative mobile
    "jordan.whitfield85@example.com": ("01",),         # patient email
    "Priya Whitfield": ("01", "02", "05", "06", "07", "10"),  # relative
    # Labelled record / provider / claim / accession numbers — the class that
    # leaked undetected until a QA pass. Each is anchored to a label the
    # deterministic layer recognises.
    "RFMP-88213": ("01",),                             # referring practice UR
    "MCDH-410287": ("05", "09"),                       # hospital UR number
    "2481726A": ("01", "08", "12"),                    # Dr Ng, provider number
    "25-0788-441907": ("08",),                         # pathology lab reference
    "CPC-4471": ("10",),                               # psychiatry clinic file no.
    "2559071T": ("10",),                               # Dr Haddad, provider number
    "2705513Y": ("11",),                               # Dr Ferro, provider number
    "WC-2025-118342": ("12", "13", "15"),              # WorkCover claim number
    "RAD-2025-77120": ("14",),                         # imaging accession number
    "2810664R": ("15",),                               # Grace Tan, provider number
}

ALL_PREFIXES = tuple(f"{n:02d}" for n in range(1, 16))

DOC_BY_PREFIX = {p.name[:2]: p for p in sorted(SAMPLE_DIR.glob("*.docx"))}


def _redacted(prefix: str) -> tuple[str, str]:
    path = DOC_BY_PREFIX.get(prefix)
    if path is None:
        pytest.skip(f"no sample document with prefix {prefix}")
    raw = ingest.extract_text(str(path))
    return raw, deidentify.deidentify(raw).redacted_text


@pytest.mark.parametrize(
    "identifier, prefix",
    [(ident, prefix) for ident, prefixes in PATIENT_IDENTIFIERS.items() for prefix in prefixes],
    ids=lambda v: v if isinstance(v, str) else str(v),
)
def test_patient_identifier_is_absent_from_redacted_text(identifier: str, prefix: str) -> None:
    raw, redacted = _redacted(prefix)
    assert identifier in raw, (
        f"doc {prefix} no longer contains {identifier!r} in the source — update PATIENT_IDENTIFIERS"
    )
    assert identifier not in redacted, (prefix, identifier, "survived de-identification")


@pytest.mark.parametrize("prefix", sorted({p for ps in PATIENT_IDENTIFIERS.values() for p in ps}))
def test_sample_document_residual_scan_is_clean(prefix: str) -> None:
    _raw, redacted = _redacted(prefix)
    findings = deidentify.residual_scan(redacted)
    assert findings == [], (prefix, findings)


@pytest.mark.parametrize("prefix", ALL_PREFIXES)
def test_the_patient_surname_alone_is_also_gone(prefix: str) -> None:
    """"Whitfield" on its own (not just the full name) must not survive anywhere."""
    raw, redacted = _redacted(prefix)
    if "Whitfield" in raw:
        assert "Whitfield" not in redacted, (prefix, "bare surname survived")
