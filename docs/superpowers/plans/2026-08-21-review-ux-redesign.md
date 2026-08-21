# Lightweight Review UX Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the per-document entity table + residual-flag list + 2-6 item
checklist with one inline click-to-redact review surface, driven by
confidence-tiered auto-redaction, so a non-technical reviewer needs at most a
handful of clicks per document instead of dozens.

**Architecture:** The detection pipeline gains a `confidence` field
(`"auto"`/`"review"`) per entity, computed from which detection layer(s)
found it. A new small module unifies low-confidence entity placeholders and
the existing residual-flag sweep into one ordered list of clickable spans. A
small custom Streamlit component (hand-rolled postMessage protocol, no CDN,
no build step) renders the redacted text with those spans as clickable
`<mark>` tags and reports which one was clicked back to Python; the resulting
action row (Redact / Confirm / Undo / Change type / Not an identifier) is
plain native Streamlit, reusing the exact same backend calls
(`deidentify.rebuild`, `deidentify.add_manual_entity`) the old per-row UI
already used. The itemized checklist is deleted; Approve unlocks once the
outstanding-span count is zero. `generation_status()` gets a short-TTL cache
to close a confirmed uncached-network-probe-per-rerun cost.

**Tech Stack:** Python 3, Streamlit (incl. `streamlit.components.v1` custom
components), vanilla JS (no framework, no build tool), pytest, Streamlit's
`AppTest` harness.

**Spec:** `docs/superpowers/specs/2026-08-21-review-ux-redesign-design.md`

## Global Constraints

- Nothing leaves the machine. The new component receives only already-derived
  HTML/placeholder text and returns only a span id string — never raw PHI,
  never a network call.
- `document.redacted_text` stays fully safe at all times (this was an
  explicit design decision — see the spec and the conversation this plan
  came from): a low-confidence entity is still redacted immediately on
  analysis, same as today. The click affordance operates on the placeholder,
  never on live un-redacted text. Only the residual-flag mechanism (already
  existing, unchanged) ever shows raw un-redacted text, exactly as it does
  today.
- When in doubt, a span goes to `"review"`, never silently `"auto"`. This
  governs every ambiguous case in Task 1 and is directly regression-tested
  against `stress_corpus/` in Task 8.
- Existing PHI-safety invariants (`assert_deidentified()`,
  `check_placeholder_integrity()`, `residual_scan()`/`batch.sweep()` as the
  final blocking gate before write) are untouched by this plan.

---

## Reference: verified against the real codebase

Facts below were confirmed by reading the actual files during planning —
they are load-bearing for the tasks that follow, not assumptions.

- **`Span` already tracks its detection layer.** `carescribe/core/deidentify.py`:
  `Span.source` is one of `"regex"` (Layer 1, structured), `"ner"`
  (Presidio+spaCy), `"gliner"` (GLiNER), or `"wrapped"` (the line-flattened
  re-run pass, itself internally regex/ner/gliner but relabelled `"wrapped"`
  when its Span is reconstructed at `deidentify.py:1703-1715`). `_SOURCE_RANK
  = {"regex": 0, "gliner": 1, "ner": 2, "wrapped": 3}` already ranks them.
- **But that layer information does not survive into an entity dict today.**
  `merge_spans()` builds entities via
  `{"type": span.entity_type, "value": text[span.start:span.end]}` — no
  `source`. Confidence tiering needs new instrumentation, not a read of
  something already there.
- **Overlap resolution is winner-take-all, not merge.** In `merge_spans()`,
  when multiple layers' spans overlap, only the longest/highest-ranked one
  survives (`occupied` bytearray, `continue` on the rest) — the others are
  discarded outright. To know whether a surviving span was corroborated by a
  second layer, you must check overlap against the pre-dedup `prepared` list
  before it's discarded, not against anything already in `kept`.
- **`mapping.dedupe_entities()` silently drops unknown dict keys.** It
  rebuilds each entity as `{"type": ..., "value": ..., "action": ...}`
  literally — any other key on the input dict (a new `confidence` key
  included) is dropped unless `dedupe_entities` is explicitly updated to
  carry it through. This is the one place a new field can silently vanish.
- **`review_flags.candidate_residuals()` already excludes placeholder
  ranges.** `_placeholder_ranges()`/`blocked()` in `review_flags.py` skip
  anything overlapping `mapping.PLACEHOLDER_RE`. This means residual-flag
  spans and entity-placeholder spans can never overlap by construction — the
  new unified span list in Task 2 does not need its own overlap resolution.
- **`review_checklist.py`'s checklist is adaptive, 2-6 items, not a fixed
  2.** `build_checklist()` always adds `read_full` and `flags_cleared`, then
  conditionally adds `table_cells`, `header_footer`, `relatives`,
  `textboxes`, `dates` depending on `DocFeatures`. All of `ChecklistItem`,
  `DocFeatures`, `describe()`, `build_checklist()` are deleted by this plan
  (see Task 4) — only `blocking_reason()` survives, with a new signature.
- **`PHI_KEYS` in `carescribe/app.py`** (line ~52) currently has
  `"checklist": {}` (filename -> set of ticked keys). This plan replaces that
  entry with `"entity_confirmed": {}` (filename -> set of confirmed entity
  value-keys) — same shape, same wipe-on-clear behavior, different meaning.
  `"flag_dismissed"` and `"flag_redacted"` are untouched — they still track
  the (unchanged) residual-flag mechanism.
- **`batch.write_review_record()`'s current signature** is
  `(name, *, ticked, entities, flags_shown, flags_redacted,
  flags_dismissed) -> Path`. This plan drops `ticked` and computes new
  auto/reviewed counts internally from `entities` (which now carry
  `confidence`) — no new caller-supplied parameter needed.
- **`_FLAG_TINTS`** (app.py line ~530) maps residual-flag kinds to highlight
  colours (`KIND_NAME`→`#fff3bf`, `KIND_ID`→`#ffd8a8`, `KIND_DATE`→`#d0ebff`,
  `KIND_INITIALS`→`#e5dbff`). The new unified rendering in Task 7 reuses
  these exact colours for residual spans, and a new neutral dotted-underline
  style for low-confidence entity spans, so nothing about the existing
  visual language changes for the mechanism reviewers already recognise.
- **`generation_status.generation_status()`** (`carescribe/core/generation_status.py`)
  is called unconditionally, uncached, from two places in
  `section_handoff()` in app.py — once when there are no approved documents
  (line ~1553), once inside `render_generation_panel()` (line ~1118) — both
  reached on every single rerun of the whole app via `main()`'s unconditional
  call chain, regardless of which step the practitioner is actually on. This
  is the confirmed avoidable per-rerun cost from the debugging pass.

---

### Task 1: Confidence tiering in the detection pipeline

**Files:**
- Modify: `carescribe/core/deidentify.py:1621-1642` (inside `merge_spans()`)
- Modify: `carescribe/core/deidentify.py:1822` (inside `add_manual_entity()`)
- Modify: `carescribe/core/mapping.py:177-203` (`dedupe_entities()`)
- Test: `tests/test_deid_pipeline.py`
- Test: `tests/test_mapping.py`

