"""
Local user accounts.

CareScribe's records store groups approved documents under a patient. This adds
the layer above that: a **user** -- one person using this copy of CareScribe --
whose patients are theirs alone. Sign up, log in, and every patient created
afterwards is filed inside that account's scope (see
:func:`carescribe.core.patients.set_active_user`).

What these accounts are, and what they are not
----------------------------------------------

CareScribe is a **local desktop app**. These accounts separate *workspaces* on a
shared machine. They are an organisational convenience, **not a security
control**:

* The patient roster stays plaintext on disk. Anyone with filesystem access to
  the app-data folder reads every patient name, in every account, regardless of
  who is logged in. Logging out does not lock anything.
* Passwords are hashed only so that a password reused from somewhere else is not
  sitting in a JSON file in the clear. That is the whole of the threat model.

Do not write a docstring, a UI string, or a test that implies more. If real
protection is ever wanted, it means encrypting each account's store with a key
derived from the password -- a different design, with a different failure mode
(a forgotten password destroys that account's roster).

Layout mirrors :mod:`carescribe.core.patients` deliberately: one folder per
user, named by an opaque id (``u_`` + 32 hex), never by the username -- an
arbitrary name a person types must never decide a path.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from . import applog

# carescribe/core/users.py -> carescribe/
_PACKAGE_ROOT = Path(__file__).resolve().parent.parent

# The launcher sets this to a per-user app-data path in the packaged app; unset
# in a source checkout, mirroring patients._ENV_VAR.
_ENV_VAR = "CARESCRIBE_USERS_DIR"

_ID_RE = re.compile(r"^u_[0-9a-f]{32}$")

RECORD_FILENAME = "user.json"

MIN_PASSWORD_LENGTH = 8
MAX_USERNAME_LENGTH = 64

# scrypt parameters. Stored per-record so a later change can rehash an old
# account on next login instead of locking it out.
_KDF = {"algorithm": "scrypt", "n": 2 ** 14, "r": 8, "p": 1, "dklen": 32}
_SALT_BYTES = 16


class UserError(RuntimeError):
    """Raised for a bad username, a weak password, or a store write failure."""


@dataclass(frozen=True)
class User:
    """One account, as the rest of the app sees it.

    Carries no hash and no salt. A dataclass repr prints every field it has, and
    this object is passed around the UI and logged -- so the secrets are simply
    not in it.
    """

    id: str
    username: str
    created_at: str  # ISO-8601 UTC, seconds
    updated_at: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def users_root() -> Path:
    """Root of the account store. Read on every call so a test can move it."""
    override = (os.environ.get(_ENV_VAR) or "").strip()
    return Path(override) if override else _PACKAGE_ROOT / "users"


def _valid_id(user_id: str) -> str:
    if not isinstance(user_id, str) or not _ID_RE.match(user_id):
        raise UserError(f"Not a user id: {user_id!r}")
    return user_id


def user_dir(user_id: str) -> Path:
    """The account's folder. Raises for a malformed id before building a path."""
    return users_root() / _valid_id(user_id)


def _record_path(user_id: str) -> Path:
    return user_dir(user_id) / RECORD_FILENAME


def _clean_username(username: str) -> str:
    name = " ".join(str(username or "").split())
    if not name:
        raise UserError("A user needs a username.")
    if len(name) > MAX_USERNAME_LENGTH:
        raise UserError(f"Username must be {MAX_USERNAME_LENGTH} characters or fewer.")
    return name


def _username_key(username: str) -> str:
    """The comparison form: whitespace-collapsed and casefolded.

    ``casefold`` rather than ``lower`` so that scripts with multi-character
    lowercase mappings compare the way a reader expects.
    """
    return " ".join(str(username or "").split()).casefold()


def _derive(password: str, salt: bytes, kdf: dict) -> bytes:
    try:
        n = int(kdf["n"])
        r = int(kdf["r"])
        p = int(kdf["p"])
        dklen = int(kdf["dklen"])
    except (KeyError, TypeError, ValueError) as exc:
        raise UserError(f"Unusable password parameters: {exc}") from exc
    return hashlib.scrypt(
        str(password).encode("utf-8"), salt=salt, n=n, r=r, p=p, dklen=dklen,
    )


