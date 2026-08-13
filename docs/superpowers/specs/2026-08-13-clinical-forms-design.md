# Clinical form generation (APS templates) — design

Status: approved, ready for planning
Date: 2026-08-13

## Problem

CareScribe's existing generation path (`carenotes.py` + `prompts/*.txt`) produces
free-form markdown (SOAP note / GP letter / discharge summary), which `_as_docx()`
renders as headings and paragraphs into a blank Word document. It has no concept
of a fixed table layout.

The practitioner needs the app to fill out three real, structured clinical forms
supplied as `.docx` templates (see `C:\Users\amirh\Desktop\output docs`):

1. **Client Treatment Review** — one table, ~20 field rows.
2. **Biopsychosocial Assessment** — two tables (clinical interview / risk / MSE /
   psychometrics, then a 4×3 formulation grid + treatment plan), ~50 field rows.
3. **Client Session Notes** — one table, ~10 field rows.

Each is almost entirely a table of `label cell → blank value cell(s)`, plus
section-header rows (label spans the full row width, no value cell) and a
signature row (must stay blank). The output must land in a copy of the *actual*
template — same fonts, styling, structure a reviewer or funder already expects —
not a rebuilt approximation.

## Scope

In scope: generating and exporting these three forms from approved,
de-identified source documents, integrated into the existing Step 5 (generate)
UI alongside the current free-form flow (which is untouched).

Out of scope: editing/adding new form templates through the UI (templates are
bundled assets); per-field manual editing (review happens via the existing
draft+refine loop); anything to do with signing the completed form.

## Architecture

### 1. Template assets

The three provided `.docx` files are bundled unmodified under
`carescribe/templates/`:

- `client_treatment_review.docx`
- `biopsychosocial_assessment.docx`
- `client_session_notes.docx`

They are read-only inputs. Nothing in this feature edits them on disk; every
fill happens on an in-memory copy (`python-docx` `Document` re-saved to a
`BytesIO`), matching the "nothing touches disk" pattern already used by
`_as_docx()` and `docx_redact.apply_redactions()`.

### 2. Form spec extraction

A new module, `carescribe/core/clinical_forms.py`, defines a `FormSpec` per
template: an ordered list of `FormField(key, label, path)` plus the location
info needed to write into the right cell later (table index, row index, and
which cell(s) in that row are the value target(s)).

The spec is *derived by walking the template's actual table structure*, not
hand-transcribed, because merged cells make `row.cells` report the same
underlying cell object multiple times and by-eye column indices are unreliable
(confirmed while inspecting the sample files — e.g. a 5-column table row can
report only 4 `cell.text` entries where a merge collapses two columns). The
walk classifies each row as one of:

- **Section/subsection header** — every cell in the row has identical text and
  that text is non-empty. Recorded as a path segment for key-building, not a
  field.
- **Spacer** — every cell is empty. Skipped.
- **Signature row** — label cell text starts with "Signature". Skipped; stays
  blank for an actual signature.
- **Field row** — first cell holds a non-empty label; a distinct empty cell
  (by underlying element identity, not just text) follows it. That first
  distinct empty cell is the value target.
- **Grid row** (the Biopsychosocial "CLINICAL FORMULATION" table) — a header
  row of column labels (Biological / Psychological / Social) followed by rows
  whose first cell is a row label (Predisposing / Precipitating / …) and whose
  remaining cells are per-column value targets. Each (row label, column label)
  pair becomes its own field.

**Field keys** are a slug of the section/subsection path plus the row (and,
for the grid, column) label — e.g. `history.substance_use`,
`mental_state_exam.mood_and_affect.mood`,
`clinical_formulation.predisposing.biological` — so that a label repeated
under two different sections (e.g. "Mood" appears both under "Current
functioning" and under "Mood and affect") gets distinct keys.

A test asserts, per template, the discovered field count and a spot-check of
known keys/labels against the bundled asset, so a future edit to a template
that shifts a row fails a test rather than silently writing into the wrong
cell.

### 3. Header fields (practitioner-entered)

Date, Practitioner, Client name, Client DOB, Session number, Item code, and
Reason for referral are entered directly by the practitioner in a small form.
These are real values — they never go through de-identification or the model,
because the practitioner already knows them exactly and getting a DOB or
session number wrong from model inference is not an acceptable failure mode
for a document like this.

### 4. Multi-document source combination

The practitioner multi-selects already-approved documents. Their
`redacted_text` is concatenated with a per-document prefix on every
placeholder (`[PATIENT]` → `[DOC1_PATIENT]`, `[DATE_2]` → `[DOC2_DATE_2]`, …)
so that two documents' independently-numbered placeholders never collide.
Each document's own `phi_map` is re-keyed with the matching prefix and the
maps are merged before the existing `mapping.reidentify_document()` call —
that function itself is unchanged.

`carenotes.assert_deidentified()` runs against the union of all contributing
documents' PHI values before anything is sent to the model, same as today.

### 5. Generation

The system/user prompt is built dynamically from the `FormSpec`'s field list
(not hand-written per-template `.txt` files, which would drift from the
template's actual structure). It carries the same anti-fabrication and
placeholder-preservation rules as `system.txt`, plus per-field instructions,
and asks the model to emit each field under a marker tied to its key:

```
<<FIELD:history.substance_use>>
... generated text, or "Not documented" ...
```

A parser turns the model's output into `{field_key: text}`. Any field the
model omits defaults to "Not documented" (existing convention, enforced in
Python rather than trusted to the model).

### 6. Review

The parsed field map renders as one scrollable draft — field label as
heading, generated text underneath — reusing the existing draft/refine state
machinery (`_draft_state`, `render_draft`, `refine_document`) unchanged. The
refine prompt gains an instruction to preserve the `<<FIELD:...>>` markers
so a follow-up instruction can't silently drop the structure the export step
depends on.

### 7. Export

A new function, `clinical_forms.fill_template(form_spec, field_values,
header_values) -> bytes`, opens the bundled template asset, writes the
header form values into the header cells, writes each re-identified field's
text into its mapped value cell(s) (multi-line text becomes multiple
paragraphs within the cell), leaves section headers/spacers/signature row
untouched, and returns the saved bytes.

This runs after the existing `finalise()` re-identification and its
unresolved-placeholder check — a report with `unresolved` placeholders left
in it is blocked from export, same gate the free-form path already has.

### 8. UI (`app.py`, Step 5)

A mode toggle is added: **Free-form note** (today's SOAP/letter/discharge
flow, byte-for-byte unchanged) vs **Clinical form** (new). Selecting Clinical
form swaps the single template dropdown for: multi-document picker, form-type
selector (the three templates), and the header mini-form. Generate/review/
refine/download follow the same visual flow as today; Download calls
`clinical_forms.fill_template(...)` instead of `_as_docx(...)`.

## Testing

- `FormSpec` extraction: field count and spot-checked keys/labels per
  template, against the real bundled asset.
- Delimited-output parser: missing fields → "Not documented"; stray non-field
  text ignored; malformed/duplicate markers handled without raising.
- Multi-document placeholder namespacing: no key collision across two
  documents that each define `[PATIENT]`; merged map re-identifies both
  correctly.
- Round-trip: fill a template in memory, reopen it, assert table dimensions
  and section-header/signature-row text are unchanged, and each field's
  value landed in the expected cell.
- Export gate: an unresolved placeholder in any field blocks export, same as
  the existing free-form path.

## Out-of-scope follow-ups (not blocking this work)

- Editing/uploading custom form templates through the UI.
- Per-field manual edit boxes (deferred per the "one scrollable draft, refine
  by instruction" decision).
