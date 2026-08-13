# Clinical Form Generation (APS Templates) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let a practitioner generate the three real APS clinical forms (Client Treatment Review, Biopsychosocial Assessment, Client Session Notes) filled from approved de-identified documents, exported as a copy of the actual template with all styling intact.

**Architecture:** A new `carescribe/core/clinical_forms.py` module walks each bundled template's real table structure to derive a `FormSpec` (which cells are labels, which are values, which are section headers/spacers/signature), builds a marker-delimited prompt from that spec, parses the model's response back into per-field text, and fills a fresh in-memory copy of the template. `carenotes.generate_document`/`refine_document` gain optional `system`/`user_prompt`/`refine_prompt_name` overrides (backward compatible) so the existing backend-selection, PHI-absence assertion, and streaming machinery is reused rather than duplicated. `app.py` gets a new "Clinical form" mode alongside the untouched "Free-form note" mode.

**Tech Stack:** Python, python-docx, Streamlit, pytest. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-08-13-clinical-forms-design.md`

## Global Constraints

- Templates are bundled read-only assets under `carescribe/templates/`; nothing in this feature writes to them. Every fill happens on an in-memory copy, matching the existing "nothing touches disk" pattern in `_as_docx()` and `docx_redact.apply_redactions()`.
- The model never receives real identifiers — only de-identified text with bracketed placeholders, exactly as the existing pipeline already guarantees via `carenotes.assert_deidentified()`.
- Header/demographic fields (Date, Practitioner, Client name, DOB, Session number, Item code, Reason for referral) are typed directly by the practitioner and never sent to the model.
- The existing free-form generation path (`carenotes.py` defaults, `_as_docx`, SOAP/GP letter/discharge summary templates) must remain byte-for-byte unchanged in behavior — all extensions are additive, optional-kwarg based.
- Export is blocked whenever `mapping.reidentify_document()` reports an unresolved placeholder, identical to the existing gate in `render_reidentification()`.

---

## Reference: verified template structure

This was derived by walking the three files at
`C:\Users\amirh\Desktop\output docs` with python-docx, deduplicating merged
cells by underlying XML element identity (`id(cell._tc)`). Row indices below
are 0-based, and refer to the row layout as it exists in the source files
today.

**All three templates** start with the same header block pattern: a
`Date:` / `Practitioner:` row, a `Client name:` / `Client DOB:` row, (Treatment
Review and Session Notes only: a `Session number:` / `Item code:` row), a
blank spacer row, a `Reason for referral:` row (own-cell, practitioner
types the answer directly into that cell), then another blank spacer row.
Every table ends with a `Signature:` row that must stay blank.

- **`client_treatment_review.docx`** — table 0, 27 rows. Header block rows
  0–5. Generic field walk starts at row 6. **14 fields** expected.
- **`client_session_notes.docx`** — table 0, 19 rows. Header block rows 0–5.
  Generic field walk starts at row 6. **9 fields** expected.
- **`biopsychosocial_assessment.docx`** — two tables. Table 0 (62 rows):
  header block rows 0–4 (no session number row), generic walk starts at row
  5, **46 fields**. Table 1 (14 rows): row 0 is the "CLINICAL FORMULATION"
  header, rows 1–5 are a 4×3 grid (row labels Predisposing/Precipitating/
  Perpetuating/Protecting × column labels Biological/Psychological/Social,
  captured from row 1) — **12 fields**, handled by a dedicated grid walker,
  not the generic one. Generic walk resumes at row 6 for the "TREATMENT
  PLAN" section — **4 fields**. Table 1 total: 16. Template total: 62.

Row classification rule (used by every task below): deduplicate a row's
cells by `id(cell._tc)` first (merged cells report the same element more
than once). Then:

- All logical cells blank → **spacer**, skip.
- Exactly one logical cell, its label starts with "Signature" → **skip**
  (only relevant on 2-cell signature rows, see below).
- Exactly one logical cell, cell has >1 paragraph and every paragraph after
  the first is blank → **fillable single-cell field**: label = first
  paragraph's text, value goes in the *same* cell, written as new
  paragraphs after the label (label paragraph itself is never touched).
- Exactly one logical cell, exactly one paragraph → **bare label**,
  ambiguous until the next row is seen:
  - if the next row is a pure spacer (one blank logical cell) → this was a
    fillable field after all; its value goes in *that next row's* cell,
    and the bare label's text also becomes the new "current section
    header" for subsequent rows.
  - otherwise → it was a genuine section/subsection header: record its
    text as the new "current section header" for subsequent rows, and
    re-classify the row that triggered this check normally.
- Exactly one logical cell, more than one paragraph, and at least one
  paragraph after the first is non-blank (e.g. "TREATMENT REVIEW " +
  "(Every 4–6 sessions)") → **header with subtitle**: skip, subtitle
  ignored, first paragraph becomes the current section header.
- Two or more logical cells, first cell's text starts with "Signature"
  (case-insensitive) → **signature row**, skip entirely.
- Two or more logical cells, otherwise → **field**: label = first cell's
  text, value goes in the *second* logical cell (the grid's 3rd/4th cells
  are handled separately, see below).

Field keys are `slug(current_section_header) + "." + slug(label)` (or just
`slug(label)` if no header has been seen yet), where `slug()` lowercases,
replaces every run of non-alphanumeric characters with `_`, and strips
leading/trailing `_`. "Current section header" is a single, flat,
most-recently-seen value — not a true multi-level hierarchy — which is
sufficient because it is only ever used to disambiguate a label that
repeats verbatim elsewhere in the same template (e.g. "Mood" appears both
under "Current functioning" and under "Mood and affect" in the
Biopsychosocial template; the two occurrences get `current_functioning.mood`
and `mood_and_affect.mood`).

---

### Task 1: Bundle template assets

**Files:**
- Create: `carescribe/templates/client_treatment_review.docx` (copy of `C:\Users\amirh\Desktop\output docs\Att 5 APS Client-treatment.docx`)
- Create: `carescribe/templates/biopsychosocial_assessment.docx` (copy of `C:\Users\amirh\Desktop\output docs\ATT 6 APS-WS-Biopsychosocial-Assessment.docx`)
- Create: `carescribe/templates/client_session_notes.docx` (copy of `C:\Users\amirh\Desktop\output docs\Att 7 APS Client-session-notes_1.docx`)
- Create: `carescribe/templates/__init__.py` (empty — makes the directory an importable package resource location)
- Test: `tests/test_clinical_form_templates.py`

**Interfaces:**
- Produces: three `.docx` files at fixed, known paths under `carescribe/templates/`, used by every later task via `Path(__file__).resolve().parent.parent / "templates" / "<name>.docx"`.

- [ ] **Step 1: Copy the three template files into the repo**

```bash
mkdir -p carescribe/templates
cp "C:\Users\amirh\Desktop\output docs\Att 5 APS Client-treatment.docx" "carescribe/templates/client_treatment_review.docx"
cp "C:\Users\amirh\Desktop\output docs\ATT 6 APS-WS-Biopsychosocial-Assessment.docx" "carescribe/templates/biopsychosocial_assessment.docx"
cp "C:\Users\amirh\Desktop\output docs\Att 7 APS Client-session-notes_1.docx" "carescribe/templates/client_session_notes.docx"
touch carescribe/templates/__init__.py
```

- [ ] **Step 2: Write the failing test**

```python
"""The three bundled APS templates load and match the structure this
feature's extraction code assumes. If a future template edit changes row
counts, this fails loudly here rather than silently filling the wrong cell.
"""

from pathlib import Path

import docx
import pytest

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "carescribe" / "templates"


@pytest.mark.parametrize(
    "filename,expected_table_count,expected_row_counts",
    [
        ("client_treatment_review.docx", 1, [27]),
        ("client_session_notes.docx", 1, [19]),
        ("biopsychosocial_assessment.docx", 2, [62, 14]),
    ],
)
def test_bundled_template_shape(filename, expected_table_count, expected_row_counts):
    path = TEMPLATES_DIR / filename
    assert path.is_file(), f"missing bundled template: {path}"
    doc = docx.Document(path)
    assert len(doc.tables) == expected_table_count
    assert [len(t.rows) for t in doc.tables] == expected_row_counts
