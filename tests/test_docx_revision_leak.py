"""
Regression: text deleted with track changes on rode out in the approved file.

Word keeps deleted text in the file. A ``<w:del>`` revision holds its words in
``w:delText`` rather than ``w:t``, so python-docx's paragraph walk does not see
it, detection never offered it to the reviewer, ``apply_redactions`` could not
rewrite it, and the residual sweep did not read it either. A clinician editing a
template with track changes on -- deleting the previous patient's name -- shipped
that name inside the "de-identified" document.

The same is true of review comments, footnotes and endnotes: separate parts of
the package that no other pass loads. And of the editor's own name, which sits
in a ``w:author`` attribute rather than in any text node.

None of it is reachable by the redactor, so the only safe outcome is the one
text boxes already get: the sweep sees it and the write is refused.

Every name here is fabricated.
"""

from __future__ import annotations

import io
import zipfile

import docx
import pytest
from docx.oxml import parse_xml

from carescribe.core import batch, deidentify, ingest

BODY_PATIENT = "Someone Ordinary"
DELETED_PATIENT = "Wilhelmina Featherstonehaugh"
COMMENT_CLINICIAN = "Dr Archibald Pemberton-Fitzroy"
REVISION_AUTHOR = "Millicent Thorncastle"

_W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


def _document(*, deleted: str = "", author: str = "Someone") -> bytes:
    """A .docx whose body is ordinary and whose revision history is not."""
    document = docx.Document()
    document.add_paragraph(f"Patient: {BODY_PATIENT}")
    if deleted:
        paragraph = document.add_paragraph()
        paragraph._p.append(
            parse_xml(
                f'<w:del {_W} w:id="1" w:author="{author}" '
                f'w:date="2024-03-05T00:00:00Z">'
                f'<w:r><w:delText xml:space="preserve">{deleted}</w:delText></w:r>'
                f"</w:del>"
            )
        )
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()


_COMMENTS_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"
)
_COMMENTS_REL = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"
)


def _with_comments_part(data: bytes, comment_text: str) -> bytes:
    """Add a word/comments.xml part, wired up the way Word wires one.

    python-docx cannot author comments, and it *drops* a part that nothing
    relates to -- so an orphan comments.xml would silently vanish during
    redaction and the test would be proving nothing. The content-type override
    and the relationship are what make this the shape of a real document.
    """
    comments = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f"<w:comments {_W}>"
        f'<w:comment w:id="1" w:author="{REVISION_AUTHOR}" w:date="2024-03-05T00:00:00Z">'
        f"<w:p><w:r><w:t>{comment_text}</w:t></w:r></w:p>"
        f"</w:comment></w:comments>"
    ).encode("utf-8")

    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as source:
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as target:
            for item in source.infolist():
                blob = source.read(item.filename)
                if item.filename == "[Content_Types].xml":
                    blob = blob.replace(
                        b"</Types>",
                        f'<Override PartName="/word/comments.xml" '
                        f'ContentType="{_COMMENTS_TYPE}"/></Types>'.encode("utf-8"),
                    )
                elif item.filename == "word/_rels/document.xml.rels":
                    blob = blob.replace(
                        b"</Relationships>",
                        f'<Relationship Id="rIdComments" Type="{_COMMENTS_REL}" '
                        f'Target="comments.xml"/></Relationships>'.encode("utf-8"),
                    )
                target.writestr(item, blob)
            target.writestr("word/comments.xml", comments)
    return output.getvalue()


def _write(source_bytes: bytes, tmp_path):
    path = tmp_path / "source.docx"
    path.write_bytes(source_bytes)
    result = deidentify.deidentify(ingest.extract_text(str(path)))
    return batch.write_approved_docx(
        "notes.docx",
        source_bytes,
        batch.approved_map(result.entities, result.known_as),
        output_dir=tmp_path / "out",
    )


# ==========================================================================
# The regression
# ==========================================================================


def test_a_tracked_deletion_is_invisible_to_the_extracted_text(tmp_path):
    """Why the sweep has to be what catches it: nothing else can see it."""
    path = tmp_path / "source.docx"
    path.write_bytes(_document(deleted=f"Patient was {DELETED_PATIENT}"))
    assert DELETED_PATIENT not in ingest.extract_text(str(path))


def test_a_name_deleted_with_track_changes_refuses_the_write(tmp_path):
    """Before the fix this wrote a file with the deleted name still inside it."""
    source = _document(deleted=f"Patient was {DELETED_PATIENT}")
    with pytest.raises(batch.BatchError, match="Refusing to write the Word file") as caught:
        _write(source, tmp_path)
    assert DELETED_PATIENT in str(caught.value)
    assert list((tmp_path / "out").glob("*.docx")) == []


def test_the_editor_named_in_a_revision_refuses_the_write(tmp_path):
    """w:author carries a clinician's name in an attribute, not a text node."""
    source = _document(deleted="some earlier wording", author=REVISION_AUTHOR)
    with pytest.raises(batch.BatchError, match="Refusing to write the Word file") as caught:
        _write(source, tmp_path)
    assert REVISION_AUTHOR in str(caught.value)


def test_a_review_comment_naming_someone_refuses_the_write(tmp_path):
    """Comments are a separate part of the package that no other pass loads."""
    source = _with_comments_part(
        _document(), f"Check this against {COMMENT_CLINICIAN}'s letter"
    )
    with pytest.raises(batch.BatchError, match="Refusing to write the Word file") as caught:
        _write(source, tmp_path)
    assert "Pemberton-Fitzroy" in str(caught.value)


# ==========================================================================
# Guards: the scan must not refuse ordinary documents
# ==========================================================================


def test_a_document_with_no_revisions_still_writes(tmp_path):
    assert _write(_document(), tmp_path).exists()


def test_a_tracked_deletion_of_ordinary_words_still_writes(tmp_path):
    """A deletion is not itself a finding -- only an identifier inside one is."""
    source = _document(deleted="the patient reports feeling somewhat better")
    assert _write(source, tmp_path).exists()


def test_a_comment_with_no_identifier_still_writes(tmp_path):
    source = _with_comments_part(_document(), "Please file under active caseload")
    # The comment's own w:author is still a name, so it is expected to refuse --
    # what this asserts is that the *comment text* alone is not the trigger.
    with pytest.raises(batch.BatchError) as caught:
        _write(source, tmp_path)
    assert "file under active caseload" not in str(caught.value)
