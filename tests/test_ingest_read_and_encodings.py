"""Ingest file-object handling, text encodings and line endings."""

import pytest

from carescribe.core import ingest


class ReadOnlySeekable:
    def __init__(self, data):
        self.data = data
        self.seeked = False

    def seek(self, pos):
        self.seeked = True

    def read(self):
        return self.data


class ReadOnly:
    def __init__(self, data):
        self.data = data

    def read(self):
        return self.data


def test_read_bytes_rewinds_a_seekable_stream_before_reading():
    """A half-consumed stream must be rewound, or the document is silently truncated."""
    fake = ReadOnlySeekable(b"clinical note")
    name, data = ingest._read_bytes(fake)
    assert fake.seeked is True
    assert name == ""
    assert data == b"clinical note"


def test_read_bytes_reads_an_unseekable_stream():
    fake = ReadOnly(b"clinical note")
    name, data = ingest._read_bytes(fake)
    assert name == ""
    assert data == b"clinical note"


def test_read_bytes_rejects_an_object_with_no_read():
    with pytest.raises(ingest.IngestError, match="Unsupported file object"):
        ingest._read_bytes(object())


def test_extract_txt_falls_back_to_cp1252_past_invalid_utf8():
    text = ingest._extract_txt("Café".encode("cp1252"))
    assert "Caf" in text
    assert "\ufffd" not in text


def test_extract_txt_strips_whitespace_and_round_trips_utf8():
    assert ingest._extract_txt("  \tCafé\n\n".encode("utf-8")) == "Café"
    assert ingest._extract_txt("Café".encode("utf-8")) == "Café"


def test_normalise_line_endings_collapses_crlf_and_bare_cr_to_lf():
    text = "Line one\r\nLine two\rLine three\nLine four\r"
    result = ingest.normalise_line_endings(text)
    assert "\r" not in result
    assert result.count("\n") == 4
