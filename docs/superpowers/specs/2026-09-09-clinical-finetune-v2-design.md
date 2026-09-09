# Clinical fine-tune v2 — honest evaluation, corpus rebuild, patient roll-up

**Date:** 2026-09-09
**Status:** Approved for implementation
**Owner:** CareScribe generation subsystem
**Supersedes in part:** `2026-09-01-local-clinical-llm-finetune-design.md` (v1),
whose §9 evaluation methodology this document replaces.

---

## 1. Why there is a v2

v1 shipped `models/carescribe-clinical-phi35-v1.Q4_K_M.gguf` (Phi-3.5-mini-instruct
3.8B, MIT, QLoRA, Q4_K_M, 2.4 GB) and `finetune/runs/phi35-v1/EVAL_REPORT.md`
records **ship gate: PASS** with 1.000 on format, faithfulness, placeholder
integrity and residual-clean, and 0.998 on style match.

Those numbers do not mean what the report implies. Four defects in the v1 data
and evaluation pipeline were found on 2026-09-09, each verified against the
committed artefacts:

**D1 — the test split is contaminated by construction.**
`finetune/assemble/pairs.py::stratified_split` shuffles within each
`form_type × specialty × styled` stratum and slices 10% test / 10% dev / 80%
train. The stratum key does not include the source vignette. `VIGNETTES`
contains **10** skeletons (the v1 spec called for 40–60), so 3,200 pairs are
roughly 320 re-renderings of each of ten clinical stories, and **every test
pair's skeleton also appears in training**. A held-out score measured this way
cannot distinguish generalisation from memorisation.

**D2 — faithfulness and format are self-marked.**
`assemble/build_target.py` renders the target by deterministically mapping
`EncounterFacts` into the form's heading skeleton, and
`assemble/validators.py` scores a draft by aligning its spans back to those same
`EncounterFacts`. Model, target and grader all derive from one artefact. A
1.000 is consistent with "reproduced the scaffold" and carries no information
about faithfulness on text the scaffold did not generate.

**D3 — `style_match` measures a dimension that does not exist.**
The v1 spec specified `datagen/vignettes/styles/` and ~30% styled pairs. **The
directory was never created.** Every one of the 25 strata in
`finetune/data/full/dataset_manifest.json` is `styled=False`. The reported
0.998 is computed over a corpus in which style never varied.

**D4 — the committed test split is never read.**
`finetune/eval/run_eval.py::main` calls `make_eval_set(n, seed=1000)`, which
re-samples the generator over the same ten vignettes; `test.jsonl` is not
opened. The function's docstring describes it as "a held-out set built exactly
like the training data (different seed)" — but a different seed over identical
skeletons is not a holdout. Found 2026-09-09 while planning V1; fixed by the
V1 plan's Task 4.

Two lesser findings, both real:

- **Gap coverage is thin.** 1,699 of 3,200 pairs (53%) have
  `documented_gaps == []`. "Not documented." is the product's primary
  anti-confabulation behaviour and it is trained on under half the corpus and
  never adversarially probed.
- **The input distribution is too regular.**
  `datagen/generator_backend.py::TemplateBackend.complete` emits `key: value`
  lines. Every training input is a tidy proforma, which independently inflates
  the format score.

v2 fixes the measurement first, then the corpus, then adds the new capability.
The order is forced: until D1–D4 are fixed, no change can be shown to help.

**New capability.** v2 adds a **multi-document patient roll-up**: condense every
document belonging to one patient into a single "where this patient is now"
brief. This is the first CareScribe task whose input is more than one document,
and it introduces a problem the single-document tasks never had (§4).

Non-goals, unchanged from v1: no change to de-identification models; no clinical
Q&A; no change to the privacy contract; no real PHI anywhere in training or
evaluation; no cloud training spend.

---

## 2. The placeholder-namespace problem, and the chosen resolution

`carescribe/core/mapping.py::assign_placeholders` numbers placeholders **per
document and positionally**: a type with exactly one value gets a bare token
(`[DATE]`), a type with several gets numbered tokens (`[DATE_1]`, `[DATE_2]`, …)
counted in that document's own entity order.

