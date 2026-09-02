# Local clinical LLM fine-tune — design

**Date:** 2026-09-01
**Status:** Approved for implementation (Approach 1)
**Owner:** CareScribe generation subsystem

---

## 1. Goal

Ship a fine-tuned ~3–4B language model, as a quantised GGUF, that CareScribe
bundles in place of the stock `Qwen2.5-3B-Instruct-Q4_K_M.gguf` for clinical
form / report generation. The model must:

- run acceptably on a **16 GB RAM laptop, CPU-only** (Q4 GGUF, ~2–3 GB), with an
  optional larger variant that downloads when a GPU is detected;
- be **redistributable in a commercial standalone app** — no research-only
  licence, no per-seat attribution burden;
- beat the stock base model, on a held-out synthetic eval set, on all four of:
  1. **Format adherence** — every required field of a SOAP / care-plan /
     progress-note / uploaded-template form is present, correctly placed, with
     no preamble or trailing commentary.
  2. **Faithfulness** — no clinical claim the source note does not support; "Not
     documented" where the source is silent.
  3. **House style** — output matches a clinic's writing conventions when
     conditioned on a style exemplar, reducing reliance on long retrieval
     prompts.
  4. **Placeholder integrity** — every `[NAME_1]` / `[DATE_3]` placeholder
     reproduced exactly; none dropped, renamed, split, or invented.

Non-goals: fine-tuning the de-identification model (regex + spaCy/Presidio stay
as they are); clinical Q&A / knowledge tasks; any change to the privacy
contract (`assert_deidentified`, the loopback pin, the no-egress tests).

---

## 2. Constraints inherited from CareScribe

| Constraint | Consequence for this work |
|---|---|
| No real PHI may be used, stored, or transmitted | Training data is **100% synthetic**. No MIMIC, no licensed notes. |
| The app opens no socket during de-id; generation only reaches `127.0.0.1:11434` | Training code lives **outside** the `carescribe/` package (new top-level `finetune/`), so `test_desktop_packaging.py` / `NoEgress` / the `environ` source scans never see it and it is never frozen into the app. |
| The model never sees a real identifier; re-identification is Python-only | The fine-tune is trained on **placeholdered** input (real `[TOKEN_n]` shapes) and must emit placeholders verbatim. Reuses `carescribe.core.mapping.check_placeholder_integrity`. |
| Everything written is de-identified; `residual_scan()` gates every write | The eval harness runs the real `residual_scan()` over every generated draft; tripping it is a hard eval failure. |
| Reviewer can verify claims the code makes | The model ships with a **model card** (base, licence, data manifest hash, eval numbers, date) surfaced in the About box. |
| Temperature pinned at 0 for local generation | All training, eval, and inference use greedy decoding. No sampling params to tune. |

---

## 3. Approach (selected)

**Structured-synthetic SFT + QLoRA on a cleanly-licensed 3–4B base, with an
automated four-metric eval and a GGUF drop-in.**

The core idea: generate each training example from **structured encounter
facts**, not from prose. Because the facts are ground truth, faithfulness,
format, and placeholder integrity are *checkable at data-build time* — a sample
that fails validation is discarded, never trained on. This mirrors the rest of
CareScribe: properties the pipeline is structured to make checkable, not just
claim.

Rejected alternatives (see brainstorm): pure constrained-decoding with no
fine-tune (doesn't move faithfulness or style; long prompts are slow on a light
laptop) — but its **GBNF grammar is adopted in Phase 5** as a belt-and-braces
guarantee on top of the fine-tune. Fine-tuning a 1–1.5B model for fully-local
training was rejected because sub-2B quality on multi-section faithful drafting
is where hallucination risk concentrates, and the 16 GB + optional-GPU floor
does not require going that small.

---

## 4. Base model

Phase 0 bake-off, decided by the Phase 4 eval harness on a 500-sample dev set
after a short (≤1 epoch) LoRA on each:

