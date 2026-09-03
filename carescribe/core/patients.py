"""
The per-patient records store.

CareScribe's output has always been a flat folder of approved de-identified
documents. This adds a persistent grouping over it: a **patient** — identified
by a real display name the clinician types — whose approved de-identified
artefacts are filed together.

What this module persists, and what it does not:

* **Persisted:** the roster. One ``patient.json`` per patient, holding the
  display name and two timestamps. The folder is an opaque id
  (``p_`` + 32 hex), never the name — an arbitrary real name carries no path.
* **Not persisted, here or anywhere:** a document's contents beyond the approved
  de-identified copies the user explicitly files, the original upload, and the
  placeholder-to-value identity map. Those rules live in
  :mod:`carescribe.core.batch`; this module routes the *same* write functions at
  a per-patient folder, it does not open a second write path.

The roster names are the one identifying thing CareScribe writes to disk — a
narrow, deliberate exception documented in ``AGENTS.md`` and the README.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from . import applog

# carescribe/core/patients.py -> carescribe/
_PACKAGE_ROOT = Path(__file__).resolve().parent.parent

# The launcher sets this to a per-user app-data path in the packaged app; in a
# source checkout it is unset and the store sits beside the package, mirroring
# how ``batch._default_output_dir()`` resolves the flat output folder.
_ENV_VAR = "CARESCRIBE_PATIENTS_DIR"

_ID_RE = re.compile(r"^p_[0-9a-f]{32}$")

ROSTER_FILENAME = "patient.json"
DOCUMENTS_SUBDIR = "documents"

# Filed-artefact suffixes, mapped to the kind shown in the UI. Kept in step with
# batch.APPROVED_SUFFIX / APPROVED_DOCX_SUFFIX / REVIEW_SUFFIX.
_KIND_BY_SUFFIX = {
    ".deid.txt": "text",
    ".deid.docx": "word",
    ".review.json": "audit",
}


class PatientError(RuntimeError):
    """Raised for a missing patient, a malformed id, or a store write failure."""


@dataclass(frozen=True)
class Patient:
    id: str
    display_name: str
    created_at: str  # ISO-8601 UTC, seconds
    updated_at: str


@dataclass(frozen=True)
class FiledDocument:
    name: str
    kind: str  # "text" | "word" | "audit"
    modified_at: str  # ISO-8601 UTC, seconds
    size_bytes: int


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def patients_root() -> Path:
    """Root of the records store.

    ``CARESCRIBE_PATIENTS_DIR`` if set, else ``<package>/patients`` — the same
    env-then-package-relative resolution ``batch`` uses for approved output.
    Read on every call so a test (or the launcher) can point it anywhere.
    """
    override = (os.environ.get(_ENV_VAR) or "").strip()
    return Path(override) if override else _PACKAGE_ROOT / "patients"


def _valid_id(patient_id: str) -> str:
    if not isinstance(patient_id, str) or not _ID_RE.match(patient_id):
        raise PatientError(f"Not a patient id: {patient_id!r}")
    return patient_id


def patient_dir(patient_id: str) -> Path:
    """The patient's folder. Raises for a malformed id before building a path."""
    return patients_root() / _valid_id(patient_id)


def patient_output_dir(patient_id: str) -> Path:
    """Where this patient's approved de-identified artefacts are filed."""
    return patient_dir(patient_id) / DOCUMENTS_SUBDIR


def _roster_path(patient_id: str) -> Path:
    return patient_dir(patient_id) / ROSTER_FILENAME


def _clean_name(display_name: str) -> str:
    name = " ".join(str(display_name or "").split())
    if not name:
        raise PatientError("A patient needs a name.")
    return name


def _read_roster(folder: Path) -> Patient | None:
    """Parse one ``patient.json``. Returns ``None`` for anything unreadable."""
    path = folder / ROSTER_FILENAME
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    name = data.get("display_name")
    if not isinstance(name, str) or not name.strip():
        return None
    ident = data.get("id")
    if not isinstance(ident, str) or not _ID_RE.match(ident):
        ident = folder.name
        if not _ID_RE.match(ident):
            return None
    return Patient(
        id=ident,
        display_name=name,
        created_at=str(data.get("created_at") or ""),
        updated_at=str(data.get("updated_at") or ""),
    )


