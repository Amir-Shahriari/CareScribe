# Changelog

The format is based on Keep a Changelog.
This project follows Semantic Versioning.

## [Unreleased]

### Fixed

- De-identification: labelled Medicare card numbers (`Medicare No:` /
  `Medicare Card Number`) are now redacted; they previously survived both the
  structured-regex layer and the residual safety-net scan.
- De-identification: an unlabelled letterhead street address is taken as a
  single span instead of being left half-redacted (`45 Kestrel Ave` and
  similar).
- De-identification: labelled `UR No` (Australian Unit Record) and
  `Provider No` identifiers are now redacted.
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

## [0.1.0] - 2026-09-01

### Added

- Local, privacy-preserving de-identification with an in-memory re-identification map.
- Care note / clinical form generation with retrieval-augmented references.
- Desktop packaging for Windows and macOS (PyInstaller).
- GitHub Actions build & draft-release pipeline.