| Candidate | Params | Licence | Notes |
|---|---|---|---|
| **Phi-3.5-mini-instruct** (primary) | 3.8B | MIT | No attribution burden; 128k context; strong format-following. |
| Granite 3.1 3B Instruct (fallback) | 3.2B | Apache-2.0 | Enterprise-tuned; clean licence. |
| Qwen2.5-3B-Instruct (reference only) | 3.1B | Qwen research licence | **Not shippable commercially.** Kept only as the quality bar to beat. |

Optional GPU variant: the same recipe applied to **Phi-3.5-mini at Q5_K_M**, or
a 7–8B Apache/MIT model (e.g. Qwen2.5-7B is Apache-2.0), offered by
`model_setup` as a download when a CUDA/Metal device is detected.

---

## 5. Architecture — five workstreams

```
finetune/
├── README.md                     # how to run each phase, and the GPU-run cost
├── pyproject.toml                # isolated deps: torch, peft, trl, transformers,
│                                 #   datasets, llama-cpp-python (convert only)
├── config/
│   ├── models.yaml               # base-model candidates + HF ids + prompt template
│   ├── datagen.yaml              # scenario mix, corpus sizes, seed
│   └── train.yaml                # QLoRA hyperparams, per candidate
├── datagen/          # WORKSTREAM A — synthetic encounters -> source notes
│   ├── schema.py                 # EncounterFacts (pydantic), FormType enum
│   ├── sampler.py                # samples EncounterFacts from weighted templates
│   ├── vignettes/                # hand-authored, non-PHI scenario skeletons
│   ├── render_note.py            # facts -> messy free-text source note
│   ├── identifiers.py            # inject fake names / NHS nos / dates / postcodes
│   └── generator_backend.py      # pluggable: ollama | openai-compatible | template
├── assemble/         # WORKSTREAM B — build SFT pairs
│   ├── deidentify_notes.py       # run REAL carescribe de-id over synthetic notes
│   ├── build_target.py           # facts + FormSpec -> ideal filled form
│   ├── validators.py             # format / faithfulness / placeholder / residual
│   ├── pairs.py                  # -> chat JSONL, stratified train/dev/test split
│   └── manifest.py               # content-hash the dataset for provenance
├── train/            # WORKSTREAM C — QLoRA + GGUF
│   ├── sft.py                    # trl SFTTrainer, 4-bit base + LoRA
│   ├── dpo.py                    # OPTIONAL phase 2: preference tuning
│   ├── merge_and_convert.sh      # merge LoRA -> HF -> gguf -> quantize Q4_K_M
│   └── modelcard.py              # emit MODEL_CARD.md from config + eval report
├── eval/             # WORKSTREAM D — the four metrics
│   ├── metrics.py                # format, faithfulness, placeholder, style
│   ├── run_eval.py               # base vs tuned, on test split + regression set
│   ├── regression.py             # existing tests/ fixtures + stress_corpus
│   └── report.py                 # EVAL_REPORT.md + JSON
└── integrate/        # WORKSTREAM E — into the app
    ├── grammar.py                # GBNF per FormType for constrained decoding
    ├── prompt_template.py        # SHARED constant, imported by carescribe too
    └── notes.md                  # About-box wiring, model_setup GPU variant
```

**Dependency order:** A → B → (C ∥ D) → E. D needs `schema.py` and
`validators.py` from A/B. E needs a finished GGUF from C.

---

## 6. Workstream A — synthetic data generation

### A.1 `EncounterFacts` schema (`datagen/schema.py`)

A pydantic model that is the single source of truth for a synthetic encounter:

- `specialty`, `encounter_type` (new / follow-up / discharge / handover / crisis)
- `demographics` — synthetic age band, sex, occupation (no identifiers here;
  identifiers are injected later at render time)
- `presenting_complaint`, `history` (list of `HistoryItem`), `pmh`, `meds`
  (list of `Medication`), `allergies`
- `examination` (list of `Finding` with `system`, `finding`, `value?`)
- `investigations` (list of `Result` with `test`, `value`, `flag?`)
- `impression` (list of `str`), `plan` (list of `PlanItem`)
- `follow_up` (interval or `None`)
- `documented_gaps` — a sampled set of fields deliberately left absent, so the
  target can legitimately say "Not documented" and the model learns to.

