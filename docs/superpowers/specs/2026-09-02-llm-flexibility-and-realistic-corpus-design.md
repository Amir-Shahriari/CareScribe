# LLM backend flexibility + realistic test corpus + full-pipeline validation

Date: 2026-09-02
Status: approved (in-chat, subagent-driven execution per user's working-style)

## Problem

Two related complaints:

1. Generation quality/flexibility is bad in practice. Root causes found by
   inspection: `OllamaBackend` (`carescribe/core/carenotes.py`) defaults
   `temperature=0.2` while `LocalGGUFBackend` deliberately uses `0.0` — the
   docstring on the latter explains 0.2 caused the bundled model to invent
   unsupported clinical details. Ollama's `default_model()`
   (`carescribe/core/ollama_client.py`) only recognises a hardcoded
   `PREFERRED_MODELS` list (`llama3.1:8b`, `qwen2.5:7b`, ...) — a larger
   installed model (e.g. Qwen2.5-32B, the user's actual target per hardware)
   is not guaranteed to be selected. There is no in-app way to choose
   backend/model at all: `backends.select_backend()` is always called with no
   `prefer` anywhere in `app.py`, so switching requires an env var + restart.
2. The document corpora (`sample_documents/` — 4 synthetic .docx for manual
   generation testing; `stress_corpus/` — 10 synthetic .txt + answer key for
   automated redaction regression) are thinner and cleaner than real clinical
   documents. The existing `pytest tests -q` suite is already 100% green
   (1045 passed / 1 skipped) against the current corpus — that bar needs to
   be re-earned against a larger, harder, more realistic set before it means
   anything.

## Goals

- Any locally-installed Ollama model is selectable and usable, not just ones
  in a hardcoded guess list; the app remembers the choice.
- Temperature is consistently 0.0 by default across all three backends
  (documented rationale already exists — just wasn't applied everywhere),
  overridable from the same settings surface.
- A Settings screen in the app: pick backend, pick Ollama model from what's
  actually installed, adjust temperature, and (secondary) configure cloud
  provider/base URL/model — API key entered per-session (never written to
  disk, matching the existing "never stored, logged, or bundled" guarantee
  in `cloud_client.py`).
- A materially larger, harder, more realistic set of dummy clinical
  documents — both for the automated redaction regression
  (`stress_corpus/`, answer-key-driven) and for manual/full-pipeline
  generation testing (`sample_documents/`).
- Run the full pipeline (de-identify → approve → combine → generate each
  form type) against the expanded `sample_documents/` set end to end,
  through a real backend, and fix whatever it surfaces.
- `pytest tests -q` at 100% pass against the expanded corpus — this is the
  concrete meaning of "the test is 100% accurate." Any redaction miss or
  over-redaction found on a new document is a real bug to fix, not a corpus
  problem to work around.

## Non-goals

- No new named cloud providers beyond the existing Anthropic + OpenAI-
  compatible wire shapes (user confirmed: focus is local, cloud stays as-is
  with just a UI instead of env-vars-only).
- No rebuild of the backend abstraction (ladder + Protocol stays); this is
  an extension, not a rewrite.
- No embeddings/vector DB work (out of scope per existing roadmap memory).

## Design

### A. Backend/settings flexibility

- New `carescribe/core/settings.py`: `load_settings()` / `save_settings()`
  against `app_data_dir() / "settings.json"`. Persisted fields: backend kind,
  chosen Ollama model, temperature (per backend or one shared value — keep it
  one shared value, YAGNI), cloud provider/base_url/model. **Never** persist
  the API key — that stays session-only (`st.session_state`), matching the
  existing security posture.
- `backends.select_backend()` already accepts `prefer`; extend its signature
  to also accept an explicit `model` and `temperature` override, threaded
  down to `OllamaBackend(model, temperature=...)`. Remove the
  `PREFERRED_MODELS` guessing from the default path — it's superseded by
  explicit user choice from `list_models()`. Keep `default_model()` as a
  fallback only for the very first run before any settings exist.
- Fix `OllamaBackend.__init__`'s `temperature` default from `0.2` to `0.0`.
- Settings UI: a new section in `app.py` (or `carescribe/ui/components.py`
  following the existing `_render_generation_model()` pattern) — backend
  radio, Ollama model select box populated from `ollama_client.list_models()`,
  temperature number input, cloud fields. Save button writes non-secret
  fields via `settings.save_settings()`; loaded at app startup and passed as
  `prefer=`/`model=`/`temperature=` into `select_backend()`.

### B. Realistic document corpus

- Expand `stress_corpus/`: add new synthetic `.txt` documents shaped like
  real referrals/discharge summaries/assessments that are longer, messier,
  and more structurally varied than the current 10 (multi-page, inconsistent
  headers, mixed date formats, nested tables rendered as text, abbreviations,
  multiple identifiers per person, letterhead noise). Each gets a
  `must_redact` / `must_preserve` entry in `answer_key.json`, same pattern as
  today — this is a data change, no test code changes needed
  (`tests/test_stress_corpus.py` already iterates the answer key).
- Expand `sample_documents/`: add more `.docx` scenarios beyond the current
  4 (e.g. discharge summary, risk assessment, case conference note, GP
  letter reply) with the same "fabricated but realistically messy" shape —
  mixed narrative/table/grid layout — so the full generation pipeline gets
  exercised against more field-coverage variety.
- Everything fabricated, same safety rules already documented in both
  READMEs (no real PHI, ever).

### C. Full-pipeline validation loop

- Run `pytest tests -q` after each corpus addition; any failure is a real
  redaction bug — fix it in `carescribe/core/deidentify.py` (or wherever it
  traces to) and re-run, not a license to weaken the answer key.
- Separately, drive the full app pipeline (ingest → de-identify → approve →
  combine sources → generate each of the 3 form types) against the expanded
  `sample_documents/` set through whatever backend is available in this
  environment (Ollama if up, else bundled local GGUF), and inspect the
  generated drafts for obviously wrong/hallucinated content given the
  0.0-temperature fix above.
- Iterate: dispatch → review results → fix or add next task → re-dispatch,
  until `pytest tests -q` is 100% green against the full expanded corpus and
  a full-pipeline generation run completes cleanly on every new sample
  document.

## Success criteria

- `pytest tests -q` — 100% pass, corpus at least ~2x current size on both
  `stress_corpus/` and `sample_documents/`.
- Settings panel lets you pick any installed Ollama model and it's actually
  used (verified by a test asserting `select_backend` honours an explicit
  model override).
- `OllamaBackend` temperature default is `0.0`.
- A full pipeline run (de-id → generate) completes without error on every
  document in the expanded `sample_documents/`.
- `graphify update .` run after all code changes.
