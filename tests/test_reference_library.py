"""Clinic reference library: paragraph chunking with heading tracking, BM25
search, upload validation. It is a clinician-facing aid — a guard test keeps it
out of the generation path.
"""

import inspect

import pytest

from carescribe.core import reference_library as rl

FORMULARY_MD = """\
# Antidepressants

## Sertraline

Start at 50 mg once daily. Review after two weeks. Maximum 200 mg daily.
Common early side effects: nausea, headache, sleep disturbance.

## Fluoxetine

Start at 20 mg once daily in the morning. Long half-life; taper is rarely
required on discontinuation.

# Referral criteria

Refer to secondary care if there is a suicide attempt, psychotic features, or
non-response to two adequate antidepressant trials.
"""


SECTIONS_MD = """\
# Sertraline

Start at 50 mg once daily. Review after two weeks. The maximum is 200 mg daily.

Nausea and headache are common in the first week and usually settle.

# Fluoxetine

Start at 20 mg each morning.
"""


@pytest.fixture(autouse=True)
def _library(tmp_path, monkeypatch):
    monkeypatch.setattr(rl.desktop, "app_data_dir", lambda: tmp_path)
    rl._CACHE.clear()
    yield tmp_path
    rl._CACHE.clear()


def test_empty_library():
    assert rl.is_empty() is True
    assert rl.search("sertraline dose") == []
    assert rl.sources() == []


def test_add_file_then_sources_and_not_empty():
    rl.add_file("formulary.md", FORMULARY_MD.encode("utf-8"))
    assert rl.is_empty() is False
    names = [name for name, _count in rl.sources()]
    assert names == ["formulary.md"]
    assert rl.sources()[0][1] >= 3  # at least the three paragraphs


def test_search_tracks_the_nearest_heading():
    rl.add_file("formulary.md", FORMULARY_MD.encode("utf-8"))
    hits = rl.search("what is the starting dose of sertraline", k=1)
    assert hits and hits[0].source == "formulary.md"
    assert hits[0].heading == "Sertraline"
    assert "50 mg once daily" in hits[0].text


def test_search_ranks_by_overlap_and_filters_zero_scores():
    rl.add_file("formulary.md", FORMULARY_MD.encode("utf-8"))
    hits = rl.search("suicide attempt psychotic features non-response referral", k=3)
    assert hits[0].heading == "Referral criteria"
    assert rl.search("orthopaedic fracture reduction technique") == []


def test_add_file_validation():
    with pytest.raises(rl.ReferenceError):
        rl.add_file("notes.pdf", b"%PDF-1.4")
    with pytest.raises(rl.ReferenceError):
        rl.add_file("empty.txt", b"   \n  ")
    with pytest.raises(rl.ReferenceError):
        rl.add_file("bad.txt", b"\xff\xfe\x00bad")


def test_duplicate_upload_name_is_suffixed():
    a = rl.add_file("guide.md", FORMULARY_MD.encode("utf-8"))
    b = rl.add_file("guide.md", FORMULARY_MD.encode("utf-8"))
    assert {a, b} == {"guide.md", "guide_2.md"}


def test_cache_refreshes_when_a_file_is_added():
    rl.add_file("a.md", "# A\n\nAlpha passage about alpha things.\n".encode())
    assert len(rl.sources()) == 1
    rl.add_file("b.md", "# B\n\nBeta passage about beta things.\n".encode())
    assert len(rl.sources()) == 2
    assert {h.source for h in rl.search("alpha beta passage", k=5)} == {"a.md", "b.md"}


def test_a_long_paragraph_is_split_into_bounded_chunks():
    body = "# Big\n\n" + ("word " * 800).strip() + "\n"
    rl.add_file("big.txt", body.encode())
    lengths = [len(c.text) for c in rl._all_chunks()]
    assert lengths and max(lengths) <= rl.MAX_CHUNK_CHARS


def test_section_granularity_merges_paragraphs_under_a_heading():
    rl.add_file("g.md", SECTIONS_MD.encode())
    hits = rl.search("nausea headache first week", k=5, granularity="section")
    sert = next(h for h in hits if h.heading == "Sertraline")
    assert "Start at 50 mg once daily" in sert.text
    assert "Nausea and headache" in sert.text


def test_sentence_granularity_returns_single_sentences():
    rl.add_file("g.md", SECTIONS_MD.encode())
    hits = rl.search("maximum daily dose review", k=5, granularity="sentence")
    assert hits
    assert all(h.text.count(".") <= 1 for h in hits)
    assert any(h.text == "Review after two weeks." for h in hits)


def test_invalid_granularity_raises():
    rl.add_file("g.md", SECTIONS_MD.encode())
    with pytest.raises(ValueError):
        rl.search("x", granularity="word")


def test_reference_library_is_not_wired_into_generation():
    from carescribe.core import clinical_forms, carenotes

    assert "reference_library" not in inspect.getsource(clinical_forms)
    assert "reference_library" not in inspect.getsource(carenotes)
