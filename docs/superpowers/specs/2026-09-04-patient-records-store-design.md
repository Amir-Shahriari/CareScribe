# Patient records store — design

**Date:** 2026-09-04
**Status:** Approved for implementation
**Owner:** CareScribe

---

## 1. Goal

Add a persistent per-patient organisation layer over CareScribe's existing
de-identified output. A clinician picks or creates a **patient** (identified by
a real display name they type), runs the normal upload -> de-identify -> review
-> approve flow, and the approved **de-identified** artefacts (`.deid.txt`,
`.deid.docx` when the source was Word, `.review.json`) are filed into that
patient's folder instead of the flat `output/deidentified/`.

Originals and the identity map are **still never written**. The only new
persisted identifying data is the patient roster: each patient's display name in
a `patient.json` inside an opaque-ID folder under
`%LOCALAPPDATA%\CareScribe\patients\`.

Stays a desktop app with the existing shortcut. **"No patient (scratch)"** keeps
today's exact behaviour.

Non-goals: encryption at rest; patient fields beyond name + timestamps;
cross-session re-identification of filed documents; in-app view/edit/re-review
of a filed document; filing generated drafts (a later increment); cross-patient
search or moving documents between patients; deploying the landing site.

## 2. Constraints inherited from CareScribe

| Constraint | Consequence |
|---|---|
| `batch.py` is the single module that writes to disk | The new per-patient writes go through the **same** three functions, parameterised — not a second copy of the sweep+refuse path |
| `sweep()` / `residual_scan()` refuses PHI on every write | Unchanged and still authoritative for a patient-folder write |
| Original document + identity map never on disk | Unchanged. `test_docx_roundtrip.py` untouched |
| Outputs must not be written next to the executable | Patient store lives under `app_data_dir()`, same as `output/` and `models/` |
| "Clear session / wipe PHI" leaves files on disk alone | `wipe_phi()` resets the selected patient to scratch; performs **no** filesystem deletion |

## 3. The one deliberate change to the privacy posture

Option B was chosen over a non-identifying code: the user enters the real name,
it shows in the picker, and it is persisted in `patient.json`. This is a narrow,
documented carve-out to "no identifying text is written to disk":

- **Persisted:** the patient roster — display names + timestamps, one
  `patient.json` per opaque-ID folder.
- **Still never persisted:** any document's contents (original *or*
  de-identified, beyond the approved de-identified copies the user explicitly
  files), and the placeholder -> value identity map.

`AGENTS.md`, the README "Privacy invariants" table + "Privacy caveat", and
`site/src/App.tsx` are updated so the stated guarantee matches the code. A new
invariants row: *Patient names are the only persisted identifier — in
`patients/<id>/patient.json`, never a document's contents, never the map;
`tests/test_patients.py` asserts no document text or mapping value can reach a
patient folder.*

## 4. Storage layout

```
<app_data_dir>/patients/
  p_<uuid4 hex>/
    patient.json            # {id, display_name, created_at, updated_at}  (UTF-8)
    documents/
      <stem>.deid.txt
      <stem>.deid.docx      # only when the source was .docx
      <stem>.review.json
```

The folder name is `"p_" + uuid4().hex` — the display name is **never** used to
build a path, so an arbitrary real name (spaces, unicode, punctuation) carries
no traversal or reserved-name risk.

Path resolution mirrors `batch._default_output_dir()`: env var
`CARESCRIBE_PATIENTS_DIR` if set (the desktop launcher sets it to
`desktop.patients_dir()`), else `<repo>/carescribe/patients/` in a source
checkout. `carescribe/patients/` is git-ignored.

## 5. Components

### 5.1 `carescribe/core/desktop.py`
- `patients_dir() -> Path` = `app_data_dir() / "patients"`.
- `ensure_dirs()` also creates it.

### 5.2 `carescribe/core/patients.py` (new)

```python
class PatientError(RuntimeError): ...

@dataclass(frozen=True)
class Patient:
    id: str            # "p_" + uuid4().hex
    display_name: str
    created_at: str    # ISO-8601 UTC, seconds
    updated_at: str

@dataclass(frozen=True)
class FiledDocument:
    name: str
    kind: str          # "text" | "word" | "audit"
    modified_at: str
    size_bytes: int

