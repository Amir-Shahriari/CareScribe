# Per-field retrieval planner — design

Status: implemented
Date: 2026-08-29

## Problem

Roadmap item E: "an agent that ranks chunking and retrieval strategies per
field being generated". Taken literally that needs multiple strategies to rank
and a reasoning step to rank them. Scoped honestly for the MVP it is: for each
template field, decide *whether* to pull exemplars / reference material, at
*what chunk granularity*, with *what query* — a lookup over a small, stable
vocabulary of field labels, not a reasoning problem.

## Decision

Ship a **deterministic `RuleBasedPlanner`** behind a `RetrievalPlanner`
protocol. An LLM-driven planner would implement the same protocol and return
the same `{field_key: RetrievalPlan}` — that is the seam, mirroring
`CloudBackend`. The planner is kept out of generation (guard test): it decides
what to *fetch*; reference results still go only to the clinician's panel.

## Scope

In scope: `core/retrieval_planner.py`; three chunk granularities in
`reference_library` (`section` / `paragraph` / `sentence`); per-field exemplar
queries and a per-field, right-granularity reference panel in the app.

Out of scope: an LLM planner; learned strategy selection; re-ranking; feeding
reference text into the model.

## Architecture

### `core/text_search.py`

`BM25` / `tokenize` were already shared here (from the exemplar work). No
change beyond what item D added (`query_tokens`).

### `core/reference_library.py`

`search(query, k=5, granularity="paragraph")`. `_split_file` gained a
`granularity`:

- `section` — every paragraph under one Markdown heading, joined (bounded).
- `paragraph` — one blank-line block (unchanged default).
- `sentence` — one sentence (`_SENTENCE_RE`), for fields that need a tight
  quote such as a dose.

`_CACHE` is now keyed by granularity. `sources()` / `is_empty()` still report
paragraph counts.

### `core/retrieval_planner.py` (new)

- `RetrievalPlan(field_key, field_label, want_exemplars, want_reference,
  granularity, query)`.
- `RuleBasedPlanner.plan(form_spec, deidentified_text)` — for each field:
  - `want_reference` / `granularity` from `_REFERENCE_RULES`, a first-match
    keyword taxonomy over the lowercased field label (`dose|medication|…` →
    sentence; `diagnos|prognos|formulation|criteria` → section;
    `risk|suicid|safeguard|…` → paragraph; `referral|discharge|relapse|…` →
    paragraph; `intervention|treatment plan|therap` → paragraph). No match →
    no reference retrieval.
  - `query` = the field's label tokens + the salient (>3-char, first-seen,
    stopword-filtered, capped) words of the source text.
  - `want_exemplars` = `getattr(field, "kind", "narrative") == "narrative"` —
    True for every current form field; the getattr keeps the seam.
- `plan(form_spec, text, planner=None)` — module-level convenience.

### `app.py`

- `_run_form_generation` builds a plan and retrieves exemplars **per field**
  with that field's planned query (replacing the whole-note
  `exemplars.retrieve_all`).
- `_render_reference_panel(spec, query)` builds a plan, runs
  `reference_library.search` per reference-wanting field at its planned
  granularity, de-duplicates passages across fields, and renders them grouped
  by field label. Still read-only, still not sent to the model.

## Testing

`tests/test_retrieval_planner.py` (8): medication field → sentence; mood field
→ no reference; risk field → paragraph; diagnoses field → section; plan covers
every field and wants exemplars for all; query = label + salient source terms
minus stopwords; planner is pluggable; not wired into generation.

`tests/test_reference_library.py` (+3): section granularity merges a heading's
paragraphs; sentence granularity yields single sentences; an invalid
granularity raises.

Full suite: 1006 passed, 1 skipped.

## Follow-ups (not blocking)

- An `LLMPlanner` implementing `RetrievalPlanner`, once there is evidence the
  rule taxonomy misses real cases.
- Feed the plan's `want_reference` fields a verbatim-quote-only reference block
  in the prompt, behind an off-by-default toggle.
- Log which plan produced which retrieval, to tune `_REFERENCE_RULES` from use.