Every leaf is either a concrete value or explicitly `None`. This is what makes
downstream validation exact.

### A.2 Scenario sampler (`datagen/sampler.py`)

- `vignettes/` holds ~40–60 hand-authored skeletons (per specialty:
  cardiology, respiratory, community mental health, general practice, elderly
  care, …) — realistic clinical shapes with placeholders for the sampler to
  fill (drug doses from a small formulary table, plausible vital ranges,
  investigation panels).
- `datagen.yaml` weights the specialty / encounter-type / messiness mix and
  fixes a seed. Target corpus: **12k train / 1.5k dev / 1.5k test** pairs after
  validation rejection (generate ~1.7× and discard failures).

### A.3 Source-note renderer (`datagen/render_note.py`)

`EncounterFacts -> str` (a realistic, *messy* clinician note — the INPUT side):

- Style axis: terse ward note · dictated letter · abbreviation-heavy · headed
  proforma · near-continuous prose.
- Noise axis: OCR-style substitutions, inconsistent casing, run-together lines,
  missing section headers — sampled per example.
- Uses `generator_backend` for the prose; the backend is pluggable:
  - `ollama` — local Ollama daemon, any instruct model the user has pulled
    (7–8B recommended for data quality);
  - `openai-compatible` — a one-time, opt-in call to any OpenAI-style endpoint
    (documented as the only place data leaves the box; the data is synthetic and
    contains only fake identifiers, so this is acceptable — but it is **off by
    default**);
  - `template` — a deterministic, model-free renderer that stitches the facts
    into prose with surface variation. Lower diversity, zero cost, no
    dependency; used for CI and for a first end-to-end dry run.
- After rendering, `identifiers.py` injects fake `[real-looking]` identifiers
  (Faker-generated UK names, NHS numbers with valid check digits, dates,
  postcodes, MRNs, provider initials) at natural positions, and records their
  spans as an answer key.

### A.4 Why the injected-then-de-identified round trip matters

The model must be trained on **exactly** the text distribution it sees in
production: output of `carescribe` de-identification, with real placeholder
tokens. Generating clean placeholdered text directly would miss de-id's
artefacts (partial redactions, `[LOCATION]`, context-anchored MRN behaviour).
So: inject real identifiers → run real de-id → train on the result.

---

## 7. Workstream B — assembling SFT pairs

### B.1 De-identify (`assemble/deidentify_notes.py`)

Import `carescribe.core.deidentify` / `batch` and run the real analyse path over
each synthetic note. Output: `(placeholdered_text, mapping, spans)`. No app, no
Streamlit, no socket. A test asserts this module imports nothing that opens one.

### B.2 Build the ideal target (`assemble/build_target.py`)

`EncounterFacts + FormType (+ optional style exemplar) -> str` (the ASSISTANT
side). Two-stage:

1. **Deterministic scaffold** — map facts into the exact heading structure of
   the form (`carescribe.prompts.carenotes_prompt` for SOAP / care-plan /
   progress; `carescribe.core.clinical_forms.get_form_spec` for uploaded
   templates). Fields whose facts are in `documented_gaps` render as "Not
   documented." This stage alone guarantees format + faithfulness + placeholder
   integrity.
2. **Optional prose polish** — pass the scaffold through `generator_backend`
   with an instruction to improve fluency *without adding or removing
   information*, then **re-validate** (B.3). If polish fails validation, keep
   the scaffold. A configurable fraction of the corpus skips polish entirely so
   the model still sees crisp structured output.

Style conditioning: for ~30% of pairs, pick a synthetic clinic style guide from
`datagen/vignettes/styles/`, prepend it to the user turn, and render the target
in that style (section order, abbreviation set, sign-off form).

### B.3 Validators (`assemble/validators.py`) — reused by eval

