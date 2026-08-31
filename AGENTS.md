# AGENTS.md — rules for automated coding agents in this repo

You are an **opencode worker** running from a task spec, in your own git
worktree. A "cockpit" Claude session assigned you the task and will review and
merge your result. Coordination is entirely through files — you never message
another agent.

## Do

1. Do exactly what the task spec says. It lists **Files in scope** — change
   only those. It lists **Do NOT touch** — respect it. If the task needs a file
   outside its scope, stop and say so in your final message rather than editing it.
2. After changing code, run `python -m pytest -q`. Don't call the task done
   with failing tests.
3. For "where is X / how does Y work" questions, run `graphify query "<question>"`
   before grepping (see `CLAUDE.md`).
4. Keep commits out of it — the worker wrapper commits your changes. Just leave
   the working tree in the finished state and stop.

## Never

- **Never weaken the de-identification guarantee**: no identifying text is
  written to disk, and the re-identification map stays in memory only.
- Never touch `main`, never `git push`, never rebase or reset shared branches.
- Never edit `.swarm/`, `.agents/`, `CLAUDE.md`, or `AGENTS.md` unless the task
  spec explicitly says to.

## Task spec shape

See `.agents/tasks/TEMPLATE.md`. A good spec has: one-paragraph goal, exact
files in scope, an explicit do-not-touch list, and checkable acceptance
criteria.
