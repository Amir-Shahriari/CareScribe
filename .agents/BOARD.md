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
| 011 | Make desktop build reproducible + self-verifying (pin bundled spaCy model, drop bogus hidden import, bump build-tool pins, add `verify_frozen.py` boot check gated into both build scripts) | cockpit | feat/retrieval-augmented-clinical-forms | **done (uncommitted)** — coder no-op'd it (qwen3-coder wandered into mapping.py, 0 edits, like 008); cockpit did it directly. `carescribe.spec` pins one model via `deidentify.PACKAGED_DEFAULT_MODEL` + `CARESCRIBE_SPACY_MODEL` override, hard-errors if absent; `sklearn.utils._typedefs` removed; `requirements-build.txt` → pyinstaller 6.21.0; new `packaging/verify_frozen.py` gated into both build scripts. Verified: clean freeze bundles `en_core_web_sm` (`dist` 866 MB→456 MB), no build ERROR, `verify_frozen.py` PASS in ~1s, absent-model path exits 1 with a clear message, `1018 passed, 1 skipped` (medgpt env). Changes left in the working tree per "commit only when asked". |
| 012 | `finetune/` scaffold + `datagen/schema.py` (`EncounterFacts` pydantic v2 model, `FormType`/`EncounterType` enums, config YAML skeletons, `finetune/tests/test_schema.py`) | quick | swarm/quick @ `0c3f794` | **partial — TIMED OUT at 600s.** Scaffold done and clean (README, pyproject, 3 config skeletons, package inits — 8 files) but ran out before `schema.py` / `test_schema.py` (the substance). Wasted ~3 min hunting the design doc, which is untracked so absent from the worker's branch. Not yet cherry-picked. `schema.py` still needs doing. |

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

### Fine-tune progress — cockpit-driven (uncommitted, on integration branch)
- `0c3f794` (quick's scaffold) cherry-picked `--no-commit` into the working tree.
- **schema:** `finetune/datagen/schema.py` — `EncounterFacts` + `Demographics`/
  `Medication`/`HistoryItem`/`Finding`/`Result`/`PlanItem` (all `extra=forbid`),
  `FormType`/`EncounterType` str-enums, identifier-shape validator on
  Demographics, `documented_gaps` must name an empty gappable field, `FIELD_NAMES`
  / `GAPPABLE_FIELDS` exports.
- **shared prompt:** `finetune/integrate/prompt_template.py` — imports the
  system/user strings verbatim from `carescribe.prompts.carenotes_prompt`,
  maps `FormType`→(system, instruction), `build_messages()` with style-exemplar
  support. One-way dep; carescribe never imports finetune.
- **tests:** `finetune/tests/test_schema.py` (7) + `test_prompt_template.py` (7),
  all green. Full repo suite **1032 passed, 1 skipped** (1018 app + 14 finetune).
- **datagen:** `sampling.py` (Choice/Weighted/Range/Subset markers + `resolve`),
  `vignettes/` package — 10 skeletons across 5 domains (general practice,
  community mental health, cardiology, respiratory, elderly care) spanning
  new/follow-up/discharge/handover/crisis; `sampler.py` — `expand()` +
  `sample_encounters()`, seeded/deterministic, `gap_probability` blanks
  gappable fields into `documented_gaps`.
- **tests:** +`test_sampler.py` (6, incl. per-vignette parametrised validity).
  Full repo suite **1047 passed, 1 skipped** (1018 app + 29 finetune).
- `graphify update .` run.
- **Next:** render_note.py + generator_backend.py (template mode) +
  identifiers.py → assemble/ (de-id wrap, build_target, the 4 validators, pairs,
  manifest) → M1 dry run (200 pairs).

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