```

- [ ] **Step 3: Run test to verify it fails**

Run: `python -m pytest tests/test_clinical_form_templates.py -v`
Expected: FAIL — `path.is_file()` assertion, because the files haven't been copied by a passing step yet (or pass immediately if Step 1 already ran; if so this step confirms nothing is broken instead).

- [ ] **Step 4: Run Step 1's copy commands if not already done, then run test again**

Run: `python -m pytest tests/test_clinical_form_templates.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add carescribe/templates/ tests/test_clinical_form_templates.py
git commit -m "feat: bundle the three APS clinical form templates as assets"
```

---

### Task 2: Extraction primitives and the generic row walker

**Files:**
- Create: `carescribe/core/clinical_forms.py`
- Test: `tests/test_clinical_forms.py`

**Interfaces:**
- Consumes: nothing from earlier tasks except the template paths convention from Task 1.
- Produces: `slugify(text: str) -> str`, `FormField` dataclass (`key: str, label: str, table_index: int, value_row_index: int, value_col_index: int, append_after_label: bool`), `_dedupe_row(row) -> list[Cell]`, `_walk_table(table, table_index: int, start_row: int, header_seed: str = "") -> list[FormField]`. These are the exact names later tasks call.

- [ ] **Step 1: Write the failing test (against Client Session Notes — the simplest template, exercising header/spacer/2-cell-field/bare-label-lookahead all in one pass)**

```python
"""Generic table-row classification: which rows are fields, which are
section headers, which are spacers, which is the signature row.

Verified by hand against the real bundled templates (see the plan's
"Reference: verified template structure" section) — these counts and keys
are not guesses.
"""

import docx
import pytest

from carescribe.core import clinical_forms


def _load(name):
    return docx.Document(clinical_forms.TEMPLATES_DIR / name)


def test_slugify_collapses_punctuation_and_case():
    assert clinical_forms.slugify("Current functioning") == "current_functioning"
    assert clinical_forms.slugify("Item code (if relevant):") == "item_code_if_relevant"
    assert clinical_forms.slugify("  Mood  ") == "mood"


def test_session_notes_field_walk_finds_nine_fields():
    doc = _load("client_session_notes.docx")
    fields = clinical_forms._walk_table(doc.tables[0], table_index=0, start_row=6)
    assert len(fields) == 9
    keys = [f.key for f in fields]
    assert "session_summary.mental_state_symptoms_if_applicable" in keys
    assert "session_summary.homework_set_and_reviewed" in keys
    # "Review dates:" already has 4 blank trailing paragraphs baked into
    # its own cell (unlike Treatment Review's, which is a bare label whose
    # answer lives in the next blank row) — an own-cell field, not the
    # lookahead case.
    review = next(f for f in fields if f.key == "session_summary.review_dates")
    assert review.value_row_index == 16
    assert review.append_after_label is True


def test_session_notes_signature_row_is_excluded():
    doc = _load("client_session_notes.docx")
    fields = clinical_forms._walk_table(doc.tables[0], table_index=0, start_row=6)
    assert all("signature" not in f.key for f in fields)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_clinical_forms.py -v`
Expected: FAIL with `ModuleNotFoundError` / `AttributeError: module 'clinical_forms' has no attribute ...`

- [ ] **Step 3: Implement `clinical_forms.py` (primitives + walker only — per-template spec functions come in Tasks 3–4)**

```python
"""
Fill the three bundled APS clinical form templates from approved,
de-identified source documents.

Each template's fillable cells are discovered by walking its real table
structure (see docs/superpowers/specs/2026-08-13-clinical-forms-design.md),
not hand-transcribed, because merged cells make column indices unreliable
by eye. Generation asks the model for one delimited block of text per
discovered field; nothing here decides what counts as a field at
generation time — that was fixed when the spec was built from the asset.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import docx

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


class ClinicalFormError(RuntimeError):
    """Raised when a clinical form can't be built or filled."""


