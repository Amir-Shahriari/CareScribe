"""Per-account scoping of the patient records store.

The store grew accounts after the fact. These tests pin the two things that
matter about how it was done: a logged-in user sees exactly their own roster and
never another account's, and the patients that existed *before* accounts are not
stranded.
"""

from __future__ import annotations

import json

import pytest

from carescribe.core import patients


@pytest.fixture(autouse=True)
def store(tmp_path, monkeypatch):
    """Point the store at a tmp dir and leave it unscoped between tests.

    ``patients`` keeps the active user in module state, so a test that forgets
    to reset it would leak into the next one.
    """
    monkeypatch.setenv("CARESCRIBE_PATIENTS_DIR", str(tmp_path))
    patients.set_active_user(None)
    yield tmp_path
    patients.set_active_user(None)


USER_A = "u_" + "a" * 32
USER_B = "u_" + "b" * 32


def test_unscoped_root_is_the_base(store):
    assert patients.patients_root() == patients.store_base() == store


def test_scoped_root_is_a_subfolder_of_the_base(store):
    patients.set_active_user(USER_A)
    assert patients.patients_root() == store / USER_A


def test_set_active_user_rejects_a_malformed_id():
    for bad in ["nope", "u_short", "p_" + "a" * 32, "u_" + "A" * 32, "../escape"]:
        with pytest.raises(patients.PatientError):
            patients.set_active_user(bad)


def test_empty_string_means_unscoped():
    patients.set_active_user(USER_A)
    patients.set_active_user("")
    assert patients.active_user() is None


def test_each_account_sees_only_its_own_patients():
    patients.set_active_user(USER_A)
    ann = patients.create_patient("Ann Smith")

    patients.set_active_user(USER_B)
    assert patients.list_patients() == []
    bob = patients.create_patient("Bob Jones")
    assert [p.display_name for p in patients.list_patients()] == ["Bob Jones"]

    patients.set_active_user(USER_A)
    assert [p.id for p in patients.list_patients()] == [ann.id]
    # And B's patient is unreachable from A, by id.
    with pytest.raises(patients.PatientError):
        patients.get_patient(bob.id)


def test_two_accounts_can_hold_the_same_patient_name():
    patients.set_active_user(USER_A)
    a = patients.create_patient("Ann Smith")
    patients.set_active_user(USER_B)
    b = patients.create_patient("Ann Smith")
    assert a.id != b.id


def test_unscoped_listing_ignores_account_folders(store):
    patients.set_active_user(USER_A)
    patients.create_patient("Ann Smith")
    patients.set_active_user(None)
    # The base now contains a u_ folder. It is not a patient.
    assert patients.list_patients() == []


def test_deleting_in_one_account_leaves_the_other_alone():
    patients.set_active_user(USER_A)
    ann = patients.create_patient("Ann Smith")
    patients.set_active_user(USER_B)
    bob = patients.create_patient("Bob Jones")
    patients.delete_patient(bob.id)

    patients.set_active_user(USER_A)
    assert [p.id for p in patients.list_patients()] == [ann.id]


def test_filed_documents_are_scoped(store):
    patients.set_active_user(USER_A)
    ann = patients.create_patient("Ann Smith")
    (patients.patient_output_dir(ann.id) / "letter.deid.txt").write_text("x", encoding="utf-8")
    assert [d.name for d in patients.filed_documents(ann.id)] == ["letter.deid.txt"]

    patients.set_active_user(USER_B)
    # Same id, different account: nothing filed, and nothing raised.
    assert patients.filed_documents(ann.id) == []


# --- migration of the pre-accounts roster ---------------------------------

def _make_legacy_patient(store, name: str) -> str:
    """A patient in the flat, pre-accounts layout."""
    patients.set_active_user(None)
    created = patients.create_patient(name)
    return created.id


def test_unscoped_patient_ids_finds_the_legacy_roster(store):
    first = _make_legacy_patient(store, "Ann Smith")
    second = _make_legacy_patient(store, "Bob Jones")
    assert sorted(patients.unscoped_patient_ids()) == sorted([first, second])


def test_migration_moves_the_legacy_roster_into_the_first_account(store):
    legacy = _make_legacy_patient(store, "Ann Smith")
    (patients.patient_output_dir(legacy) / "letter.deid.txt").write_text("x", encoding="utf-8")

    assert patients.migrate_unscoped_into(USER_A) == 1

    # Gone from the base, present for A, and the filed document came along.
    assert patients.unscoped_patient_ids() == []
    patients.set_active_user(USER_A)
    assert [p.display_name for p in patients.list_patients()] == ["Ann Smith"]
    assert [d.name for d in patients.filed_documents(legacy)] == ["letter.deid.txt"]


def test_migration_is_a_no_op_when_there_is_nothing_to_move():
    assert patients.migrate_unscoped_into(USER_A) == 0


def test_migration_rejects_a_malformed_user_id():
    with pytest.raises(patients.PatientError):
        patients.migrate_unscoped_into("not-a-user")


def test_migration_never_overwrites_an_existing_destination(store):
    legacy = _make_legacy_patient(store, "Ann Smith")
    # A patient with that exact id already filed under the account.
    target = store / USER_A / legacy
    (target / patients.DOCUMENTS_SUBDIR).mkdir(parents=True)
    (target / patients.ROSTER_FILENAME).write_text(
        json.dumps({"id": legacy, "display_name": "Someone Else",
                    "created_at": "", "updated_at": ""}),
        encoding="utf-8",
    )

    assert patients.migrate_unscoped_into(USER_A) == 0
    # The existing entry is untouched and the legacy folder is still there.
    patients.set_active_user(USER_A)
    assert [p.display_name for p in patients.list_patients()] == ["Someone Else"]
    patients.set_active_user(None)
    assert patients.unscoped_patient_ids() == [legacy]


def test_second_account_inherits_nothing(store):
    _make_legacy_patient(store, "Ann Smith")
    patients.migrate_unscoped_into(USER_A)
    assert patients.migrate_unscoped_into(USER_B) == 0
    patients.set_active_user(USER_B)
    assert patients.list_patients() == []