def _write_roster(patient: Patient) -> None:
    path = _roster_path(patient.id)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "id": patient.id,
        "display_name": patient.display_name,
        "created_at": patient.created_at,
        "updated_at": patient.updated_at,
    }
    try:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except OSError as exc:
        raise PatientError(f"Could not write the patient record: {exc}") from exc


def create_patient(display_name: str) -> Patient:
    """Create a patient folder and roster entry. Returns the new record."""
    name = _clean_name(display_name)
    patient_id = "p_" + uuid.uuid4().hex
    stamp = _now()
    patient = Patient(id=patient_id, display_name=name, created_at=stamp, updated_at=stamp)
    try:
        patient_output_dir(patient_id).mkdir(parents=True, exist_ok=False)
    except OSError as exc:  # pragma: no cover - uuid collision is not reachable
        raise PatientError(f"Could not create the patient folder: {exc}") from exc
    _write_roster(patient)
    applog.log("patient created id=%s", patient_id)
    return patient


def list_patients() -> list[Patient]:
    """Every readable patient, sorted by name (case-insensitive) then id.

    A folder with a missing or unparseable ``patient.json`` is skipped and
    logged, never raised — one bad entry must not take out the picker.
    """
    root = patients_root()
    if not root.is_dir():
        return []
    try:
        children = list(root.iterdir())
    except OSError as exc:
        applog.warn("could not list the patient store: %s", exc)
        return []
    found: list[Patient] = []
    for child in children:
        if not child.is_dir() or not _ID_RE.match(child.name):
            continue
        patient = _read_roster(child)
        if patient is None:
            applog.warn("skipping unreadable patient folder %s", child.name)
            continue
        found.append(patient)
    found.sort(key=lambda p: (p.display_name.casefold(), p.id))
    return found


def get_patient(patient_id: str) -> Patient:
    """One patient by id. Raises :class:`PatientError` if it is not there."""
    patient = _read_roster(patient_dir(patient_id))
    if patient is None:
        raise PatientError(f"No such patient: {patient_id}")
    return patient


def rename_patient(patient_id: str, display_name: str) -> Patient:
    """Change a patient's display name, keeping ``created_at``."""
    name = _clean_name(display_name)
    existing = get_patient(patient_id)
    updated = Patient(
        id=existing.id,
        display_name=name,
        created_at=existing.created_at,
        updated_at=_now(),
    )
    _write_roster(updated)
    applog.log("patient renamed id=%s", patient_id)
    return updated


def delete_patient(patient_id: str) -> None:
    """Remove a patient folder and everything filed in it."""
    folder = patient_dir(patient_id)
    if not folder.is_dir():
        raise PatientError(f"No such patient: {patient_id}")
    try:
        shutil.rmtree(folder)
    except OSError as exc:
        raise PatientError(f"Could not delete the patient folder: {exc}") from exc
    applog.log("patient deleted id=%s", patient_id)


def filed_documents(patient_id: str) -> list[FiledDocument]:
    """Approved artefacts filed for this patient, newest first."""
    folder = patient_output_dir(patient_id)
    if not folder.is_dir():
        return []
    scored: list[tuple[float, FiledDocument]] = []
    for child in folder.iterdir():
        if not child.is_file():
            continue
        kind = next(
            (k for suffix, k in _KIND_BY_SUFFIX.items() if child.name.endswith(suffix)),
            None,
        )
        if kind is None:
            continue
        try:
            stat = child.stat()
        except OSError:
            continue
        scored.append((
            stat.st_mtime,
            FiledDocument(
                name=child.name,
                kind=kind,
                modified_at=datetime.fromtimestamp(
                    stat.st_mtime, tz=timezone.utc
                ).isoformat(timespec="seconds"),
                size_bytes=stat.st_size,
            ),
        ))
    # Sort on the raw mtime, not the second-truncated string, so files written
    # within the same second still come back in the order they were filed.
    scored.sort(key=lambda pair: (pair[0], pair[1].name), reverse=True)
    return [doc for _, doc in scored]


__all__ = [
    "DOCUMENTS_SUBDIR",
    "FiledDocument",
    "Patient",
    "PatientError",
    "ROSTER_FILENAME",
    "create_patient",
    "delete_patient",
    "filed_documents",
    "get_patient",
    "list_patients",
    "patient_dir",
    "patient_output_dir",
    "patients_root",
    "rename_patient",
]