def _check_password(password: str) -> str:
    if not isinstance(password, str) or password == "":
        raise UserError("A user needs a password.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise UserError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
    return password


def _read_record(folder: Path) -> dict | None:
    """Parse one ``user.json``. Returns ``None`` for anything unreadable."""
    try:
        data = json.loads((folder / RECORD_FILENAME).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    username = data.get("username")
    if not isinstance(username, str) or not username.strip():
        return None
    ident = data.get("id")
    if not isinstance(ident, str) or not _ID_RE.match(ident):
        ident = folder.name
        if not _ID_RE.match(ident):
            return None
    # A record without a usable credential is not a usable account. Reading it
    # as one would put a name on the login screen that can never be signed in
    # to, and would let a half-written file masquerade as a user. Skip it here,
    # once, rather than making every caller re-check.
    if (
        not isinstance(data.get("username_key"), str)
        or not isinstance(data.get("password_hash"), str)
        or not isinstance(data.get("salt"), str)
        or not isinstance(data.get("kdf"), dict)
    ):
        return None
    data["id"] = ident
    return data


def _as_user(record: dict) -> User:
    return User(
        id=record["id"],
        username=record["username"],
        created_at=str(record.get("created_at") or ""),
        updated_at=str(record.get("updated_at") or ""),
    )


def _write_record(record: dict) -> None:
    path = _record_path(record["id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(
            json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except OSError as exc:
        raise UserError(f"Could not write the user record: {exc}") from exc


def _records() -> list[dict]:
    """Every readable account record. A damaged one is skipped, never raised.

    One unparseable folder must not take out the login screen -- the same rule
    ``patients.list_patients`` follows for the roster.
    """
    root = users_root()
    if not root.is_dir():
        return []
    try:
        children = list(root.iterdir())
    except OSError as exc:
        applog.warn("could not list the user store: %s", exc)
        return []
    found: list[dict] = []
    for child in children:
        if not child.is_dir() or not _ID_RE.match(child.name):
            continue
        record = _read_record(child)
        if record is None:
            applog.warn("skipping unreadable user folder %s", child.name)
            continue
        found.append(record)
    return found


def username_taken(username: str) -> bool:
    """Case-insensitively, is this username already in use?"""
    key = _username_key(username)
    if not key:
        return False
    return any(record.get("username_key") == key for record in _records())


def create_user(username: str, password: str) -> User:
    """Create an account. Raises :class:`UserError` if it cannot."""
    name = _clean_username(username)
    _check_password(password)
    key = _username_key(name)
    if any(record.get("username_key") == key for record in _records()):
        raise UserError(f"That username is already taken: {name}")

    user_id = "u_" + uuid.uuid4().hex
    salt = secrets.token_bytes(_SALT_BYTES)
    kdf = dict(_KDF)
    stamp = _now()
    record = {
        "id": user_id,
        "username": name,
        "username_key": key,
        "salt": salt.hex(),
        "password_hash": _derive(password, salt, kdf).hex(),
        "kdf": kdf,
        "created_at": stamp,
        "updated_at": stamp,
    }
    try:
        user_dir(user_id).mkdir(parents=True, exist_ok=False)
    except OSError as exc:  # pragma: no cover - uuid collision is not reachable
        raise UserError(f"Could not create the user folder: {exc}") from exc
    _write_record(record)
    applog.log("user created id=%s", user_id)
    return _as_user(record)


def authenticate(username: str, password: str) -> User | None:
    """The account for these credentials, or ``None``.

    One return value for every failure -- unknown username, wrong password,
    corrupt record. The caller must not be able to tell which, and neither must
    the person at the keyboard.
    """
    key = _username_key(username)
    if not key or not isinstance(password, str) or password == "":
        return None
    for record in _records():
        if record.get("username_key") != key:
            continue
        stored = record.get("password_hash")
        salt_hex = record.get("salt")
        kdf = record.get("kdf")
        if (
            not isinstance(stored, str)
            or not isinstance(salt_hex, str)
            or not isinstance(kdf, dict)
        ):
            applog.warn("user record is missing its credentials id=%s", record.get("id"))
            return None
        try:
            salt = bytes.fromhex(salt_hex)
            candidate = _derive(password, salt, kdf)
            expected = bytes.fromhex(stored)
        except (ValueError, UserError) as exc:
            applog.warn("could not verify user id=%s: %s", record.get("id"), exc)
            return None
        if hmac.compare_digest(candidate, expected):
            applog.log("user authenticated id=%s", record["id"])
            return _as_user(record)
        return None
    return None


def get_user(user_id: str) -> User:
    """One account by id. Raises :class:`UserError` if it is not there."""
    record = _read_record(user_dir(user_id))
    if record is None:
        raise UserError(f"No such user: {user_id}")
    return _as_user(record)


def list_users() -> list[User]:
    """Every readable account, sorted by username (case-insensitive) then id."""
    found = [_as_user(record) for record in _records()]
    found.sort(key=lambda user: (user.username.casefold(), user.id))
    return found


def any_users() -> bool:
    """Is there at least one account? Decides signup-first vs login-first."""
    return bool(_records())


def change_password(user_id: str, old_password: str, new_password: str) -> User:
    """Replace a password, re-salting. Raises if ``old_password`` is wrong."""
    record = _read_record(user_dir(user_id))
    if record is None:
        raise UserError(f"No such user: {user_id}")
    if authenticate(record["username"], old_password) is None:
        raise UserError("The current password is not correct.")
    _check_password(new_password)
    salt = secrets.token_bytes(_SALT_BYTES)
    kdf = dict(_KDF)
    record["salt"] = salt.hex()
    record["password_hash"] = _derive(new_password, salt, kdf).hex()
    record["kdf"] = kdf
    record["updated_at"] = _now()
    _write_record(record)
    applog.log("user password changed id=%s", user_id)
    return _as_user(record)


__all__ = [
    "MAX_USERNAME_LENGTH",
    "MIN_PASSWORD_LENGTH",
    "RECORD_FILENAME",
    "User",
    "UserError",
    "any_users",
    "authenticate",
    "change_password",
    "create_user",
    "get_user",
    "list_users",
    "user_dir",
    "username_taken",
    "users_root",
]