Consequently, documents de-identified **independently do not share a namespace**:

- `[DATE_2]` in one document and `[DATE_2]` in another are different dates.
- One clinician is `[PROVIDER_1]` in one document and `[PROVIDER_2]` in another.
- A document with one date says `[DATE]`; a document with three says `[DATE_1]`.

`carescribe/core/patients.py` persists only the patient roster; **no identity
map is stored**, so filed documents cannot be reconciled after the fact.

Naively concatenating the filed `.deid.txt` documents for a patient would
therefore invite the model to coreference tokens that do not share a referent.
The failure mode is a fluent, plausible, wrong summary — and the existing
`placeholder_integrity` validator would not catch it, because it checks only
that tokens are reproduced, not that they denote one thing.

### Options considered

| | approach | verdict |
|---|---|---|
| A | Per-patient `value → token` registry on disk | **Rejected.** Persists identifier values, reopening the carve-out deliberately limited to the display name on 2026-09-04. |
| A′ | Per-patient `salted-hash(value) → token` registry | **Deferred as a documented seam.** Preserves the privacy contract and gives stable tokens, but permanently forfeits cross-session re-identification. Adopt only if roll-ups are ever needed over documents whose originals are gone. |
| B | **De-identify the bundle as one unit** | **Selected.** |
| C | Train the model never to coreference across documents | **Rejected.** No privacy or store change, but "current medications" across a timeline stops being trustworthy, which removes the clinical value of the feature. |

### B — the selected approach

Never split the namespace in the first place. A roll-up takes the **original**
documents, concatenates them with explicit document fences, and runs
de-identification **once over the whole bundle**. The namespace is consistent by
construction, `assign_placeholders` is untouched, and the privacy contract does
not move.

This is consistent with how the product is already understood to work: the
2026-09-04 decision recorded that clinicians retain the original documents and
CareScribe files only de-identified output. The roll-up's *output* is still
filed into the patient folder like any other approved artefact.

**The property that makes this design cohere:** datagen builds its training
bundles the same way production builds its input (§5.2), so the model is trained
on exactly the token distribution it will be asked to read.

---

## 3. Workstream V1 — evaluation you can believe

This lands first and is independently valuable: it says whether the model
already shipping is any good.

### 3.1 Hold out vignettes, not rows

Add `vignette_id` to `Pair.meta` and to the split key, and reserve **entire
vignette families for dev and test**. Splitting proceeds over vignettes, then
over strata within the training vignettes.

Because a vignette is the unit of holdout, dev/test size is governed by how many
vignettes exist — another reason §4 raises the vignette count before retraining.

**Acceptance:** no `vignette_id` appears in more than one split; asserted by a
test over the emitted manifest.

### 3.2 Report contamination rather than assuming its absence

`eval/report.py` gains an overlap section: for each test target, the maximum
character 5-gram Jaccard similarity against any training target; report median
and p95, and the count above 0.6. A high number voids the scores printed above
it, and the report says so in text.

**Acceptance:** the v1 corpus, re-split by §3.1, reports materially lower
overlap than the v1 random split — demonstrating the metric detects the defect
it exists to detect.

### 3.3 Break self-marking on faithfulness

Keep the fact-aligned validator; it is fast, deterministic and useful for
data-build rejection. Add a **second, independent grader** for evaluation only:

- `eval/judge.py` — an LLM grader over the local Ollama daemon, default
  `qwen3.8:27b`, greedy, given **the source note and the draft only, never
  `EncounterFacts`**. It answers, per draft: is every clinical claim supported
  by the source; does any required-but-absent field get asserted anyway.
- The judge is a different model family and size from the model under test, and
  sees a different artefact than the scaffold was built from, so it cannot
  reward reproduction of the scaffold.
- Both scores are reported. **Disagreement between graders is the signal**; the
  report shows the confusion, not just the means.
- The judge is evaluation-only and lives behind the existing socket-boundary
  test: it must not be importable from `carescribe/`.

**Acceptance:** a deliberately confabulated draft (a fact injected that is absent
from the source) scores clean under the fact-aligned validator when the injected
fact happens to match a facts leaf, and is caught by the judge.