| Validator | Method | Pass condition |
|---|---|---|
| `format_score` | Parse output headings against the `FormType` spec | All required fields present & correctly ordered; no text before the first heading or after the last field |
| `faithfulness` | Each factual span in the draft must align to an `EncounterFacts` leaf; each `documented_gaps` field must read "Not documented"; no numeric value absent from facts | Zero unsupported claims, zero contradicted values |
| `placeholder_integrity` | `carescribe.core.mapping.check_placeholder_integrity(draft, mapping.keys())` | Empty issue list |
| `residual_clean` | `carescribe.core.deidentify.residual_scan(draft)` | No hits |

A pair is kept only if all four pass on the (scaffold or polished) target.

### B.4 Pair format (`assemble/pairs.py`)

Chat JSONL, one object per line:

```json
{
  "messages": [
    {"role": "system", "content": "<carenotes_prompt _SHARED_RULES + form system prompt>"},
    {"role": "user",   "content": "<optional style exemplar>\n<USER_TEMPLATE with placeholdered note + instruction>"},
    {"role": "assistant", "content": "<validated target form>"}
  ],
  "meta": {"form_type": "...", "specialty": "...", "styled": true, "polished": false}
}
```

The system/user construction imports the **real** `carescribe.prompts.
carenotes_prompt` strings so training and production prompts cannot drift.
Split is stratified on `form_type` × `specialty` × `styled`.

### B.5 Manifest (`assemble/manifest.py`)

SHA-256 over the sorted pair list → `dataset_manifest.json` (counts per stratum,
generator backend + model, seed, `carescribe` git SHA). The hash goes in the
model card.

---

## 8. Workstream C — training

### C.1 SFT (`train/sft.py`)

- `trl` `SFTTrainer`, 4-bit NF4 base (`bitsandbytes`), LoRA r=16 α=32 dropout
  0.05 on attention + MLP projections.
- Chat template = the base model's own (from `models.yaml`); loss masked to
  assistant tokens.
- 2–3 epochs, cosine schedule, LR 1e-4, effective batch 16 via grad
  accumulation, `bf16`, packing on, max-seq 4096.
- Fits a single 24 GB GPU (RTX 4090 / A10 / L4). ~1–3 h for 12k pairs.
- Checkpoints + `trainer_state.json` saved; eval-on-dev every N steps calls the
  Phase D metrics, not just loss.

### C.2 Optional DPO (`train/dpo.py`) — phase 2

For each kept pair, synthesise a **rejected** variant: drop a required section,
inject one unsupported finding, or corrupt one placeholder. `trl` `DPOTrainer`
on (chosen, rejected) sharpens faithfulness + integrity beyond what SFT gives.
Gated on Phase 1 eval showing residual failures worth the extra run.

### C.3 Merge & convert (`train/merge_and_convert.sh`)

`peft` merge → HF fp16 → `llama.cpp/convert_hf_to_gguf.py` → `llama-quantize`
to `Q4_K_M` (and `Q5_K_M` for the GPU variant). Output:
`carescribe-clinical-<base>-v<N>.Q4_K_M.gguf`.

### C.4 Model card (`train/modelcard.py`)

`MODEL_CARD.md`: base model + licence, LoRA config, `dataset_manifest.json`
hash, generator backend, eval report table (tuned vs base vs Qwen reference),
build date, `carescribe` SHA, known limitations (synthetic-data ceiling,
specialty coverage). Shipped in the app.

---

## 9. Workstream D — evaluation

### D.1 Metrics (`eval/metrics.py`)

The four B.3 validators, plus:

- `latency` — median tok/s and seconds-to-draft via `llama-cpp-python` on a
  pinned CPU thread count, on a reference machine profile.
- `style_match` — when a pair is styled: embedding cosine + section-order edit
  distance between draft and target.

### D.2 Runner (`eval/run_eval.py`)

Runs base and tuned GGUF (greedy, temp 0) over:

1. the held-out **test split** (never seen in training), and
2. a **regression set**: the `sample_documents/`, `stress_corpus/` docs, and the
   existing `tests/test_generation*.py` / `tests/test_app_clinical_forms.py`
   fixtures, de-identified through the real pipeline.

