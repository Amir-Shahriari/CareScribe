"""
The reviewer gate: candidate highlighting, the adaptive checklist, and the
no-PHI audit sidecar.

This is the backstop that catches whatever the automated layers miss, so what
matters here is that it stays *usable*: a clean document must not manufacture
friction, and a risky one must not be tickable without looking.

Everything here is fabricated.
"""

import json

import pytest

from carescribe import app as carescribe_app
from carescribe.core import batch, review_checklist, review_flags


# ==========================================================================
# Task 1 — the highlighter finds what got missed
# ==========================================================================

MISSED = """[CLINIC]
Harrogate, North Yorkshire

Patient: [PATIENT]
Adeyinka was seen at Kirkstall Lane Surgery on 21 July 2026 at 10:15.
Case No: 990214. Earlier notes refer to M.A.R. throughout.
"""


def _flag_values(text):
    return {flag.text for flag in review_flags.candidate_residuals(text)}


@pytest.mark.parametrize(
    "value",
    ["Adeyinka", "Harrogate", "Kirkstall Lane Surgery", "990214", "21 July 2026",
     "10:15", "M.A.R."],
)
def test_a_planted_residual_is_flagged(value):
    assert value in _flag_values(MISSED)


@pytest.mark.parametrize(
    "kind, value",
    [(review_flags.KIND_NAME, "Adeyinka"), (review_flags.KIND_ID, "990214"),
     (review_flags.KIND_DATE, "21 July 2026"),
     (review_flags.KIND_INITIALS, "M.A.R.")],
)
def test_each_flag_carries_its_kind_and_reason(kind, value):
    flag = next(f for f in review_flags.candidate_residuals(MISSED) if f.text == value)
    assert flag.kind == kind
    assert flag.why


def test_flag_offsets_point_at_the_span():
    for flag in review_flags.candidate_residuals(MISSED):
        assert MISSED[flag.char_start : flag.char_end] == flag.text


CLINICAL = """[PATIENT] was detained under Section 3 of the Mental Health Act.
HoNOS was 18, PHQ-9 was 12 and GAD-7 was 9. The diagnosis is EUPD.
Olanzapine 10mg at night, Aspirin 75mg once daily and Atorvastatin 80mg nocte.
An ECG was normal, eGFR 88, BMI 24, T3/T4 in range. Reviewed on the ward.
"""


@pytest.mark.parametrize(
    "term",
    ["Mental Health Act", "Section 3", "HoNOS", "PHQ-9", "GAD-7", "EUPD",
     "Olanzapine", "Aspirin", "Atorvastatin", "ECG", "eGFR", "BMI", "T3"],
)
def test_clinical_and_legal_terms_are_not_flagged(term):
    flagged = " | ".join(_flag_values(CLINICAL))
    assert term not in flagged


def test_a_dose_is_not_flagged_as_an_id():
    """Five-digit rule must not fire on "10mg" style clinical numbers."""
    ids = {
        f.text for f in review_flags.candidate_residuals(CLINICAL)
        if f.kind == review_flags.KIND_ID
    }
    assert ids == set()


def test_placeholders_are_never_flagged():
    for flag in review_flags.candidate_residuals(MISSED):
        assert not flag.text.startswith("[")


def test_a_clean_document_produces_no_flags():
    clean = "[PATIENT] was reviewed on the ward and remains well.\n"
    assert review_flags.candidate_residuals(clean) == []


def test_one_decision_covers_every_repeat():
    text = "Adeyinka attended. Adeyinka was reviewed. Adeyinka went home.\n"
    flags = review_flags.candidate_residuals(text)
    assert [f.text for f in flags].count("Adeyinka") == 1


def test_dismissing_a_flag_clears_it():
    flags = review_flags.candidate_residuals(MISSED)
    target = next(f for f in flags if f.text == "Adeyinka")
    remaining = review_flags.outstanding(flags, [target.key])
    assert target not in remaining
    assert len(remaining) == len(flags) - 1


