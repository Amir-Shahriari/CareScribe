# Sample source documents

Synthetic `.docx` files for manually exercising the clinical-forms pipeline
(upload → de-identify → approve → combine sources → generate a form). All
names, dates, addresses, phone numbers, Medicare numbers and clinical detail
are **fabricated** — none of this is real PHI.

They're deliberately shaped like real inputs: a mix of narrative paragraphs,
two-column detail grids ("Full name: ..."), and multi-column data tables
(medications, lab panels, session logs, standardised score tables, risk grids,
range-of-motion measurements), all about the same fictional client (Jordan
Whitfield) so they can be combined together. Documents `08`–`15` add
non-psychology document types — pathology, imaging, a medication chart, a
WorkCover certificate — so the pipeline is exercised against numeric result
tables, accession numbers, claim numbers and clinic file numbers, not just
letters.

| File | Mimics | Feeds which form best |
|---|---|---|
| `01_gp_referral_letter.docx` | GP referral letter | Biopsychosocial Assessment (background, meds, family hx) |
| `02_biopsychosocial_intake_notes.docx` | Clinician intake assessment | Biopsychosocial Assessment |
| `03_session_log_progress_notes.docx` | Session log + outcome measures | Client Session Notes |
| `04_treatment_review_source.docx` | Treatment review letter | Client Treatment Review |
| `05_discharge_summary.docx` | Hospital discharge summary | Biopsychosocial Assessment (medical/incident history) |
| `06_risk_assessment.docx` | Structured risk assessment + safety plan | Biopsychosocial Assessment, Client Session Notes |
| `07_case_conference_note.docx` | MDT case conference minutes | Client Treatment Review |
| `08_pathology_report.docx` | Pathology report — FBC/biochemistry result tables, lab reference no. | Biopsychosocial Assessment (medical history) |
| `09_medication_chart.docx` | Inpatient medication administration chart — dense drug grid, UR no. | Biopsychosocial Assessment (medications) |
| `10_psychiatry_review_letter.docx` | Consultant psychiatrist review letter — prose, clinic file no. | Client Treatment Review, Biopsychosocial Assessment |
| `11_psychometric_report.docx` | Psychometric assessment report — WAIS-IV / DASS / PCL score tables | Client Session Notes, Client Treatment Review |
| `12_workcover_certificate.docx` | WorkCover certificate of capacity — claim no., insurer, certificate period | Client Treatment Review |
| `13_gp_progress_note.docx` | Short GP progress note (SOAP) | Client Session Notes |
| `14_imaging_report.docx` | Radiology report — XR/CT prose findings, accession no. | Biopsychosocial Assessment (medical history) |
| `15_physiotherapy_letter.docx` | Physiotherapy progress letter — range-of-motion measurement grid, provider no. | Client Treatment Review |

To test: upload one or more of these in the app's document step, pick or create
a patient in the patient bar, run them through de-identification/approval (the
approved de-identified copies are filed under that patient), then switch to
**Clinical form** mode and generate each of the three form types — combining
`01`+`02` for the Biopsychosocial Assessment gives the richest test since that
form has the most fields (62).

`tests/test_patient_pipeline.py` drives this whole flow automatically for all
15 documents and asserts nothing identifying reaches the patient store;
`tests/test_sample_document_identifiers.py` is the per-identifier answer key.

Regenerate with `python make_sample_docs.py` (run from this directory) if you
need to tweak the content.
