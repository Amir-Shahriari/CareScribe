# Changelog

The format is based on Keep a Changelog.
This project follows Semantic Versioning.

## [Unreleased]

### Added

- **Local user accounts.** CareScribe now opens on a sign-in screen. Sign up
  once, and the patients you create are filed under your account: another
  account on the same computer sees its own roster and not yours. Accounts live
  in `carescribe/core/users.py`, one opaque-id folder per user, with passwords
  hashed using `hashlib.scrypt` and a per-account salt.

  These accounts are **workspace separation, not a security control**. Both the
  patient roster and the account roster are plaintext on disk, and anyone with
  filesystem access to the app-data folder can read every name without signing
  in. The sign-in screen says so in as many words; do not soften that copy.
  Passwords are hashed so that a password reused from somewhere else is not
  sitting in a file in the clear — that is the whole of the threat model.
- **The first account inherits the existing roster.** Patients created before
  accounts existed are moved into the first account created, so an established
  user loses nothing on upgrade. Later accounts start empty. The move is
  conservative: a folder whose destination already exists is left alone and
  logged rather than merged or overwritten.
- **A patient browser.** Below the patient bar, a searchable and scrollable
  list of your patients, each showing how many documents are filed. Opening one
  lists its filed artefacts grouped by kind, with de-identified text and review
  records readable in place and Word documents offered as downloads.
- Signing out clears every document, identity map, and draft from the session,
  so the next person to sign in on the same machine inherits nothing.

### Fixed

- De-identification: labelled Medicare card numbers (`Medicare No:` /
  `Medicare Card Number`) are now redacted; they previously survived both the
  structured-regex layer and the residual safety-net scan.
- De-identification: an unlabelled letterhead street address is taken as a
  single span instead of being left half-redacted (`45 Kestrel Ave` and
  similar).
- De-identification: labelled `UR No` (Australian Unit Record) and
  `Provider No` identifiers are now redacted.
- De-identification: labelled `Clinic File` / `File No` record numbers and
  pathology/imaging `Accession No` identifiers are now redacted (the value
  shape was already handled, only the label was missing).
- De-identification: `… period:` / `… cover:` / `… expiry:` / `… validity:`
  date fields are treated as identity dates, and both ends of a labelled date
  range (`Certificate period: <date> to <date>`) are redacted, not just the
  first — a WorkCover certificate of capacity previously leaked its second date.
- De-identification: public crisis and support lines (Lifeline, 1800RESPECT,
  Samaritans, Beyond Blue, Kids Helpline, and similar) are preserved via
  `carescribe/core/protected_terms.txt` instead of being over-redacted as
  personal identifiers.
- Generation: the model's own reasoning, planning and self-corrections are
  stripped from the draft instead of being shown to the clinician; the system
  prompt now also forbids them, and `think` is disabled on the Ollama request.

### Added

- Patient records store: a patient bar above the pipeline lets you file a
  batch's approved **de-identified** output under a named patient
  (`<app-data>/patients/<id>/documents/`) instead of the shared folder, with a
  read-only "Filed documents" list, rename, and delete. The patient's display
  name in `patient.json` is the only identifying data persisted; the folder is
  an opaque id, and a document's contents and the identity map never reach it
  (`carescribe/core/patients.py`, `tests/test_patients.py`). "No patient
  (scratch)" keeps the original shared-folder behaviour.
- Regression tests locking in the above: `tests/test_medicare_number_leak.py`,
  `tests/test_letterhead_address_leak.py`, `tests/test_labelled_id_leaks.py`,
  `tests/test_crisis_lines_preserved.py`, and a `sample_documents/` identifier
  answer-key net in `tests/test_sample_document_identifiers.py`.
- Eight more `sample_documents/` types (pathology report, medication chart,
  psychiatry review letter, psychometric report, WorkCover certificate, GP
  progress note, imaging report, physiotherapy letter — all for the same
  fictional patient) so the pipeline is exercised against numeric result
  tables, accession/claim/clinic-file numbers and range fields, not just
  letters. `tests/test_patient_pipeline.py` drives all 15 end to end through
  the per-patient store and asserts nothing identifying is filed.

## [0.1.0] - 2026-09-01

### Added

- Local, privacy-preserving de-identification with an in-memory re-identification map.
- Care note / clinical form generation with retrieval-augmented references.
- Desktop packaging for Windows and macOS (PyInstaller).
- GitHub Actions build & draft-release pipeline.
