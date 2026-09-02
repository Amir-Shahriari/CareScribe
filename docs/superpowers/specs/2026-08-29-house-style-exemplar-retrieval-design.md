# House-style exemplar retrieval — design

Status: implemented
Date: 2026-08-29

## Problem

Clinical-form generation (`core/clinical_forms.py`) fills a template from the
de-identified source with a fixed prompt. Every clinic's notes read the same.
The "your clinic's own paperwork" pitch wants generation to match *this
clinic's* wording — its house style — learned from its own past drafts.

This is the first retrieval-augmented piece (roadmap item C). It is scoped to
prove the loop — chunk, retrieve, augment — without a vector database or an
embedding model.

## Scope

In scope: store a clinic's de-identified form drafts; retrieve the closest past
values for each field being generated; inject them into that field's prompt
line as style examples. Local, offline, no new dependencies.

Out of scope: semantic embeddings (documented follow-up, pluggable behind
`exemplars.retrieve`); cross-field or whole-note retrieval; retrieval over
reference material or guidelines (roadmap item D); an agent that picks a
retrieval strategy (item E); editing or deleting stored exemplars from the UI.

## Architecture

### New module `core/exemplars.py`

- **Storage** — `<app_data_dir>/exemplars/<form_id>.jsonl`, one appended JSON
  object per line: `{"fields": {field_key: text, …}, "saved_at": "…"}`. Values
  are placeholder text only. Human-inspectable, no database.
- **`add_exemplar(form_id, field_values)`** — drops blank / `"Not documented"`
  values, then runs `deidentify.residual_scan` over the rest and **raises
  `ExemplarError` (writing nothing)** on any finding. An exemplar must be as
  clean as an approved output. `deidentify` is imported lazily so the retrieval
  path never loads the NLP stack.
- **`retrieve(form_id, field_key, query, k=3)`** — collects the stored,
  de-duplicated, non-empty values for that field and ranks them with a
  hand-rolled **Okapi BM25** (`_BM25`, standard library only) against the
  tokenised query. Returns the top `k` texts; if there are `≤ k`, returns them
  all unranked.
- **`retrieve_all(form_id, field_keys, query, k=3)`** — `{field_key: [texts]}`
  for every key that has at least one exemplar; empty dict when the store is
  empty.
- A per-form in-memory cache keyed on the file's mtime.

### `core/clinical_forms.py`

- `build_prompt(form_spec, deidentified_text, exemplars=None)` — each field's
  line in the system prompt is followed by indented
  `house-style example: <flattened text>` lines. A new rule 7 in the preamble:
  *"take STYLE from them only, never facts; every clinical fact must come from
  the source text."*
- `generate_form_document` / `refine_form_document` gain an `exemplars=`
  keyword, threaded straight into `build_prompt`. No change to
  `carenotes.generate_document` — the assembled prompt still passes through
  `assert_deidentified()`.

### `app.py`

- `_run_form_generation` calls `exemplars.retrieve_all(form_id, field keys,
  combined_text)` and passes the result to `generate_form_document`.
- `render_form_draft` gains a **★ Save as house-style example** button
  (`exemplars.add_exemplar(spec.form_id, draft["field_values"])` — the
  de-identified values, never the re-identified ones) and a caption showing how
  many are on file.

## Privacy

- Exemplars are placeholder text. `add_exemplar` refuses anything
  `residual_scan` flags.
- Retrieval is pure local Python (BM25). No socket, no model.
- The generation prompt still goes through `assert_deidentified()`; example
  text is de-identified by construction (it came from a prior draft's
  placeholder output).

## Testing

`tests/test_exemplars.py` (11 tests), storage in a monkeypatched temp dir:

- add → count → file on disk; cache refreshes when the file grows.
- `add_exemplar` refuses a value holding a phone-shaped identifier, and refuses
  an all-blank / all-"Not documented" record.
- `retrieve` ranks by BM25 overlap with the query, de-dupes, ignores records
  missing the field, and respects `k`.
- `retrieve_all` omits fields with no exemplars.
- `build_prompt` injects the example lines and the style-only caveat; without
  exemplars the prompt is unchanged.
- `generate_form_document` threads exemplars into the system prompt (recording
  backend).

Full suite: 986 passed, 1 skipped.

## Follow-ups (not blocking)

- Semantic retrieval behind the same `retrieve` signature (local
  sentence-transformers, or the Ollama embeddings endpoint when it is up).
- Weight the BM25 query by field label as well as source text.
- Manage (view / delete) stored exemplars in the UI.