# ==========================================================================
# Task 2 / 4 — the checklist adapts, and stays short when it can
# ==========================================================================

def test_a_clean_plain_note_asks_only_the_two_always_items():
    features = review_checklist.DocFeatures()
    items = review_checklist.build_checklist(features)
    assert [item.key for item in items] == ["read_full", "flags_cleared"]


def test_a_risky_document_earns_the_extra_items():
    features = review_checklist.DocFeatures(
        has_table=True, has_relatives=True, has_textbox=True,
        has_header_footer=True, has_dates=True,
    )
    keys = [item.key for item in review_checklist.build_checklist(features)]
    assert keys == [
        "read_full", "flags_cleared", "table_cells", "header_footer",
        "relatives", "textboxes", "dates",
    ]


def test_the_flags_item_is_unsatisfiable_while_a_flag_is_outstanding():
    features = review_checklist.DocFeatures(n_candidate_flags=3, flags_outstanding=2)
    item = next(
        i for i in review_checklist.build_checklist(features) if i.key == "flags_cleared"
    )
    assert not item.auto_satisfied
    assert "2" in item.hint


def test_the_flags_item_satisfies_once_every_flag_is_decided():
    features = review_checklist.DocFeatures(n_candidate_flags=3, flags_outstanding=0)
    item = next(
        i for i in review_checklist.build_checklist(features) if i.key == "flags_cleared"
    )
    assert item.auto_satisfied


def test_features_are_derived_from_the_document():
    document = batch.Document(
        name="letter.txt",
        raw_text="Patient: Wei Chen\nWard: Cedar Ward\nNHS No: 943 476 5919\n\nSeen today.\n",
        redacted_text="[PATIENT] was seen.\n",
        entities=[
            {"type": "RELATIVE_NAME", "value": "Mei Chen", "placeholder": "[RELATIVE]"},
            {"type": "DATE", "value": "1 May 2026", "placeholder": "[DATE]"},
            {"type": "MRN", "value": "990214", "placeholder": "[MRN]"},
        ],
    )
    features = review_checklist.describe(document)
    assert features.has_table
    assert features.has_relatives
    assert features.has_dates
    assert features.has_ids
    assert not features.has_textbox


# ==========================================================================
# The gate — blocked while anything is outstanding
# ==========================================================================

def test_approval_is_blocked_while_a_flag_is_outstanding():
    items = review_checklist.build_checklist(
        review_checklist.DocFeatures(flags_outstanding=1)
    )
    reason = review_checklist.blocking_reason(items, set(), [], 1)
    assert reason
    assert "highlighted" in reason


def test_approval_is_blocked_while_the_sweep_has_findings():
    items = review_checklist.build_checklist(review_checklist.DocFeatures())
    reason = review_checklist.blocking_reason(items, {"read_full", "flags_cleared"},
                                              ["01632 960 188"], 0)
    assert "safety sweep" in reason


def test_approval_is_blocked_until_every_item_is_ticked():
    items = review_checklist.build_checklist(review_checklist.DocFeatures())
    assert review_checklist.blocking_reason(items, {"read_full"}, [], 0)


def test_approval_unblocks_once_everything_is_resolved():
    items = review_checklist.build_checklist(review_checklist.DocFeatures())
    ticked = {item.key for item in items}
    assert review_checklist.blocking_reason(items, ticked, [], 0) == ""


def test_the_gate_unblocks_after_dismissing_the_last_flag():
    flags = review_flags.candidate_residuals(MISSED)
    assert flags
    dismissed = [flag.key for flag in flags]
    outstanding = len(review_flags.outstanding(flags, dismissed))
    items = review_checklist.build_checklist(
        review_checklist.DocFeatures(n_candidate_flags=len(flags),
                                     flags_outstanding=outstanding)
    )
    ticked = {item.key for item in items}
    assert review_checklist.blocking_reason(items, ticked, [], outstanding) == ""


