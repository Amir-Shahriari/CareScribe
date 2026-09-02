"""Document ingestion checks. No network, no temp copies of PHI."""

import io

import pytest

from carescribe.core import ingest


class FakeUpload(io.BytesIO):
    def __init__(self, name: str, data: bytes):
        super().__init__(data)
        self.name = name


def test_reads_utf8_text():
    assert ingest.extract_text(FakeUpload("a.txt", "Margaret Chen — cardiology".encode())) == (
        "Margaret Chen — cardiology"
    )


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig", "cp1252", "latin-1"])
def test_reads_the_encodings_clinical_exports_use(encoding):
    assert "Chen" in ingest.extract_text(FakeUpload("a.txt", "Margaret Chen".encode(encoding)))


def test_reads_a_file_path(tmp_path):
    path = tmp_path / "note.txt"
    path.write_text("Patient: Alice Brown", encoding="utf-8")
    assert ingest.extract_text(str(path)) == "Patient: Alice Brown"


@pytest.mark.parametrize(
    "line_ending", ["\r\n", "\r"], ids=["crlf", "cr"]
)
def test_txt_line_endings_are_normalised_to_lf(line_ending):
    """A Windows-authored .txt file must not leak its raw \\r into the pipeline.

    De-identify relies on several \\n-anchored patterns (letterhead
    "Town, County" lines, footer sign-offs) to find identifiers on their own
    line. A stray \\r left in front of those anchors makes the match silently
    fail — an ingest-level bug, not a deidentify one, since the same text read
    via Path.read_text() (which normalises newlines) never showed it.
    """
    raw = line_ending.join(["Line one", "Line two", "Line three"]).encode("utf-8")
    text = ingest.extract_text(FakeUpload("a.txt", raw))
    assert "\r" not in text
    assert text == "Line one\nLine two\nLine three"


def test_rejects_an_unsupported_type():
    with pytest.raises(ingest.IngestError, match="Unsupported file type"):
        ingest.extract_text(FakeUpload("scan.xyz", b"data"))


def test_rejects_legacy_doc_with_a_useful_message():
    with pytest.raises(ingest.IngestError, match="save the document as .docx|\\.docx"):
        ingest.extract_text(FakeUpload("old.doc", b"data"))


def test_rejects_an_empty_file():
    with pytest.raises(ingest.IngestError, match="empty"):
        ingest.extract_text(FakeUpload("a.txt", b""))


def test_rejects_a_file_with_no_extractable_text():
    with pytest.raises(ingest.IngestError, match="No text could be extracted|OCR"):
        ingest.extract_text(FakeUpload("a.txt", b"   \n  \t "))
