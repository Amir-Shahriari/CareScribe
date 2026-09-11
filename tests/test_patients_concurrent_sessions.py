"""Two signed-in sessions must not see each other's account.

Streamlit serves every concurrent session from its own ScriptRunner thread
inside a SINGLE process. The active account used to live in a plain module
global, reasoned about as safe because "Streamlit runs one script top-to-bottom
per rerun" — true of one session, false of two. Any file I/O inside a store call
releases the GIL, so session A could read the roster while scoped to session B's
account, and file a document into the wrong clinician's folder. That is the one
guarantee accounts exist to make (README: "another account on the same computer
sees its own roster, not yours").

Sequential tests cannot see this; these run the sessions concurrently and force
the interleaving with a barrier.
"""

from __future__ import annotations

import threading

import pytest

from carescribe.core import patients

USER_A = "u_" + "a" * 32
USER_B = "u_" + "b" * 32


@pytest.fixture(autouse=True)
def _scratch_store(tmp_path, monkeypatch):
    monkeypatch.setenv("CARESCRIBE_PATIENTS_DIR", str(tmp_path / "patients"))
    patients.set_active_user(None)
    yield
    patients.set_active_user(None)


def _run_two_sessions(body):
    """Run `body(user_id)` on two threads, interleaved at a barrier."""
    barrier = threading.Barrier(2, timeout=10)
    results: dict[str, object] = {}
    errors: list[BaseException] = []

    def session(user_id: str) -> None:
        try:
            results[user_id] = body(user_id, barrier)
        except BaseException as exc:  # noqa: BLE001 — surfaced below
            errors.append(exc)

    threads = [
        threading.Thread(target=session, args=(user,), daemon=True)
        for user in (USER_A, USER_B)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=15)
    assert not errors, errors
    return results


def test_the_active_account_does_not_leak_between_sessions():
    """Each session must read back the account it set, not the other one."""

    def body(user_id, barrier):
        patients.set_active_user(user_id)
        # Both sessions are now scoped. A shared global would have been
        # overwritten by whichever thread set it last.
        barrier.wait()
        return patients.active_user()

    results = _run_two_sessions(body)
    assert results[USER_A] == USER_A
    assert results[USER_B] == USER_B


def test_the_store_path_does_not_leak_between_sessions():
    """The path is what actually decides which clinician's folder is written."""

    def body(user_id, barrier):
        patients.set_active_user(user_id)
        barrier.wait()
        return patients.patients_root()

    results = _run_two_sessions(body)
    assert results[USER_A].name == USER_A
    assert results[USER_B].name == USER_B
    assert results[USER_A] != results[USER_B]


def test_a_document_is_filed_under_the_session_that_created_it():
    """End to end: create a patient in each session, check the roster split."""

    def body(user_id, barrier):
        patients.set_active_user(user_id)
        barrier.wait()
        created = patients.create_patient(f"Patient of {user_id[:6]}")
        barrier.wait()
        return created.id, [p.id for p in patients.list_patients()]

    results = _run_two_sessions(body)
    for user_id in (USER_A, USER_B):
        created_id, roster = results[user_id]
        other = USER_B if user_id == USER_A else USER_A
        other_created = results[other][0]
        assert created_id in roster
        assert other_created not in roster, (
            f"{user_id} can see {other}'s patient — the accounts scope leaked"
        )


def test_a_fresh_thread_starts_unscoped():
    """A thread that never signed in gets the flat pre-accounts layout."""
    patients.set_active_user(USER_A)
    seen: list[object] = []

    thread = threading.Thread(target=lambda: seen.append(patients.active_user()))
    thread.start()
    thread.join(timeout=10)

    assert seen == [None]
    assert patients.active_user() == USER_A
