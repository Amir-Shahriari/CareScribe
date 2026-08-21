"""
Batch loading and the approved-write path.

The privacy invariant under test: the only thing that reaches disk is
de-identified text, and the write refuses anything the safety sweep flags.
"""

import io
import json

import pytest

from carescribe.core import batch, deidentify


class FakeUpload(io.BytesIO):
    """Stands in for a Streamlit UploadedFile."""

    def __init__(self, name: str, data: bytes):
        super().__init__(data)
        self.name = name


# ==========================================================================
# Loading
# ==========================================================================

def test_load_documents_reads_every_file():
    docs, errors = batch.load_documents(
        [FakeUpload("a.txt", b"Patient: Alice Brown"), FakeUpload("b.txt", b"Patient: Bob Grey")]
    )
    assert errors == []
    assert set(docs) == {"a.txt", "b.txt"}
    assert docs["a.txt"].raw_text == "Patient: Alice Brown"


def test_one_bad_file_does_not_sink_the_batch():
    docs, errors = batch.load_documents(
        [FakeUpload("good.txt", b"Patient: Alice Brown"), FakeUpload("bad.xyz", b"data")]
    )
    assert set(docs) == {"good.txt"}
    assert len(errors) == 1 and "bad.xyz" in errors[0]


def test_duplicate_filenames_are_reported():
    docs, errors = batch.load_documents(
        [FakeUpload("a.txt", b"one two three"), FakeUpload("a.txt", b"four five six")]
    )
    assert len(docs) == 1
    assert any("duplicate" in message for message in errors)


def test_list_folder_finds_documents(tmp_path):
    (tmp_path / "one.txt").write_text("Patient: Alice Brown", encoding="utf-8")
    (tmp_path / "two.txt").write_text("Patient: Bob Grey", encoding="utf-8")
    (tmp_path / "notes.xlsx").write_bytes(b"nope")
    (tmp_path / "done.deid.txt").write_text("[PATIENT]", encoding="utf-8")

    found = [p.name for p in batch.list_folder(tmp_path)]
    assert found == ["one.txt", "two.txt"]  # already-approved output is skipped


def test_list_folder_rejects_a_missing_path(tmp_path):
    with pytest.raises(batch.BatchError):
        batch.list_folder(tmp_path / "nope")


def test_list_folder_rejects_an_empty_folder(tmp_path):
    with pytest.raises(batch.BatchError):
        batch.list_folder(tmp_path)


def test_analyze_document_populates_state(raw_text):
    document = batch.Document(name="summary.txt", raw_text=raw_text)
    batch.analyze_document(document)
    assert document.analyzed and not document.error
    assert document.entities and document.redacted_text
    assert "943 476 5919" not in document.redacted_text


# ==========================================================================
# Output naming
# ==========================================================================

@pytest.mark.parametrize(
    "name,expected",
    [
        ("summary.pdf", "summary"),
        ("a b/c.txt", "c"),
        ("../../escape.txt", "escape"),
        ("weird name (1).docx", "weird_name_1"),
        ("", "document"),
    ],
)
def test_safe_stem(name, expected):
    assert batch.safe_stem(name) == expected


def test_approved_path_lands_in_the_output_folder():
    path = batch.approved_path("summary.pdf")
    assert path.parent == batch.OUTPUT_DIR
    assert path.name == "summary.deid.txt"


# ==========================================================================
# The write path
# ==========================================================================

def test_write_approved_writes_deidentified_text(tmp_path, monkeypatch, raw_text):
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "deidentified")
    result = deidentify.deidentify(raw_text)

    destination = batch.write_approved("summary.txt", result.redacted_text)

    assert destination.exists()
    assert destination.read_text(encoding="utf-8") == result.redacted_text


def test_written_file_contains_no_identifier(tmp_path, monkeypatch, raw_text):
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "deidentified")
    result = deidentify.deidentify(raw_text)
    destination = batch.write_approved("summary.txt", result.redacted_text)

    written = destination.read_text(encoding="utf-8")
    for value in result.phi_map.values():
        assert value not in written


def test_write_refuses_text_that_still_leaks(tmp_path, monkeypatch, raw_text):
    """The guarantee must not depend on the UI having run the sweep first."""
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "deidentified")
    leaky = deidentify.deidentify(raw_text).redacted_text + "\nCall 01632 960 188.\n"

    with pytest.raises(batch.BatchError, match="Refusing to write"):
        batch.write_approved("summary.txt", leaky)

    assert not batch.approved_path("summary.txt").exists()


def test_write_refuses_empty_text(tmp_path, monkeypatch):
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "deidentified")
    with pytest.raises(batch.BatchError):
        batch.write_approved("summary.txt", "   ")


def test_write_approved_takes_no_mapping_argument():
    """The signature is the guarantee: there is nowhere to pass PHI in.

    `acknowledged` carries only strings the reviewer read in the de-identified
    text, so it is not a channel for the original document or the map.
    """
    import inspect

    parameters = inspect.signature(batch.write_approved).parameters
    positional = [
        name for name, p in parameters.items()
        if p.kind is not inspect.Parameter.KEYWORD_ONLY
    ]
    assert positional == ["name", "deidentified_text"]
    assert set(parameters) == {"name", "deidentified_text", "acknowledged"}


# ==========================================================================
# The safety sweep and dismissals
# ==========================================================================

def test_sweep_matches_residual_scan_when_nothing_is_dismissed(raw_text):
    redacted = deidentify.deidentify(raw_text).redacted_text
    assert batch.sweep(redacted) == deidentify.residual_scan(redacted)


def test_sweep_drops_a_dismissed_finding(raw_text):
    leaky = deidentify.deidentify(raw_text).redacted_text + "\nCall 01632 960 188.\n"
    assert batch.sweep(leaky) == ["01632 960 188"]
    assert batch.sweep(leaky, ["01632 960 188"]) == []


def test_dismissal_is_case_insensitive(raw_text):
    leaky = deidentify.deidentify(raw_text).redacted_text + "\nSeen by Aoife O'Sullivan.\n"
    findings = batch.sweep(leaky)
    assert findings
    assert batch.sweep(leaky, [value.upper() for value in findings]) == []


def test_a_dismissed_finding_lets_the_write_through(tmp_path, monkeypatch, raw_text):
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "deidentified")
    leaky = deidentify.deidentify(raw_text).redacted_text + "\nCall 01632 960 188.\n"

    with pytest.raises(batch.BatchError):
        batch.write_approved("summary.txt", leaky)

    path = batch.write_approved("summary.txt", leaky, acknowledged=["01632 960 188"])
    assert path.exists()


def test_review_record_counts_auto_vs_reviewed_identifiers(tmp_path, monkeypatch):
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path)
    entities = [
        {"type": "PROVIDER_NAME", "value": "Dr Ng", "action": "Redact", "confidence": "auto"},
        {"type": "PATIENT_NAME", "value": "Jo Bloggs", "action": "Redact", "confidence": "review"},
        {"type": "LOCATION", "value": "Bolton", "action": "Keep", "confidence": "review"},
    ]
    path = batch.write_review_record(
        "doc.txt", entities=entities, flags_shown=0, flags_redacted=0, flags_dismissed=0,
    )
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["identifiers_auto_redacted"] == 1
    assert record["identifiers_reviewed_by_practitioner"] == 1
    assert "checklist_confirmed" not in record