# ==========================================================================
# Task 3 — the audit sidecar carries counts, never content
# ==========================================================================

ENTITIES = [
    {"type": "PATIENT_NAME", "value": "Mariam Aisha Rahman",
     "placeholder": "[PATIENT]", "action": "Redact"},
    {"type": "RELATIVE_NAME", "value": "Yusuf Rahman",
     "placeholder": "[RELATIVE]", "action": "Redact"},
    {"type": "MRN", "value": "990214", "placeholder": "[MRN]", "action": "Redact"},
    {"type": "NHS_NUMBER", "value": "943 476 5919",
     "placeholder": "[NHS_NO]", "action": "Keep"},
]


@pytest.fixture
def record(tmp_path, monkeypatch):
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "out")
    path = batch.write_review_record(
        "referral.docx",
        ticked=["read_full", "flags_cleared", "table_cells"],
        entities=ENTITIES,
        flags_shown=7,
        flags_redacted=2,
        flags_dismissed=5,
    )
    return path, json.loads(path.read_text(encoding="utf-8"))


def test_the_sidecar_records_the_review(record):
    path, data = record
    assert path.name == "referral" + batch.REVIEW_SUFFIX
    assert data["document"] == "referral.docx"
    assert data["checklist_confirmed"] == ["flags_cleared", "read_full", "table_cells"]
    assert data["candidate_flags"] == {"shown": 7, "redacted": 2, "dismissed": 5}
    assert data["reviewed_at"]


def test_the_sidecar_tallies_placeholders_by_type(record):
    _, data = record
    # The Keep row contributed nothing — it was never redacted.
    assert data["placeholders_by_type"] == {
        "MRN": 1, "PATIENT_NAME": 1, "RELATIVE_NAME": 1
    }


@pytest.mark.parametrize(
    "value",
    ["Mariam Aisha Rahman", "Yusuf Rahman", "990214", "943 476 5919",
     "Mariam", "Rahman"],
)
def test_the_sidecar_contains_no_identifier_value(record, value):
    path, _ = record
    assert value not in path.read_text(encoding="utf-8")


def test_the_sidecar_contains_no_mapping(record):
    _, data = record
    flat = json.dumps(data)
    assert "phi_map" not in flat
    assert "[PATIENT]" not in flat
    assert "[MRN]" not in flat


def test_no_corpus_identifier_reaches_the_sidecar(tmp_path, monkeypatch):
    """The real test: nothing the corpus calls an identifier may appear."""
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "out")
    key = json.loads(
        (batch._PACKAGE_ROOT.parent / "stress_corpus" / "answer_key.json")
        .read_text(encoding="utf-8")
    )
    entities = [
        {"type": "PATIENT_NAME", "value": v, "placeholder": "[PATIENT]",
         "action": "Redact"}
        for document in key["documents"]
        for v in document["must_redact"]
    ]
    path = batch.write_review_record(
        "corpus.txt", ticked=["read_full"], entities=entities,
        flags_shown=0, flags_redacted=0, flags_dismissed=0,
    )
    written = path.read_text(encoding="utf-8")
    for document in key["documents"]:
        for value in document["must_redact"]:
            assert value not in written, value


# ==========================================================================
# Task 4 — no friction where there is no risk
# ==========================================================================

def test_a_clean_note_needs_only_two_ticks_end_to_end():
    document = batch.Document(
        name="note.txt",
        raw_text="Seen in clinic today. He remains well.",
        redacted_text="Seen in clinic today. He remains well.",
        entities=[],
    )
    features = review_checklist.describe(document)
    items = review_checklist.build_checklist(features)
    assert len(items) == 2
    ticked = {item.key for item in items}
    assert review_checklist.blocking_reason(items, ticked, [], 0) == ""


def test_the_app_registers_the_new_state_keys_for_wiping():
    """A dismissal key holds the span text, so it must be wiped with the rest."""
    for key in ("checklist", "flag_dismissed", "flag_redacted"):
        assert key in carescribe_app.PHI_KEYS