### 3.4 Delete `style_match`; re-earn it later

Remove the metric from `eval/metrics.py` and from the report. It is reinstated
in V2 once `styles/` exists and styled pairs are in the corpus (§4.2). Reporting
a number for a dimension the corpus never varied is worse than reporting none.

### 3.5 Adversarial gap probe as a first-class metric

A dedicated probe set in which `documented_gaps` is forced non-empty and the
absent field is one the form requires. The metric is **confabulation rate**: the
fraction of probes where the model asserts a value instead of writing
"Not documented." This becomes a ship-gate metric in its own right.

### 3.6 Re-score v1 honestly

Run the whole harness over the existing v1 GGUF and the base, and publish the
new numbers **beside** the old ones in `EVAL_REPORT.md`, with a note explaining
why they differ. The expectation is a substantial fall. That is the deliverable,
not a regression.

---

## 4. Workstream V2 — corpus rebuild

### 4.1 The lever is vignettes, not row count

The v1 spec's target of 12k pairs is not the constraint; 3,200 rows over 10
skeletons already saturates what those skeletons can teach. Raising rows without
raising skeletons buys overfitting.

- **Author 40–60 vignettes**, up from 10, broadening beyond the current five
  specialties (cardiology, respiratory, community mental health, general
  practice, elderly care).
- Corpus size follows from vignette count at a fixed renderings-per-vignette
  budget, rather than being set independently.

Vignettes are clinical content. They are drafted for the user's review, and the
user is the approver of clinical plausibility (§7).

### 4.2 Build `datagen/vignettes/styles/`

6–10 synthetic clinic style guides — section order, abbreviation set,
sign-off form, heading casing. Applied to ~30% of pairs, prepended to the user
turn, with the target rendered in that style. This makes style a real trainable
axis and re-enables `style_match` (§3.4) as a meaningful metric.

### 4.3 Raise gap coverage

Target ~70% of pairs carrying at least one `documented_gaps` entry, up from 47%,
so "Not documented." is a well-trained behaviour rather than an occasional one.

### 4.4 Replace the source-note generator

`TemplateBackend` stays for CI and deterministic dry runs. Corpus builds move to
the Ollama backend so input notes carry realistic messiness — abbreviations,
missing headers, run-together lines, dictation artefacts.

**Throughput constraint, measured:** the RTX 5080 has 16 GB VRAM; every Ollama
model currently pulled is a ~17 GB Qwen3.8-27B variant, which will not fit and
will spill to CPU. At corpus scale this is prohibitive. **Recommendation: pull a
~8–14B instruct model for datagen** — the bar for a *messy input note* is
diversity, not brilliance — and reserve the 27B for the judge role in §3.3,
which runs over far fewer items.

The final model choice is the user's (§7).

---

## 5. Workstream V3 — the patient roll-up task

### 5.1 `PatientTimeline`

A new schema in `datagen/schema.py`: an ordered list of 2–6 `EncounterFacts` for
**one** synthetic patient, with explicit **supersession semantics**:

- medications change between encounters (dose titration, start, stop);
- problems are introduced, persist, or resolve;
- follow-ups are fulfilled by a later encounter or remain outstanding.

Supersession is recorded structurally, not inferred from prose, so the target
and the validators remain exact — the same property that made v1's data-build
checkable.

`FormType` gains `PATIENT_SUMMARY`.

### 5.2 Bundle construction — identical to production

1. Render each encounter to a source note via the §4.4 backend.
2. Inject identifiers **consistently across the timeline**: one patient name and
   NHS number throughout, clinicians recurring where the timeline says the same
   person was involved.
3. Concatenate with explicit document fences (`--- DOCUMENT n ---`).
4. Run the **real** `carescribe` de-identification once over the whole bundle.

Step 4 is the production path from §2, exercised at data-build time. A test
asserts the resulting bundle's namespace is collision-free: each token maps to
exactly one source value across the whole bundle.

### 5.3 Target

Built deterministically from the timeline:

