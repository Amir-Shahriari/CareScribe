"""The local account store.

These accounts are workspace separation on a desktop app, not a security
control -- the patient roster is plaintext on disk either way. So what is
tested here is correctness and robustness: that a password never lands on disk
in the clear, that one damaged record cannot take out the login screen, and
that a username (arbitrary text a person types) never decides a path.
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from carescribe.core import users


@pytest.fixture(autouse=True)
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("CARESCRIBE_USERS_DIR", str(tmp_path))
    return tmp_path


# --- the happy path -------------------------------------------------------

def test_create_then_authenticate_round_trip():
    created = users.create_user("ann", "correct horse")
    signed_in = users.authenticate("ann", "correct horse")
    assert signed_in is not None
    assert signed_in.id == created.id
    assert signed_in.username == "ann"


def test_username_is_stored_as_typed_but_matched_case_insensitively():
    users.create_user("Ann Smith", "correct horse")
    assert users.authenticate("ann smith", "correct horse") is not None
    assert users.list_users()[0].username == "Ann Smith"


def test_username_is_whitespace_normalised():
    users.create_user("  Ann   Smith ", "correct horse")
    assert users.list_users()[0].username == "Ann Smith"
    assert users.authenticate("Ann Smith", "correct horse") is not None


def test_any_users_flips_once_an_account_exists():
    assert users.any_users() is False
    users.create_user("ann", "correct horse")
    assert users.any_users() is True


# --- failures the caller must not be able to tell apart --------------------

def test_wrong_password_returns_none():
    users.create_user("ann", "correct horse")
    assert users.authenticate("ann", "wrong horse") is None


def test_unknown_username_returns_none():
    users.create_user("ann", "correct horse")
    assert users.authenticate("nobody", "correct horse") is None


def test_empty_password_returns_none_rather_than_raising():
    users.create_user("ann", "correct horse")
    assert users.authenticate("ann", "") is None


# --- what create_user refuses ---------------------------------------------

def test_duplicate_username_is_rejected_case_insensitively():
    users.create_user("ann", "correct horse")
    with pytest.raises(users.UserError):
        users.create_user("ANN", "different pass")


def test_blank_username_is_rejected():
    for bad in ["", "   ", "\t\n"]:
        with pytest.raises(users.UserError):
            users.create_user(bad, "correct horse")


def test_overlong_username_is_rejected():
    with pytest.raises(users.UserError):
        users.create_user("a" * (users.MAX_USERNAME_LENGTH + 1), "correct horse")


def test_short_password_is_rejected_at_the_boundary():
    with pytest.raises(users.UserError):
        users.create_user("ann", "a" * (users.MIN_PASSWORD_LENGTH - 1))
    # Exactly the minimum is fine.
    assert users.create_user("bob", "a" * users.MIN_PASSWORD_LENGTH) is not None


def test_a_password_of_spaces_is_a_real_password():
    """Nothing trims a password. Only the username is normalised."""
    users.create_user("ann", " " * 10)
    assert users.authenticate("ann", " " * 10) is not None
    assert users.authenticate("ann", "") is None


# --- secret hygiene -------------------------------------------------------

def test_the_plaintext_password_is_nowhere_on_disk(store):
    secret = "correct horse battery staple"
    users.create_user("ann", secret)
    for path in store.rglob("*"):
        if path.is_file():
            assert secret.encode("utf-8") not in path.read_bytes()


def test_the_same_password_produces_different_salts_and_hashes(store):
    users.create_user("ann", "correct horse")
    users.create_user("bob", "correct horse")
    records = [
        json.loads(p.read_text(encoding="utf-8"))
        for p in store.rglob(users.RECORD_FILENAME)
    ]
    assert len({r["salt"] for r in records}) == 2
    assert len({r["password_hash"] for r in records}) == 2


def test_the_user_object_carries_no_secrets():
    user = users.create_user("ann", "correct horse")
    field_names = {f.name for f in dataclasses.fields(user)}
    assert "password_hash" not in field_names
    assert "salt" not in field_names
    # A dataclass repr prints every field, so this catches a field added later.
    assert "correct horse" not in repr(user)


def test_the_username_never_becomes_a_path(store):
    """A username is arbitrary text. Only the opaque id may name a folder."""
    users.create_user("../../escape", "correct horse")
    users.create_user("C:\\Windows", "correct horse")
    children = [c for c in store.iterdir()]
    assert all(c.is_dir() and users._ID_RE.match(c.name) for c in children)
    assert len(children) == 2


# --- a store that has been damaged on disk --------------------------------

def test_listing_an_absent_store_is_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("CARESCRIBE_USERS_DIR", str(tmp_path / "nothing-here"))
    assert users.list_users() == []
    assert users.any_users() is False
    assert users.authenticate("ann", "correct horse") is None


@pytest.mark.parametrize(
    "content",
    [
        None,                       # no user.json at all
        "not json at all",
        '["a", "list"]',            # valid JSON, wrong shape
        '{"username": ""}',         # present but blank
        '{"username": "ann"}',      # no credentials
    ],
)
def test_a_damaged_record_is_skipped_not_raised(store, content):
    users.create_user("ann", "correct horse")
    broken = store / ("u_" + "f" * 32)
    broken.mkdir()
    if content is not None:
        (broken / users.RECORD_FILENAME).write_text(content, encoding="utf-8")

    # The good account still lists and still authenticates.
    assert [u.username for u in users.list_users()] == ["ann"]
    assert users.authenticate("ann", "correct horse") is not None


def test_a_record_with_unusable_kdf_parameters_fails_closed(store):
    users.create_user("ann", "correct horse")
    record_path = next(store.rglob(users.RECORD_FILENAME))
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["kdf"] = {"n": "not a number", "r": 8, "p": 1, "dklen": 32}
    record_path.write_text(json.dumps(record), encoding="utf-8")

    assert users.authenticate("ann", "correct horse") is None


def test_a_file_masquerading_as_a_user_folder_is_ignored(store):
    users.create_user("ann", "correct horse")
    (store / ("u_" + "e" * 32)).write_text("not a folder", encoding="utf-8")
    assert [u.username for u in users.list_users()] == ["ann"]


def test_a_near_miss_folder_name_is_ignored(store):
    users.create_user("ann", "correct horse")
    (store / ("u_" + "a" * 31)).mkdir()      # one hex short
    (store / ("u_" + "A" * 32)).mkdir()      # uppercase hex
    assert [u.username for u in users.list_users()] == ["ann"]


# --- lookups and password change ------------------------------------------

def test_get_user_by_id():
    created = users.create_user("ann", "correct horse")
    assert users.get_user(created.id).username == "ann"


def test_get_user_rejects_a_malformed_id():
    for bad in ["nope", "u_short", "p_" + "a" * 32, "../escape"]:
        with pytest.raises(users.UserError):
            users.get_user(bad)


def test_list_users_is_sorted_case_insensitively():
    for name in ["zoe", "Ann", "bob"]:
        users.create_user(name, "correct horse")
    assert [u.username for u in users.list_users()] == ["Ann", "bob", "zoe"]


def test_change_password_replaces_the_credential():
    created = users.create_user("ann", "correct horse")
    users.change_password(created.id, "correct horse", "a different one")
    assert users.authenticate("ann", "correct horse") is None
    assert users.authenticate("ann", "a different one") is not None


def test_change_password_refuses_a_wrong_current_password():
    created = users.create_user("ann", "correct horse")
    with pytest.raises(users.UserError):
        users.change_password(created.id, "not it", "a different one")
    assert users.authenticate("ann", "correct horse") is not None


def test_change_password_enforces_the_minimum_length():
    created = users.create_user("ann", "correct horse")
    with pytest.raises(users.UserError):
        users.change_password(created.id, "correct horse", "short")


def test_change_password_re_salts(store):
    created = users.create_user("ann", "correct horse")
    before = json.loads((store / created.id / users.RECORD_FILENAME).read_text(encoding="utf-8"))
    users.change_password(created.id, "correct horse", "a different one")
    after = json.loads((store / created.id / users.RECORD_FILENAME).read_text(encoding="utf-8"))
    assert before["salt"] != after["salt"]


def test_username_taken():
    users.create_user("ann", "correct horse")
    assert users.username_taken("ANN") is True
    assert users.username_taken("  ann  ") is True
    assert users.username_taken("bob") is False
    assert users.username_taken("") is False
