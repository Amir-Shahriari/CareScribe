# AGENTS.md — how automated agents work in this repo

Three agents collaborate here. Coordination is through git and the task
board (`.agents/BOARD.md`); they do not message each other directly.

| Agent | Role |
|-------|------|
| **Claude Code** | Plans, splits work into task specs, reviews every diff, merges, keeps the graph current. |
| **Hermes** (local `qwen3.8-27b-ctx64k`) | Primary implementer. |
| **opencode** (omniroute cloud models, or local `qwen3-coder-30b-ctx32k`) | Parallel and overflow work, large-context reads. |

## Rules for any agent doing work here

1. Read `.agents/BOARD.md` for the current tasks and who owns what.
2. One task = one branch: `agent/<id>-<slug>`, branched from
   `feat/retrieval-augmented-clinical-forms`. Never commit straight to that
   branch or to `main`.
3. Change only the files your task spec (`.agents/tasks/<id>-*.md`) lists.
   Ask before touching anything outside that set.
4. After changing code: run `python -m pytest -q` and `graphify update .`.
   Do not mark a task done with failing tests.
5. Commit messages: imperative and scoped, e.g. `fix(review): ...`. Do not add
   co-author or session trailers unless explicitly asked.
6. Never weaken the de-identification guarantee: no identifying text is written
   to disk, and the re-identification map stays in memory only.
7. For codebase questions run `graphify query "<question>"` before grepping
   (see `CLAUDE.md`).
8. Push your branch once the task's acceptance criteria are met. Claude Code
   reviews and merges.
