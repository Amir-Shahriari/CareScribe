"""
The per-patient records store.

`patients.py` owns no detection logic — it is filesystem + JSON. The invariant
it must not break: nothing identifying beyond the roster display name reaches
disk. The folder is an opaque id, never the name; an approved de-identified
write routed through a patient folder clears the same `sweep()` bar as the flat
output folder.

Everything here is fabricated.
"""

import json
import time
from pathlib import Path

import pytest

from carescribe.core import batch, deidentify, patients


@pytest.fixture(autouse=True)
def _store(tmp_path, monkeypatch):
    """Point the store at a scratch dir for every test."""
    root = tmp_path / "patients"
    monkeypatch.setenv("CARESCRIBE_PATIENTS_DIR", str(root))
    return root


# --------------------------------------------------------------------------
# create / identify
# --------------------------------------------------------------------------

def test_create_makes_an_opaque_id_folder_not_the_name(_store):
    p = patients.create_patient("Margaret Elizabeth Chen")
    assert p.id.startswith("p_") and len(p.id) == 34
    assert (_store / p.id / "patient.json").is_file()
    assert (_store / p.id / "documents").is_dir()
    # the real name is nowhere in the directory tree's paths
    for path in _store.rglob("*"):
        assert "Margaret" not in path.name and "Chen" not in path.name


def test_patient_json_round_trips_the_name(_store):
    p = patients.create_patient("Dr Ríoghnach O'Brien-Ng")
    data = json.loads((_store / p.id / "patient.json").read_text(encoding="utf-8"))
    assert data["display_name"] == "Dr Ríoghnach O'Brien-Ng"
    assert data["id"] == p.id
    assert data["created_at"] and data["updated_at"]


@pytest.mark.parametrize("bad", ["", "   ", "\n\t"])
def test_create_rejects_a_blank_name(bad):
    with pytest.raises(patients.PatientError):
        patients.create_patient(bad)


def test_create_strips_surrounding_whitespace():
    p = patients.create_patient("  Alex Stone  ")
    assert p.display_name == "Alex Stone"


def test_duplicate_display_names_are_allowed_and_distinct():
    a = patients.create_patient("John Smith")
    b = patients.create_patient("John Smith")
    assert a.id != b.id
    names = [p.id for p in patients.list_patients()]
    assert a.id in names and b.id in names


# --------------------------------------------------------------------------
# list / get
# --------------------------------------------------------------------------

def test_list_is_sorted_by_name_case_insensitively():
    patients.create_patient("zoe adams")
    patients.create_patient("Aaron Boyd")
    patients.create_patient("mona lang")
    assert [p.display_name for p in patients.list_patients()] == [
        "Aaron Boyd", "mona lang", "zoe adams",
    ]


def test_list_skips_a_corrupt_entry_without_raising(_store):
    good = patients.create_patient("Real Patient")
    broken = _store / ("p_" + "a" * 32)
    (broken / "documents").mkdir(parents=True)
    (broken / "patient.json").write_text("{ not json", encoding="utf-8")
    missing_json = _store / ("p_" + "b" * 32)
    missing_json.mkdir()
    listed = patients.list_patients()
    assert [p.id for p in listed] == [good.id]


def test_get_returns_the_patient():
    p = patients.create_patient("Priya Raman")
    assert patients.get_patient(p.id).display_name == "Priya Raman"


def test_get_raises_for_an_unknown_id():
    with pytest.raises(patients.PatientError):
        patients.get_patient("p_" + "b" * 32)


@pytest.mark.parametrize("bad_id", ["", "nope", "p_short", "../etc", "p_" + "g" * 32])
def test_a_malformed_id_never_becomes_a_path(bad_id):
    with pytest.raises(patients.PatientError):
        patients.patient_dir(bad_id)


# --------------------------------------------------------------------------
# rename / delete
# --------------------------------------------------------------------------

def test_rename_updates_the_name_and_touches_updated_at(_store):
    p = patients.create_patient("Old Name")
    time.sleep(1.05)
    renamed = patients.rename_patient(p.id, "New Name")
    assert renamed.display_name == "New Name"
    assert renamed.created_at == p.created_at
    assert renamed.updated_at >= p.updated_at
    assert patients.get_patient(p.id).display_name == "New Name"


def test_rename_rejects_a_blank_name():
    p = patients.create_patient("Keeps Name")
    with pytest.raises(patients.PatientError):
        patients.rename_patient(p.id, "  ")


