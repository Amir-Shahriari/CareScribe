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
    "Jordan Elliot Whitfield": ("01", "02", "03", "04", "05", "06", "07"),
    "12/04/1985": ("01", "02", "04", "05", "06", "07"),
    "2934 5671 0": ("01", "05", "06", "07"),          # Medicare number
    "MCDH-410287": ("05",),                            # hospital UR number
    "2481726A": ("01",),                              # provider number
    "Priya Whitfield": ("01", "02", "05", "06", "07"),  # relative
    "45 Kestrel Ave": ("01", "05"),                   # patient home address
}

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


def test_the_patient_surname_alone_is_also_gone() -> None:
    """"Whitfield" on its own (not just the full name) must not survive anywhere."""
    for prefix in ("01", "02", "03", "04", "05", "06", "07"):
        raw, redacted = _redacted(prefix)
        if "Whitfield" in raw:
            assert "Whitfield" not in redacted, (prefix, "bare surname survived")
