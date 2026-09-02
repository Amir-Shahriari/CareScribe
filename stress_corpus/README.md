# Stress corpus

Twenty synthetic clinical documents plus `answer_key.json`, used as a permanent
regression net for the leaks found on real document #2 and for every
subsequent hard case added since.

**Everything here is fabricated.** Invented names, format-valid but fake NHS
numbers, phone numbers from Ofcom's `01632 960xxx` landline and `07700 900xxx`
mobile drama ranges, `example.co.uk` email addresses. No real patient,
clinician, or site appears in any of it — the same rule the `tests/` fixture
follows.

> **Do not add a real patient document to this folder.** It is committed to git.
> A de-identified real document is still not something to push to a remote, and
> the answer key would have to name the identifiers in the clear to be useful,
> which defeats the point entirely. Reproduce the *shape* of a real document
> that broke the pipeline, with fabricated values.

## What each document covers

| Document | Exercises |
|---|---|
| `doc01_community_mh_letter.txt` | all five bugs — the closest reconstruction of document #2 |
| `doc02_cardiology_discharge.txt` | line-split name, initials, facility short forms, in-prose vs anchored dates |
| `doc03_outpatient_clinic_letter.txt` | three record-number label shapes, header town + county, attendee list |
| `doc04_ward_handover.txt` | `A. Surname` against a full name in the header, labelled date fields |
| `doc05_gp_referral.txt` | hyphenated surname, `known as` alias, initials, two label styles |
| `doc06_psych_clinic_letter.txt` | CPA number, ward name, next-of-kin pairing, Mental Health Act / CPA clinical content preserved |
| `doc07_cmht_family_review.txt` | three family members sharing one surname, ward name, separate appointment vs last-seen dates |
| `doc08_wrapped_referral.txt` | a patient name wrapped across a line break, a case number, an organisation name wrapped across a line break (`Kirkstall Lane\nSurgery`) |
| `doc09_crisis_contact_log.txt` | multiple untitled contact dates and a time in one log, ward name, Mental Health Act content preserved |
| `doc10_mha_assessment.txt` | initials alias resolving to the full patient name, case number, ward name, dense Mental Health Act / Mental Capacity Act section content preserved |
| `doc11_multi_identifier_cpn_review.txt` | four identifiers in one document, mixed date formats (`15/03/2026` / `15-Mar-2026` / `15th March 2026`), plain-text medication table |
| `doc12_safeguarding_referral.txt` | dense letterhead block, abbreviated name references (`Mr Smith` / `J. Smith` / `Jas. Smith`) all resolving to one identity, bracketed non-identifier text preserved |
| `doc13_ocr_style_discharge_summary.txt` | OCR-style hyphen-broken words, three identifier number formats for one person, mixed ISO and DD/MM/YY dates |
| `doc14_family_therapy_notes.txt` | family members sharing a surname, an unlabelled phone number in prose, pronoun-only references after a named mention |
| `doc15_risk_assessment_grid.txt` | a risk-assessment grid with the same identifiers repeated per row, a clinician sign-off with registration number and direct-dial phone |
| `doc16_out_of_area_transfer.txt` | the same client carrying two different local record numbers (sending trust's and receiving trust's), two separate letterhead address/phone blocks |
| `doc17_email_correspondence_thread.txt` | an email thread (`From:`/`To:`/`Subject:`/`Sent:` headers, a `-----Original Message-----` quoted reply) with the same names and email addresses repeated across the original and the quote |
| `doc18_court_report.txt` | a solicitor's name and firm, a court case reference number, a date of birth spelled out in prose (`the fourteenth of July, nineteen eighty-five`) |
| `doc19_pharmacy_medication_review.txt` | a dense medication table with a different prescriber per row, so several distinct names and registration numbers must each be redacted independently |
| `doc20_telephone_triage_log.txt` | a timestamped call log in informal shorthand, an Ofcom mobile drama-range number (`07700 900xxx`) |

## The answer key

```json
{"documents": [
  {"file": "...", "covers": [...], "must_redact": [...], "must_preserve": [...]}
]}
```

- `must_redact` — must be **absent** from the de-identified output.
- `must_preserve` — must be **present**. Over-redaction damages clinical meaning
  and is the failure a reviewer cannot catch by reading the output alone.

Whitespace is normalised on both sides before comparison, so a name the document
split across a line break still matches its single-line spelling in the key.

## Running it

```bash
pytest tests/test_stress_corpus.py -q   # CI gate, one test per string
python tests/stress_report.py           # per-document breakdown, non-zero exit on failure
```

Adding a document is a data change: drop the `.txt` in, add its entry to
`answer_key.json`, and it is covered from the next run. No test code changes.