def patients_root() -> Path
def create_patient(display_name: str) -> Patient       # blank/whitespace -> PatientError
def list_patients() -> list[Patient]                   # name-sorted; skips unreadable, logs
def get_patient(patient_id: str) -> Patient            # PatientError if absent
def rename_patient(patient_id: str, display_name: str) -> Patient
def delete_patient(patient_id: str) -> None            # shutil.rmtree(patient_dir)
def patient_dir(patient_id: str) -> Path
def patient_output_dir(patient_id: str) -> Path        # patient_dir / "documents"
def filed_documents(patient_id: str) -> list[FiledDocument]   # mtime desc
```

Pure filesystem + JSON. No detection logic. `patient_id` is validated against
`^p_[0-9a-f]{32}$` before being turned into a path (defence in depth even though
callers only pass ids from `list_patients()`).

### 5.3 `carescribe/core/batch.py`

Add a keyword-only `output_dir: Path | None = None` to `write_approved`,
`write_approved_docx`, `write_review_record`, `approved_path`,
`approved_docx_path`, `review_record_path`. `None` -> module `OUTPUT_DIR` at call
time, so `monkeypatch.setattr(batch, "OUTPUT_DIR", ...)` and every existing
caller are unaffected. Each writer does `dest_dir = output_dir or OUTPUT_DIR`
then `dest_dir.mkdir(parents=True, exist_ok=True)`.

### 5.4 `carescribe/app.py`

- `DEFAULTS` gains `"patient_id": ""` (NOT in `PHI_KEYS` — the id is opaque).
- `wipe_phi()` resets `st.session_state["patient_id"] = ""`. No FS deletion.
- `render_patient_bar()` — a bordered card rendered in `main()` before the
  `steps` loop: a `selectbox` of `["No patient (scratch)"] + patients`, a
  "＋ New patient" name input + button, and rename/delete for the selected one.
  Collisions on display name show a short id suffix. Below it,
  `render_filed_documents(patient_id)` when a real patient is selected.
- `_active_output_dir() -> Path | None` — `patients.patient_output_dir(pid)` when
  a patient is selected, else `None`.
- Thread `output_dir=_active_output_dir()` into the three `batch.write_*` calls
  in `render_approval()` and `render_batch_approve()`, and into
  `write_approved_word()`.
- The "Approved files are written to ..." caption reflects the active
  destination.
- `render_filed_documents()` — a table (filename, filed date, type) each with a
  `st.download_button`. Read-only; no rendering of contents, no re-review.

### 5.5 `run_app.py`
Set `environment["CARESCRIBE_PATIENTS_DIR"] = str(desktop.patients_dir())`
alongside the existing `CARESCRIBE_OUTPUT_DIR`.

### 5.6 `.gitignore`
Add `carescribe/patients/`.

## 6. Data flow

1. User picks/creates a patient -> `st.session_state["patient_id"]`.
2. Upload / de-identify / review unchanged.
3. On approve, `_active_output_dir()` is passed to `write_approved`,
   `write_approved_docx`, `write_review_record`; they file into
   `patients/<id>/documents/`. Scratch -> flat folder, exactly as today.
4. `filed_documents()` reads that folder back for the "Filed documents" list.
5. Re-identification is session-only, as today — the map is gone once the
   session ends.

## 7. Failure handling

| Situation | Behaviour |
|---|---|
| `patient.json` missing / unparseable | `list_patients()` skips it, `applog.warn`; never raises into the UI (mirrors `settings.load_settings`) |
| FS error in create / rename / delete | `PatientError` -> `st.error`; rest of the app usable |
| Torn `patient.json` write | Treated as "unparseable" -> skipped; roster entry is recreatable |
| `sweep()` finds PHI in a patient-folder write | Nothing is filed; the UI shows the finding — identical to the flat-folder path today |
| Unknown / malformed `patient_id` | `PatientError` before any path is built |

## 8. Testing

**`tests/test_patients.py` (new)** — opaque-id folder shape; `patient.json`
round-trips the name; `create_patient` rejects blank; `list_patients` skips a
corrupt entry and stays sorted; rename updates name + `updated_at`; delete
removes the tree; `patient_output_dir` path; `filed_documents` ordering + kinds;
**no-PHI assertion** — real `deidentify.deidentify()` then
`batch.write_approved(..., output_dir=patient_output_dir(pid))`, then assert no
mapping value and nothing `residual_scan` flags appears anywhere under
`patients/`; default-dir-under-app-data + `CARESCRIBE_PATIENTS_DIR` override.

**`tests/test_batch.py`** — `output_dir=` cases for the three writers and
`approved_path(name, output_dir=...)`; existing `OUTPUT_DIR`-monkeypatch tests
unchanged and still pass.

**`tests/test_app.py`** — one AppTest: point `CARESCRIBE_PATIENTS_DIR` at
`tmp_path`, create a patient, approve a document, assert the `.deid.txt` lands
under `patients/<id>/documents/`. If AppTest makes patient creation awkward,
this drops to a `batch`-level routing test (noted in the PR).

**Not covered:** Streamlit table rendering details, Explorer behaviour,
multi-instance races.

Full `pytest -q` + `finetune/` + `stress_report.py` must stay green (baseline
1608 passed / 1 skipped, stress 20/20 - 0 leaks - 0 over-redactions).

## 9. Work order

1. `desktop.py` — `patients_dir()`, `ensure_dirs()`.
2. `patients.py` + `test_patients.py` (TDD, isolated).
3. `batch.py` `output_dir` param + `test_batch.py`.
4. `app.py` — patient bar, routing, filed-docs list, `wipe_phi` reset, captions
   + `test_app.py`.
5. `run_app.py` env + `.gitignore`.
6. Docs — README, `site/src/App.tsx`, `AGENTS.md`, `CHANGELOG.md` (swarm workers).
7. Full suite + stress + finetune; `graphify update .`.

## 10. Rejected alternatives

- **Folder named `safe_stem(display_name)`** — reintroduces the real name into a
  filesystem path and collides when two patients share a name.
- **Single `patients/roster.json` index** — one corruption point for the whole
  roster, needs its own locking; per-folder JSON degrades one patient at a time
  and matches "a folder per patient" literally.
- **`batch` writers taking a full `Path` destination** — moves naming logic out
  of the one module that owns every write and lets a caller point a write
  anywhere.
- **Separate `patients`-owned write functions** — two copies of the PHI-refusal
  path, which `batch.py`'s "single module that writes" docstring exists to
  prevent.
- **Patient bar in the sidebar** — it changes where approved output is filed, so
  it belongs next to the pipeline it affects, not in session/status.