def test_delete_removes_the_whole_tree(_store):
    p = patients.create_patient("To Be Deleted")
    (patients.patient_output_dir(p.id) / "x.deid.txt").write_text("[PATIENT]", encoding="utf-8")
    patients.delete_patient(p.id)
    assert not (_store / p.id).exists()
    assert p.id not in [q.id for q in patients.list_patients()]


def test_delete_an_unknown_id_raises():
    with pytest.raises(patients.PatientError):
        patients.delete_patient("p_" + "c" * 32)


# --------------------------------------------------------------------------
# paths / filed documents
# --------------------------------------------------------------------------

def test_patient_output_dir_is_under_the_patient_folder(_store):
    p = patients.create_patient("Path Check")
    assert patients.patient_output_dir(p.id) == _store / p.id / "documents"


def test_filed_documents_lists_newest_first_with_kinds():
    p = patients.create_patient("Filed Docs")
    out = patients.patient_output_dir(p.id)
    (out / "a.deid.txt").write_text("[PATIENT]", encoding="utf-8")
    time.sleep(0.02)
    (out / "a.review.json").write_text("{}", encoding="utf-8")
    time.sleep(0.02)
    (out / "a.deid.docx").write_bytes(b"PK\x03\x04stub")
    filed = patients.filed_documents(p.id)
    assert [f.name for f in filed] == ["a.deid.docx", "a.review.json", "a.deid.txt"]
    assert {f.kind for f in filed} == {"word", "audit", "text"}
    assert all(f.size_bytes > 0 and f.modified_at for f in filed)


def test_filed_documents_is_empty_for_a_new_patient():
    p = patients.create_patient("Nothing Filed")
    assert patients.filed_documents(p.id) == []


# --------------------------------------------------------------------------
# the privacy invariant: an approved write routed here still refuses PHI,
# and nothing identifying lands under patients/
# --------------------------------------------------------------------------

def test_an_approved_write_routed_to_a_patient_folder_lands_there(raw_text):
    p = patients.create_patient("Routing Check")
    result = deidentify.deidentify(raw_text)
    dest = batch.write_approved(
        "summary.txt", result.redacted_text,
        output_dir=patients.patient_output_dir(p.id),
    )
    assert dest == patients.patient_output_dir(p.id) / "summary.deid.txt"
    assert dest.read_text(encoding="utf-8") == result.redacted_text


def test_no_mapping_value_or_residual_identifier_reaches_the_store(_store, raw_text):
    p = patients.create_patient("Leak Check")
    result = deidentify.deidentify(raw_text)
    batch.write_approved(
        "summary.txt", result.redacted_text,
        output_dir=patients.patient_output_dir(p.id),
    )
    batch.write_review_record(
        "summary.txt", entities=result.entities,
        flags_shown=0, flags_redacted=0, flags_dismissed=0, attested=True,
        output_dir=patients.patient_output_dir(p.id),
    )
    blob = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in _store.rglob("*") if path.is_file()
    )
    for value in result.phi_map.values():
        assert value not in blob
    assert deidentify.residual_scan(blob) == []


def test_write_still_refuses_text_that_carries_an_identifier(_store):
    p = patients.create_patient("Refusal Check")
    with pytest.raises(batch.BatchError):
        batch.write_approved(
            "leaky.txt", "Patient NHS No 943 476 5919 seen today.",
            output_dir=patients.patient_output_dir(p.id),
        )


# --------------------------------------------------------------------------
# location
# --------------------------------------------------------------------------

def test_root_follows_the_env_override(_store):
    assert patients.patients_root() == _store


def test_root_defaults_under_app_data_without_the_env(monkeypatch):
    monkeypatch.delenv("CARESCRIBE_PATIENTS_DIR", raising=False)
    from carescribe.core import desktop
    # In a checkout this is the package-relative fallback; in a bundle it is
    # app-data. Either way it ends in "patients".
    assert patients.patients_root().name == "patients"


def test_filed_kind_suffixes_track_the_batch_write_suffixes():
    # filed_documents() classifies by suffix; keep it honest against batch.
    assert set(patients._KIND_BY_SUFFIX) == {
        batch.APPROVED_SUFFIX, batch.APPROVED_DOCX_SUFFIX, batch.REVIEW_SUFFIX,
    }