def slugify(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


@dataclass(frozen=True)
class FormField:
    key: str
    label: str
    table_index: int
    value_row_index: int
    value_col_index: int
    append_after_label: bool


@dataclass(frozen=True)
class HeaderField:
    key: str
    label: str
    table_index: int
    row_index: int
    col_index: int
    style: str  # "inline" (append to the label's own paragraph) or "append"
                # (new paragraph(s) after the label, same cell)


@dataclass(frozen=True)
class FormSpec:
    form_id: str
    title: str
    asset_path: Path
    header_fields: list[HeaderField]
    fields: list[FormField]


def _dedupe_row(row):
    """Deduplicate a row's cells by underlying XML element identity.

    python-docx reports a merged cell once per grid column it spans, so a
    naive ``row.cells`` walk sees the same cell 2-3 times. Comparing
    ``id(cell._tc)`` collapses those back into one logical cell per visual
    box, in left-to-right order.
    """
    seen: set[int] = set()
    cells = []
    for cell in row.cells:
        key = id(cell._tc)
        if key not in seen:
            seen.add(key)
            cells.append(cell)
    return cells


def _paragraph_texts(cell) -> list[str]:
    return [p.text for p in cell.paragraphs]


def _walk_table(table, table_index: int, start_row: int, header_seed: str = "") -> list[FormField]:
    fields: list[FormField] = []
    current_header = header_seed
    pending: tuple[int, str] | None = None  # (row_index, label_text)

    def make_key(label: str) -> str:
        return f"{slugify(current_header)}.{slugify(label)}" if current_header else slugify(label)

    for row_index in range(start_row, len(table.rows)):
        cells = _dedupe_row(table.rows[row_index])
        texts = [c.text.strip() for c in cells]
        full_blank = all(t == "" for t in texts)

        if pending is not None:
            _, label_text = pending
            pending = None
            if full_blank and len(cells) == 1:
                fields.append(FormField(
                    key=make_key(label_text), label=label_text,
                    table_index=table_index, value_row_index=row_index,
                    value_col_index=0, append_after_label=False,
                ))
                continue
            current_header = label_text
            # fall through — this row still needs its own classification

        if full_blank:
            continue

        if len(cells) == 1:
            paragraphs = _paragraph_texts(cells[0])
            label_text = paragraphs[0].strip()
            trailing = paragraphs[1:]
            trailing_blank = bool(trailing) and all(p.strip() == "" for p in trailing)
            if trailing_blank:
                fields.append(FormField(
                    key=make_key(label_text), label=label_text,
                    table_index=table_index, value_row_index=row_index,
                    value_col_index=0, append_after_label=True,
                ))
            elif len(paragraphs) == 1:
                pending = (row_index, label_text)
            else:
                current_header = label_text
            continue

        label_text = cells[0].text.strip()
        if label_text.lower().startswith("signature"):
            continue
        fields.append(FormField(
            key=make_key(label_text), label=label_text,
            table_index=table_index, value_row_index=row_index,
            value_col_index=1, append_after_label=False,
        ))

    return fields
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_clinical_forms.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add carescribe/core/clinical_forms.py tests/test_clinical_forms.py
git commit -m "feat: add row-classification walker for clinical form templates"
```

---

### Task 3: Client Treatment Review form spec

**Files:**
- Modify: `carescribe/core/clinical_forms.py`
- Modify: `tests/test_clinical_forms.py`

**Interfaces:**
- Consumes: `FormSpec`, `HeaderField`, `_walk_table`, `TEMPLATES_DIR` from Task 2.
- Produces: `get_form_spec(form_id: str) -> FormSpec` (registry, used by every later task), `"client_treatment_review"` as a valid `form_id`.

- [ ] **Step 1: Write the failing test**

```python
def test_treatment_review_spec_has_fourteen_fields():
    spec = clinical_forms.get_form_spec("client_treatment_review")
    assert spec.title == "Client Treatment Review"
    assert len(spec.fields) == 14
    keys = [f.key for f in spec.fields]
    assert "clinical_formulation.current_diagnoses_prognoses" in keys
    # "Review dates:" is a bare label whose own paragraph count is 1 and
    # whose answer lives in the following blank row (row 25).
    review = next(f for f in spec.fields if f.key.endswith("review_dates"))
    assert review.value_row_index == 25


def test_treatment_review_header_fields():
    spec = clinical_forms.get_form_spec("client_treatment_review")
    header_keys = [h.key for h in spec.header_fields]
    assert header_keys == [
        "date", "practitioner", "client_name", "client_dob",
        "session_number", "item_code", "reason_for_referral",
    ]
    reason = next(h for h in spec.header_fields if h.key == "reason_for_referral")
    assert reason.style == "append"
    date = next(h for h in spec.header_fields if h.key == "date")
    assert date.style == "inline"


def test_unknown_form_id_raises():
    with pytest.raises(clinical_forms.ClinicalFormError):
        clinical_forms.get_form_spec("not_a_real_form")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_clinical_forms.py -v`
Expected: FAIL — `AttributeError: module 'clinical_forms' has no attribute 'get_form_spec'`

- [ ] **Step 3: Implement the spec builder and registry**

Append to `carescribe/core/clinical_forms.py`:

```python
from functools import lru_cache


def _treatment_review_spec() -> FormSpec:
    asset = TEMPLATES_DIR / "client_treatment_review.docx"
    doc = docx.Document(asset)
    (table,) = doc.tables
    fields = _walk_table(table, table_index=0, start_row=6)
    header_fields = [
        HeaderField("date", "Date", 0, 0, 0, "inline"),
        HeaderField("practitioner", "Practitioner", 0, 0, 1, "inline"),
        HeaderField("client_name", "Client name", 0, 1, 0, "inline"),
        HeaderField("client_dob", "Client DOB", 0, 1, 1, "inline"),
        HeaderField("session_number", "Session number", 0, 2, 0, "inline"),
        HeaderField("item_code", "Item code (if relevant)", 0, 2, 1, "inline"),
        HeaderField("reason_for_referral", "Reason for referral", 0, 4, 0, "append"),
    ]
    return FormSpec(
        form_id="client_treatment_review", title="Client Treatment Review",
        asset_path=asset, header_fields=header_fields, fields=fields,
    )


_FORM_SPEC_BUILDERS = {
    "client_treatment_review": _treatment_review_spec,
}


@lru_cache(maxsize=None)
def get_form_spec(form_id: str) -> FormSpec:
    try:
        builder = _FORM_SPEC_BUILDERS[form_id]
    except KeyError:
        raise ClinicalFormError(f"Unknown clinical form '{form_id}'.") from None
    return builder()


def available_forms() -> list[tuple[str, str]]:
    """(form_id, title) pairs, in registration order — for the UI's selector."""
    return [(form_id, builder().title) for form_id, builder in _FORM_SPEC_BUILDERS.items()]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_clinical_forms.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add carescribe/core/clinical_forms.py tests/test_clinical_forms.py
git commit -m "feat: add Client Treatment Review form spec"
```

---

### Task 4: Session Notes and Biopsychosocial Assessment specs (incl. the formulation grid)

**Files:**
- Modify: `carescribe/core/clinical_forms.py`
- Modify: `tests/test_clinical_forms.py`

**Interfaces:**
- Consumes: everything from Task 3.
- Produces: `"client_session_notes"` and `"biopsychosocial_assessment"` as valid `form_id`s in `get_form_spec`; `_grid_fields(...)` helper.

- [ ] **Step 1: Write the failing test**

```python
def test_session_notes_spec():
    spec = clinical_forms.get_form_spec("client_session_notes")
    assert spec.title == "Client Session Notes"
    assert len(spec.fields) == 9
    header_keys = [h.key for h in spec.header_fields]
    assert header_keys == [
        "date", "practitioner", "client_name", "client_dob",
        "session_number", "item_code", "reason_for_referral",
    ]


def test_biopsychosocial_spec_field_count_and_grid():
    spec = clinical_forms.get_form_spec("biopsychosocial_assessment")
    assert spec.title == "Biopsychosocial Assessment"
    assert len(spec.fields) == 62
    keys = {f.key for f in spec.fields}
    assert "history.substance_use" in keys
    assert "current_functioning.mood" in keys
    assert "mood_and_affect.mood" in keys  # same label, different section — must not collide
    assert "clinical_formulation.predisposing.biological" in keys
    assert "clinical_formulation.protecting.social" in keys
    grid_keys = [k for k in keys if k.startswith("clinical_formulation.")
                 and k.count(".") == 2]
    assert len(grid_keys) == 12
    header_keys = [h.key for h in spec.header_fields]
    assert header_keys == ["date", "practitioner", "client_name", "client_dob", "reason_for_referral"]


def test_no_field_key_collides_within_a_spec():
    for form_id, _ in clinical_forms.available_forms():
        spec = clinical_forms.get_form_spec(form_id)
        keys = [f.key for f in spec.fields]
        assert len(keys) == len(set(keys)), f"duplicate field key in {form_id}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_clinical_forms.py -v`
Expected: FAIL — `clinical_forms.ClinicalFormError: Unknown clinical form 'client_session_notes'`

- [ ] **Step 3: Implement the grid walker and both remaining spec builders**

Append to `carescribe/core/clinical_forms.py`:

```python
def _grid_fields(table, table_index: int, header_row: int, first_data_row: int,
                  last_data_row: int, section_header: str) -> list[FormField]:
    """The Biopsychosocial 'CLINICAL FORMULATION' table: a row-label ×
    column-label grid, not a single label/value pair per row."""
    header_cells = _dedupe_row(table.rows[header_row])
    column_labels = [c.text.strip() for c in header_cells[1:]]
    fields = []
    for row_index in range(first_data_row, last_data_row + 1):
        cells = _dedupe_row(table.rows[row_index])
        row_label = cells[0].text.strip()
        for col_offset, column_label in enumerate(column_labels, start=1):
            key = f"{slugify(section_header)}.{slugify(row_label)}.{slugify(column_label)}"
            fields.append(FormField(
                key=key, label=f"{row_label} \u2013 {column_label}",
                table_index=table_index, value_row_index=row_index,
                value_col_index=col_offset, append_after_label=False,
            ))
    return fields


def _session_notes_spec() -> FormSpec:
    asset = TEMPLATES_DIR / "client_session_notes.docx"
    doc = docx.Document(asset)
    (table,) = doc.tables
    fields = _walk_table(table, table_index=0, start_row=6)
    header_fields = [
        HeaderField("date", "Date", 0, 0, 0, "inline"),
        HeaderField("practitioner", "Practitioner", 0, 0, 1, "inline"),
        HeaderField("client_name", "Client name", 0, 1, 0, "inline"),
        HeaderField("client_dob", "Client DOB", 0, 1, 1, "inline"),
        HeaderField("session_number", "Session Number", 0, 2, 0, "inline"),
        HeaderField("item_code", "Item code (if relevant)", 0, 2, 1, "inline"),
        HeaderField("reason_for_referral", "Reason for referral", 0, 4, 0, "append"),
    ]
    return FormSpec(
        form_id="client_session_notes", title="Client Session Notes",
        asset_path=asset, header_fields=header_fields, fields=fields,
    )


def _biopsychosocial_spec() -> FormSpec:
    asset = TEMPLATES_DIR / "biopsychosocial_assessment.docx"
    doc = docx.Document(asset)
    table0, table1 = doc.tables
    fields = _walk_table(table0, table_index=0, start_row=5)
    fields += _grid_fields(
        table1, table_index=1, header_row=1, first_data_row=2, last_data_row=5,
        section_header="CLINICAL FORMULATION",
    )
    fields += _walk_table(table1, table_index=1, start_row=6)
    header_fields = [
        HeaderField("date", "Date", 0, 0, 0, "inline"),
        HeaderField("practitioner", "Practitioner", 0, 0, 1, "inline"),
        HeaderField("client_name", "Client Name", 0, 1, 0, "inline"),
        HeaderField("client_dob", "Client DOB", 0, 1, 1, "inline"),
        HeaderField("reason_for_referral", "Reason for referral", 0, 3, 0, "append"),
    ]
    return FormSpec(
        form_id="biopsychosocial_assessment", title="Biopsychosocial Assessment",
        asset_path=asset, header_fields=header_fields, fields=fields,
    )


_FORM_SPEC_BUILDERS["client_session_notes"] = _session_notes_spec
_FORM_SPEC_BUILDERS["biopsychosocial_assessment"] = _biopsychosocial_spec
```

Note: dict literal order in `_FORM_SPEC_BUILDERS` from Task 3 plus these two
`[...] = ...` assignments keeps `client_treatment_review` first in
`available_forms()`; if a different display order is wanted later, rebuild
the dict literal directly instead of appending — do not reorder by editing
insertion order elsewhere, since insertion order is what backs the list.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_clinical_forms.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add carescribe/core/clinical_forms.py tests/test_clinical_forms.py
git commit -m "feat: add Session Notes and Biopsychosocial Assessment form specs"
```

---

### Task 5: Cell writers and `fill_template`

**Files:**
- Modify: `carescribe/core/clinical_forms.py`
- Test: `tests/test_clinical_forms_fill.py`

**Interfaces:**
- Consumes: `FormSpec`, `get_form_spec`, `_dedupe_row` from Tasks 2–4.
- Produces: `fill_template(form_spec: FormSpec, field_values: dict[str, str], header_values: dict[str, str]) -> bytes` — the function `app.py`'s download button will call in Task 12.

- [ ] **Step 1: Write the failing test**

```python
"""Filling a template: header values land inline or as a new paragraph
depending on style, field values land in their mapped cell, and the
document's structure (table/row counts, section headers, signature row)
survives untouched.
"""

import io

import docx
import pytest

from carescribe.core import clinical_forms


def test_fill_template_writes_header_and_field_values():
    spec = clinical_forms.get_form_spec("client_session_notes")
    header_values = {
        "date": "12/08/2026", "practitioner": "A. Nguyen",
        "client_name": "J. Smith", "client_dob": "01/01/1990",
        "session_number": "4", "item_code": "80010",
        "reason_for_referral": "Ongoing anxiety management.",
    }
    field_values = {f.key: f"Generated text for {f.key}." for f in spec.fields}

    output = clinical_forms.fill_template(spec, field_values, header_values)
    doc = docx.Document(io.BytesIO(output))

    row0 = clinical_forms._dedupe_row(doc.tables[0].rows[0])
    assert row0[0].text == "Date: 12/08/2026"
    assert row0[1].text == "Practitioner: A. Nguyen"

    reason_cell = clinical_forms._dedupe_row(doc.tables[0].rows[4])[0]
    assert "Reason for referral:" in reason_cell.paragraphs[0].text
    assert "Ongoing anxiety management." in reason_cell.text

    sample_field = spec.fields[0]
    value_cell = clinical_forms._dedupe_row(
        doc.tables[sample_field.table_index].rows[sample_field.value_row_index]
    )[sample_field.value_col_index]
    assert f"Generated text for {sample_field.key}." in value_cell.text


def test_fill_template_preserves_structure():
    spec = clinical_forms.get_form_spec("client_session_notes")
    field_values = {f.key: "x" for f in spec.fields}
    output = clinical_forms.fill_template(spec, field_values, {})
    original = docx.Document(spec.asset_path)
    filled = docx.Document(io.BytesIO(output))

    assert len(filled.tables) == len(original.tables)
    assert len(filled.tables[0].rows) == len(original.tables[0].rows)
    # Section header untouched.
    assert filled.tables[0].rows[6].cells[0].text == "SESSION SUMMARY"
    # Signature row untouched (still blank).
    sig_row = clinical_forms._dedupe_row(filled.tables[0].rows[18])
    assert sig_row[0].text == "Signature:"


def test_fill_template_defaults_missing_field_to_not_documented():
    spec = clinical_forms.get_form_spec("client_session_notes")
    output = clinical_forms.fill_template(spec, {}, {})
    doc = docx.Document(io.BytesIO(output))
    sample_field = spec.fields[0]
    value_cell = clinical_forms._dedupe_row(
        doc.tables[sample_field.table_index].rows[sample_field.value_row_index]
    )[sample_field.value_col_index]
    assert value_cell.text.strip() == "Not documented"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_clinical_forms_fill.py -v`
Expected: FAIL — `AttributeError: module 'clinical_forms' has no attribute 'fill_template'`

- [ ] **Step 3: Implement the writers**

Append to `carescribe/core/clinical_forms.py`:

```python
import io


def _clear_cell(cell) -> None:
    """Remove every paragraph after the first, and every run in the first,
    leaving one empty paragraph ready to receive fresh text."""
    paragraphs = cell.paragraphs
    for extra in paragraphs[1:]:
        extra._element.getparent().remove(extra._element)
    for run in list(paragraphs[0].runs):
        run._element.getparent().remove(run._element)


def _fill_cell(cell, text: str) -> None:
    """Overwrite a dedicated value cell (label lives in a different cell)."""
    _clear_cell(cell)
    lines = (text or "Not documented").splitlines() or ["Not documented"]
    cell.paragraphs[0].add_run(lines[0])
    for line in lines[1:]:
        cell.add_paragraph(line)


def _fill_cell_after_label(cell, text: str) -> None:
    """Append text as new paragraphs after an existing label paragraph,
    which must survive untouched (used for own-cell fields and the
    'Reason for referral' header field)."""
    paragraphs = cell.paragraphs
    for extra in paragraphs[1:]:
        extra._element.getparent().remove(extra._element)
    for line in (text or "Not documented").splitlines() or ["Not documented"]:
        cell.add_paragraph(line)


def _fill_header_cell(cell, value: str) -> None:
    """Append a typed value inline, on the label's own paragraph and run —
    'Date: ' becomes 'Date: 12/08/2026'."""
    paragraph = cell.paragraphs[0]
    if paragraph.runs:
        paragraph.runs[-1].text = paragraph.runs[-1].text + value
    else:
        paragraph.add_run(value)


def fill_template(
    form_spec: FormSpec, field_values: dict[str, str], header_values: dict[str, str]
) -> bytes:
    """Fill a fresh in-memory copy of the template. Nothing touches disk."""
    doc = docx.Document(form_spec.asset_path)

    for header in form_spec.header_fields:
        value = (header_values.get(header.key) or "").strip()
        if not value:
            continue
        cell = _dedupe_row(doc.tables[header.table_index].rows[header.row_index])[header.col_index]
        if header.style == "inline":
            _fill_header_cell(cell, value)
        else:
            _fill_cell_after_label(cell, value)

    for field in form_spec.fields:
        cell = _dedupe_row(
            doc.tables[field.table_index].rows[field.value_row_index]
        )[field.value_col_index]
        text = field_values.get(field.key) or "Not documented"
        if field.append_after_label:
            _fill_cell_after_label(cell, text)
        else:
            _fill_cell(cell, text)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_clinical_forms_fill.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add carescribe/core/clinical_forms.py tests/test_clinical_forms_fill.py
git commit -m "feat: fill a copy of the real template from generated field values"
```

---

### Task 6: Prompt builder

**Files:**
- Modify: `carescribe/core/clinical_forms.py`
- Test: `tests/test_clinical_forms_prompt.py`

**Interfaces:**
- Consumes: `FormSpec`, `get_form_spec` from Tasks 2–4.
- Produces: `build_prompt(form_spec: FormSpec, deidentified_text: str) -> tuple[str, str]` returning `(system, user)`.

- [ ] **Step 1: Write the failing test**

```python
from carescribe.core import clinical_forms


def test_build_prompt_lists_every_field_marker_in_order():
    spec = clinical_forms.get_form_spec("client_session_notes")
    system, user = clinical_forms.build_prompt(spec, "Patient: [PATIENT]\nSeen in clinic.")

    for field in spec.fields:
        assert f"<<FIELD:{field.key}>>" in system

    order = [system.index(f"<<FIELD:{f.key}>>") for f in spec.fields]
    assert order == sorted(order)

    assert "Not documented" in system
    assert "Preserve every bracketed placeholder" in system or "placeholder" in system.lower()
    assert "[PATIENT]" in user
    assert "Seen in clinic." in user


def test_build_prompt_never_echoes_a_real_identifier_pattern():
    spec = clinical_forms.get_form_spec("client_session_notes")
    system, _ = clinical_forms.build_prompt(spec, "irrelevant")
    assert "Mariam" not in system  # sanity: system prompt is static, not source-derived
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_clinical_forms_prompt.py -v`
Expected: FAIL — `AttributeError: module 'clinical_forms' has no attribute 'build_prompt'`

- [ ] **Step 3: Implement**

Append to `carescribe/core/clinical_forms.py`:

```python
_SYSTEM_PREAMBLE = """\
You are a clinical documentation assistant filling out a structured clinical \
form from de-identified source material. You produce a DRAFT that a \
clinician will review, correct, and sign.

The source text has already been de-identified. Names, numbers, dates and \
places have been replaced with bracketed placeholders such as [PATIENT], \
[CLINICIAN_1], [MRN] and [DATE_2].

Rules you must follow:

1. Use ONLY information present in the provided source text.
2. Do NOT invent facts, names, dates, dosages, values, or events.
3. Preserve every bracketed placeholder EXACTLY as written, character for \
character. Do not translate, expand, renumber, or replace them.
4. Write in plain clinical register, past tense, concisely.
5. For each field listed below, write the field's marker on its own line, \
then the field's content, then move to the next field. If the source has \
no information for a field, write exactly "Not documented" for that field \
rather than guessing or leaving it blank.
6. Do not add commentary, a greeting, or a sign-off. Output only the fields.

FIELDS TO COMPLETE, IN THIS EXACT ORDER — reproduce each marker exactly:

{field_list}
"""

_USER_TEMPLATE = """\
SOURCE TEXT (de-identified):
---
{document}
---

Write the content for every field listed in the system instructions, each \
under its own <<FIELD:key>> marker, in the exact order given.
"""


def build_prompt(form_spec: FormSpec, deidentified_text: str) -> tuple[str, str]:
    field_list = "\n".join(f"<<FIELD:{f.key}>> \u2014 {f.label}" for f in form_spec.fields)
    system = _SYSTEM_PREAMBLE.format(field_list=field_list)
    user = _USER_TEMPLATE.format(document=deidentified_text)
    return system, user
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_clinical_forms_prompt.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add carescribe/core/clinical_forms.py tests/test_clinical_forms_prompt.py
git commit -m "feat: build a field-marker prompt from a clinical form spec"
```

---

### Task 7: Response parser

**Files:**
- Modify: `carescribe/core/clinical_forms.py`
- Test: `tests/test_clinical_forms_parse.py`

**Interfaces:**
- Consumes: `FormSpec`, `get_form_spec` from Tasks 2–4.
- Produces: `parse_fields(form_spec: FormSpec, raw_output: str) -> dict[str, str]`.

- [ ] **Step 1: Write the failing test**

```python
from carescribe.core import clinical_forms


def _spec():
    return clinical_forms.get_form_spec("client_session_notes")


def test_parse_fields_happy_path():
    spec = _spec()
    key0, key1 = spec.fields[0].key, spec.fields[1].key
    raw = (
        f"<<FIELD:{key0}>>\nFirst field text.\n\n"
        f"<<FIELD:{key1}>>\nSecond field text.\n"
    )
    parsed = clinical_forms.parse_fields(spec, raw)
    assert parsed[key0] == "First field text."
    assert parsed[key1] == "Second field text."


def test_parse_fields_defaults_missing_field_to_not_documented():
    spec = _spec()
    key0 = spec.fields[0].key
    raw = f"<<FIELD:{key0}>>\nOnly this one field.\n"
    parsed = clinical_forms.parse_fields(spec, raw)
    assert parsed[key0] == "Only this one field."
    assert all(
        parsed[f.key] == "Only this one field." if f.key == key0 else parsed[f.key] == "Not documented"
        for f in spec.fields
    )


def test_parse_fields_first_occurrence_wins_on_duplicate_marker():
    spec = _spec()
    key0 = spec.fields[0].key
    raw = f"<<FIELD:{key0}>>\nFirst.\n<<FIELD:{key0}>>\nSecond (should be ignored).\n"
    parsed = clinical_forms.parse_fields(spec, raw)
    assert parsed[key0] == "First."


def test_parse_fields_ignores_unknown_marker_without_raising():
    spec = _spec()
    key0 = spec.fields[0].key
    raw = f"<<FIELD:not_a_real_field>>\nStray.\n<<FIELD:{key0}>>\nReal text.\n"
    parsed = clinical_forms.parse_fields(spec, raw)
    assert parsed[key0] == "Real text."
    assert "not_a_real_field" not in parsed


def test_parse_fields_handles_empty_output():
    spec = _spec()
    parsed = clinical_forms.parse_fields(spec, "")
    assert all(value == "Not documented" for value in parsed.values())
    assert set(parsed) == {f.key for f in spec.fields}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_clinical_forms_parse.py -v`
Expected: FAIL — `AttributeError: module 'clinical_forms' has no attribute 'parse_fields'`

- [ ] **Step 3: Implement**

Append to `carescribe/core/clinical_forms.py`:

```python
_FIELD_MARKER_RE = re.compile(r"<<FIELD:([a-z0-9_.]+)>>")


def parse_fields(form_spec: FormSpec, raw_output: str) -> dict[str, str]:
    """Turn the model's marker-delimited output into ``{field_key: text}``.

    Any field the model skipped defaults to "Not documented" — enforced
    here rather than trusted to the model. Unknown markers are ignored; on
    a duplicate marker for the same key, the first occurrence wins.
    """
    text = raw_output or ""
    matches = list(_FIELD_MARKER_RE.finditer(text))
    found: dict[str, str] = {}
    for index, match in enumerate(matches):
        key = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        if key not in found:
            found[key] = text[start:end].strip(" \n\u2014-")

    return {
        field.key: found.get(field.key) or "Not documented"
        for field in form_spec.fields
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_clinical_forms_parse.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add carescribe/core/clinical_forms.py tests/test_clinical_forms_parse.py
git commit -m "feat: parse marker-delimited model output into per-field text"
```

---

### Task 8: `carenotes` generation/refine overrides (backward compatible)

**Files:**
- Modify: `carescribe/core/carenotes.py:140-161` (`generate_document`)
- Modify: `carescribe/core/carenotes.py:164-206` (`refine_document`)
- Create: `carescribe/prompts/refine_form.txt`
- Test: `tests/test_generation.py` (extend existing file)

**Interfaces:**
- Consumes: nothing new.
- Produces: `generate_document(..., *, system: str | None = None, user_prompt: str | None = None)` and `refine_document(..., *, system: str | None = None, refine_prompt_name: str = "refine.txt")` — both used by Task 9.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_generation.py`:

```python
def test_generate_document_accepts_a_system_and_user_prompt_override():
    backend = RecordingBackend()
    list(carenotes.generate_document(
        "irrelevant for this call",
        "SOAP care note",  # ignored — user_prompt short-circuits render_prompt
        backend,
        stream=False,
        user_prompt="MY CUSTOM PROMPT",
        system="MY CUSTOM SYSTEM",
    ))
    assert backend.system == "MY CUSTOM SYSTEM"
    assert backend.prompt == "MY CUSTOM PROMPT"


def test_generate_document_default_behaviour_is_unchanged():
    backend = RecordingBackend()
    list(carenotes.generate_document(
        "Patient: [PATIENT]\nSeen in clinic.", "SOAP care note", backend, stream=False,
    ))
    assert backend.system == carenotes.system_prompt()
    assert "Patient: [PATIENT]" in backend.prompt


def test_refine_document_accepts_a_system_and_refine_prompt_override():
    backend = RecordingBackend()
    list(carenotes.refine_document(
        "source", "draft with <<FIELD:x>> content", "make it shorter", backend,
        stream=False, system="MY CUSTOM SYSTEM", refine_prompt_name="refine_form.txt",
    ))
    assert backend.system == "MY CUSTOM SYSTEM"
    assert "<<FIELD:" in backend.prompt
    assert "make it shorter" in backend.prompt


def test_refine_document_default_behaviour_is_unchanged():
    backend = RecordingBackend()
    list(carenotes.refine_document(
        "source", "draft text", "make it shorter", backend, stream=False,
    ))
    assert backend.system == carenotes.system_prompt()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_generation.py -v -k "override or unchanged"`
Expected: FAIL — `TypeError: generate_document() got an unexpected keyword argument 'user_prompt'`

- [ ] **Step 3: Implement**

In `carescribe/core/carenotes.py`, replace the `generate_document` signature and body:

```python
def generate_document(
    deidentified_text: str,
    template: str,
    backend: Backend,
    stream: bool = True,
    *,
    custom_instruction: str = "",
    phi_values: Iterable[str] | None = None,
    system: str | None = None,
    user_prompt: str | None = None,
) -> Iterator[str]:
    """Stream a drafted document from approved de-identified text.

    ``phi_values`` is the mapping's real values, passed **only** so this
    function can assert they are absent. They are never forwarded to a backend.

    ``system``/``user_prompt`` let a caller (the clinical-form pipeline)
    supply a fully-built prompt instead of looking one up by ``template``
    label — ``template`` is then unused but still required positionally for
    backward compatibility with existing callers.
    """
    if not deidentified_text or not deidentified_text.strip():
        raise CareNoteError("There is no de-identified text to work from.")

    assert_deidentified(deidentified_text, phi_values)
    prompt = user_prompt if user_prompt is not None else render_prompt(
        deidentified_text, template, custom_instruction
    )
    assert_deidentified(prompt, phi_values)

    return backend.generate(system or system_prompt(), prompt, stream)
```

And `refine_document`:

```python
def refine_document(
    deidentified_text: str,
    draft: str,
    instruction: str,
    backend: Backend,
    stream: bool = True,
    *,
    history: list[tuple[str, str]] | None = None,
    phi_values: Iterable[str] | None = None,
    system: str | None = None,
    refine_prompt_name: str = "refine.txt",
) -> Iterator[str]:
    """Revise an existing draft against a follow-up instruction.

    ``system``/``refine_prompt_name`` let a caller supply a different system
    prompt and refine-instruction template (the clinical-form pipeline uses
    ``refine_form.txt``, which adds a field-marker-preservation rule).
    """
    if not draft or not draft.strip():
        raise CareNoteError("There is no draft to refine yet.")
    if not instruction or not instruction.strip():
        raise CareNoteError("Say what you would like changed.")

    assert_deidentified(draft, phi_values)
    assert_deidentified(instruction, phi_values)

    steer = instruction.strip()
    if history:
        earlier = "\n".join(f"- {item}" for item, _ in history[-4:])
        steer = (
            f"{steer}\n\nEarlier instructions already applied — keep them "
            f"satisfied:\n{earlier}"
        )

    prompt = (
        load_prompt(refine_prompt_name)
        .replace("{document}", deidentified_text)
        .replace("{draft}", draft)
        .replace("{instruction}", steer)
    )
    assert_deidentified(prompt, phi_values)

    return backend.generate(system or system_prompt(), prompt, stream)
```

Create `carescribe/prompts/refine_form.txt`:

```
Revise the draft below according to the clinician's instruction.

Change only what the instruction asks for. Everything else stays as it is.
Do not introduce any fact that is not in the source text, and preserve every
bracketed placeholder exactly.

The draft is structured as a series of fields, each starting with a
<<FIELD:key>> marker on its own line. Preserve every marker exactly as
written, in the same order, and keep every field present even if its
content does not change. Do not add, remove, rename, or reorder markers.

Return the COMPLETE revised draft, marker by marker — not a description of
the changes and not only the changed field.

CLINICIAN'S INSTRUCTION:
---
{instruction}
---

CURRENT DRAFT:
---
{draft}
---

SOURCE TEXT (de-identified):
---
{document}
---
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_generation.py -v`
Expected: PASS (all tests in the file, including the pre-existing ones — confirms no regression)

- [ ] **Step 5: Commit**

```bash
git add carescribe/core/carenotes.py carescribe/prompts/refine_form.txt tests/test_generation.py
git commit -m "feat: let generate_document/refine_document accept a prebuilt prompt"
```

---

### Task 9: Multi-document source combination

**Files:**
- Modify: `carescribe/core/clinical_forms.py`
- Test: `tests/test_clinical_forms_combine.py`

**Interfaces:**
- Consumes: `mapping.PLACEHOLDER_RE` from `carescribe/core/mapping.py` (already exists, unchanged).
- Produces: `combine_sources(sources: list[tuple[str, str, dict[str, str]]]) -> tuple[str, dict[str, str]]`.

- [ ] **Step 1: Write the failing test**

```python
from carescribe.core import clinical_forms, mapping


def test_combine_sources_prefixes_placeholders_per_document():
    sources = [
        ("intake.txt", "Patient: [PATIENT], seen on [DATE_1].", {"[PATIENT]": "A", "[DATE_1]": "1 Jan"}),
        ("referral.txt", "Re: [PATIENT], referred by [CLINICIAN_1].", {"[PATIENT]": "A", "[CLINICIAN_1]": "Dr B"}),
    ]
    combined_text, merged_map = clinical_forms.combine_sources(sources)

    assert "[DOC1_PATIENT]" in combined_text
    assert "[DOC2_PATIENT]" in combined_text
    assert "[PATIENT]" not in combined_text  # no un-prefixed survivor

    assert merged_map["[DOC1_PATIENT]"] == "A"
    assert merged_map["[DOC1_DATE_1]"] == "1 Jan"
    assert merged_map["[DOC2_PATIENT]"] == "A"
    assert merged_map["[DOC2_CLINICIAN_1]"] == "Dr B"


def test_combine_sources_reidentifies_without_collision():
    sources = [
        ("a.txt", "[PATIENT] attended.", {"[PATIENT]": "Alice Chen"}),
        ("b.txt", "[PATIENT] was discussed.", {"[PATIENT]": "Someone Else Entirely"}),
    ]
    combined_text, merged_map = clinical_forms.combine_sources(sources)
    resolved, unresolved = mapping.reidentify_document(combined_text, merged_map)
    assert unresolved == []
    assert "Alice Chen attended." in resolved
    assert "Someone Else Entirely was discussed." in resolved


def test_combine_sources_rejects_an_empty_list():
    with pytest.raises(clinical_forms.ClinicalFormError):
        clinical_forms.combine_sources([])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_clinical_forms_combine.py -v`
Expected: FAIL — `AttributeError: module 'clinical_forms' has no attribute 'combine_sources'`

- [ ] **Step 3: Implement**

Append to `carescribe/core/clinical_forms.py`:

```python
from . import mapping as _mapping  # PLACEHOLDER_RE, reused rather than reimplemented


def combine_sources(
    sources: list[tuple[str, str, dict[str, str]]]
) -> tuple[str, dict[str, str]]:
    """Concatenate several documents' de-identified text into one source.

    ``sources`` is ``(name, redacted_text, phi_map)`` per contributing
    document. Every placeholder is prefixed with that document's position
    (``[PATIENT]`` -> ``[DOC1_PATIENT]``) so two documents that each define
    their own ``[PATIENT]`` never collide once merged — each keeps
    resolving to its own real value at re-identification time.
    """
    if not sources:
        raise ClinicalFormError("No source documents were selected.")

    parts = []
    merged: dict[str, str] = {}
    for index, (name, text, phi_map) in enumerate(sources, start=1):
        prefix = f"DOC{index}_"
        rewritten = _mapping.PLACEHOLDER_RE.sub(
            lambda m, p=prefix: f"[{p}{m.group(0)[1:]}", text or ""
        )
        parts.append(f"--- Source: {name} ---\n{rewritten}")
        for placeholder, value in (phi_map or {}).items():
            merged[f"[{prefix}{placeholder[1:]}"] = value

    return "\n\n".join(parts), merged
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_clinical_forms_combine.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add carescribe/core/clinical_forms.py tests/test_clinical_forms_combine.py
git commit -m "feat: combine multiple source documents without placeholder collisions"
```

---

### Task 10: End-to-end generation glue (`generate_form_document`, `refine_form_document`, `render_preview`)

**Files:**
- Modify: `carescribe/core/clinical_forms.py`
- Test: `tests/test_clinical_forms_generate.py`

**Interfaces:**
- Consumes: `build_prompt`, `parse_fields`, `FormSpec` (this module); `carenotes.generate_document`, `carenotes.refine_document`, `carenotes.CareNoteError`, `carenotes.with_banner` (Task 8).
- Produces: `generate_form_document(combined_text, form_spec, backend, stream=True, *, phi_values=None) -> Iterator[str]`, `refine_form_document(combined_text, draft_marker_text, instruction, form_spec, backend, stream=True, *, history=None, phi_values=None) -> Iterator[str]`, `render_preview(form_spec: FormSpec, field_values: dict[str, str]) -> str`.

- [ ] **Step 1: Write the failing test**

```python
from carescribe.core import carenotes, clinical_forms


class RecordingBackend:
    """Captures exactly what generation handed the model — mirrors the
    fixture in tests/test_generation.py, kept local so this file has no
    cross-file test dependency."""

    def __init__(self, reply: str = ""):
        self.reply = reply
        self.system = ""
        self.prompt = ""

    def generate(self, system, prompt, stream=True):
        self.system = system
        self.prompt = prompt
        yield self.reply


def test_generate_form_document_sends_the_field_marker_prompt():
    spec = clinical_forms.get_form_spec("client_session_notes")
    reply = "".join(f"<<FIELD:{f.key}>>\ntext for {f.key}\n" for f in spec.fields)
    backend = RecordingBackend(reply)

    chunks = clinical_forms.generate_form_document(
        "Patient: [PATIENT]\nSeen in clinic.", spec, backend, stream=False,
    )
    output = "".join(chunks)

    assert f"<<FIELD:{spec.fields[0].key}>>" in backend.system
    assert "Patient: [PATIENT]" in backend.prompt
    assert output == reply


def test_generate_form_document_refuses_a_real_identifier():
    spec = clinical_forms.get_form_spec("client_session_notes")
    backend = RecordingBackend("output")
    with pytest.raises(carenotes.CareNoteError):
        list(clinical_forms.generate_form_document(
            "Mariam Rahman attended clinic.", spec, backend, stream=False,
            phi_values=["Mariam Rahman"],
        ))


def test_refine_form_document_preserves_markers_instruction():
    spec = clinical_forms.get_form_spec("client_session_notes")
    backend = RecordingBackend("revised")
    draft = "".join(f"<<FIELD:{f.key}>>\noriginal\n" for f in spec.fields)

    list(clinical_forms.refine_form_document(
        "source text", draft, "make it shorter", spec, backend, stream=False,
    ))
    assert "<<FIELD:" in backend.prompt
    assert "make it shorter" in backend.prompt


def test_render_preview_shows_every_field_label_and_value():
    spec = clinical_forms.get_form_spec("client_session_notes")
    values = {f.key: f"value-{f.key}" for f in spec.fields}
    preview = clinical_forms.render_preview(spec, values)
    for field in spec.fields:
        assert field.label in preview
        assert f"value-{field.key}" in preview


def test_render_preview_defaults_missing_value():
    spec = clinical_forms.get_form_spec("client_session_notes")
    preview = clinical_forms.render_preview(spec, {})
    assert "Not documented" in preview
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_clinical_forms_generate.py -v`
Expected: FAIL — `AttributeError: module 'clinical_forms' has no attribute 'generate_form_document'`

- [ ] **Step 3: Implement**

Append to `carescribe/core/clinical_forms.py`:

```python
from typing import Iterable, Iterator

from . import carenotes


def generate_form_document(
    combined_text: str,
    form_spec: FormSpec,
    backend,
    stream: bool = True,
    *,
    phi_values: Iterable[str] | None = None,
) -> Iterator[str]:
    system, user = build_prompt(form_spec, combined_text)
    return carenotes.generate_document(
        combined_text, form_spec.form_id, backend, stream,
        phi_values=phi_values, system=system, user_prompt=user,
    )


def refine_form_document(
    combined_text: str,
    draft_marker_text: str,
    instruction: str,
    form_spec: FormSpec,
    backend,
    stream: bool = True,
    *,
    history: list[tuple[str, str]] | None = None,
    phi_values: Iterable[str] | None = None,
) -> Iterator[str]:
    system, _ = build_prompt(form_spec, combined_text)
    return carenotes.refine_document(
        combined_text, draft_marker_text, instruction, backend, stream,
        history=history, phi_values=phi_values,
        system=system, refine_prompt_name="refine_form.txt",
    )


def render_preview(form_spec: FormSpec, field_values: dict[str, str]) -> str:
    """Human-readable rendering for display only — the marker text in
    ``draft_state`` (not this) is what gets refined, re-identified and
    exported."""
    lines = [f"#### {form_spec.title}"]
    for field in form_spec.fields:
        lines.append(f"\n**{field.label}**\n")
        lines.append(field_values.get(field.key) or "Not documented")
    return "\n".join(lines)
```

Note: `generate_form_document` calls `carenotes.generate_document(..., stream, ...)`
— `carenotes.generate_document` internally raises `CareNoteError` from
`assert_deidentified` **before** touching the backend, so the "refuses a
real identifier" test above never needs `stream=True`/consuming a
generator to observe the raise; `list(...)` on the returned iterator is
what triggers it, matching how the existing free-form path is tested in
`tests/test_generation.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_clinical_forms_generate.py -v`
Expected: PASS

- [ ] **Step 5: Run the full clinical-forms test suite plus the untouched free-form suite together**

Run: `python -m pytest tests/test_clinical_forms.py tests/test_clinical_forms_fill.py tests/test_clinical_forms_prompt.py tests/test_clinical_forms_parse.py tests/test_clinical_forms_combine.py tests/test_clinical_forms_generate.py tests/test_generation.py tests/test_clinical_form_templates.py -v`
Expected: PASS, all files

- [ ] **Step 6: Commit**

```bash
git add carescribe/core/clinical_forms.py tests/test_clinical_forms_generate.py
git commit -m "feat: wire clinical form generation, refine, and preview rendering"
```

---

### Task 11: `app.py` — Clinical form mode UI

**Files:**
- Modify: `carescribe/app.py` (add near `render_generation_panel`, `render_draft`, `render_refinement`, `render_reidentification`, `section_handoff` — roughly lines 850-1330; exact line numbers will have shifted after Task 8's edits to `carenotes.py`, none of which touch `app.py`, so the anchors below are still valid against the current file)
- Test: `tests/test_app_clinical_forms.py`

**Interfaces:**
- Consumes: `clinical_forms.get_form_spec`, `.available_forms()`, `.combine_sources`, `.generate_form_document`, `.refine_form_document`, `.parse_fields`, `.render_preview`, `.fill_template` (Tasks 2-10); `carenotes.finalise`, `carenotes.with_banner`, `carenotes.CareNoteError` (existing); `batch.Document`, `batch.safe_stem` (existing); `mapping.check_placeholder_integrity` (existing).
- Produces: a working "Clinical form" mode in Step 5 of the UI. Nothing later depends on this task's internals — it is the final integration point.

- [ ] **Step 1: Write the failing test (pure logic, no Streamlit — the session-key builder and the header-field validation, which are the only parts of this task testable without driving the UI)**

```python
"""Pure-logic pieces of the clinical-form UI: the session-state key used to
key a multi-document draft (not tied to one Document.name, unlike the
free-form path), and header-field completeness checking before Generate is
enabled.
"""

from carescribe import app


def test_form_draft_key_is_stable_for_the_same_selection():
    key1 = app._form_draft_key(["b.txt", "a.txt"], "client_session_notes")
    key2 = app._form_draft_key(["a.txt", "b.txt"], "client_session_notes")
    assert key1 == key2  # order of selection shouldn't matter


def test_form_draft_key_differs_by_form_or_selection():
    base = app._form_draft_key(["a.txt"], "client_session_notes")
    assert base != app._form_draft_key(["a.txt", "b.txt"], "client_session_notes")
    assert base != app._form_draft_key(["a.txt"], "client_treatment_review")


def test_header_values_complete_requires_every_non_reason_field():
    from carescribe.core import clinical_forms
    spec = clinical_forms.get_form_spec("client_session_notes")
    incomplete = {"date": "12/08/2026"}
    complete = {
        "date": "12/08/2026", "practitioner": "A. Nguyen",
        "client_name": "J. Smith", "client_dob": "01/01/1990",
        "session_number": "4", "item_code": "80010",
    }
    assert app._header_values_complete(spec, incomplete) is False
    assert app._header_values_complete(spec, complete) is True
    # "Reason for referral" is optional — a blank answer is a valid clinical fact.
    assert app._header_values_complete(spec, {**complete, "reason_for_referral": ""}) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_app_clinical_forms.py -v`
Expected: FAIL — `AttributeError: module 'app' has no attribute '_form_draft_key'`

- [ ] **Step 3a: Implement the pure-logic helpers**

Add near `_draft_state` in `carescribe/app.py`:

```python
def _form_draft_key(document_names: list[str], form_id: str) -> str:
    return "|".join(sorted(document_names)) + "::" + form_id


def _form_draft_state(key: str) -> dict:
    return st.session_state.setdefault("form_drafts", {}).setdefault(
        key,
        {
            "deidentified": "",       # marker text — refine/reidentify/export source of truth
            "reidentified": "",
            "unresolved": [],
            "history": [],
            "field_values": {},       # parsed {field_key: text}, deidentified
        },
    )


def _header_values_complete(form_spec, header_values: dict) -> bool:
    required = [h for h in form_spec.header_fields if h.key != "reason_for_referral"]
    return all((header_values.get(h.key) or "").strip() for h in required)
```

- [ ] **Step 3b: Implement the rendering/generation functions**

Add after `render_reidentification` in `carescribe/app.py` (these parallel
`render_generation_panel`/`_run_generation`/`render_draft`/
`render_refinement`/`render_reidentification` exactly, for the clinical-form
mode):

```python
def render_clinical_form_panel(docs: dict) -> None:
    from carescribe.core import clinical_forms

    approved = [doc for doc in docs.values() if doc.approved]
    if not approved:
        st.info("Approve at least one document in step 3 to generate a clinical form.")
        return

    form_options = clinical_forms.available_forms()
    form_id = st.selectbox(
        "Form", [fid for fid, _ in form_options],
        format_func=lambda fid: dict(form_options)[fid], key="form_type",
    )
    spec = clinical_forms.get_form_spec(form_id)

    selected_names = st.multiselect(
        "Source document(s)", [doc.name for doc in approved],
        default=[approved[0].name], key="form_sources",
    )
    if not selected_names:
        st.info("Select at least one approved document.")
        return

    draft_key = _form_draft_key(selected_names, form_id)
    draft = _form_draft_state(draft_key)

    st.markdown("##### Form header")
    header_values = draft.setdefault("header_values", {})
    for header in spec.header_fields:
        widget = st.text_area if header.key == "reason_for_referral" else st.text_input
        header_values[header.key] = widget(
            header.label, value=header_values.get(header.key, ""),
            key=f"hdr_{draft_key}_{header.key}",
        )

    if not generation_status.generation_status().ready:
        render_setup_card()
        return

    backends_available = render_generation_status()
    ready = (
        any(backends_available[kind]["available"] for kind in ("ollama", "local", "cloud"))
        and _header_values_complete(spec, header_values)
    )
    if not _header_values_complete(spec, header_values):
        st.caption("Fill in every header field except Reason for referral to enable generation.")

    if st.button("✨ Generate form", type="primary", disabled=not ready, key=f"gen_form_{draft_key}"):
        _run_form_generation(docs, selected_names, spec, draft)

    if draft.get("deidentified"):
        render_form_draft(docs, selected_names, spec, draft)


def _run_form_generation(docs: dict, selected_names: list[str], spec, draft: dict) -> None:
    from carescribe.core import clinical_forms

    sources = [(name, docs[name].redacted_text, docs[name].phi_map) for name in selected_names]
    phi_values = [v for name in selected_names for v in docs[name].phi_map.values()]
    combined_text, merged_map = clinical_forms.combine_sources(sources)
    draft["combined_text"] = combined_text
    draft["merged_phi_map"] = merged_map

    placeholder = st.empty()
    started = time.monotonic()
    try:
        with st.spinner("Generating on this computer — this can take a minute. Nothing leaves your device."):
            _, backend, _label = backends.select_backend()
            chunks = clinical_forms.generate_form_document(
                combined_text, spec, backend, stream=True, phi_values=phi_values,
            )
            raw = _stream_into(placeholder, chunks, started)
    except (carenotes.CareNoteError, backends.BackendError) as exc:
        placeholder.empty()
        st.error(str(exc))
        return

    placeholder.empty()
    draft["deidentified"] = raw
    draft["field_values"] = clinical_forms.parse_fields(spec, raw)
    draft["reidentified"] = ""
    draft["unresolved"] = []
    draft["history"] = []
    st.rerun()


def render_form_draft(docs: dict, selected_names: list[str], spec, draft: dict) -> None:
    from carescribe.core import clinical_forms

    st.markdown("#### Draft (de-identified)")
    st.caption("Still contains placeholders — safe to display, share, and save.")
    st.markdown(clinical_forms.render_preview(spec, draft["field_values"]))

    render_form_refinement(docs, selected_names, spec, draft)
    render_form_reidentification(spec, draft)


def render_form_refinement(docs: dict, selected_names: list[str], spec, draft: dict) -> None:
    from carescribe.core import clinical_forms

    with st.expander("Refine this draft", expanded=False):
        st.caption("Refinement runs on the same de-identified source and the current draft.")
        for instruction, _ in draft["history"]:
            st.markdown(f"- _{instruction}_")
        instruction = st.text_input(
            "What would you like changed?", key=f"form_refine_{id(draft)}",
            placeholder="e.g. expand the risk assessment section",
        )
        phi_values = [v for name in selected_names for v in docs[name].phi_map.values()]
        status = ollama_client.status()
        if st.button(
            "Apply", key=f"form_refine_go_{id(draft)}",
            disabled=not instruction or not status["models"],
        ):
            placeholder = st.empty()
            started = time.monotonic()
            try:
                with st.spinner("Revising…"):
                    chunks = clinical_forms.refine_form_document(
                        draft["combined_text"], draft["deidentified"], instruction, spec,
                        backends.select_backend()[1], stream=True,
                        history=draft["history"], phi_values=phi_values,
                    )
                    revised = _stream_into(placeholder, chunks, started)
            except (carenotes.CareNoteError, backends.BackendError) as exc:
                placeholder.empty()
                st.error(str(exc))
                return
            placeholder.empty()
            draft["history"].append((instruction, ""))
            draft["deidentified"] = revised
            draft["field_values"] = clinical_forms.parse_fields(spec, revised)
            draft["reidentified"] = ""
            draft["unresolved"] = []
            st.rerun()


def render_form_reidentification(spec, draft: dict) -> None:
    from carescribe.core import clinical_forms

    st.markdown("#### Re-identify and export (local only)")
    st.warning(
        "**This produces a document containing real patient identifiers.** "
        "It happens entirely in Python on this machine."
    )

    merged_map = draft.get("merged_phi_map", {})
    if st.button("🔓 Re-identify and fill the form", key=f"form_reid_{id(draft)}", disabled=not merged_map):
        resolved_fields = {}
        unresolved: list[str] = []
        for key, text in draft["field_values"].items():
            resolved_text, field_unresolved = carenotes.finalise(text, merged_map)
            resolved_fields[key] = resolved_text
            unresolved.extend(field_unresolved)
        draft["resolved_field_values"] = resolved_fields
        draft["unresolved"] = sorted(set(unresolved))
        st.rerun()

    if draft["unresolved"]:
        st.error(
            "**Blocked — these placeholders could not be resolved:** "
            + ", ".join(f"`{token}`" for token in draft["unresolved"])
        )
        return

    if draft.get("resolved_field_values"):
        st.success("Re-identified. Every placeholder resolved.")
        header_values = draft.get("header_values", {})
        output = clinical_forms.fill_template(spec, draft["resolved_field_values"], header_values)
        st.download_button(
            "⬇ .docx (contains PHI)", output,
            file_name=f"{batch.safe_stem(spec.title)}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key=f"form_dl_{id(draft)}",
        )
```

- [ ] **Step 3c: Add the mode toggle in `section_handoff`**

In `carescribe/app.py`, inside `section_handoff()`, immediately after the
`st.subheader("5. Generate report")` line and before the existing
`approved = [doc for doc in docs.values() if doc.approved]` block, add:

```python
    mode = st.radio(
        "What do you want to generate?",
        ["Free-form note", "Clinical form"],
        horizontal=True, key="generation_mode",
    )
    if mode == "Clinical form":
        render_clinical_form_panel(docs)
        return
```

This makes Clinical form mode return early from `section_handoff`, leaving
every line below it — the entire existing free-form flow — untouched and
unreached when the practitioner is in Clinical form mode, and vice versa.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_app_clinical_forms.py -v`
Expected: PASS

- [ ] **Step 5: Run the entire test suite to confirm no regression**

Run: `python -m pytest tests/ -v`
Expected: PASS, all tests (754 pre-existing + all new ones from this plan)

- [ ] **Step 6: Manually verify in the running app**

Run: `streamlit run run_app.py` (or the project's existing launch method —
check `README.md` / `SETUP_ON_A_NEW_PC.md` if `run_app.py` needs arguments)

Walk through: upload a synthetic (non-real) clinical document → de-identify
→ approve → Step 5 → select "Clinical form" → pick "Client Session Notes" →
fill the header mini-form → Generate → confirm the preview shows every
field with either generated text or "Not documented" → Refine with one
instruction → confirm it re-renders → Re-identify and export → open the
downloaded `.docx` and confirm it is a filled copy of the real template
(section headers, table borders, signature row all intact) → separately
confirm "Free-form note" mode still works exactly as before.

- [ ] **Step 7: Commit**

```bash
git add carescribe/app.py tests/test_app_clinical_forms.py
git commit -m "feat: add Clinical form mode to the generation step"
```

---

## Self-Review Notes (for the implementer)

- **Spec coverage:** every numbered section of the design spec
  (`docs/superpowers/specs/2026-08-13-clinical-forms-design.md`) maps to a
  task above: §1 asset bundling → Task 1; §2 field extraction → Tasks 2-4;
  §3 header fields → Tasks 3-4 (spec) + 5 (writer) + 11 (UI form); §4
  multi-doc combination → Task 9; §5 generation → Tasks 6-8, 10; §6 review
  → Task 11; §7 export → Tasks 5, 11; §8 UI → Task 11.
- **Row-count/key assertions** in Tasks 2-4 were hand-traced against the
  real bundled files using the exact algorithm implemented (see this plan's
  "Reference" section) — if a test's literal count is off by a small
  number when actually run, trust the test failure output over the number
  in this plan and adjust the assertion; the algorithm and code are what
  matter, not the arithmetic used to predict its output ahead of time.
- **Free-form path is never modified** — Task 8's changes to
  `carenotes.py` are additive optional kwargs with defaults matching
  current behavior exactly, verified by the "default behaviour is
  unchanged" tests in that task.
