# Task board

Branch base: `feat/retrieval-augmented-clinical-forms`
Status flow: `backlog` → `in-progress` → `review` → `done`
Task specs: `.swarm/queue/<worker>/<id>-<slug>.task.md`

| id | task | owner | branch | status |
|----|------|-------|--------|--------|
| 001 | Client-facing download & install guide | quick | swarm/quick | failed — worker produced nothing (32k ctx overflow); redone as 004 |
| 002 | Consolidate desktop-build deps into requirements-build.txt | coder | swarm/coder | failed — `database is locked`; retried as 003 |
| 003 | Consolidate desktop-build deps (retry of 002) | coder | swarm/coder | **done** — merged `4e4c903`, tests green |
| 004 | Client-facing download & install guide (redo of 001) | coder | swarm/coder | **done** — merged `c790460` (cockpit polish pass), tests green |
| 005 | GitHub Actions build & release pipeline | coder | swarm/coder | **done** — merged `4e54712`, YAML validated, tests green |
| 006 | build-info helper module (`carescribe/core/buildinfo.py` + test) | coder | swarm/coder | **done** — merged `4276965`, tests green (pipeline smoke; finalized by cockpit) |
| 007 | root `CHANGELOG.md` (Keep a Changelog, 0.1.0) | quick | swarm/quick | **done** — merged `786318b`, tests green (pipeline smoke; finalized by cockpit) |
| 008 | tiny `summary()` helper + test | coder | swarm/coder | **no-op** — worker relaunched OK and ran, but qwen3-coder emitted a malformed tool call; zero edits. Pipeline plumbing verified; nothing to merge. |
| 009 | `docs/swarm-pipeline.md` one-liner | quick | swarm/quick | **done** — merged `978efe5`, tests green. Full self-service loop (pickup→commit→result→done) confirmed on patched worker (~5 min; qwen3.8@64k is slow). |
| 010 | `buildinfo.user_agent()` + test | coder | swarm/coder | **done** — merged `356369a`, `1015 passed`. First task run with the codebase orientation map prepended; coder used proper tool calls, 36s. |
| 011 | desktop build reproducible + self-verifying | cockpit | `a2d9345` | **done, committed.** coder no-op'd; cockpit wrote it. |
| 012 | `finetune/` scaffold + schema | quick→cockpit | `0c3f794`→`ca54bd8` | quick TIMED OUT after scaffold only; cockpit wrote `schema.py` + rest, folded into `ca54bd8`. |
| 013 | `finetune/datagen/generator_backend.py` | coder | `25884c2` | **done, cherry-picked.** coder produced working code + 7 tests, then idled into the 600s cap. |
| 014 | `finetune/datagen/identifiers.py` | quick→cockpit | `7e0ba39` | quick TIMED OUT with ZERO edits (10 min reading). cockpit wrote it (stdlib, no Faker). |

### Worker capability ceiling on the fine-tune workstream (2026-09-01)
coder (qwen3-coder-30b) no-op'd 008 and 011; quick (qwen3.8-27b) timed out on 012
before the real work. Both local workers are proving too slow / unreliable for
correctness-sensitive multi-file work (pydantic schemas, validators that reuse
carescribe internals, eval metrics). Options on the table for the fine-tune
build-out: (a) cockpit hand-drives the substantive modules, workers for
mechanical bits only; (b) bump worker models in `.swarm/config.json` + relaunch;
(c) proper `writing-plans` pass then execute. Awaiting user direction.
Also: the design doc must be committed so worker branches can see it.

