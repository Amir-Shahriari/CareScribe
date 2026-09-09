"""A binary file renamed .txt must be refused, not decoded into gibberish.

cp1252 and latin-1 accept nearly every byte, so without a sniff the bytes of a
.docx decode "successfully" and reach de-identification as if they were the
patient's clinical text.
"""

from __future__ import annotations

import io
import zipfile

import pytest

from carescribe.core import ingest


def _upload(name: str, data: bytes):
    buffer = io.BytesIO(data)
    buffer.name = name
    return buffer


def _fake_docx_bytes() -> bytes:
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        archive.writestr("word/document.xml", "<w:document/>")
    return out.getvalue()


def test_real_text_is_still_accepted():
    text = "Patient: [PATIENT]\nSeen on [DATE_1].\n"
    assert ingest.extract_text(_upload("note.txt", text.encode("utf-8"))).startswith(
        "Patient:"
    )


def test_cp1252_clinical_text_is_still_accepted():
    """Windows exports are a real input; the sniff must not reject them."""
    data = "Café review — dose increased to 5mg\n".encode("cp1252")
    assert "dose increased" in ingest.extract_text(_upload("note.txt", data))


def test_a_nul_byte_marks_the_file_binary():
    assert ingest._looks_binary(b"hello\x00world")


def test_plain_prose_is_not_binary():
    assert not ingest._looks_binary(b"Patient seen today. Plan: review in 6 weeks.\n")


def test_empty_data_is_not_reported_binary():
    """Emptiness is handled by extract_text's own guard, not this one."""
    assert not ingest._looks_binary(b"")


def test_a_renamed_docx_is_refused():
    with pytest.raises(ingest.IngestError, match="not plain text"):
        ingest.extract_text(_upload("note.txt", _fake_docx_bytes()))


def test_the_refusal_names_a_way_forward():
    with pytest.raises(ingest.IngestError, match=r"\.docx or \.pdf"):
        ingest.extract_text(_upload("note.txt", _fake_docx_bytes()))