- **Active problems** — unresolved only; resolved problems must be absent.
- **Trajectory** — chronological, one line per encounter.
- **Current medications** — the latest encounter's list, superseding earlier ones.
- **Outstanding actions** — follow-ups not fulfilled by a later encounter.
- **Not documented** — for fields absent across the whole timeline.

### 5.4 Two new validators

The existing four cannot catch the failures specific to this task:

- **Temporal correctness** — current medications equal the latest encounter's;
  no resolved problem appears in the active list; no outstanding action was
  fulfilled by a later encounter.
- **Cross-document coreference** — every token in the summary occurs in the
  bundle, and no token is attributed to two referents.

Both run at data-build rejection time and in evaluation, as with v1's four.

### 5.5 Sequence-length budget

Current pairs are ~2,678 characters median, 5,612 maximum (roughly 700 and 1,500
tokens). A 4-document bundle runs ~3–5k tokens, so `max_seq_length` rises from
3,072 toward ~8,192.

On 16 GB with QLoRA and gradient checkpointing this implies `batch_size` 1–2 with
increased gradient accumulation to hold the effective batch. **The number is
measured before it is committed to `train.yaml`**, by a short profiling run — not
assumed here.

CPU inference latency at bundle length must also be measured against the 16 GB
laptop profile; the §6 ship gate carries a latency ceiling for the roll-up
separate from the single-document one, because prefill cost scales with the
bundle.

---

## 6. Ship gate for v2

On the §3 harness, over **held-out vignettes**:

1. v2 ≥ v1 on format, faithfulness (both graders), placeholder integrity,
   residual-clean.
2. Confabulation rate (§3.5) strictly lower than v1's.
3. `style_match` reported and ≥ base, now that the axis exists.
4. Roll-up: temporal correctness and cross-document coreference both ≥ 0.95 on
   held-out timelines.
5. No regression on the real-document regression set.
6. Median seconds-to-draft ≤ 1.15× the stock base on the 16 GB CPU profile, with
   a separately stated roll-up latency figure.
7. Train/test overlap (§3.2) reported and low.

A number that cannot be computed is reported as absent, never as a default.

---

## 7. What needs the user

| item | why |
|---|---|
| Which datagen model to pull (§4.4) | Throughput vs quality trade-off; or accept the runtime of what is installed |
| Review of the 40–60 vignettes (§4.1) | Clinical plausibility is the user's call; drafts are prepared for review |
| Any real-note validation before clinical use | Out of scope here; governance requirement, unchanged from v1 |

No cloud spend. Training stays on the local 5080.

---

## 8. Integration

- A roll-up entry point taking N uploaded originals: de-identify as one bundle
  (§2), generate, re-identify in-session, file the result to the patient folder.
- `carescribe/core/desktop.py::find_local_model` already prefers
  `carescribe-clinical-*.gguf` over the stock model, so the v2 GGUF drops in
  with no wiring change; only the bundled-model name in docs and the model card
  need updating.
- Privacy contract untouched: no new identifier reaches disk, the identity map
  stays in-session, and the existing no-egress and packaging tests must stay
  green.

---

## 9. Testing strategy

- `finetune/tests/` continues to run CPU-only, separately from the app suite.
- New tests: vignette-disjoint splits (§3.1); overlap metric detects the v1
  defect (§3.2); judge catches an injected confabulation (§3.3); bundle
  namespace is collision-free (§5.2); both new validators reject a corrupted
  timeline (§5.4).
- The socket-boundary test extends to `eval/judge.py`: nothing under
  `carescribe/` may import it.
- The existing app suite is untouched and must stay green throughout.

---

## 10. Milestones

| | deliverable | gate |
|---|---|---|
| **V1** | Honest eval harness; v1 re-scored | Real numbers published beside the old; overlap reported |
| **V2** | 40–60 vignettes, styles, new generator backend | Corpus stats; spot-read; gap rate ~70% |
| **V3** | `PatientTimeline`, roll-up datagen, two new validators | Bundle namespace provably collision-free |
| **V4** | Retrain; evaluate v2 vs v1 vs base | §6 ship gate |
| **V5** | Roll-up wired into the app, filed to patient | App suite green; privacy tests green |

V1 is worth landing on its own: it is the only thing that says whether the model
already in `models/` is any good.