### D.3 Report (`eval/report.py`)

`EVAL_REPORT.md` + `eval_report.json`. **Ship gate:** tuned ≥ base on all four
target metrics on the test split, **no regression** on the regression set, and
median seconds-to-draft ≤ 1.15× the stock Qwen2.5-3B baseline on the 16 GB
CPU profile.

---

## 10. Workstream E — integration

1. **Prompt template as shared constant** (`integrate/prompt_template.py`):
   promote the exact system/user construction to one module imported by both
   `finetune/` and `carescribe`, so a future prompt edit can't silently
   invalidate the fine-tune. Add a test asserting the two match.
2. **Grammar-constrained decoding** (`integrate/grammar.py`): a GBNF per
   `FormType` that fixes the heading skeleton and forbids emitting a `[` that
   doesn't open a known placeholder. Wired into `LocalGGUFBackend` behind a
   flag, on by default for built-in forms.
3. **Model swap:** drop the new GGUF into `models/`; `LocalGGUFBackend` and the
   `carescribe.spec` `models/*.gguf` glob need no change. Bump the bundled-model
   name in `model_setup` / docs.
4. **GPU variant:** `model_setup` detects CUDA/Metal and offers the Q5_K_M / 7B
   variant as a one-time download (reuses the existing first-run fetch path).
5. **About box:** render `MODEL_CARD.md` — consistent with CareScribe's
   "reviewer can verify" stance.
6. **Licence file:** ship the base model's licence (`MIT`/`Apache-2.0`) in the
   app bundle; `carescribe.iss` / macOS `Info.plist` unchanged otherwise.

---

## 11. What needs a human / external resource

| Item | Why | Owner |
|---|---|---|
| Cloud GPU for the training run (~$10, ~2 h, 24 GB) | Can't provision paid infra unattended | **User** (or user provides a key + spend approval) |
| Decision to enable `openai-compatible` datagen backend | Sends *synthetic* text off-box; off by default | **User** |
| Final base-model pick if bake-off is close | Licensing / product call | **User** (default: Phi-3.5-mini) |
| Any real-note validation before clinical use | Out of scope here; governance requirement | **User** |

Everything else — datagen, assembly, validators, eval, training scripts, GGUF
conversion, integration — is built and unit-tested locally on CPU.

---

## 12. Milestones (testable deliverables)

- **M1 — Pipeline dry run:** `template` backend, 200 pairs, all validators
  green, JSONL + manifest produced. *Testable: inspect pairs, run eval harness
  on the stock base model.*
- **M2 — Full synthetic corpus:** 12k/1.5k/1.5k with the `ollama` backend,
  stratification report, manifest hash. *Testable: dataset stats, spot-read.*
- **M3 — Dry-run LoRA on CPU:** 1 epoch, tiny, just proves `sft.py` →
  `merge_and_convert.sh` → GGUF loads in `llama-cpp-python`. *Testable: model
  runs, produces a form.*
- **M4 — Real run + eval:** QLoRA on the GPU box, `EVAL_REPORT.md` with
  tuned-vs-base numbers. *Testable: the ship gate in §9.3.*
- **M5 — Integrated build:** new GGUF in `models/`, grammar decoding wired,
  model card in About box, desktop build green. *Testable: run the app, generate
  a form, confirm the privacy tests still pass.*

M1–M3 and all code/tests: no external dependency. M4: the GPU run. M5: after M4.

---

## 13. Testing strategy

- `finetune/` gets its own `tests/` (pytest), CPU-only, run in CI separately
  from the app suite.
- Every `assemble/` and `datagen/` module: unit tests with fixed seeds.
- A test asserts no `finetune/` module imported by `assemble`/`eval` opens a
  socket (mirrors `test_app.py::test_pipeline_opens_no_socket`).
- `eval/regression.py` is wired so a future `carescribe` change that breaks
  generation shows up here too.
- The existing app test suite is untouched and must stay green throughout.
