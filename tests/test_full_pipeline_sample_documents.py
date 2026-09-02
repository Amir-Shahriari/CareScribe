# tests/test_full_pipeline_sample_documents.py
"""
Runs every ``sample_documents/*.docx`` through the full pipeline: ingest ->
de-identify -> approve (write de-identified text) -> combine sources ->
generate each clinical form type. A stub backend stands in for a real model
so this runs anywhere, with no GPU/network/Ollama dependency; it proves the
plumbing, not generation quality (that's a manual/informational check, see
this file's docstring in the plan).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from carescribe.core import batch, clinical_forms, deidentify, ingest

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_documents"
DOCX_FILES = sorted(SAMPLE_DIR.glob("*.docx"))


class _StubBackend:
    """Deterministic stand-in for a real generation backend."""

    def generate(self, system, prompt, stream=True, *, grammar=None):
        yield "[stub generation output]"


@pytest.mark.skipif(not DOCX_FILES, reason="no sample_documents/*.docx present")
@pytest.mark.parametrize("path", DOCX_FILES, ids=lambda p: p.name)
def test_ingest_and_deidentify_every_sample_document(path):
    text = ingest.extract_text(str(path))
    assert text.strip(), f"{path.name} extracted no text"
    result = deidentify.deidentify(text)
    assert result.redacted_text.strip()
    # The safety sweep must find no structured identifier left behind —
    # same bar tests/test_stress_corpus.py holds the stress corpus to.
    findings = deidentify.residual_scan(result.redacted_text)
    structured = [f for f in findings if any(c.isdigit() for c in f) or "@" in f]
    assert structured == [], (path.name, structured)


@pytest.mark.skipif(len(DOCX_FILES) < 2, reason="need at least 2 sample documents to combine")
def test_combined_sources_generate_every_form_type_with_a_stub_backend():
    texts = []
    for path in DOCX_FILES:
        text = ingest.extract_text(str(path))
        texts.append(deidentify.deidentify(text).redacted_text)
    combined = "\n\n".join(texts)
    backend = _StubBackend()
    for form_id, _title in clinical_forms.available_forms():
        spec = clinical_forms.get_form_spec(form_id)
        chunks = clinical_forms.generate_form_document(
            combined, spec, backend, stream=False, phi_values=[], acknowledged=set()
        )
        output = "".join(chunks)
        assert output.strip(), form_id
