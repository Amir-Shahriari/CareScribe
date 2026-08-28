# Clinic-uploaded clinical form templates — design

Status: implemented
Date: 2026-08-29

## Problem

The clinical-form panel (`core/clinical_forms.py`, spec
`2026-08-13-clinical-forms-design.md`) already parses a table-based `.docx`
into a `FormSpec`, fills it from de-identified source text, and re-identifies
locally. But it only works for the **three bundled APS templates**. The
per-template builder functions hand-code everything the parser cannot yet
infer:

- `start_row` for the body walk (6 / 6 / 5),
- the header cells' `(row, col)` coordinates and `style`,
- the "CLINICAL FORMULATION" grid range (`header_row=1, first_data_row=2,
  last_data_row=5`).

A clinic cannot use its own form. That is the gap this closes.

## Scope

In scope: a practitioner uploads a table-based `.docx`; CareScribe infers its
`FormSpec`, stores it, and lists it in the form selector alongside the bundled
three. Generation, refinement, re-identification, and export are unchanged —
a user template is just another `FormSpec`.

Out of scope: RAG / retrieval of exemplars or reference material; an agent
that ranks chunking strategies; editing a parsed field tree in the UI;
heading-based (non-table) documents; OCR; a private-API generation backend.

## Architecture

### New module `core/template_ingest.py`

Reuses `clinical_forms._walk_table` and `clinical_forms._grid_fields`
verbatim. It supplies only the three inferred inputs:

1. **`_infer_header(table)` → `(header_fields, body_start_row)`.**
   Walks table 0 from the top. A row is a metadata row when every non-blank
   deduped cell matches a known identifier label (`Date`, `Practitioner`,
   `Client name`, `Client DOB`, `Session number`, `Item code…`) via
   `slugify`. Each becomes an `inline` `HeaderField` at its `(row, col)`. A
   single blank row between two metadata rows stays in the block. After the
   metadata rows, an optional full-width `Reason for referral:` label row
   becomes an `append` `HeaderField` and its trailing blank row is consumed.
   `body_start_row` is the first row past all of that.

2. **`_find_grids(table, start_row)` → list of
   `(banner, header, first_data, last_data, section)`.**
   A grid is a full-width banner, then a row whose first deduped cell is empty
   and whose remaining cells are short column headers, then ≥2 rows whose
   first cell is a label and whose remaining cells are blank.

3. **`_parse_document`** stitches them together: for each table, walk the
   non-grid row ranges with `_walk_table(..., end_row=...)` and feed grid
   ranges to `_grid_fields`. `_walk_table` gained an optional `end_row`
   parameter (default = unchanged behaviour).

A regression test parses each bundled template through this generic path and
asserts the field keys, `(table, row, col, append_after_label)` anchors, and
header `(key, style, row, col)` tuples are **identical** to the hand-tuned
builder's output. The generalisation is proven, not hoped.

### Persistence

An uploaded template is stored as its own file under
`<app_data_dir>/templates/<form_id>.docx` (the `.docx` is the source of
truth, re-parsed on load — parsing is fast and deterministic) with a
`<form_id>.json` sidecar holding `{form_id, title}` for the selector.
`form_id` is `slugify(filename stem)`, de-duplicated against the bundled ids
and existing files (`form`, `form_2`, …). A blank template carries no PHI, so
persisting it does not touch the identity-mapping invariant.

`save_template` validates by parsing **before** writing anything; an
un-parseable `.docx` (no table, no fields, duplicate field keys) raises
`ClinicalFormError` and nothing is stored.

### Registry integration (`core/clinical_forms.py`)

- `available_forms()` — bundled forms, then `template_ingest.user_form_options()`.
  Wrapped so a broken user template cannot hide the bundled ones.
- `get_form_spec(form_id)` — falls back to `template_ingest.load_user_spec`
  when `form_id` is not a bundled builder. `@lru_cache` is cleared on save
  and delete.
- Lazy imports both directions to avoid a circular import.

### UI (`app.py`)

`_render_template_uploader()` renders an expander above the form selector:
upload `.docx` → parse for a preview (field count, section count, field
labels) → **Save this template** persists it and reruns. Parse failures show
the `ClinicalFormError` message inline.

## Testing

`tests/test_template_ingest.py`:

- Generic parser reproduces all three bundled specs field-for-field.
- `_infer_header` returns body-start 6 / 6 / 5.
- `_find_grids` finds the one formulation grid at `(1, 2, 5)`.
- `_walk_table(end_row=…)` clips to a prefix of the full walk.
- A synthetic template (built with `python-docx` in the test — no
  third-party file vendored) parses to the expected header + fields, and a
  fill round-trip lands each sentinel in its cell with banners intact.
- `save_template` → `available_forms()` → `get_form_spec()` → `fill_template()`
  end to end, against a monkeypatched `app_data_dir`.
- A `.docx` with no table is rejected; a duplicate upload name gets a
  distinct id; `available_forms()` survives a missing templates dir.
- A saved user template works through `build_prompt` / `parse_fields`.

Full suite: 965 passed, 1 skipped (15 new tests in `test_template_ingest.py`).

## Follow-ups (not blocking)

- Delete-a-template affordance in the UI (`template_ingest.delete_template`
  already exists).
- Land a freshly-saved template as the selected form (Streamlit widget-key
  constraints made this awkward to do cleanly in one rerun).
- Non-table / heading-based templates, once a real one exists to design against.
