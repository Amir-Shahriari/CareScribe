# Lightweight review UX for de-identification — design

## Problem

Step 3 ("Review & approve") currently asks a non-technical practitioner to work
through three separate manual mechanisms per document before they can approve
it:

1. **The entity table** (`render_entity_table`) — an editable grid with one row
   per *every* detected identifier, regardless of how confident the detector
   was.
2. **The flagged-residuals list** (`render_flag_decisions`) — a separate list
   of candidate residual spans the safety-net sweep additionally highlights,
   each needing an individual "Redact this" / "Not an identifier" click.
3. **A 2-item checklist** (`render_checklist`) — two tick boxes ("I have read
   the full redacted text", "every flagged span has been checked") that must
   both be ticked before the Approve button unlocks.

For a batch of a few documents this is tedious but survivable. At the batch
sizes a real GP workload produces (dozens of documents), it becomes a wall of
near-identical manual decisions — a document with 30 detected identifiers
means roughly 30+ clicks before that one document can even be approved. Two
concrete problems follow directly from this:

- **It is unusable for a non-technical reviewer.** The point of automated
  de-identification is that the system does the work; today the UI still
  asks the human to re-confirm nearly everything the system already found.
- **It is the mechanism behind a real crash.** A debugging pass (see
  conversation history) confirmed via a real crash log and a direct
  reproduction (20 documents driven through the full tick/tick/approve cycle
  via Streamlit's `AppTest` harness) that per-document review cost is flat,
  not quadratic — but every one of those manual clicks triggers a full-page
  Streamlit rerun, and every rerun currently pays for at least one uncached
  network probe (`generation_status()` pinging Ollama). A batch that requires
  hundreds of clicks means hundreds of avoidable reruns and avoidable network
  probes, which is the exposure window in which the observed "connection
  error" crash (a live reconnect-loop in the log, zero caught exceptions)
  occurred. Reducing click count is therefore not just a UX nicety — it
  shrinks the crash's actual trigger condition.

## Goals

- Cut the default number of manual decisions per document to near zero:
  only genuinely uncertain identifiers should require a click.
- Replace list-based review with inline click-to-redact on highlighted text,
  matching how a human actually reads a document.
- Keep (and strengthen) the audit trail — fewer clicks must not mean weaker
  evidence of human review.
- Reduce the number of full-page reruns a large batch requires, both by
  needing fewer clicks and by not paying avoidable per-rerun costs.
- Change nothing about the underlying detection engine, the "nothing leaves
  this machine" guarantee, or `assert_deidentified()` / placeholder-integrity
  enforcement. This is a presentation/interaction change, not a detection
  change.

## Non-goals

- Not replacing or retuning the detection layers (structured regex,
  Presidio+spaCy, GLiNER, residual scan) — only how their output is surfaced.
- Not building batch-wide multi-document review (per the design discussion,
  review stays one document at a time, just lighter).
- Not changing Step 5 (generation) — a template pick plus a free-text
  instruction is already the only meaningful input there.
- Not adding new infrastructure beyond one small custom Streamlit component.

## Current state (for reference)

- `carescribe/app.py`: `render_entity_table`, `render_flag_decisions`,
  `render_checklist`, `render_approval`, `render_highlighted_preview` —
  the four pieces being consolidated.
- `carescribe/core/review_flags.py` — computes candidate residual spans
  (`candidate_residuals`) from the redacted text; `outstanding()` filters to
  undecided ones.
- `carescribe/core/review_checklist.py` — `describe()` / `build_checklist()`
  / `blocking_reason()` drive the current 2-item checklist and the Approve
  button's disabled state.
- `carescribe/core/batch.py` — `write_review_record()` writes the audit
  record on approval, including the `ticked` checklist keys; `sweep()` is the
  safety-net residual scan run right before write.
- `carescribe/core/generation_status.py` — `generation_status()`, called
  unconditionally on every rerun in `section_handoff()`, not cached.

## Architecture

### 1. Confidence tiering (drives what gets a click at all)

Every detected entity already carries a `type` and comes from one of the
layered detectors. This design needs each entity's confidence classified
into two tiers before it reaches the UI:

- **Auto-redact (no click, no display as an open flag):**
  - Any span from Layer 1 (structured regex) — deterministic pattern
    matches (NHS/MRN numbers, labelled dates, phone numbers, emails,
    postcodes) are pattern-certain by construction.
  - Any span independently confirmed by 2+ detection layers (e.g.
    Presidio+spaCy *and* GLiNER agreeing, or an NER hit reinforced by a
    structured-pattern anchor nearby).
- **Needs a decision (rendered as a clickable highlighted span):**
  - Single-layer NER-only hits (spaCy alone, or GLiNER alone) with no
    corroboration.
  - Every span from the safety-net residual scan (`batch.sweep` /
    `review_flags.candidate_residuals`) — this pass exists specifically to
    catch what the layers above missed, so it is never silently
    auto-resolved; surfacing it is the point.

Implementation note (to verify, not assume, during planning): confirm
whether the current entity/span model already records how many layers hit a
given span (e.g. something `merge_spans`/`_collapse_person_identities`
already tracks during merge), or whether a small addition to the merge step
is needed to expose that. This is additive instrumentation, not a rework of
the merge logic itself.

### 2. One primary review view, not three

Step 3 becomes: the redacted text, rendered once, with only "needs a
decision" spans highlighted and clickable. Nothing else is required reading.

- The full per-identifier table (`render_entity_table`) moves into a
  collapsed `st.expander("Show full detected-identifier table")` — still
  available for anyone who wants to audit everything or hand-correct an
  auto-redacted entry, but no longer part of the required path.
- `render_flag_decisions`' separate list is removed as a separate UI block;
  its content (the still-outstanding flags) becomes exactly the set of spans
  rendered as clickable highlights in the primary view.
- The 2-item checklist (`render_checklist`) is removed. Approve stays
  disabled (via `review_checklist.blocking_reason`, updated accordingly)
  until every "needs a decision" span has an actual decision — the click
  record itself is the evidence of review, not a blind tick box.

### 3. The click-to-redact component

A small custom Streamlit component, e.g. `carescribe/components/highlight_review/`
(a static JS file + a thin Python wrapper — no build toolchain, following
the pattern Streamlit's own docs use for minimal custom components):

- **Python → JS:** the redacted text as HTML with each "needs a decision"
  span wrapped in `<mark data-span-id="...">`, plus a small manifest per
  span (its text, the reason it was flagged, its suggested type).
- **JS:** renders that HTML as-is (matching the current highlighted-preview
  visual style already in `render_highlighted_preview`), attaches a click
  listener to every `<mark>`. On click it sends `{span_id}` back to Streamlit
  through the component's value channel and shows a small inline popover
  anchored at that word with three actions:
  - **Redact** — uses the detected type/placeholder (same effect as today's
    "Redact this").
  - **Not an identifier** — dismiss (same effect as today's "Not an
    identifier", document-scoped only, never saved).
  - **Change type** — a small dropdown, for the rare case the detector
    guessed the wrong entity type.
- **Python receives** the component's return value each rerun. A rerun is
  only triggered when the returned value actually changes (a real click
  happened) — spans that are merely displayed cost nothing extra per rerun.
  This is also the mechanism that fixes the click-count-driven crash risk:
  cost now scales with *actions taken*, not with how many spans are shown.
- Only already-redacted placeholder text and span metadata ever cross into
  the component — never raw PHI — so this introduces no new PHI exposure
  surface beyond what `render_highlighted_preview` already renders today.

### 4. Attestation & audit trail

- The Approve button's disabled state comes from "every needs-a-decision
  span for this document has a decision" (redacted, dismissed, or
  auto-resolved), computed the same way `review_checklist.blocking_reason`
  does today, just without the two generic tick-box keys.
- `batch.write_review_record()` keeps writing an audit record on every
  approval. Its `ticked` field is replaced with what actually happened:
  counts (and which) of auto-redacted vs. manually-redacted vs. dismissed
  spans, and confirmation that the outstanding-flag count was zero at
  approval time. This is a strictly more specific record than two generic
  boolean ticks.
- The "Human review required" warning banner (`render_approval`) stays —
  its meaning shifts from "tick two boxes" to "the highlighted words are
  what to review."

### 5. Crash-risk fixes

- Wrap `generation_status.generation_status()` in a short-TTL cache (e.g.
  `st.cache_data(ttl=5)` — `cache_data`, not `cache_resource`: the return
  value is a small plain dataclass, not a singleton resource, so it should be
  the copy-per-call, time-expiring cache) so the Ollama/filesystem probe it
  makes runs at most once every few seconds, not on every single rerun
  anywhere in the app.
- No further infrastructure changes (no async work, no background threads) —
  the click-count reduction from sections 2–3 is the dominant fix for the
  crash's actual trigger condition (rerun volume during a large batch); the
  cache change closes the one confirmed avoidable per-rerun cost found during
  debugging.

## Testing

- Extend `tests/test_review_gate.py` and `tests/test_app.py` (`AppTest`-based)
  for the new confidence-tiering logic: assert structured-regex and
  multi-layer-agreement spans never appear as clickable flags; assert
  single-layer and residual-scan spans do.
- New tests for the custom component's Python wrapper: given a redacted text
  and a list of "needs a decision" spans, assert the emitted HTML wraps the
  right substrings with the right `data-span-id`s (JS-side click handling is
  not something `AppTest` can exercise directly — cover it with a narrow,
  documented manual/smoke check instead, matching how the project already
  treats other browser-only concerns).
- Extend the batch-crash reproduction approach used during debugging (driving
  N documents through `AppTest`) to confirm per-document rerun count drops
  to roughly one (an Approve click) for the common case of a document with
  no uncertain spans, versus today's baseline.
- `batch.write_review_record()` tests updated for the new record shape.
- Regression: existing `tests/test_stress_corpus.py` / `stress_corpus/`
  corpus must still fully redact everything in `must_redact` — the
  confidence-tiering change must not accidentally auto-*keep* anything that
  should be redacted; when in doubt a span goes to "needs a decision", never
  silently kept.

## Out-of-scope follow-ups (not blocking this work)

- Batch-wide (multi-document) review in one pass — considered and explicitly
  deferred during design; documents stay reviewed one at a time.
- Any change to Step 5 (generation) — already matches the "one big input is
  the prompt" goal.
- Any change to the detection engine's accuracy/tuning.
