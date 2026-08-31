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

All five feature tasks resolved. Integration branch `feat/retrieval-augmented-clinical-forms`
is at `17629e0`, `1013 passed, 1 skipped`.

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
