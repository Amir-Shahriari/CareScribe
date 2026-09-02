# Clinic reference library — design

Status: implemented
Date: 2026-08-29

## Problem

Roadmap item D: a clinic wants its formulary, care pathways, and local
protocols available while drafting. But a local model asked to fold a guideline
into a note **paraphrases** it, and a paraphrased dose, contraindication, or
referral criterion is a clinical-safety defect — categorically worse than a
style miss.

## Decision

Reference material is **retrieved for the clinician, not for the model.** The
review UI shows verbatim passages with their source; the clinician decides what
to use. The generation path is untouched — `reference_library` is not imported
by `clinical_forms` or `carenotes`, and a test enforces that. Prompt-injection
(with a hard "quote verbatim, never paraphrase" rule, off by default) is a
possible later addition; the retrieval core is the same either way.

## Scope

In scope: a local library of `.txt` / `.md` reference files; paragraph-level
BM25 search; a read-only "Relevant reference material" panel in the clinical-
form draft view; upload / remove in the panel.

Out of scope: feeding references into generation; PDF ingestion; per-field
retrieval; semantic search; versioning references.

## Architecture

### Shared `core/text_search.py` (new; refactor)

`BM25` and `tokenize` lifted out of `exemplars.py` (identical implementation)
so both retrieval features share one scorer. Added `query_tokens()` — tokenize
minus a short function-word list, applied to the **query side only**. On a tiny
corpus of short passages a stray "the" otherwise outranks a rare content word;
`exemplars.retrieve` now uses it too.

### New `core/reference_library.py`

- **Storage** — `<app_data_dir>/reference/*.{txt,md}`. Published clinical
  references, no patient data.
- **`_split_file`** — paragraph chunks (blank-line separated), each tagged with
  the nearest preceding Markdown heading; sub-`MIN_CHUNK_CHARS` fragments
  dropped, over-`MAX_CHUNK_CHARS` paragraphs split.
- **`search(query, k=5) -> list[ReferenceHit]`** — BM25 over
  `chunk.text + " " + chunk.heading`, `query_tokens` on the query, `score > 0`
  only. `ReferenceHit(source, heading, text, score)`.
- **`sources()`**, **`is_empty()`**, **`add_file(name, bytes)`** (UTF-8 + non-
  empty + parses to ≥1 chunk; `.txt`/`.md` only; de-duplicated filename),
  **`remove_file(name)`**.
- A cache keyed on the `(name, mtime, size)` tuple of the directory listing.

### `app.py`

- `_render_reference_uploader()` — an expander in the clinical-form panel:
  lists loaded files with passage counts and a Remove button, and an
  uploader + "Add to library".
- `_render_reference_panel(query)` — in `render_form_draft`, below the
  house-style row: runs `search(draft["combined_text"])` and renders the top
  passages as blockquotes with source labels. Read-only. A caption states it is
  not sent to the model.

## Privacy / safety

- Reference files are not patient data; the panel says so.
- Retrieval is local BM25 — no socket, no model.
- The model never receives reference text (guard test:
  `test_reference_library_is_not_wired_into_generation`).

## Testing

`tests/test_reference_library.py` (9 tests): empty library; add → sources /
not-empty; heading tracked onto the matching chunk; ranking by overlap and the
`score > 0` filter; upload validation (suffix, empty, non-UTF-8); duplicate
name suffixing; cache refresh on add; long-paragraph splitting bounded by
`MAX_CHUNK_CHARS`; the not-wired-into-generation guard.

`tests/test_exemplars.py` unchanged and still green after the `text_search`
refactor.

Full suite: 995 passed, 1 skipped.

## Follow-ups (not blocking)

- Optional prompt-injection mode: reference snippets in the prompt with a
  verbatim-quote-only rule and per-snippet citation markers, gated by a toggle
  that defaults off.
- Semantic retrieval behind `search`.
- PDF / DOCX reference ingestion (reuse `core/ingest.py`).