**Interfaces:**
- Produces: every entity dict returned by `deidentify.analyze()` /
  `deidentify.deidentify()` / `deidentify.rebuild()` now has a
  `"confidence"` key, value `"auto"` or `"review"`. Missing/unrecognised
  values normalise to `"review"` (safe default).

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_deid_pipeline.py — add near the other merge_spans-level tests

def test_a_structured_regex_hit_is_auto_confidence():
    """An NHS number is Layer 1 (regex) — pattern-certain, no review needed."""
    text = "NHS number: 943 476 5919"
    entities = deidentify.analyze(text)
    nhs = next(e for e in entities if e["type"] == "NHS_NUMBER")
    assert nhs["confidence"] == "auto"


def test_a_single_layer_ner_only_hit_needs_review():
    """A bare forename with no structural corroboration is single-layer."""
    text = "Zephyrine mentioned she felt better today."
    entities = deidentify.analyze(text)
    person = next((e for e in entities if e["type"] == "PATIENT_NAME" or e["type"] == "PERSON"), None)
    assert person is not None
    assert person["confidence"] == "review"


def test_two_layers_agreeing_is_auto_confidence():
    """GLiNER and Presidio/spaCy both firing on the same span is corroboration."""
    if not (deidentify.USE_NER and deidentify.USE_GLINER):
        pytest.skip("requires both NER and GLiNER installed")
    text = "The patient, Margaret Elizabeth Chen, was reviewed today."
    entities = deidentify.analyze(text)
    person = next(e for e in entities if "Chen" in e["value"])
    assert person["confidence"] == "auto"


def test_a_manually_added_entity_is_auto_confidence():
    """The add action IS the human decision — no second click to confirm it."""
    text = "Seen by the coordinator, Zaphod, today."
    result = deidentify.add_manual_entity(text, [], "Zaphod")
    entity = next(e for e in result.entities if e["value"] == "Zaphod")
    assert entity["confidence"] == "auto"
```

```python
# tests/test_mapping.py — add near the other dedupe_entities tests

def test_dedupe_entities_keeps_confidence():
    entities = [{"type": "PERSON", "value": "Jo Bloggs", "confidence": "auto"}]
    result = mapping.dedupe_entities(entities)
    assert result[0]["confidence"] == "auto"


def test_dedupe_entities_defaults_missing_confidence_to_review():
    entities = [{"type": "PERSON", "value": "Jo Bloggs"}]
    result = mapping.dedupe_entities(entities)
    assert result[0]["confidence"] == "review"


def test_dedupe_entities_worst_case_wins_across_duplicates():
    """If ANY occurrence of a value was low-confidence, the whole entity is."""
    entities = [
        {"type": "PERSON", "value": "Jo Bloggs", "confidence": "auto"},
        {"type": "PERSON", "value": "jo bloggs", "confidence": "review"},
    ]
    result = mapping.dedupe_entities(entities)
    assert len(result) == 1
    assert result[0]["confidence"] == "review"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_deid_pipeline.py -k confidence -v tests/test_mapping.py -k confidence -v`
Expected: FAIL — `KeyError: 'confidence'` or assertion failures, since no
entity carries the field yet.

- [ ] **Step 3: Implement — `mapping.dedupe_entities()`**

Replace the body of `dedupe_entities()` (`carescribe/core/mapping.py:177-203`):

```python
def dedupe_entities(entities: Iterable[dict]) -> list[dict]:
    """Drop blank and duplicate entities, keeping first-seen order and casing.

    Duplicates are matched case-insensitively on the value; the first spelling
    encountered wins, so re-identification restores the document's own casing.
    The reviewer's Redact/Keep choice rides along — a duplicate row must not
    silently re-enable a value they turned off.

    ``confidence`` (``"auto"`` or ``"review"``) rides along too, aggregated
    worst-case: if any occurrence of a value was only ``"review"``-grade, the
    whole deduped entity is ``"review"`` — one weak occurrence means the
    reviewer's single decision for this value has to actually be reviewed.
    Missing or unrecognised confidence defaults to ``"review"``, never
    ``"auto"`` — an entity this function has never seen a confidence claim
    for is not one it will silently wave through.
    """
    seen: dict[str, dict] = {}
    for entity in entities:
        # Collapse internal whitespace so a value the document wrapped across a
        # line ("Oluwaseun\nAdeyinka") is the same entity as the same name
        # written inline. Matching stays whitespace-tolerant either way, but the
        # canonical key, the review table and the approved map all want one
        # spelling rather than two.
        value = " ".join(str(entity.get("value", "") or "").split())
        if len(value) < MIN_VALUE_LENGTH:
            continue
        key = value.casefold()
        confidence = str(entity.get("confidence") or "review")
        if confidence != "auto":
            confidence = "review"
        if key in seen:
            if confidence != "auto":
                seen[key]["confidence"] = "review"
            continue
        seen[key] = {
            "type": normalise_type(entity.get("type")),
            "value": value,
            "action": normalise_action(entity.get("action")),
            "confidence": confidence,
        }
    return list(seen.values())
