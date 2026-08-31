# Task board

Branch base: `feat/retrieval-augmented-clinical-forms`
Status flow: `backlog` → `in-progress` → `review` → `done`
Task specs: `.swarm/queue/<worker>/<id>-<slug>.task.md`

| id | task | owner | branch | status |
|----|------|-------|--------|--------|
| 001 | Client-facing download & install guide | quick | swarm/quick | failed — worker produced nothing; reassigned as 004 |
| 002 | Consolidate desktop-build deps into requirements-build.txt | coder | swarm/coder | failed — `database is locked`; retried as 003 |
| 003 | Consolidate desktop-build deps (retry of 002) | coder | swarm/coder | done — merged @ 4e4c903, tests green (1013 passed) |
| 004 | Client-facing download & install guide (redo of 001) | coder | swarm/coder | in-progress |
| 005 | GitHub Actions build & release pipeline (`.github/workflows/release.yml`) | coder | swarm/coder | in-progress |

## Notes

- `quick` worker (ollama-shim qwen3.8-27b) is unreliable — 001 returned zero
  changes after reading files. Routing everything to `coder` for now.
- Workers run in conda `base`, which has no `pytest`. The cockpit verifies the
  test suite on the integration branch using the `medgpt` env after each merge.
- "Verify + fix the build end-to-end" is folded into 005: `workflow_dispatch`
  on `.github/workflows/release.yml` runs the Windows + macOS PyInstaller freeze
  on real runners, which is the end-to-end check. Needs a push to run.
