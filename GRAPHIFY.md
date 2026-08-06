# The CareScribe knowledge graph

This repo is indexed as a queryable knowledge graph in `graphify-out/`. The point is that a
new session can find its way around CareScribe by asking the graph instead of grepping and
re-reading files.

Built with [graphify](https://github.com/Graphify-Labs/graphify) (PyPI package `graphifyy`,
CLI `graphify`).

---

## Start here in a new session

Ask the graph before opening source files:

```bash
graphify query "how does approved text reach disk without the identity mapping?"
graphify path "Privacy Invariants" "write_approved()"
graphify explain "residual_scan()"
```

- `query` — BFS over the graph for a plain-language question. Add `--budget 3000` when the
  answer gets truncated, `--dfs` to trace one path rather than fan out.
- `path A B` — shortest chain between two things, with the relation on each hop.
- `explain X` — one node, its source location, and every edge in and out.

`graphify-out/GRAPH_REPORT.md` is the broad-strokes read: god nodes, community structure,
surprising connections. Use it for orientation, not for answering a specific question — the
three commands above return far less noise.

`graphify-out/graph.html` opens in any browser with no server. It is the fastest way to see
the shape of the thing.

Node names in `path` and `explain` must match the graph's labels — `write_approved()` with
the parens, `Privacy Invariants` in title case. Run `query` first if you are unsure what a
thing is called.

---

## What is actually in the graph

429 nodes, 754 edges, 40 labeled communities, from 24 files (21 Python, README, requirements,
the test fixture).

Two kinds of node, and the distinction matters:

- **Code nodes** — extracted from Python by tree-sitter AST. Deterministic, local, no LLM
  involved. Functions, classes, methods, and their `calls` / `contains` / `references` edges.
- **Concept and rationale nodes** — extracted from the three prose files by a model. These
  carry the *why*: `Privacy Invariants`, `Precision vs Recall Trade-off`,
  `REDACT_INPROSE_DATES Flag`, `Generation Handoff Contract`, and so on.

The interesting edges are the ones joining the two, tagged `rationale_for`. `Single Write
Path --rationale_for--> write_approved()` is how the graph answers "why is this written this
way", which is exactly what is expensive to reconstruct from source alone.

Every edge is tagged `EXTRACTED` (explicit in the source) or `INFERRED` (the model connected
it). Trust them differently — `graphify explain` prints the tag on every edge.

Three hyperedges capture groups that no pairwise edge does: `The Five-layer De-identification
Stack`, `PHI Containment Guarantees`, `Approve-time Write Flow`.

### No PHI is in the graph

The semantic pass deliberately created **no nodes for identifier values** from
`tests/synthetic_patient_discharge_summary.txt` — the fixture appears as concepts
(`Recall Cases In Fixture`, `Line-break-split Name Case`), never as the strings themselves.
`graph.json` was checked and contains no NHS number, phone, postcode, email, MRN, DOB, or
patient name.

Some clinician names do appear, inside docstrings the graph mirrors verbatim from committed
test files. That is existing repo content, not new exposure.

**Keep it that way.** If a future run adds real documents to the corpus, the graph becomes a
PHI artifact and must not be committed. The fixture is safe because it is fabricated.

---

## Keeping it current

A **post-commit git hook is installed** and re-runs AST extraction after every commit. Code
changes stay reflected with no action and no token cost. `graphify hook status` to check;
the hook embeds an absolute interpreter path, so re-run `graphify hook install` after
reinstalling or upgrading graphify.

The hook does **not** re-read prose. After editing `README.md`, `requirements.txt`, or the
fixture, refresh the concept layer by hand:

```bash
graphify update .          # re-extract changed files (AST only, free)
```

For a full rebuild including the semantic pass over docs, run `/graphify .` in Claude Code.
If a refactor deleted code and the rebuild is smaller than the existing graph, graphify
refuses to shrink `graph.json` — pass `--force` when the shrink is intentional.

### The community labels are hand-written, and fragile

The 40 community names (`Residual Safety Sweep`, `Privacy Invariants`, `Name Variant
Expansion`, …) were written by hand. They are not regenerated for free.

A rebuild reuses `.graphify_labels.json` only for communities whose membership is unchanged,
checked against `.graphify_labels.json.sig`. Any community whose membership shifted gets
silently renamed after its highest-degree member — so a labeled community becomes
`deidentify.py` and the map gets worse without anything failing.

If you see this on a rebuild:

```
[graphify watch] community set changed since labeling (40 saved labels, 42 communities now;
renamed 40 community(ies) by their hub)
```

the names are gone. Re-label the affected communities and rewrite the `.sig` sidecar
alongside — `graphify.cluster.community_member_sigs(communities)` produces it. Without the
sidecar the check degrades to comparing community *counts*, which is why one added file
wiped all 40 names once already.

Every rebuild also writes a dated backup (`graphify-out/<YYYY-MM-DD>/`) before overwriting.
That is the way back from a bad rebuild.

### `.graphifyignore` keeps the graph about CareScribe

`.claude/`, `CLAUDE.md`, `GRAPHIFY.md` and `graphify-out/` are excluded. They were not
initially, and a rebuild pulled them in, added two communities, and renamed all 40 — the
graph started describing its own tooling. Leave the ignore file in place.

Note that removing files from the corpus is fail-closed: graphify keeps nodes for files that
left the scan corpus but still exist on disk, and says so. A full re-extract is what actually
purges them.

---

## What is committed, and why

`graph.json`, `GRAPH_REPORT.md`, `graph.html`, and `manifest.json` are committed — they are
the map, and a fresh clone should have it without rebuilding.

`.gitignore` excludes the machine-local pieces: `.graphify_python` and `.graphify_root` hold
absolute paths into this machine's conda env, `cost.json` is a local token tally, and
`cache/` is a rebuild accelerator, not shared state.

A git merge driver is registered for `graph.json`, so two branches that both rebuild the
graph union-merge instead of conflicting.

---

## Environment notes for this machine

The graph was built with the `medgpt` conda env at
`C:\Users\amirh\miniconda3\envs\medgpt\python.exe`, recorded in
`graphify-out/.graphify_python`. If graphify ever reports `No module named 'graphify'`, that
file is pointing at the wrong interpreter — delete it and it gets re-resolved, or
`pip install graphifyy` into whichever env is active.

**PowerShell:** use `graphify .`, not `/graphify .` — a leading slash is a path separator
there. The `/graphify` form is for the Claude Code prompt.

`CLAUDE.md` has a graphify section and `.claude/settings.json` has PreToolUse hooks that
nudge toward `graphify query` before raw file reads. That is what makes the graph the default
path in a new session rather than something to remember.

---

## Known-benign diagnostics

`graphify diagnose multigraph` reports on this graph:

- **43 dangling-endpoint edges** — imports of external modules (`pathlib`, `pytest`,
  `streamlit`, `re`, `pandas`, `ollama`) that have no node of their own. Expected.
- **15–17 collapsed edges** — the same node pair carrying both `calls` and `references`,
  merged when the undirected graph is built. Expected.

Neither indicates corruption. Two nodes are flagged as weakly connected — `Longest-match-wins
Overlap Resolution` and `Person Typing From Context` — which is a real thin spot in the
concept layer, not a build error.
