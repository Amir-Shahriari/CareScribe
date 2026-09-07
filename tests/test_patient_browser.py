"""Display helpers for the patient browser.

Pure functions over plain data, so these tests need no Streamlit session and no
store on disk.
"""

from __future__ import annotations

import pytest

from carescribe.core.patients import FiledDocument, Patient
from carescribe.ui import patient_browser as pb


def person(name: str, ident: str = "") -> Patient:
    return Patient(
        id=ident or ("p_" + f"{abs(hash(name)):032x}"[:32]),
        display_name=name,
        created_at="2026-09-01T00:00:00+00:00",
        updated_at="2026-09-01T00:00:00+00:00",
    )


def document(name: str, kind: str = "text", size: int = 1024,
             modified: str = "2026-09-07T18:41:00+00:00") -> FiledDocument:
    return FiledDocument(name=name, kind=kind, modified_at=modified, size_bytes=size)


# --- filter_patients -------------------------------------------------------

ROSTER = [person("Ann Smith"), person("Bob Jones"), person("anna bell")]


def test_empty_query_returns_everything():
    assert pb.filter_patients(ROSTER, "") == ROSTER


def test_whitespace_only_query_returns_everything():
    assert pb.filter_patients(ROSTER, "   \t ") == ROSTER


def test_match_is_case_insensitive():
    names = [p.display_name for p in pb.filter_patients(ROSTER, "ANN")]
    assert names == ["Ann Smith", "anna bell"]


def test_match_is_a_substring_not_a_prefix():
    assert [p.display_name for p in pb.filter_patients(ROSTER, "mith")] == ["Ann Smith"]


def test_query_whitespace_is_normalised():
    assert [p.display_name for p in pb.filter_patients(ROSTER, "  ann   smith ")] == ["Ann Smith"]


def test_no_matches_is_empty():
    assert pb.filter_patients(ROSTER, "zzzz") == []


def test_input_is_never_mutated():
    before = list(ROSTER)
    pb.filter_patients(ROSTER, "ann")
    assert ROSTER == before


def test_order_is_preserved():
    result = pb.filter_patients(ROSTER, "")
    assert [p.display_name for p in result] == [p.display_name for p in ROSTER]


# --- human_size ------------------------------------------------------------

@pytest.mark.parametrize("size,expected", [
    (0, "0 B"),
    (1023, "1023 B"),
    (1024, "1.0 KB"),
    (1536, "1.5 KB"),
    (1048576, "1.0 MB"),
    (1073741824, "1.0 GB"),
])
def test_human_size(size, expected):
    assert pb.human_size(size) == expected


def test_human_size_survives_nonsense():
    assert pb.human_size(-1) == "unknown size"
    assert pb.human_size("not a number") == "unknown size"


# --- format_modified -------------------------------------------------------

def test_format_modified_renders_utc():
    assert pb.format_modified("2026-09-07T18:41:00+00:00") == "2026-09-07 18:41 UTC"


def test_format_modified_assumes_utc_when_naive():
    assert pb.format_modified("2026-09-07T18:41:00") == "2026-09-07 18:41 UTC"


@pytest.mark.parametrize("raw", ["not a date", "", "2026-13-45"])
def test_format_modified_returns_bad_input_unchanged(raw):
    assert pb.format_modified(raw) == raw


# --- grouping --------------------------------------------------------------

def test_grouping_drops_nothing_and_omits_empty_buckets():
    docs = [document("a.deid.txt"), document("b.deid.docx", "word"),
            document("c.deid.txt")]
    grouped = pb.group_documents_by_kind(docs)
    assert set(grouped) == {"text", "word"}
    assert sum(len(v) for v in grouped.values()) == 3


def test_grouping_preserves_order_within_a_bucket():
    docs = [document("first.deid.txt"), document("second.deid.txt")]
    assert [d.name for d in pb.group_documents_by_kind(docs)["text"]] == [
        "first.deid.txt", "second.deid.txt"
    ]


def test_an_unknown_kind_keeps_its_raw_value():
    grouped = pb.group_documents_by_kind([document("x.pdf", "pdf")])
    assert "pdf" in grouped


def test_kind_label_falls_back_for_an_unknown_kind():
    assert pb.kind_label("text") == "Text"
    assert pb.kind_label("pdf") == "Pdf"


def test_ordered_kinds_puts_known_first_then_the_rest_sorted():
    grouped = {"audit": [], "zeta": [], "word": [], "alpha": []}
    assert pb.ordered_kinds(grouped) == ["word", "audit", "alpha", "zeta"]


# --- labels ----------------------------------------------------------------

def test_document_label_carries_name_size_and_time():
    label = pb.document_label(document("letter.deid.txt", size=12700))
    assert "letter.deid.txt" in label
    assert "12.4 KB" in label
    assert "2026-09-07 18:41 UTC" in label


@pytest.mark.parametrize("count,tail", [
    (0, "no documents"), (1, "1 document"), (5, "5 documents"),
])
def test_patient_summary_pluralises(count, tail):
    assert pb.patient_summary(person("Ann Smith"), count) == f"Ann Smith  ·  {tail}"
