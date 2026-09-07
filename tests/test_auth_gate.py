"""The sign-in gate, end to end through the real app.

Two things are being pinned here. First, that the gate actually gates: a
visitor who is not signed in gets the login screen and *none* of the pipeline.
Second, that accounts scope the roster -- what one account creates, another
does not see.

These accounts are workspace separation on a desktop app, not a security
boundary: the roster is plaintext on disk and this suite does not pretend
otherwise. What is tested is that the app behaves the way the UI says it does.
"""

from __future__ import annotations

import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import pytest  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

from carescribe.core import patients, users  # noqa: E402

APP = str(Path(__file__).resolve().parent.parent / "carescribe" / "app.py")


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    """Accounts and patients both land in tmp, never in the checkout."""
    monkeypatch.setenv("CARESCRIBE_USERS_DIR", str(tmp_path / "users"))
    monkeypatch.setenv("CARESCRIBE_PATIENTS_DIR", str(tmp_path / "patients"))
    patients.set_active_user(None)
    yield tmp_path
    patients.set_active_user(None)


def run(**session) -> AppTest:
    app = AppTest.from_file(APP, default_timeout=120)
    for key, value in session.items():
        app.session_state[key] = value
    app.run()
    assert not app.exception, [e.value for e in app.exception]
    return app


def text(app: AppTest) -> str:
    """Everything the screen said, for coarse assertions."""
    parts = [m.value for m in app.markdown]
    parts += [c.value for c in app.caption]
    parts += [i.value for i in app.info]
    parts += [e.value for e in app.error]
    parts += [s.value for s in app.success]
    return " ".join(str(p) for p in parts)


# --- the gate gates --------------------------------------------------------

def test_a_visitor_who_is_not_signed_in_sees_the_sign_in_screen():
    app = run()
    assert "Sign in to CareScribe" in text(app)


def test_the_pipeline_does_not_render_behind_the_gate():
    app = run()
    # The sidebar is built inside main(), after the gate. Nothing of it should
    # exist -- no wipe button, no session stats.
    assert [b.label for b in app.sidebar.button] == []
    assert "step-tracker" not in text(app)


def test_the_first_visit_offers_signup_not_a_login_form():
    app = run()
    assert "No accounts on this computer yet" in text(app)


def test_once_an_account_exists_the_login_form_is_offered():
    users.create_user("ann", "correct horse")
    app = run()
    assert "No accounts on this computer yet" not in text(app)


# --- signing in ------------------------------------------------------------

def test_a_signed_in_session_reaches_the_app():
    created = users.create_user("ann", "correct horse")
    app = run(user_id=created.id, username=created.username)
    assert "Sign in to CareScribe" not in text(app)
    assert any("wipe PHI" in b.label for b in app.sidebar.button)


def test_the_account_panel_names_the_signed_in_user():
    created = users.create_user("ann", "correct horse")
    app = run(user_id=created.id, username=created.username)
    assert "ann" in text(app)
    assert any(b.key == "sign_out" for b in app.sidebar.button)


def test_signing_out_returns_to_the_gate():
    created = users.create_user("ann", "correct horse")
    app = run(user_id=created.id, username=created.username)
    app.sidebar.button(key="sign_out").click().run()
    assert app.session_state["user_id"] == ""
    assert "Sign in to CareScribe" in text(app)


def test_signing_out_wipes_the_documents_in_memory():
    from carescribe.core import batch
    from tests.fixtures import DISCHARGE_SUMMARY

    created = users.create_user("ann", "correct horse")
    docs = {"a.txt": batch.Document(name="a.txt", raw_text=DISCHARGE_SUMMARY)}
    app = run(user_id=created.id, username=created.username,
              docs=docs, order=list(docs), selected="a.txt")
    app.sidebar.button(key="sign_out").click().run()
    assert app.session_state["docs"] == {}
    assert app.session_state["order"] == []


# --- the honesty the UI owes the user --------------------------------------

def test_the_gate_says_accounts_are_not_a_security_control():
    body = text(run()).casefold()
    assert "not a security control" in body
    assert "unencrypted" in body


# --- scoping, through the app ---------------------------------------------

def test_a_new_account_sees_none_of_another_accounts_patients():
    ann = users.create_user("ann", "correct horse")
    patients.set_active_user(ann.id)
    patients.create_patient("Patient One")
    patients.set_active_user(None)

    bob = users.create_user("bob", "correct horse")
    app = run(user_id=bob.id, username=bob.username)
    assert "Patient One" not in text(app)


def test_an_account_sees_its_own_patients_in_the_browser():
    ann = users.create_user("ann", "correct horse")
    patients.set_active_user(ann.id)
    patients.create_patient("Patient One")
    patients.set_active_user(None)

    app = run(user_id=ann.id, username=ann.username)
    assert "Patient One" in text(app)


def test_the_browser_reports_a_filed_document():
    ann = users.create_user("ann", "correct horse")
    patients.set_active_user(ann.id)
    created = patients.create_patient("Patient One")
    (patients.patient_output_dir(created.id) / "letter.deid.txt").write_text(
        "redacted", encoding="utf-8"
    )
    patients.set_active_user(None)

    app = run(user_id=ann.id, username=ann.username)
    assert "1 document" in text(app)


# --- the first account inherits the pre-accounts roster --------------------

def test_the_first_account_created_through_the_ui_inherits_the_old_roster():
    # A patient from before accounts existed: created unscoped.
    patients.set_active_user(None)
    legacy = patients.create_patient("Legacy Patient")

    app = run()
    app.text_input(key="sign_up_username").set_value("ann").run()
    app.text_input(key="sign_up_password").set_value("correct horse").run()
    app.text_input(key="sign_up_confirm").set_value("correct horse").run()
    app.button[0].click().run()

    user_id = app.session_state["user_id"]
    assert user_id, "signing up should sign the new account in"
    patients.set_active_user(user_id)
    assert [p.id for p in patients.list_patients()] == [legacy.id]
    assert patients.unscoped_patient_ids() == []


def test_a_second_account_inherits_nothing():
    patients.set_active_user(None)
    patients.create_patient("Legacy Patient")
    first = users.create_user("ann", "correct horse")
    patients.migrate_unscoped_into(first.id)
    patients.set_active_user(None)

    second = users.create_user("bob", "correct horse")
    patients.set_active_user(second.id)
    assert patients.list_patients() == []