### Fine-tune hardware facts (2026-09-01)
User will train on their **own local GPU: RTX 5080, 16 GB VRAM**. Fits QLoRA on
≤8B comfortably; 3–4B ideal. **MedGemma-27B cannot be trained on 16 GB** and is
not CPU-laptop-viable for inference — if wanted, it's the optional GPU-detected
inference variant only (stock or LoRA'd later on rented 24 GB+).

### Fine-tune decisions locked (2026-09-01)
- **Execution:** cockpit hand-drives the build (workers can't carry it);
  commit only when the user asks.
- **Base model:** Phase-0 **bake-off Phi-3.5-mini-instruct (MIT) vs
  MedGemma-4B-it (Gemma/HAI-DEF)**, decide by the 4-metric eval on the 5080,
  default to Phi-3.5-mini if within noise. MedGemma-27B wired later as the
  GPU-detected inference upgrade only.

### Fine-tune progress — cockpit-driven, COMMITTED on integration branch

Commits after `356369a`:
- `e9bcc3b` fix(carenotes): token-bound the mapping-value generation guard
  (the app bug the user hit — see "App bug" below)
- `a2d9345` build: reproducible + self-verifying freeze (was task 011)
- `ca54bd8` feat(finetune): scaffold + schema + sampler + vignettes + prompt_template
- `25884c2` swarm(coder): 013-generator-backend  (cherry-picked; coder's only useful output)
- `bc776e5` feat(finetune): assemble layer + M1 dry-run pipeline
- `7e0ba39` feat(finetune): stdlib identifier injector (was task 014)

**All fine-tune code built & tested (M1–M3 + M5 wiring). Full repo 1101
passed, 1 skipped. ~83 finetune tests.** Commits `e9bcc3b`..`51440f1`.

`finetune/` complete:
- `datagen/` — schema, sampling, vignettes×10 / 5 domains, sampler,
  render_note (4 styles), identifiers (stdlib, valid NHS check digit),
  generator_backend.
- `assemble/` — deidentify_notes (real de-id, no-socket test),
  build_target (deterministic fact→form scaffold), validators (4 gates),
  pairs, manifest, **build_dataset** (`python -m finetune.assemble.build_dataset`
  → M1: 200/200 validated pairs, 176/12/12 split + manifest).
- `eval/` — metrics (gates reused + style_match), run_eval (Completer
  protocol, GgufCompleter, ship gate ≤1.15× latency), regression
  (stress_corpus + sample_documents), report (EVAL_REPORT.md).
  `python -m finetune.eval --base-gguf X --tuned-gguf Y`.
- `train/` — sft.py (QLoRA for 16 GB: 4-bit NF4, r16/a32, batch1×accum16,
  grad-ckpt, paged_adamw_8bit, assistant-only loss), merge_and_convert.sh,
  modelcard.py, dpo.py (make_rejected tested; trainer a stub).
- `integrate/` — prompt_template (shared w/ carescribe), grammar.py (GBNF:
  pins headings, bare `[` impossible outside a known placeholder).
- `config/` — models.yaml (bake-off candidates + licences), train.yaml
  (5080 hyperparams), datagen.yaml (corpus mix).
- `finetune/README.md` — M1–M5 run guide with exact M4 commands.

**REMAINING = the user's:** M2 full corpus (needs local Ollama 7–8B for
prose polish), **M4 the QLoRA run on the RTX 5080** (per README), then
M5 wiring the winning GGUF + grammar + model card into the app.

### M3–M5 DONE — model trained, evaluated, integrated (2026-09-01)
Commits `dd3b495`..`c984518`. Ran on the RTX 5080 (torch cu128 in
`qwarm_env`; carescribe + pydantic installed there too for the eval).

- **Corpus (M1/M2-lite):** `finetune/data/full/` — 2500 synthetic encounters
  → 2014/243/243, `template` backend, all validators green. Logging silenced
  (the running desktop app holds `carescribe.log` open; every emit from a batch
  process spews a logging-error block — silence `logging.getLogger("carescribe")`).
- **sft.py fixed for trl 1.12 / transformers 5.16** (`warmup_ratio`→`warmup_steps`,
  `max_seq_length`→`max_length`, `torch_dtype`→`dtype`, `from_yaml` now reads
  every runtime field — `packing:false` was ignored). packing off (no
  flash-attn on Windows).
- **M4:** Phi-3.5-mini + QLoRA r16/a32, 3 epochs / 378 steps, ~35 min,
  `train_loss 0.037`. Adapter at `finetune/runs/phi35-v1/adapter/`.
- **GGUF:** merge → `convert_hf_to_gguf.py` (needs `tokenizer.model` copied into
  the merged dir; `PYTHONPATH` = llama.cpp `gguf-py`) → `llama-quantize.exe`
  Q4_K_M → **`carescribe-clinical-phi35-v1.Q4_K_M.gguf` (2.28 GB)** in `models/`.
- **Eval — SHIP GATE PASS.** Held-out synthetic (50): format 0.52→1.00,
  faithfulness 0.74→1.00, placeholder 1.00→1.00, residual 0.94→1.00,
  style 0.55→1.00; median s/draft 5.42→4.41 (tuned faster — learned to stop).
  Regression (10 real de-identified stress_corpus docs): no regression,
  residual 0.70→0.90. `finetune/runs/phi35-v1/EVAL_REPORT.md`.
- **M5:** `desktop.find_local_model()` prefers `carescribe-clinical-*.gguf`;
  app sidebar "Generation model" section + model-card expander;
  `MODEL_CARD.md` rendered from manifest + eval. Verified end-to-end through
  `carenotes.generate_document` (the fixed `assert_deidentified` guard passes;
  no leak, faithful).
- **Known rough edges (v2 work):** the corpus is `template`-backend only
  (deterministic scaffold targets), so the model slightly overfits the exact
  scaffold format and wobbles on very short out-of-distribution prose notes
  ("Objective" without the `**O — Objective**` markup, a garbled "Not
  documented"). Tighten with M2 (ollama prose backend), a larger/more varied
  corpus, and 2 epochs instead of 3. `integrate/grammar.py` (GBNF) is built
  but not yet wired into `LocalGGUFBackend` — would hard-fix the format wobble.
- Full repo suite: **1103 passed, 1 skipped.**

### SWARM WORKERS: not viable for this build (2026-09-01)
Tally on fine-tune tasks: coder no-op'd 008 & 011, produced working code on
013 (then idled into the 600s cap); quick timed out on 012 (scaffold only)
and 014 (zero edits — 10 min just reading files). qwen3-coder-30b is
unreliable at tool-calling; qwen3.8-27b @ 64k is too slow to read context +
write a file in 600s. Cockpit is hand-driving the rest. To revive the swarm:
bump `.swarm/config.json` models to something stronger and relaunch.

### App bug the user hit (2026-09-01) — FIXED in `e9bcc3b`
Clinical-form generation refused with "the text handed to the model still
contains a value from the identity mapping". Root cause: `assert_deidentified`
did a raw casefolded **substring** test floored at `MIN_VALUE_LENGTH` (2), so a
2-char mapping value ("mm", an honorific fragment, initials, a hand-added
token) matched inside ordinary words ("co**mm**unity") and blocked a clean
draft. Fixed: match on token boundaries. Regression tests added. A real
standalone short leak still blocks.

## Local clinical LLM fine-tune (started 2026-09-01)

User wants a fine-tuned ~3–4B GGUF that replaces stock Qwen2.5-3B for
generation so the lightweight local model is faithful and low-hallucination.
Approved design at `docs/superpowers/specs/2026-09-01-local-clinical-llm-finetune-design.md`
(Approach 1: structured-synthetic SFT + QLoRA + 4-metric eval + GGUF drop-in).
Dependency order A→B→(C∥D)→E. Swarm builds all code/tests (M1–M3, M5 wiring);
the GPU training run (M4) and the base-model pick (default Phi-3.5-mini, MIT)
are the user's. "Generate dummy patient docs across domains" is Workstream A —
implemented as reusable `finetune/datagen/vignettes/` skeletons + a model-free
`template` renderer, feeding real de-id + validators, not one-off free-written
files (free-written notes have no ground-truth target to check faithfulness
against, which is the whole point).

Feature tasks done. Pipeline verified end-to-end on the patched workers.
Integration branch `feat/retrieval-augmented-clinical-forms` at `356369a`,
`1015 passed, 1 skipped` (verified in the `medgpt` env).

### Workers now get a codebase map (2026-09-01)
`swarm-prep.ps1` writes `<repo>/.swarm/orientation.md` at every launch — a
~4 KB slice of `graphify-out/GRAPH_REPORT.md` (Summary, Community Hubs
navigation, God Nodes) or, if there's no graphify output, a file tree + README
head. `worker.ps1` prepends it to every task prompt as read-only context,
capped by `-OrientMaxChars` (default 9000; per-worker `orient_max_chars` in
`config.json`, 0 disables). If the `graphify` CLI is on PATH, prep also runs
`graphify update` first. So task specs can name real modules and expect the
worker to know where they live.

### Worker-quality note (not a plumbing bug)
`coder` = `ollama/qwen3-coder-30b-ctx32k` is inconsistent at tool-calling under
opencode: correct on 006, malformed `<function=…>` text on 008 (no edits). If it
keeps no-opping, switch it to a shim variant in `.swarm/config.json` and
relaunch. `quick` = `qwen3.8-27b-ctx64k` is reliable but slow (~5 min/small task).

## Pipeline incident 2026-09-01 (fixed)

Tasks 006/007 were picked up by both workers and opencode wrote the files, but
`opencode run` never exited, so `worker.ps1` blocked forever before the commit /
result / done steps — the queue looked dead. Root-caused and fixed in the swarm
engine (`C:\Users\amirh\swarm\`):

- `worker.ps1`: new `-RunTimeoutSec` (default 600). `opencode run` now runs as a
  job with a hard wall-clock cap; on timeout the opencode/node process tree for
  that worktree is killed (`Clear-WorktreeProcs`, scoped by worktree path) and
  the run is recorded as `status: TIMED OUT`. Same reaper runs before every task
  so a leaked run never accumulates.
- `swarm-launch-workers.ps1`: before launching, reaps stale `worker.ps1` /
  `opencode` processes bound to this repo's worktrees (fixes double-processing
  and stale `-Model` — e.g. the old 32k `quick`). Passes `-RunTimeoutSec`
  (optional per-worker `run_timeout_sec` in `config.json`).
- `swarm-prep.ps1`: cockpit brief now documents the timeout + the
  relaunch-to-change-model rule.

006/007 were finalized by the cockpit (commit + cherry-pick + result) since the
old wedged workers couldn't. Relaunch via `swarm-launch-workers.ps1` to get the
patched, timeout-protected workers running.

## What shipped

- `packaging/requirements-build.txt` — pinned PyInstaller build-only deps;
  `build_windows.ps1` / `build_macos.sh` install from it. `requirements.txt`
  (runtime, auditable) untouched.
- `docs/download-and-install.md` + a `## Download` link in `README.md` — a
  non-technical Windows/macOS install guide (SmartScreen / Gatekeeper
  walkthrough, first-run model download, low-RAM Ollama path, output paths).
- `.github/workflows/release.yml` — `build-windows` + `build-macos` freeze the
  app on clean runners (`CARESCRIBE_BUNDLE_MODEL=0`); `release` attaches both
  installers to a **draft** GitHub Release on a `v*` tag. `workflow_dispatch`
  runs the two build jobs only — this is the end-to-end build verification
  (needs a push to run; nothing was pushed).

## Worker notes

- **`quick` worker fixed.** Root cause: model was `qwen3.8-27b-ctx32k`; a doc
  task that reads several large files + opencode's own system prompt overflows
  32k, Ollama truncates from the front, the model loses the task and stops with
  no edits (exactly what 001 did). qwen3.8 tool-calling itself is fine (verified
  directly). Fix: `.swarm/config.json` now points `quick` at
  `ollama-shim/qwen3.8-27b-ctx64k` (the 64k Ollama variant already existed);
  added that model to `~/.config/opencode/opencode.json` under the `ollama-shim`
  provider (backup: `opencode.json.bak-20260901-075337-cockpit`).
  **The running `quick` terminal must be restarted** — it was launched with the
  old `-Model` arg and does not re-read config.json.
- Keep `quick`'s task specs small (few files in scope, no "read the whole
  module") — 64k helps but qwen3.8 is dense and slow (~15-20 tok/s at 64k).
- Workers run in conda `base`, which has no `pytest`. The cockpit verifies the
  suite on the integration branch with the `medgpt` env after each merge.

## UI refinement — calm-clinical, elevated (2026-09-01)

Refinement (identity/copy/behaviour kept) of the incumbent CareScribe world,
driven by the `impeccable` skill. Direction: a clinical instrument that always
shows the reviewer where they stand in an irreversible pipeline.

- `carescribe/ui/theme.py` — the stylesheet (was `_APP_CSS` in app.py), now a
  module with the direction contract in its docstring; refined tokens, themed
  browser surfaces (scrollbars/caret/selection/link), tabular-nums, and blocks
  for the new components.
- `carescribe/ui/components.py` — a drawn 1.5px-stroke SVG icon set (no emoji)
  + HTML helpers: `hero()` (dynamic privacy pill), `step_tracker()` (Load →
  De-identify → Review → Approve → Generate; fills as the reviewer advances —
  the signature interaction), `chip()`/`status_chip()`, `detection_layer()`,
  `stat_strip()`, `empty_state()`.
- `app.py` — `main()` renders masthead + tracker (step from pipeline state);
  `render_sidebar()` uses the icons + chip layers + stat strip;
  `section_batch_status()` is now a `.cs-table` with status chips;
  `privacy_indicator()` uses `:material/` icons.
- Tests: `tests/test_ui_components.py` (7), `tests/test_app.py` title check
  updated. Full repo **1110 passed, 1 skipped**.
- Verified in Chrome end-to-end: tracker fills through load→de-id→review,
  chip table renders, no console errors.
- Commits `e5d7d27`, `8ca9360`.

### Swarm tasks 015 / 016 — both failed, cockpit did them
- **015** (batch-status chip table → coder): worker branch was on a stale
  base (pre-UI-module) and rebuilt `ui/components.py` + `ui/theme.py` as
  trivial stubs that would clobber the real ones; still called `st.dataframe`.
  Rejected, not cherry-picked. Cockpit wrote it.
- **016** (ui-component tests → quick): `opencode run` usage error, 0 edits.
  Cockpit wrote it.
Swarm workers remain unreliable for this repo (see earlier tally); they also
need their base reset to the current integration branch, not a stale one.