```

- [ ] **Step 4: Implement — `deidentify.merge_spans()` confidence tiering**

In `carescribe/core/deidentify.py`, replace lines 1621-1642 (from
`prepared.sort(` through the `entities = mapping.dedupe_entities(...)` call)
with:

```python
    prepared.sort(
        key=lambda s: (
            -(s.end - s.start),
            _SOURCE_RANK.get(s.source, 9),
            -s.score,
            s.start,
        )
    )

    occupied = bytearray(len(text))
    kept: list[Span] = []
    for span in prepared:
        if any(occupied[span.start : span.end]):
            continue
        occupied[span.start : span.end] = b"\x01" * (span.end - span.start)
        kept.append(span)

    kept.sort(key=lambda s: s.start)

    def _confidence(span: Span) -> str:
        """"auto" if this span is safe to redact with no manual decision.

        Layer 1 (regex) is pattern-certain by construction. Anything else is
        "auto" only if a second, independent layer's candidate also covered
        this exact region while spans were still being resolved — real
        corroboration, not just one layer's guess. Checked against
        ``prepared`` (every candidate, before the occupied-bytearray dedup
        above threw the losers away), because ``kept`` only has the single
        surviving span per region and has already lost that information.
        """
        if span.source == "regex":
            return "auto"
        sources = {
            other.source
            for other in prepared
            if other.start < span.end and span.start < other.end
        }
        return "auto" if len(sources) >= 2 else "review"

    entities = mapping.dedupe_entities(
        {
            "type": span.entity_type,
            "value": text[span.start : span.end],
            "confidence": _confidence(span),
        }
        for span in kept
    )
```

- [ ] **Step 5: Implement — `add_manual_entity()` auto-confidence**

In `carescribe/core/deidentify.py:1822`, change:

```python
    rows.append({"type": mapping.normalise_type(entity_type), "value": value, "placeholder": ""})
```

to:

```python
    rows.append({
        "type": mapping.normalise_type(entity_type),
        "value": value,
        "placeholder": "",
        "confidence": "auto",
    })
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/test_deid_pipeline.py tests/test_mapping.py -v`
Expected: PASS, including all pre-existing tests in both files (this change
is additive to the entity dict shape — nothing existing reads a `confidence`
key today, so nothing existing should break; verify by running the full
files, not just the new tests).

- [ ] **Step 7: Commit**

```bash
git add carescribe/core/deidentify.py carescribe/core/mapping.py tests/test_deid_pipeline.py tests/test_mapping.py
git commit -m "feat: add confidence tiering (auto/review) to detected entities"
```

---

### Task 2: Unified review-span module

**Files:**
- Create: `carescribe/core/review_spans.py`
- Test: `tests/test_review_spans.py`

**Interfaces:**
- Consumes: `review_flags.candidate_residuals(text) -> list[Flag]`,
  `review_flags.outstanding(flags, dismissed) -> list[Flag]` (existing,
  unchanged); `mapping.normalise_action`, `mapping.REDACT` (existing);
  entity dicts with the `confidence` key from Task 1.
- Produces: `ReviewSpan` dataclass (`id: str`, `char_start: int`,
  `char_end: int`, `kind: str`, `text: str`, `why: str`, `entity_type: str
  = ""`, `flag_kind: str = ""`), constants `KIND_ENTITY = "entity"`,
  `KIND_RESIDUAL = "residual"`, and
  `review_spans(redacted_text, entities, confirmed, dismissed=()) ->
  list[ReviewSpan]` — the one function later tasks call to get "everything
  this document still needs a decision on."

- [ ] **Step 1: Write the failing test**

```python
# tests/test_review_spans.py
from carescribe.core import mapping, review_spans


def _entity(value, entity_type="PERSON", confidence="review", placeholder=None, action=mapping.REDACT):
    return {
        "type": entity_type,
        "value": value,
        "confidence": confidence,
        "action": action,
        "placeholder": placeholder or f"[{entity_type}]",
    }


def test_auto_confidence_entities_produce_no_span():
    text = "Seen by [PROVIDER_1] today."
    spans = review_spans.review_spans(
        text, [_entity("Dr Ng", "PROVIDER_1", confidence="auto", placeholder="[PROVIDER_1]")], set(),
    )
    assert spans == []


def test_review_confidence_entity_produces_an_entity_span_at_its_placeholder():
    text = "Seen by [PATIENT] today."
    spans = review_spans.review_spans(
        text, [_entity("Jo Bloggs", "PATIENT", confidence="review", placeholder="[PATIENT]")], set(),
    )
    assert len(spans) == 1
    span = spans[0]
    assert span.kind == review_spans.KIND_ENTITY
    assert text[span.char_start:span.char_end] == "[PATIENT]"
    assert span.id == "entity:jo bloggs"


def test_a_confirmed_entity_produces_no_span():
    text = "Seen by [PATIENT] today."
    entity = _entity("Jo Bloggs", "PATIENT", confidence="review", placeholder="[PATIENT]")
    spans = review_spans.review_spans(text, [entity], {"jo bloggs"})
    assert spans == []


def test_every_occurrence_of_a_repeated_placeholder_is_a_span():
    text = "[PATIENT] was seen. [PATIENT] improved."
    entity = _entity("Jo Bloggs", "PATIENT", confidence="review", placeholder="[PATIENT]")
    spans = review_spans.review_spans(text, [entity], set())
    assert len(spans) == 2
    assert all(s.id == "entity:jo bloggs" for s in spans)


def test_a_kept_entity_produces_no_span():
    """action=Keep means the reviewer already decided — nothing to click."""
    text = "Bolton was mentioned."
    entity = _entity("Bolton", "LOCATION", confidence="review", placeholder="[LOCATION]", action=mapping.KEEP)
    spans = review_spans.review_spans(text, [entity], set())
    assert spans == []


def test_residual_flags_appear_as_residual_spans():
    text = "Contact Adeyinka on arrival."
    spans = review_spans.review_spans(text, [], set())
    assert any(s.kind == review_spans.KIND_RESIDUAL and s.text == "Adeyinka" for s in spans)


def test_dismissed_residual_flags_are_excluded():
    text = "Contact Adeyinka on arrival."
    from carescribe.core import review_flags
    flag = review_flags.candidate_residuals(text)[0]
    spans = review_spans.review_spans(text, [], set(), dismissed=[flag.key])
    assert spans == []


def test_spans_are_sorted_by_position():
    text = "[PATIENT] met Adeyinka."
    entity = _entity("Jo Bloggs", "PATIENT", confidence="review", placeholder="[PATIENT]")
    spans = review_spans.review_spans(text, [entity], set())
    assert [s.char_start for s in spans] == sorted(s.char_start for s in spans)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_review_spans.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'carescribe.core.review_spans'`

- [ ] **Step 3: Write the implementation**

```python
# carescribe/core/review_spans.py
"""
Unifies the two things a reviewer might still need to act on in one
document's redacted text into one clickable, ordered list.

The two sources are different in kind. A low-confidence *entity* was already
found and already redacted (Task 1's confidence tiering just isn't sure about
it) — the reviewer is confirming or correcting a placeholder that is already
safe. A *residual* candidate (:mod:`.review_flags`) is the opposite: raw text
the layers missed entirely, still sitting un-redacted in what is nominally
"redacted" text. Both need a human decision; this module is only the part
that merges them into one span list so the UI has a single thing to render.

Kept separate from :mod:`.review_flags` on purpose: that module's job is the
permissive text-pattern sweep itself, one thing done well. This module's job
is purely the merge.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import mapping, review_flags

KIND_ENTITY = "entity"
KIND_RESIDUAL = "residual"


@dataclass(frozen=True)
class ReviewSpan:
    """One clickable span in a document's redacted text."""

    id: str
    char_start: int
    char_end: int
    kind: str  # KIND_ENTITY or KIND_RESIDUAL
    text: str  # the placeholder ("[PATIENT_2]") for an entity span,
    # the raw candidate text for a residual span
    why: str
    entity_type: str = ""  # set for KIND_ENTITY only
    flag_kind: str = ""  # set for KIND_RESIDUAL only — review_flags.KIND_*


def _entity_spans(
    redacted_text: str, entities: list[dict], confirmed: set[str]
) -> list[ReviewSpan]:
    """Placeholder occurrences for low-confidence, not-yet-confirmed entities."""
    spans: list[ReviewSpan] = []
    for entity in entities:
        if mapping.normalise_action(entity.get("action")) != mapping.REDACT:
            continue
        if str(entity.get("confidence") or "review") != "review":
            continue
        value_key = str(entity.get("value", "")).strip().casefold()
        if not value_key or value_key in confirmed:
            continue
        placeholder = str(entity.get("placeholder", "") or "")
        if not placeholder:
            continue
        entity_type = str(entity.get("type", "OTHER_ID"))
        start = 0
        while True:
            found = redacted_text.find(placeholder, start)
            if found == -1:
                break
            spans.append(
                ReviewSpan(
                    id=f"entity:{value_key}",
                    char_start=found,
                    char_end=found + len(placeholder),
                    kind=KIND_ENTITY,
                    text=placeholder,
                    why=f"detected as {entity_type} by a single layer — worth a second look",
                    entity_type=entity_type,
                )
            )
            start = found + len(placeholder)
    return spans


def _residual_spans(
    redacted_text: str, dismissed: list[str] | tuple[str, ...]
) -> list[ReviewSpan]:
    flags = review_flags.outstanding(
        review_flags.candidate_residuals(redacted_text), dismissed
    )
    return [
        ReviewSpan(
            id=f"residual:{flag.key}",
            char_start=flag.char_start,
            char_end=flag.char_end,
            kind=KIND_RESIDUAL,
            text=flag.text,
            why=flag.why,
            flag_kind=flag.kind,
        )
        for flag in flags
    ]


def review_spans(
    redacted_text: str,
    entities: list[dict],
    confirmed: set[str],
    dismissed: list[str] | tuple[str, ...] = (),
) -> list[ReviewSpan]:
    """Every clickable span in ``redacted_text``, in reading order.

    ``confirmed`` is the set of (casefolded) entity values the reviewer has
    already clicked "Confirm" on for this document. ``dismissed`` is the
    existing per-document dismissed-residual-flag list
    (:func:`carescribe.app.flag_dismissals`), unchanged from today.
    """
    spans = _entity_spans(redacted_text, entities, confirmed)
    spans.extend(_residual_spans(redacted_text, dismissed))
    spans.sort(key=lambda span: span.char_start)
    return spans


__all__ = ["KIND_ENTITY", "KIND_RESIDUAL", "ReviewSpan", "review_spans"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_review_spans.py -v`
Expected: PASS, all 9 tests.

- [ ] **Step 5: Commit**

```bash
git add carescribe/core/review_spans.py tests/test_review_spans.py
git commit -m "feat: add review_spans module unifying entity and residual review targets"
```

---

### Task 3: Click-to-redact custom Streamlit component

**Files:**
- Create: `carescribe/components/__init__.py`
- Create: `carescribe/components/highlight_review/__init__.py`
- Create: `carescribe/components/highlight_review/frontend/index.html`
- Test: `tests/test_highlight_review_component.py`

**Interfaces:**
- Produces: `highlight_review(html: str, *, key: str | None = None) -> str
  | None` — renders `html` (expected to contain `<mark
  data-span-id="...">...</mark>` tags) inside the component's iframe and
  returns the `data-span-id` of whichever `<mark>` was most recently
  clicked, or `None` if nothing has been clicked yet in this widget's
  lifetime.

This is a "no build tool" custom component: `declare_component(...,
path=...)` serves a directory of static files directly, no npm/webpack
involved. The frontend hand-rolls Streamlit's component postMessage protocol
in vanilla JS rather than pulling in `streamlit-component-lib` from a CDN —
this app is offline-first, and a CDN script tag would be a network
dependency on every render, which is exactly the kind of thing this
codebase explicitly avoids everywhere else (see `carescribe/core/ollama_client.py`'s
module docstring on why even an installed package is kept off the
dependency list). The protocol itself (`streamlit:componentReady`,
`streamlit:render`, `streamlit:setComponentValue`, `streamlit:setFrameHeight`)
is Streamlit's own stable, documented low-level component message contract.

- [ ] **Step 1: Write the failing test**

Component click-handling itself is browser JS and out of `AppTest`'s reach
(same category of thing this codebase already treats as a documented,
narrow manual-check gap — see how `has_text_boxes` review is handled). What
*is* testable without a browser: that the Python wrapper is importable,
declares the component correctly, and returns `None` by default.

```python
# tests/test_highlight_review_component.py
from pathlib import Path

from carescribe.components.highlight_review import highlight_review


def test_frontend_file_exists():
    frontend = Path(__file__).resolve().parent.parent / "carescribe" / "components" / "highlight_review" / "frontend" / "index.html"
    assert frontend.exists()


def test_frontend_has_no_external_script_or_link_tags():
    """Offline-first: nothing in this file may fetch from a CDN."""
    frontend = Path(__file__).resolve().parent.parent / "carescribe" / "components" / "highlight_review" / "frontend" / "index.html"
    text = frontend.read_text(encoding="utf-8")
    assert "http://" not in text
    assert "https://" not in text


def test_wrapper_is_callable_and_importable():
    assert callable(highlight_review)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_highlight_review_component.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write `carescribe/components/__init__.py`**

```python
"""Custom Streamlit components used by the CareScribe UI."""
```

- [ ] **Step 4: Write `carescribe/components/highlight_review/frontend/index.html`**

```html
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<style>
  html, body { margin: 0; padding: 0; }
  body {
    font-family: ui-monospace, "Cascadia Code", "Consolas", monospace;
    font-size: 0.82rem;
    line-height: 1.6;
  }
  #doc {
    white-space: pre-wrap;
    padding: 10px;
    max-height: 360px;
    overflow: auto;
    border: 1px solid rgba(128, 128, 128, .35);
    border-radius: 6px;
  }
  mark {
    cursor: pointer;
  }
  mark:hover {
    outline: 2px solid #495057;
  }
</style>
</head>
<body>
<div id="doc"></div>
<script>
  // Streamlit's component postMessage protocol, hand-rolled — no external
  // library, no CDN. Three message types out (componentReady,
  // setComponentValue, setFrameHeight), one in (render).
  function sendValue(value) {
    window.parent.postMessage({ type: "streamlit:setComponentValue", value: value }, "*");
  }

  function setFrameHeight() {
    window.parent.postMessage(
      { type: "streamlit:setFrameHeight", height: document.documentElement.scrollHeight },
      "*"
    );
  }

  function onRender(event) {
    var args = (event.data && event.data.args) || {};
    var doc = document.getElementById("doc");
    doc.innerHTML = args.html || "";
    var marks = doc.querySelectorAll("mark[data-span-id]");
    for (var i = 0; i < marks.length; i++) {
      marks[i].addEventListener("click", (function (mark) {
        return function () {
          sendValue(mark.getAttribute("data-span-id"));
        };
      })(marks[i]));
    }
    setFrameHeight();
  }

  window.addEventListener("message", function (event) {
    if (event.data && event.data.type === "streamlit:render") {
      onRender(event);
    }
  });

  window.parent.postMessage({ type: "streamlit:componentReady", apiVersion: 1 }, "*");
  setFrameHeight();
</script>
</body>
</html>
```

- [ ] **Step 5: Write `carescribe/components/highlight_review/__init__.py`**

```python
"""
Click-to-redact highlighted text.

Renders already-redacted (or already-flagged) text with clickable
``<mark data-span-id="...">`` spans, and reports which one the reviewer
clicked. Everything that crosses into or out of this component is already
placeholder text or a span id string — never raw PHI. See ``frontend/index.html``
for the (hand-rolled, no external dependency) client side.
"""

from __future__ import annotations

import os

import streamlit.components.v1 as components

_FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
_component = components.declare_component("highlight_review", path=_FRONTEND_DIR)


def highlight_review(html: str, *, key: str | None = None) -> str | None:
    """Render ``html`` and return the ``data-span-id`` of the last click.

    Returns ``None`` until the reviewer has clicked a highlighted span at
    least once for this widget instance.
    """
    return _component(html=html, key=key, default=None)


__all__ = ["highlight_review"]
```

- [ ] **Step 6: Run test to verify it passes**

Run: `pytest tests/test_highlight_review_component.py -v`
Expected: PASS, all 3 tests.

- [ ] **Step 7: Manual smoke check (required — this is the one part no
      automated test in this codebase can cover)**

Run a throwaway script to confirm the click round-trip actually works in a
real browser before Task 7 wires this into the main app:

```python
# scratch_smoke_test.py — not committed, delete after use
import streamlit as st
from carescribe.components.highlight_review import highlight_review

html = 'Seen by <mark data-span-id="a">Dr Ng</mark> on <mark data-span-id="b">12/04/1985</mark>.'
clicked = highlight_review(html, key="smoke")
st.write("Clicked:", clicked)
```

Run: `streamlit run scratch_smoke_test.py`, click each highlighted word in
the browser, confirm `st.write` shows the matching span id after each
click. If it does not: the most likely gap is a Streamlit-version
difference in the exact `postMessage` message shape — check the installed
`streamlit` version's `frontend/src/streamlit.tsx` (or the component docs
for that version) for the current `RENDER_EVENT`/`setComponentValue`
contract and adjust `index.html` accordingly. Do not proceed to Task 7
until this passes.

- [ ] **Step 8: Commit**

```bash
git add carescribe/components/
git commit -m "feat: add click-to-redact custom Streamlit component"
```

---

### Task 4: Simplify `review_checklist.py` to a two-input gate

**Files:**
- Modify: `carescribe/core/review_checklist.py` (whole file)
- Modify: `tests/test_review_gate.py`

**Interfaces:**
- Produces: `blocking_reason(residual: list[str], outstanding: int) -> str`
  — everything else in the module's current public surface
  (`ChecklistItem`, `DocFeatures`, `describe`, `build_checklist`) is
  deleted; nothing later in this plan calls them.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_review_gate.py — replace the checklist-era tests (see Step 4)
# with these, testing the new two-input blocking_reason directly

from carescribe.core import review_checklist


def test_blocking_reason_empty_when_nothing_outstanding():
    assert review_checklist.blocking_reason([], 0) == ""


def test_blocking_reason_reports_residual_first():
    reason = review_checklist.blocking_reason(["Bolton"], 3)
    assert "1 finding" in reason


def test_blocking_reason_reports_outstanding_spans():
    reason = review_checklist.blocking_reason([], 2)
    assert "2" in reason and "span" in reason
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_review_gate.py -k blocking_reason -v`
Expected: FAIL — `TypeError: blocking_reason() missing 2 required positional
arguments` (the old 4-arg signature is still in place).

- [ ] **Step 3: Replace `carescribe/core/review_checklist.py`**

```python
"""
The approval gate.

Approval unlocks once nothing is outstanding: the blocking safety sweep
found nothing, and every clickable span the reviewer was shown has a
decision (redacted, confirmed, dismissed, or corrected). The click record
itself — the redact/confirm/dismiss decisions logged per document — is the
evidence a review happened; there is no separate itemised checklist to tick.
"""

from __future__ import annotations


def blocking_reason(residual: list[str], outstanding: int) -> str:
    """Why Approve is disabled, in one short line. Empty string means it isn't."""
    if residual:
        return f"The safety sweep found {len(residual)} finding(s) to resolve."
    if outstanding:
        return f"{outstanding} highlighted span(s) still need a decision."
    return ""


__all__ = ["blocking_reason"]
```

- [ ] **Step 4: Delete the now-obsolete checklist tests**

In `tests/test_review_gate.py`, delete these tests — they exercise
`describe()`/`build_checklist()`/`ChecklistItem`/`DocFeatures`, all removed
in Step 3:

- `test_a_clean_plain_note_asks_only_the_two_always_items`
- `test_a_risky_document_earns_the_extra_items`
- `test_the_flags_item_is_unsatisfiable_while_a_flag_is_outstanding`
- `test_the_flags_item_satisfies_once_every_flag_is_decided`
- `test_features_are_derived_from_the_document`
- `test_approval_is_blocked_until_every_item_is_ticked`
- `test_a_clean_note_needs_only_two_ticks_end_to_end`

Update these — they test real gate behaviour that still applies, just
through the new 2-arg `blocking_reason`:

```python
def test_approval_is_blocked_while_a_flag_is_outstanding():
    reason = review_checklist.blocking_reason([], 1)
    assert reason != ""


def test_approval_is_blocked_while_the_sweep_has_findings():
    reason = review_checklist.blocking_reason(["Some Name"], 0)
    assert reason != ""


def test_approval_unblocks_once_everything_is_resolved():
    reason = review_checklist.blocking_reason([], 0)
    assert reason == ""


def test_the_gate_unblocks_after_dismissing_the_last_flag():
    # Was: blocking_reason(items, ticked, residual, flags_outstanding)
    # with flags_outstanding going 1 -> 0 after the last dismissal.
    assert review_checklist.blocking_reason([], 1) != ""
    assert review_checklist.blocking_reason([], 0) == ""
```

Leave `test_the_sidecar_records_the_review`, `test_the_sidecar_tallies_placeholders_by_type`,
`test_the_sidecar_contains_no_identifier_value`, `test_the_sidecar_contains_no_mapping`,
`test_no_corpus_identifier_reaches_the_sidecar`, and
`test_the_app_registers_the_new_state_keys_for_wiping` in place for now —
Task 5 and Task 7 update them.

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_review_gate.py -v`
Expected: The tests touched in Steps 3-4 PASS. Tests referencing `ticked=`
or `PHI_KEYS["checklist"]` still FAIL at this point — Task 5 and Task 7 fix
those; do not chase them here.

- [ ] **Step 6: Commit**

```bash
git add carescribe/core/review_checklist.py tests/test_review_gate.py
git commit -m "refactor: replace itemised checklist with a two-input approval gate"
```

---

### Task 5: Update `batch.write_review_record()` for the new attestation model

**Files:**
- Modify: `carescribe/core/batch.py:292-337`
- Modify: `tests/test_batch.py`
- Modify: `tests/test_review_gate.py`

**Interfaces:**
- Produces: `write_review_record(name, *, entities, flags_shown,
  flags_redacted, flags_dismissed) -> Path` — `ticked` parameter removed.
  Record shape gains `"identifiers_auto_redacted": int` and
  `"identifiers_reviewed_by_practitioner": int`, replacing
  `"checklist_confirmed"`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_batch.py

def test_review_record_counts_auto_vs_reviewed_identifiers(tmp_path, monkeypatch):
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path)
    entities = [
        {"type": "PROVIDER_NAME", "value": "Dr Ng", "action": "Redact", "confidence": "auto"},
        {"type": "PATIENT_NAME", "value": "Jo Bloggs", "action": "Redact", "confidence": "review"},
        {"type": "LOCATION", "value": "Bolton", "action": "Keep", "confidence": "review"},
    ]
    path = batch.write_review_record(
        "doc.txt", entities=entities, flags_shown=0, flags_redacted=0, flags_dismissed=0,
    )
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["identifiers_auto_redacted"] == 1
    assert record["identifiers_reviewed_by_practitioner"] == 1
    assert "checklist_confirmed" not in record
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_batch.py -k auto_vs_reviewed -v`
Expected: FAIL — `TypeError: write_review_record() missing 1 required
keyword-only argument: 'ticked'`.

- [ ] **Step 3: Implement**

Replace `carescribe/core/batch.py:292-330` (`write_review_record`'s
signature through the `record = {...}` block):

```python
def write_review_record(
    name: str,
    *,
    entities,
    flags_shown: int,
    flags_redacted: int,
    flags_dismissed: int,
) -> Path:
    """Write the no-PHI audit sidecar for one approved document.

    Evidence that a consistent review happened, and nothing more. It records
    *counts* and *types*: how many redacted identifiers were auto-resolved
    by confidence tiering versus actually reviewed by the practitioner, how
    many highlighted residual spans were shown and what became of them, and
    how many placeholders of each type the document ended up with.

    It deliberately holds no identifier value, no placeholder-to-value mapping,
    and no document text. There is no parameter through which one could reach
    it — the entity values are counted here and discarded, never written.
    """
    tally: dict[str, int] = {}
    auto_redacted = 0
    reviewed_redacted = 0
    for entity in entities or []:
        entity_type = str(entity.get("type", "") or "OTHER_ID")
        if mapping.normalise_action(entity.get("action")) != mapping.REDACT:
            continue
        tally[entity_type] = tally.get(entity_type, 0) + 1
        if str(entity.get("confidence", "review")) == "auto":
            auto_redacted += 1
        else:
            reviewed_redacted += 1

    record = {
        "document": Path(name).name,
        "reviewed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "identifiers_auto_redacted": auto_redacted,
        "identifiers_reviewed_by_practitioner": reviewed_redacted,
        "candidate_flags": {
            "shown": int(flags_shown),
            "redacted": int(flags_redacted),
            "dismissed": int(flags_dismissed),
        },
        "placeholders_by_type": dict(sorted(tally.items())),
        "contains_phi": False,
    }
