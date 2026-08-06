# Stress corpus

Five synthetic clinical documents plus `answer_key.json`, used as a permanent
regression net for the leaks found on real document #2.

**Everything here is fabricated.** Invented names, format-valid but fake NHS
numbers, phone numbers from Ofcom's `01632 960xxx` drama range, `example.co.uk`
email addresses. No real patient, clinician, or site appears in any of it — the
same rule the `tests/` fixture follows.

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
