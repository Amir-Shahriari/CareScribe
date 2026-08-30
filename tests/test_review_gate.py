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
# The gate — only the authoritative safety sweep blocks
# ==========================================================================

def test_blocking_reason_empty_when_nothing_outstanding():
    assert review_checklist.blocking_reason([], 0) == ""


def test_blocking_reason_reports_residual_first():
    reason = review_checklist.blocking_reason(["Bolton"], 3)
    assert "1 finding" in reason


def test_advisory_spans_do_not_block_approval():
    """Low-confidence redactions are already in place; the permissive flags are
    advisory. Neither gates the write — only the authoritative sweep does."""
    assert review_checklist.blocking_reason([], 2) == ""
    assert review_checklist.blocking_reason([], 99) == ""


def test_an_advisory_flag_alone_no_longer_blocks_approval():
    """The streamlined gate: a permissive flag the reviewer left untouched does
    not grey Approve. The sweep re-run inside write_approved still refuses any
    real identifier, so the guarantee holds."""
    assert review_checklist.blocking_reason([], 1) == ""


def test_approval_is_blocked_while_the_sweep_has_findings():
    reason = review_checklist.blocking_reason(["Some Name"], 0)
    assert reason != ""


def test_approval_unblocks_once_everything_is_resolved():
    reason = review_checklist.blocking_reason([], 0)
    assert reason == ""


def test_the_gate_unblocks_after_dismissing_the_last_flag():
    flags = review_flags.candidate_residuals(MISSED)
    assert flags
    dismissed = [flag.key for flag in flags]
    outstanding = len(review_flags.outstanding(flags, dismissed))
    assert review_checklist.blocking_reason([], outstanding) == ""


# ==========================================================================
# Task 3 — the audit sidecar carries counts, never content
# ==========================================================================

ENTITIES = [
    {"type": "PATIENT_NAME", "value": "Mariam Aisha Rahman",
     "placeholder": "[PATIENT]", "action": "Redact", "confidence": "review"},
    {"type": "RELATIVE_NAME", "value": "Yusuf Rahman",
     "placeholder": "[RELATIVE]", "action": "Redact", "confidence": "review"},
    {"type": "MRN", "value": "990214", "placeholder": "[MRN]", "action": "Redact",
     "confidence": "auto"},
    {"type": "NHS_NUMBER", "value": "943 476 5919",
     "placeholder": "[NHS_NO]", "action": "Keep", "confidence": "auto"},
]


@pytest.fixture
def record(tmp_path, monkeypatch):
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "out")
    path = batch.write_review_record(
        "referral.docx",
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
    # MRN is the only Redact-action row marked "auto"; the other two Redact
    # rows are "review". The Keep row (NHS_NUMBER) contributes to neither
    # count — it was never redacted.
    assert data["identifiers_auto_redacted"] == 1
    assert data["identifiers_reviewed_by_practitioner"] == 2
    assert data["candidate_flags"] == {"shown": 7, "redacted": 2, "dismissed": 5}
    assert data["reviewed_at"]
    # Not passed by the fixture, so it defaults to False.
    assert data["reviewer_attested"] is False


def test_the_sidecar_records_the_attestation(tmp_path, monkeypatch):
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "out")
    path = batch.write_review_record(
        "referral.docx", entities=ENTITIES,
        flags_shown=0, flags_redacted=0, flags_dismissed=0, attested=True,
    )
    assert json.loads(path.read_text(encoding="utf-8"))["reviewer_attested"] is True


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
        "corpus.txt", entities=entities,
        flags_shown=0, flags_redacted=0, flags_dismissed=0,
    )
    written = path.read_text(encoding="utf-8")
    for document in key["documents"]:
        for value in document["must_redact"]:
            assert value not in written, value


def test_the_app_registers_the_new_state_keys_for_wiping():
    """A dismissal key holds the span text, so it must be wiped with the rest."""
    for key in ("entity_confirmed", "flag_dismissed", "flag_redacted"):
        assert key in carescribe_app.PHI_KEYS