```

(The `OUTPUT_DIR.mkdir(...)` / write / `return destination` lines immediately
below are unchanged.)

- [ ] **Step 4: Update the two existing callers in `tests/test_review_gate.py`**

Line ~235 — change:
```python
        ticked=["read_full", "flags_cleared", "table_cells"],
```
to nothing (delete the line; the surrounding `write_review_record(...)` call
keeps its other keyword arguments).

Line ~293 — change:
```python
        "corpus.txt", ticked=["read_full"], entities=entities,
```
to:
```python
        "corpus.txt", entities=entities,
```

Update `test_the_sidecar_records_the_review` and any assertion in that file
checking `record["checklist_confirmed"]` to instead check
`record["identifiers_auto_redacted"]` / `record["identifiers_reviewed_by_practitioner"]`
are present and are `int`s (read the surrounding test to match its existing
`record` fixture shape rather than guessing — it is parametrized via a
`record` fixture near the top of the sidecar test block).

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_batch.py tests/test_review_gate.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add carescribe/core/batch.py tests/test_batch.py tests/test_review_gate.py
git commit -m "feat: record auto-redacted vs practitioner-reviewed counts in the review sidecar"
```

---

### Task 6: Cache `generation_status()`

**Files:**
- Modify: `carescribe/core/generation_status.py:66`
- Test: `tests/test_generation_setup.py`

