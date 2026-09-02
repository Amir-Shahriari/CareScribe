# Sample source documents

Synthetic `.docx` files for manually exercising the clinical-forms pipeline
(upload → de-identify → approve → combine sources → generate a form). All
names, dates, addresses, phone numbers, Medicare numbers and clinical detail
are **fabricated** — none of this is real PHI.

They're deliberately shaped like real inputs: a mix of narrative paragraphs,
two-column detail grids ("Full name: ..."), and multi-column data tables
(medications, session logs, standardised measures, risk grids), all about the
same fictional client (Jordan Whitfield) so they can be combined together.

| File | Mimics | Feeds which form best |
|---|---|---|
| `01_gp_referral_letter.docx` | GP referral letter | Biopsychosocial Assessment (background, meds, family hx) |
| `02_biopsychosocial_intake_notes.docx` | Clinician intake assessment | Biopsychosocial Assessment |
| `03_session_log_progress_notes.docx` | Session log + outcome measures | Client Session Notes |
| `04_treatment_review_source.docx` | Treatment review letter | Client Treatment Review |
| `05_discharge_summary.docx` | Hospital discharge summary | Biopsychosocial Assessment (medical/incident history) |
| `06_risk_assessment.docx` | Structured risk assessment + safety plan | Biopsychosocial Assessment, Client Session Notes |
| `07_case_conference_note.docx` | MDT case conference minutes | Client Treatment Review |

To test: upload one or more of these in the app's document step, run them
through de-identification/approval, then switch to **Clinical form** mode and
generate each of the three form types — combining `01`+`02` for the
Biopsychosocial Assessment gives the richest test since that form has the
most fields (62).

Regenerate with `python make_sample_docs.py` (run from this directory) if you
need to tweak the content.