**Interfaces:**
- Produces: `generation_status()` unchanged in signature/return type — only
  gains a `st.cache_data(ttl=5)` decorator. Callers in app.py are
  unaffected; this task alone is what closes the confirmed
  uncached-per-rerun-network-probe cost.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_generation_setup.py

def test_generation_status_is_cached(monkeypatch):
    """A second call within the TTL must not re-probe Ollama."""
    from carescribe.core import generation_status, ollama_client

    calls = {"n": 0}

    def fake_is_up():
        calls["n"] += 1
        return False

    monkeypatch.setattr(ollama_client, "is_up", fake_is_up)
    generation_status.generation_status.clear()  # st.cache_data API
    generation_status.generation_status()
    generation_status.generation_status()
    assert calls["n"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_generation_setup.py -k is_cached -v`
Expected: FAIL — `calls["n"] == 2` (no caching yet), or `AttributeError:
'function' object has no attribute 'clear'` (not decorated yet).

- [ ] **Step 3: Implement**

In `carescribe/core/generation_status.py`, add the import and decorator:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import streamlit as st

from . import backends, desktop, ollama_client
```

and change:

```python
def generation_status() -> Status:
```

to:

```python
@st.cache_data(ttl=5)
def generation_status() -> Status:
```

Update the docstring's first line from "Cheap enough to call on entering the
panel." to:

```python
    """Inspect what is available, cached for 5 seconds.

    Called unconditionally on every rerun regardless of which step the
    practitioner is on, so this is cached rather than merely "cheap" — an
    uncached call here was a confirmed source of avoidable per-rerun cost
    during a large review batch. The Ollama probe is a loopback HTTP call to
    a daemon already running on this machine — it never leaves the box, and
    it fails closed to "not running".
    """
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_generation_setup.py -v`
Expected: PASS, including all pre-existing tests in the file (adding a cache
decorator must not change any returned value — re-run the full file, not
just the new test, to confirm).

- [ ] **Step 5: Commit**

```bash
git add carescribe/core/generation_status.py tests/test_generation_setup.py
git commit -m "perf: cache generation_status() to stop probing Ollama on every rerun"
```

---

### Task 7: Wire the new review surface into `carescribe/app.py`

**Files:**
- Modify: `carescribe/app.py` (see exact regions below)
- Test: `tests/test_app.py`

**Interfaces:**
- Consumes: `review_spans.review_spans` (Task 2),
  `highlight_review` (Task 3), `review_checklist.blocking_reason` (Task 4),
  `batch.write_review_record` (Task 5) — all with the signatures those
  tasks produced.
- Produces: `render_review(document) -> int` (returns the outstanding-span
  count), `entity_confirmed(document) -> set[str]` (mirrors the existing
  `flag_dismissals(document) -> list[str]` pattern at app.py:547-548).

- [ ] **Step 1: Update imports and `PHI_KEYS`**

At `carescribe/app.py:35-38`, change:

```python
from carescribe.core import (  # noqa: E402
    applog, backends, batch, carenotes, deidentify, desktop, generation_status,
    ingest, mapping, model_setup, ollama_client, review_checklist, review_flags,
)
```

to:

```python
from carescribe.core import (  # noqa: E402
    applog, backends, batch, carenotes, deidentify, desktop, generation_status,
    ingest, mapping, model_setup, ollama_client, review_checklist, review_flags,
    review_spans,
)
from carescribe.components.highlight_review import highlight_review  # noqa: E402
```

At `carescribe/app.py:52-70` (`PHI_KEYS`), change:

```python
    "checklist": {},        # filename -> set of ticked checklist keys
```

to:

```python
    "entity_confirmed": {}, # filename -> set of confirmed low-confidence entity value-keys
```

- [ ] **Step 2: Add `entity_confirmed()` helper next to `flag_dismissals()`**

At `carescribe/app.py:547-548`, immediately after `flag_dismissals`, add:

```python
def entity_confirmed(document: batch.Document) -> set[str]:
    return st.session_state.entity_confirmed.setdefault(document.name, set())
```

- [ ] **Step 3: Replace `render_highlighted_preview` + `render_flag_decisions`
      + `render_checklist` with one `render_review`**

Delete `render_highlighted_preview` (app.py:551-599),
`render_flag_decisions` (app.py:602-638), and `render_checklist`
(app.py:641-668) in full — every line of behaviour they had is reproduced
(residual redact/dismiss unchanged; low-confidence entity confirm/undo/retype
new) by the two functions below. Insert both in their place, keeping the
existing `_FLAG_TINTS` dict above them:

```python
def _review_span_style(span: review_spans.ReviewSpan) -> str:
    if span.kind == review_spans.KIND_ENTITY:
        # Already redacted, already safe — a dotted underline says "worth a
        # second look", not "this is exposed text", which the solid tints
        # below correctly reserve for residual (never-redacted) candidates.
        return "border-bottom:2px dotted #868e96;padding:0 1px"
    tint = _FLAG_TINTS.get(span.flag_kind, "#f1f3f5")
    return f"background:{tint};padding:0 2px;border-radius:2px"


def _render_review_html(document: batch.Document, spans: list) -> str:
    text = document.redacted_text
    parts: list[str] = []
    cursor = 0
    for span in spans:
        parts.append(html.escape(text[cursor : span.char_start]))
        parts.append(
            f'<mark data-span-id="{html.escape(span.id)}" '
            f'style="{_review_span_style(span)}" '
            f'title="{html.escape(span.why)}">'
            f'{html.escape(text[span.char_start : span.char_end])}</mark>'
        )
        cursor = span.char_end
    parts.append(html.escape(text[cursor:]))
    return "".join(parts)


def render_review(document: batch.Document) -> int:
    """The single primary review surface: highlighted text, click to decide.

    Returns how many spans are still outstanding, so the caller can drive
    the Approve gate without recomputing this list a second time.
    """
    spans = review_spans.review_spans(
        document.redacted_text, document.entities,
        entity_confirmed(document), flag_dismissals(document),
    )

    st.markdown("#### Redacted preview")
    st.caption("This exact text is what approval writes to disk.")
    if spans:
        st.caption(
            f"{len(spans)} span(s) need a decision — click a highlighted word below."
        )
    else:
        st.caption("Nothing needs a second look in this document.")

    clicked = highlight_review(
        _render_review_html(document, spans), key=f"hl_{document.name}"
    )
    _render_span_action(document, spans, clicked)

    # The interactive view above is the working copy; this is the plain,
    # authoritative, copy-pasteable text — the same role the old
    # render_highlighted_preview's second st.text_area played, kept
    # unstyled and disabled on purpose so it's never mistaken for editable.
    st.text_area(
        "Redacted", document.redacted_text, height=200,
        label_visibility="collapsed", disabled=True,
        key=f"preview_exact_{document.name}",
    )

    with st.expander("Show full detected-identifier table"):
        render_entity_table(document)

    return len(spans)


def _render_span_action(document: batch.Document, spans: list, clicked_id: str | None) -> None:
    if not clicked_id:
        return
    match = next((s for s in spans if s.id == clicked_id), None)
    if match is None:
        return  # already resolved by an earlier click this session

    st.markdown(f"**`{match.text}`** — {match.why}")

    if match.kind == review_spans.KIND_ENTITY:
        value_key = clicked_id.split(":", 1)[1]
        confirm_col, undo_col, retype_col = st.columns([1, 1, 2])
        with confirm_col:
            if st.button("✅ Confirm", key=f"conf_{document.name}_{value_key}"):
                entity_confirmed(document).add(value_key)
                st.rerun()
        with undo_col:
            if st.button("↩ Undo (restore text)", key=f"undo_{document.name}_{value_key}"):
                for entity in document.entities:
                    if entity["value"].strip().casefold() == value_key:
                        entity["action"] = mapping.KEEP
                refresh(document, document.entities)
                st.rerun()
        with retype_col:
            new_type = st.selectbox(
                "Change type", list(mapping.ENTITY_TYPES),
                key=f"retype_{document.name}_{value_key}", label_visibility="collapsed",
            )
            if st.button("Apply type", key=f"retype_go_{document.name}_{value_key}"):
                for entity in document.entities:
                    if entity["value"].strip().casefold() == value_key:
                        entity["type"] = new_type
                refresh(document, document.entities)
                st.rerun()
    else:
        flag_key = clicked_id.split(":", 1)[1]
        redact_col, dismiss_col = st.columns(2)
        with redact_col:
            if st.button("Redact this", key=f"resred_{document.name}_{flag_key}"):
                try:
                    result = deidentify.add_manual_entity(
                        document.raw_text, document.entities, match.text
                    )
                except deidentify.DeidentificationError as exc:
                    st.error(str(exc))
                else:
                    document.entities = result.entities
                    document.redacted_text = result.redacted_text
                    document.phi_map = result.phi_map
                    document.approved = False
                    st.session_state.flag_redacted[document.name] = (
                        st.session_state.flag_redacted.get(document.name, 0) + 1
                    )
                    st.rerun()
        with dismiss_col:
            if st.button("Not an identifier", key=f"resdis_{document.name}_{flag_key}"):
                flag_dismissals(document).append(flag_key)
                st.rerun()
```

- [ ] **Step 4: Update `section_review()` to call `render_review` instead of
      `render_highlighted_preview`**

At `carescribe/app.py:799-805`, change:

```python
    left, right = st.columns(2)
    with left:
        render_entity_table(document)
    with right:
        st.markdown("#### Redacted preview")
        st.caption("This exact text is what approval writes to disk.")
        render_highlighted_preview(document)

    render_flag_decisions(document)
    render_add_missed(document)
    render_coverage(document)
```

to:

```python
    outstanding = render_review(document)
    render_add_missed(document)
    render_coverage(document)
```

(`render_entity_table` no longer renders directly in `section_review` — it
now only renders inside `render_review`'s collapsed expander. `outstanding`
is threaded through to `render_approval` in Step 5, replacing the
now-deleted `outstanding_flags(document)` call there.)

- [ ] **Step 5: Update `render_approval()`**

At `carescribe/app.py:671` (`render_approval`'s signature) through the end of
the function (~line 757), make three changes:

1. Change the signature to accept the outstanding count from Step 4:

```python
def render_approval(document: batch.Document, outstanding: int) -> None:
```

2. Delete the checklist block:

```python
    items = render_checklist(document)
    ticked = st.session_state.checklist.get(document.name, set())
    reason = review_checklist.blocking_reason(
        items, ticked, document.residual, len(outstanding_flags(document))
    )
```

replace with:

```python
    reason = review_checklist.blocking_reason(document.residual, outstanding)
```

3. In the approve button's success branch, remove the `ticked=` keyword
   argument from the `write_review_record` call:

```python
                batch.write_review_record(
                    document.name,
                    entities=document.entities,
                    flags_shown=len(document_flags(document)),
                    flags_redacted=st.session_state.flag_redacted.get(document.name, 0),
                    flags_dismissed=len(flag_dismissals(document)),
                )
```

- [ ] **Step 6: Update `section_review()`'s call to `render_approval`**

At the end of `section_review()` (app.py:818), change:

```python
    render_approval(document)
```

to:

```python
    render_approval(document, outstanding)
```

- [ ] **Step 7: Delete the now-unused `outstanding_flags` and
      `document_flags` if no longer referenced**

`document_flags` is still used inside `render_approval` (for
`flags_shown=len(document_flags(document))`) — keep it. `outstanding_flags`
(app.py:543-544) is no longer called anywhere after Steps 3-6 removed its
only two call sites (`render_highlighted_preview`, `render_flag_decisions`,
`render_checklist`, all deleted). Delete it:

```python
def outstanding_flags(document: batch.Document) -> list:
    return review_flags.outstanding(document_flags(document), flag_dismissals(document))
```

Grep to confirm before deleting: `grep -rn "outstanding_flags" carescribe/
tests/` should show zero remaining call sites after Step 6.

- [ ] **Step 8: Update `tests/test_app.py`**

Search the file for any test asserting on the old checklist UI (checkbox
widgets keyed `chk_...`, or `app.checkbox`/`app.session_state["checklist"]`
references) and update them to the new model: approving a document with only
auto-confidence entities should now require zero checkbox interaction, just
the Approve click. Add:

```python
def test_a_document_with_only_auto_confidence_entities_needs_one_click():
    """The core promise of this redesign: nothing outstanding, no ticks."""
    state = analysed_batch(1)
    document = next(iter(state["docs"].values()))
    for entity in document.entities:
        entity["confidence"] = "auto"
    app = run_app(**state)
    reason_captions = [c.value for c in app.caption if "Approve is disabled" in c.value]
    assert reason_captions == []
```

(`analysed_batch` is the existing fixture at the top of `test_app.py` — read
it before writing this test, since it currently produces entities without a
`confidence` key at all via `batch.analyze_document`, which after Task 1
will populate real confidence values from the real pipeline; forcing every
entity to `"auto"` here isolates this test from what the detector happens to
decide for the fixture's specific text.)

- [ ] **Step 9: Run the full test file to verify it passes**

Run: `pytest tests/test_app.py tests/test_review_gate.py tests/test_batch.py -v`
Expected: PASS. If any pre-existing test in `test_app.py` still references
`checklist`/`chk_`/`render_highlighted_preview`/`outstanding_flags`, update
it per Step 8's pattern rather than deleting it outright unless it is
testing behaviour this plan intentionally removed (the itemised checklist
itself).

- [ ] **Step 10: Commit**

```bash
git add carescribe/app.py tests/test_app.py
git commit -m "feat: replace entity table + flag list + checklist with one click-to-redact review view"
```

---

### Task 8: Stress-corpus regression and batch-size rerun-count check

**Files:**
- Modify: `tests/test_stress_corpus.py`
- Modify: `tests/test_app.py`

**Interfaces:**
- Consumes: `stress_corpus/answer_key.json`'s `must_redact` /
  `must_preserve` fields (existing), `deidentify.analyze` (Task 1's
  `confidence` field).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_stress_corpus.py — add alongside the existing corpus-driven tests

def test_auto_confidence_never_covers_a_must_preserve_value(document_path, answer_key_entry):
    """Confidence tiering must never make the reviewer's job LESS safe.

    An "auto" entity skips the reviewer entirely, so if confidence tiering
    ever marked something "auto" that should have stayed KEPT (a place name,
    a clinical term), that value would be silently redacted with no chance
    to catch it — a correctness regression this test exists specifically to
    prevent, independent of whether it was redacted at all.
    """
    text = document_path.read_text(encoding="utf-8")
    entities = deidentify.analyze(text)
    preserved = {v.casefold() for v in answer_key_entry.get("must_preserve", [])}
    for entity in entities:
        if entity["value"].casefold() in preserved:
            # A detector that flagged a must-preserve value at all is already
            # a precision bug the existing corpus tests catch; this test only
            # adds: if it happened, it must not ALSO have skipped review.
            assert entity["confidence"] == "review"
```

(Read the existing parametrization fixtures near the top of
`tests/test_stress_corpus.py` — `document_path`/`answer_key_entry` above are
illustrative names; match whatever the file's actual `@pytest.mark.parametrize`
source already uses for iterating `stress_corpus/` documents against
`answer_key.json`, rather than introducing a second parametrization scheme.)

- [ ] **Step 2: Run test to verify it fails or passes cleanly**

Run: `pytest tests/test_stress_corpus.py -k auto_confidence -v`
Expected: PASS immediately if Task 1 was implemented correctly (there
should be no must-preserve values reaching "auto" confidence in the first
place, since "auto" only applies to structured-regex or multi-layer hits,
and a must-preserve value by definition isn't a real identifier for either
layer to agree on). If this FAILS, it has found a real bug in Task 1 —
stop and fix Task 1's `_confidence()` logic before continuing; do not weaken
this test to make it pass.

- [ ] **Step 3: Add the batch-size click-count regression to `tests/test_app.py`**

This formalises the manual reproduction done during debugging (20 documents
driven through `AppTest`, confirming flat per-document cost) into a real,
permanent regression test — now checking click *count*, not just timing,
since click count is what this whole plan set out to reduce.

```python
def test_a_batch_of_clean_documents_needs_roughly_one_click_each():
    """The actual goal of this redesign, made concrete and regression-tested."""
    state = analysed_batch(5)
    for document in state["docs"].values():
        for entity in document.entities:
            entity["confidence"] = "auto"
    app = run_app(**state)

    clicks = 0
    for name in list(state["docs"]):
        app.session_state["selected"] = name
        app.run()
        clicks += 1  # selecting the document
        app.button(key=f"approve_{name}").click()
        app.run()
        clicks += 1  # the one Approve click
        assert state["docs"][name].approved

    # 5 documents, 2 interactions each (select + approve) — no per-document
    # checkbox ticks, no per-span decisions, since every entity is "auto".
    assert clicks == 10
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_stress_corpus.py tests/test_app.py -v`
Expected: PASS.

- [ ] **Step 5: Run the full suite**

Run: `pytest -q`
Expected: PASS, with the total test count higher than the pre-plan baseline
(this plan adds tests in every task and only removes the ones Task 4
explicitly names as obsolete).

- [ ] **Step 6: Commit**

```bash
git add tests/test_stress_corpus.py tests/test_app.py
git commit -m "test: add confidence-tiering safety regression and click-count regression"
```

---

## Self-Review Notes

- **Spec coverage:** §1 (one primary view) → Tasks 3, 7. §2 (confidence
  tiering) → Task 1. §3 (click component) → Task 3. §4 (attestation/audit) →
  Tasks 4, 5. §5 (crash-risk: caching) → Task 6; (crash-risk: fewer reruns)
  is the natural consequence of Tasks 1-3, verified in Task 8. §6
  (unchanged: detection engine, Step 5, Clinical Form flow) → no task
  touches any of these, by design.
- **The redacted-text-safety decision** (show placeholders, not raw text,
  for low-confidence entities) was resolved during planning as a
  clarifying question separate from the original spec's brainstorming pass,
  since it materially affects a PHI-safety invariant the spec didn't
  explicitly pin down. It is now load-bearing throughout Tasks 2, 3, and 7 —
  flagged here so a reviewer of this plan sees it was a deliberate,
  user-confirmed choice, not an unstated assumption.
- **Placeholder scan:** no TBD/TODO remain. The one explicitly-flagged
  uncertainty (Task 3, Step 7 — exact Streamlit component postMessage
  contract) is real code plus a concrete verification action with a
  documented fallback, not a placeholder.
- **Type/name consistency checked:** `ReviewSpan` (Task 2) is consumed with
  the same field names in Task 7 (`span.kind`, `span.char_start`,
  `span.char_end`, `span.id`, `span.text`, `span.why`, `span.flag_kind`).
  `entity_confirmed(document) -> set[str]` (Task 7, Step 2) matches its use
  in `render_review`/`_render_span_action`. `blocking_reason(residual,
  outstanding)` (Task 4) matches its call in `render_approval` (Task 7, Step
  5). `write_review_record(..., entities=...)` without `ticked` (Task 5)
  matches its call site (Task 7, Step 5).
