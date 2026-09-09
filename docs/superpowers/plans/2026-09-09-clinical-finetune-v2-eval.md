# Clinical fine-tune v2 — V1 honest evaluation harness

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace an evaluation harness that cannot distinguish memorisation from capability, then re-score the shipped v1 model with it and publish the honest numbers.

**Architecture:** Four changes, in dependency order. Thread the source vignette through the data so it can be held out; persist enough per-pair state that evaluation can read a committed held-out split from disk instead of re-sampling; add two graders the training scaffold cannot satisfy by construction (an independent LLM judge, and an adversarial gap probe); report train/test overlap so a future reader can tell whether the scores above it mean anything.

**Tech Stack:** Python 3.11, pydantic v2, pytest. Judge runs on the local Ollama daemon (`127.0.0.1:11434`) and is evaluation-only. No new third-party dependencies.

**Spec:** `docs/superpowers/specs/2026-09-09-clinical-finetune-v2-design.md`

## Global Constraints

- All work is under `finetune/`. **Nothing in `carescribe/` may import from `finetune/`** — the reverse is allowed and expected. `finetune/eval/judge.py` opens a socket to the Ollama daemon and must never become reachable from the app.
- `finetune/tests/` runs CPU-only and must not require a GPU, a GGUF, or a running Ollama daemon. Anything needing the daemon is skipped when it is absent.
- The existing app suite (`pytest tests -q`) is untouched and must stay green after every task.
- Determinism: every sampler, splitter and probe takes an explicit `seed` and produces identical output for a given seed.
- Greedy decoding (`temperature 0`) everywhere — training, evaluation, judging, production.
- No real PHI. All data is synthetic; identifiers are Faker-generated.
- **A metric that cannot be computed is reported as absent, never as a default value.**

---

## Defects this plan fixes

Referenced by number throughout. D1–D3 are from the spec; **D4 was found while writing this plan** and is not in the spec.

- **D1** — `stratified_split` keys on `form_type × specialty × styled`, not the source vignette, so every test pair's skeleton is also in training.
- **D2** — `build_target` renders targets from `EncounterFacts`; `validators` score drafts back against the same `EncounterFacts`. Self-marking.
- **D3** — `style_match` is reported over a corpus where `styled=False` in all 25 strata; `vignettes/styles/` was never created.
- **D4** — `run_eval.main()` calls `make_eval_set(n, seed=1000)`, which re-samples from the same 10 vignettes. **The committed `test.jsonl` is never read.** Its docstring claims "held-out … (different seed)", which is false: a different seed over identical skeletons is not held out.

---

### Task 1: Thread `vignette_id` through to pair metadata

Nothing can be held out by vignette until the vignette is recorded. `Vignette.id` exists but `sampler.expand()` drops it.

**Files:**
- Modify: `finetune/datagen/schema.py` (add field to `EncounterFacts`, ~line 150)
- Modify: `finetune/datagen/sampler.py:36-85` (`expand`)
- Modify: `finetune/assemble/validators.py` (`_numbers_in_facts`, exclude the id)
- Modify: `finetune/assemble/pairs.py:33-88` (`make_pair`, `make_template_pair`)
- Test: `finetune/tests/test_vignette_id.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `EncounterFacts.vignette_id: str` (default `""`), and `Pair.meta["vignette_id"]: str`. Tasks 3 and 5 rely on both.

- [ ] **Step 1: Write the failing test**

```python
# finetune/tests/test_vignette_id.py
"""vignette_id must survive expand() -> EncounterFacts -> Pair.meta."""
import random

from finetune.assemble.pairs import make_pair
from finetune.datagen.sampler import expand
from finetune.datagen.schema import FormType
from finetune.datagen.vignettes import VIGNETTES


def test_expand_records_the_source_vignette_id():
    vignette = VIGNETTES[0]
    facts = expand(vignette, random.Random(0))
    assert facts.vignette_id == vignette.id
    assert facts.vignette_id != ""


def test_pair_meta_carries_the_vignette_id():
    facts = expand(VIGNETTES[0], random.Random(0))
    pair = make_pair(facts, FormType.SOAP, "doc [PATIENT]", "**Subjective**\nx")
    assert pair.meta["vignette_id"] == VIGNETTES[0].id


def test_digits_in_the_vignette_id_are_not_supported_numbers():
    """The id is bookkeeping. A skeleton named cardio_hf_02 must not make
    "02" a number the draft is allowed to state."""
    from finetune.assemble.validators import _numbers_in_facts

    facts = expand(VIGNETTES[0], random.Random(0)).model_copy(
        update={"vignette_id": "cardio_hf_0299"}
    )
    assert "0299" not in _numbers_in_facts(facts)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest finetune/tests/test_vignette_id.py -v`
Expected: FAIL — `AttributeError: 'EncounterFacts' object has no attribute 'vignette_id'`.

- [ ] **Step 3: Implement**

In `finetune/datagen/schema.py`, add to `EncounterFacts` immediately after `documented_gaps`:

```python
    # Bookkeeping, not clinical content: which vignette skeleton produced this
    # encounter. Used to hold entire skeletons out of training (see the v2 eval
    # design). Excluded from the faithfulness blob in assemble.validators.
    vignette_id: str = ""
```

In `finetune/datagen/sampler.py`, inside `expand()`, add to the `fields` dict:

```python
        vignette_id=vignette.id,
```

In `finetune/assemble/validators.py`, exclude the id from the supported-numbers
set. The function there is `_numbers_in_facts` (it collects numbers, not a
general text blob — an earlier draft of this plan called it `_supported_blob`,
which does not exist):

```python
def _numbers_in_facts(facts: EncounterFacts) -> set[str]:
    # vignette_id is bookkeeping, not a clinical fact. A skeleton named
    # "cardio_hf_02" would otherwise make "02" a number the draft may state.
    blob = " ".join(_flatten_strings(facts.model_dump(exclude={"vignette_id"})))
    return set(_NUM_RE.findall(blob))
```

In `finetune/assemble/pairs.py`, add to the `meta=` dict of **both** `make_pair` and `make_template_pair`:

```python
            "vignette_id": facts.vignette_id,
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest finetune/tests/test_vignette_id.py finetune/tests/test_schema.py finetune/tests/test_sampler.py finetune/tests/test_validators.py -v`
Expected: PASS, all four files.

- [ ] **Step 5: Commit**

```bash
git add finetune/datagen/schema.py finetune/datagen/sampler.py finetune/assemble/validators.py finetune/assemble/pairs.py finetune/tests/test_vignette_id.py
git commit -m "feat(finetune): record source vignette_id on facts and pair meta"
```

---

### Task 2: Persist what evaluation needs to reconstruct an item

D4's fix requires reading held-out items from disk. `Pair` stores only `messages` and `meta`, and faithfulness scoring needs `EncounterFacts`. The de-identified document is currently recoverable only by string-surgery on the built user message, which is fragile.

**Files:**
- Modify: `finetune/assemble/pairs.py:33-88`
- Test: `finetune/tests/test_pair_roundtrip.py`

**Interfaces:**
- Consumes: `Pair.meta["vignette_id"]` from Task 1.
- Produces: `Pair.meta` additionally carries `"document": str`, `"known_placeholders": list[str]`, `"facts": dict` (a `model_dump()` of `EncounterFacts`). Task 3's `load_eval_items` reads exactly these three keys.

Note: `train/sft.py` reads only `messages`; extra `meta` keys are inert for training.

- [ ] **Step 1: Write the failing test**

```python
# finetune/tests/test_pair_roundtrip.py
"""A written pair must carry enough to rebuild an eval item from disk."""
import json
import random

from finetune.assemble.pairs import make_pair
from finetune.datagen.sampler import expand
from finetune.datagen.schema import EncounterFacts, FormType
from finetune.datagen.vignettes import VIGNETTES


def _pair():
    facts = expand(VIGNETTES[0], random.Random(0))
    return facts, make_pair(
        facts,
        FormType.SOAP,
        "Name: [PATIENT]\nSeen: [DATE]",
        "**Subjective**\nx",
        known_placeholders=["[PATIENT]", "[DATE]"],
    )


def test_meta_carries_document_and_placeholders():
    _, pair = _pair()
    assert pair.meta["document"] == "Name: [PATIENT]\nSeen: [DATE]"
    assert pair.meta["known_placeholders"] == ["[PATIENT]", "[DATE]"]


def test_facts_survive_a_json_round_trip():
    facts, pair = _pair()
    revived = EncounterFacts(**json.loads(pair.to_json_line())["meta"]["facts"])
    assert revived.presenting_complaint == facts.presenting_complaint
    assert revived.vignette_id == facts.vignette_id
    assert revived.documented_gaps == facts.documented_gaps
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest finetune/tests/test_pair_roundtrip.py -v`
Expected: FAIL — `make_pair() got an unexpected keyword argument 'known_placeholders'`.

- [ ] **Step 3: Implement**

In `finetune/assemble/pairs.py`, change `make_pair`'s signature to accept the placeholders and record all three keys:

```python
def make_pair(
    facts: EncounterFacts,
    form: FormType,
    placeholdered_document: str,
    target: str,
    *,
    style_exemplar: str | None = None,
    polished: bool = False,
    known_placeholders: Sequence[str] = (),
) -> Pair:
```

and add to its `meta=` dict:

```python
            "document": placeholdered_document,
            "known_placeholders": list(known_placeholders),
            "facts": facts.model_dump(mode="json"),
```

Apply the same three `meta` keys and the same keyword-only `known_placeholders` parameter to `make_template_pair`.

In `finetune/assemble/build_dataset.py`, pass the placeholders at both call sites:

```python
            pairs.append(make_template_pair(
                facts, spec, deid.placeholdered_text, target,
                known_placeholders=deid.known_placeholders,
            ))
        else:
            pairs.append(make_pair(
                facts, form, deid.placeholdered_text, target,
                known_placeholders=deid.known_placeholders,
            ))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest finetune/tests/test_pair_roundtrip.py finetune/tests/test_assemble_pipeline.py finetune/tests/test_build_dataset.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add finetune/assemble/pairs.py finetune/assemble/build_dataset.py finetune/tests/test_pair_roundtrip.py
git commit -m "feat(finetune): persist document, placeholders and facts in pair meta"
```

---

### Task 3: Split by vignette, not by row (fixes D1)

**Files:**
- Modify: `finetune/assemble/pairs.py:94-124`
- Modify: `finetune/assemble/build_dataset.py` (`main`, the `stratified_split` call)
- Modify: `finetune/assemble/manifest.py:44-65` (record the split mode and per-split vignettes)
- Test: `finetune/tests/test_split_by_vignette.py`

**Interfaces:**
- Consumes: `Pair.meta["vignette_id"]` from Task 1.
- Produces: `split_by_vignette(pairs, *, dev_frac=0.1, test_frac=0.1, seed=0) -> dict[str, list[Pair]]`, keys `"train" | "dev" | "test"`. Manifest gains `"split_mode": "vignette_disjoint"` and `"split_vignettes": {"train": [...], "dev": [...], "test": [...]}`.

- [ ] **Step 1: Write the failing test**

```python
# finetune/tests/test_split_by_vignette.py
"""Holdout is by vignette: a skeleton in test is absent from train."""
import pytest

from finetune.assemble.pairs import Pair, split_by_vignette


def _pairs(n_vignettes=10, per=20):
    return [
        Pair(messages=[], meta={"vignette_id": f"v{v}", "form_type": "soap",
                                "specialty": "cardiology", "styled": False})
        for v in range(n_vignettes)
        for _ in range(per)
    ]


def _ids(group):
    return {p.meta["vignette_id"] for p in group}


def test_no_vignette_appears_in_two_splits():
    splits = split_by_vignette(_pairs(), seed=0)
    train, dev, test = _ids(splits["train"]), _ids(splits["dev"]), _ids(splits["test"])
    assert train & test == set()
    assert train & dev == set()
    assert dev & test == set()


def test_every_pair_is_placed_exactly_once():
    pairs = _pairs()
    splits = split_by_vignette(pairs, seed=0)
    assert sum(len(g) for g in splits.values()) == len(pairs)


def test_the_split_is_deterministic_for_a_seed():
    assert _ids(split_by_vignette(_pairs(), seed=7)["test"]) == \
           _ids(split_by_vignette(_pairs(), seed=7)["test"])


def test_too_few_vignettes_to_hold_out_is_an_error_not_a_silent_empty_split():
    """With 2 vignettes there is no honest holdout. Say so, don't return {}."""
    with pytest.raises(ValueError, match="vignette"):
        split_by_vignette(_pairs(n_vignettes=2), seed=0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest finetune/tests/test_split_by_vignette.py -v`
Expected: FAIL — `ImportError: cannot import name 'split_by_vignette'`.

- [ ] **Step 3: Implement**

Add to `finetune/assemble/pairs.py` (keep `stratified_split` for now; Task 9 removes its last caller):

```python
def split_by_vignette(
    pairs: Sequence[Pair],
    *,
    dev_frac: float = 0.1,
    test_frac: float = 0.1,
    seed: int = 0,
) -> dict[str, list[Pair]]:
    """Split so that no vignette skeleton appears in more than one split.

    Row-level splitting cannot answer "does this generalise" when a handful of
    skeletons each produce hundreds of rows: the test rows are re-renderings of
    stories the model trained on. The unit of holdout is therefore the vignette.

    Raises ValueError when there are too few vignettes for an honest holdout —
    an empty test split that reads as a pass is the failure this guards against.
    """
    import random

    by_vignette: dict[str, list[Pair]] = {}
    for p in pairs:
        vid = str(p.meta.get("vignette_id", ""))
        if not vid:
            raise ValueError("pair has no vignette_id; run Task 1 first")
        by_vignette.setdefault(vid, []).append(p)

    ids = sorted(by_vignette)
    n_test = max(1, round(len(ids) * test_frac))
    n_dev = max(1, round(len(ids) * dev_frac))
    if len(ids) < n_test + n_dev + 1:
        raise ValueError(
            f"{len(ids)} vignettes cannot yield a disjoint train/dev/test split "
            f"(need at least {n_test + n_dev + 1}); author more vignettes"
        )

    random.Random(seed).shuffle(ids)
    assign = {
        "test": ids[:n_test],
        "dev": ids[n_test : n_test + n_dev],
        "train": ids[n_test + n_dev :],
    }
    return {
        name: [p for vid in sorted(group) for p in by_vignette[vid]]
        for name, group in assign.items()
    }
```

Export it in `__all__`. In `build_dataset.main`, replace the split call:

```python
    splits = split_by_vignette(result["pairs"], seed=seed)
```

and update the import on line 27 to `from finetune.assemble.pairs import make_pair, split_by_vignette, write_jsonl`.

In `manifest.build_manifest`, add before the `return`:

```python
    split_vignettes = {
        name: sorted({str(p.meta.get("vignette_id", "")) for p in group})
        for name, group in splits.items()
    }
```

and add these two keys to the returned dict:

```python
        "split_mode": "vignette_disjoint",
        "split_vignettes": split_vignettes,
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest finetune/tests/test_split_by_vignette.py finetune/tests/test_build_dataset.py -v`
Expected: PASS. `test_build_dataset` may now raise the "too few vignettes" error if its fixture uses fewer than three; if so, widen that fixture's vignette pool rather than weakening the guard.

- [ ] **Step 5: Commit**

```bash
git add finetune/assemble/pairs.py finetune/assemble/build_dataset.py finetune/assemble/manifest.py finetune/tests/test_split_by_vignette.py
git commit -m "fix(finetune): hold out whole vignettes, not rows (D1)"
```

---

### Task 4: Evaluate the committed held-out split (fixes D4)

**Files:**
- Modify: `finetune/eval/run_eval.py:54-79` (`make_eval_set` docstring), `:218-250` (`main`)
- Test: `finetune/tests/test_load_eval_items.py`

**Interfaces:**
- Consumes: `Pair.meta` keys `document`, `known_placeholders`, `facts` (Task 2); `split_by_vignette` output written to `test.jsonl` (Task 3).
- Produces: `load_eval_items(path: str | Path) -> list[EvalItem]`. `run_eval.main` gains `--test-jsonl PATH`.

- [ ] **Step 1: Write the failing test**

```python
# finetune/tests/test_load_eval_items.py
"""Eval reads the committed held-out split; it does not re-sample."""
import random

from finetune.assemble.pairs import make_pair, write_jsonl
from finetune.datagen.sampler import expand
from finetune.datagen.schema import FormType
from finetune.datagen.vignettes import VIGNETTES
from finetune.eval.run_eval import load_eval_items


def test_items_rebuild_from_a_written_jsonl(tmp_path):
    facts = expand(VIGNETTES[0], random.Random(0))
    pair = make_pair(
        facts, FormType.SOAP, "Name: [PATIENT]", "**Subjective**\nx",
        known_placeholders=["[PATIENT]"],
    )
    path = tmp_path / "test.jsonl"
    write_jsonl([pair], path)

    items = load_eval_items(path)
    assert len(items) == 1
    assert items[0].document == "Name: [PATIENT]"
    assert items[0].form is FormType.SOAP
    assert items[0].known_placeholders == ["[PATIENT]"]
    assert items[0].facts.vignette_id == VIGNETTES[0].id
    assert items[0].target == "**Subjective**\nx"


def test_a_pair_written_before_task_2_is_rejected_loudly(tmp_path):
    """An old jsonl lacks document/facts. Fail, don't silently eval on nothing."""
    import json

    path = tmp_path / "old.jsonl"
    path.write_text(json.dumps({"messages": [], "meta": {"form_type": "soap"}}) + "\n",
                    encoding="utf-8")
    try:
        load_eval_items(path)
    except ValueError as exc:
        assert "document" in str(exc)
    else:
        raise AssertionError("expected ValueError for a pre-Task-2 jsonl")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest finetune/tests/test_load_eval_items.py -v`
Expected: FAIL — `ImportError: cannot import name 'load_eval_items'`.

- [ ] **Step 3: Implement**

Add to `finetune/eval/run_eval.py`:

```python
def load_eval_items(path: str | Path) -> list[EvalItem]:
    """Rebuild eval items from a committed split file.

    Evaluation must read the split that training held out. Re-sampling the
    generator with a different seed re-draws the same vignette skeletons, which
    measures memorisation and reports it as generalisation.
    """
    import json
    from pathlib import Path as _Path

    items: list[EvalItem] = []
    with _Path(path).open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            meta = json.loads(line).get("meta", {})
            for key in ("document", "facts", "known_placeholders"):
                if key not in meta:
                    raise ValueError(
                        f"{path}:{lineno} has no {key!r} in meta — this file "
                        f"predates the v2 pair format; rebuild the dataset"
                    )
            items.append(
                EvalItem(
                    facts=EncounterFacts(**meta["facts"]),
                    form=FormType(meta["form_type"]),
                    document=meta["document"],
                    known_placeholders=list(meta["known_placeholders"]),
                    target=json.loads(line)["messages"][-1]["content"],
                )
            )
    return items
```

Add `from pathlib import Path` to the imports and `"load_eval_items"` to `__all__`.

Replace `make_eval_set`'s misleading docstring:

```python
    """Build items by re-sampling the generator.

    NOT a held-out set: a different seed re-draws the same vignette skeletons.
    Use :func:`load_eval_items` against a vignette-disjoint split for any number
    that will be reported. Kept for smoke tests and dry runs.
    """
```

In `main()`, make the held-out file the default path and re-sampling the explicit opt-out:

```python
    ap.add_argument("--test-jsonl", default="finetune/data/full/test.jsonl",
                    help="committed held-out split to evaluate on")
    ap.add_argument("--resample", action="store_true",
                    help="re-sample instead of reading the held-out split "
                         "(NOT held out; smoke tests only)")
```

and replace the `items = make_eval_set(...)` line with:

```python
    if args.resample:
        print("WARNING: --resample is not a held-out evaluation.")
        items = make_eval_set(args.n, seed=args.seed)
    else:
        items = load_eval_items(args.test_jsonl)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest finetune/tests/test_load_eval_items.py finetune/tests/test_eval.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add finetune/eval/run_eval.py finetune/tests/test_load_eval_items.py
git commit -m "fix(finetune): evaluate the committed held-out split, not a resample (D4)"
```

---

### Task 5: Report train/test overlap

A holdout claim should be checkable by the reader of the report, not taken on trust.

**Files:**
- Create: `finetune/eval/overlap.py`
- Modify: `finetune/eval/report.py:27-70`
- Test: `finetune/tests/test_overlap.py`

**Interfaces:**
- Consumes: nothing from earlier tasks (operates on plain strings).
- Produces: `overlap_report(train_targets: Sequence[str], test_targets: Sequence[str]) -> dict` with keys `median`, `p95`, `n_above_0_6`, `n`. `build_report` gains a keyword-only `overlap: dict | None = None`.

- [ ] **Step 1: Write the failing test**

```python
# finetune/tests/test_overlap.py
"""Character 5-gram overlap between test targets and their nearest train target."""
from finetune.eval.overlap import max_similarity, overlap_report


def test_identical_text_is_one():
    assert max_similarity("the patient was seen today", ["the patient was seen today"]) == 1.0


def test_unrelated_text_is_low():
    assert max_similarity("chest pain on exertion", ["dispense fluoride varnish"]) < 0.2


def test_report_counts_the_high_overlap_tail():
    train = ["alpha bravo charlie delta echo"]
    test = ["alpha bravo charlie delta echo", "zulu yankee xray whisky victor"]
    r = overlap_report(train, test)
    assert r["n"] == 2
    assert r["n_above_0_6"] == 1
    assert r["median"] < 1.0


def test_empty_train_reports_absent_not_zero():
    """No training text means the metric is uncomputable, not 0.0."""
    assert overlap_report([], ["anything"])["median"] is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest finetune/tests/test_overlap.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'finetune.eval.overlap'`.

- [ ] **Step 3: Implement**

```python
# finetune/eval/overlap.py
"""Train/test contamination, measured rather than assumed.

A held-out score means nothing if the held-out text is a near-copy of something
in training. This reports how close each test target is to its nearest training
target, so a reader can discount the scores printed above it.
"""

from __future__ import annotations

from typing import Sequence


def _grams(text: str, n: int = 5) -> set[str]:
    squashed = " ".join(text.lower().split())
    if len(squashed) < n:
        return {squashed} if squashed else set()
    return {squashed[i : i + n] for i in range(len(squashed) - n + 1)}


def similarity(a: str, b: str) -> float:
    """Jaccard over character 5-grams, 0..1."""
    ga, gb = _grams(a), _grams(b)
    if not ga or not gb:
        return 0.0
    return len(ga & gb) / len(ga | gb)


def max_similarity(text: str, corpus: Sequence[str]) -> float:
    """Similarity between ``text`` and its nearest neighbour in ``corpus``."""
    return max((similarity(text, other) for other in corpus), default=0.0)


def overlap_report(
    train_targets: Sequence[str], test_targets: Sequence[str]
) -> dict:
    """Distribution of each test target's nearest-train-neighbour similarity.

    Returns ``median``/``p95`` as ``None`` when uncomputable — an absent metric
    is reported as absent, never as 0.0.
    """
    if not train_targets or not test_targets:
        return {"median": None, "p95": None, "n_above_0_6": 0, "n": len(test_targets)}
    sims = sorted(max_similarity(t, train_targets) for t in test_targets)
    return {
        "median": round(sims[len(sims) // 2], 4),
        "p95": round(sims[min(len(sims) - 1, int(len(sims) * 0.95))], 4),
        "n_above_0_6": sum(1 for s in sims if s > 0.6),
        "n": len(sims),
    }


__all__ = ["max_similarity", "overlap_report", "similarity"]
```

In `finetune/eval/report.py`, add `overlap: dict | None = None` as a keyword-only parameter of `build_report`, and append this block before the `payload = {` line:

```python
    if overlap is not None:
        lines += ["", "## Train/test overlap", ""]
        if overlap["median"] is None:
            lines.append("Not computable (no training targets supplied).")
        else:
            lines += [
                f"- median nearest-train similarity: {overlap['median']:.3f}",
                f"- p95: {overlap['p95']:.3f}",
                f"- test targets above 0.6: {overlap['n_above_0_6']} of {overlap['n']}",
                "",
                "High overlap voids the scores above: a near-copy of a training "
                "target measures recall of the corpus, not capability.",
            ]
```

and add `"overlap": overlap,` to the `payload` dict. Thread the same keyword through `write_report` (it already forwards `**kw`).

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest finetune/tests/test_overlap.py finetune/tests/test_eval.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add finetune/eval/overlap.py finetune/eval/report.py finetune/tests/test_overlap.py
git commit -m "feat(finetune): report train/test overlap alongside the scores"
```

---

### Task 6: Remove `style_match` (fixes D3)

The corpus has no styled pairs, so the metric scores a dimension that never varied. It returns in V2 when `vignettes/styles/` exists.

**Files:**
- Modify: `finetune/eval/metrics.py` (delete `style_match`, `_headings`, `_order_agreement`, `_lexical_overlap`, `_HEADING_RE`; drop the field from `DraftScore` and `aggregate`; drop the `style_target` parameter of `score_draft`)
- Modify: `finetune/eval/report.py` (delete the `style_match` row block)
- Modify: `finetune/tests/test_eval.py` (drop style assertions)
- Test: `finetune/tests/test_no_style_metric.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `DraftScore` loses `style_match`; `score_draft` loses `style_target`. No later task in this plan uses either.

- [ ] **Step 1: Write the failing test**

```python
# finetune/tests/test_no_style_metric.py
"""style_match is withdrawn until styled pairs exist (v2 design D3)."""
import dataclasses

from finetune.eval.metrics import DraftScore, aggregate


def test_draft_score_has_no_style_field():
    assert "style_match" not in {f.name for f in dataclasses.fields(DraftScore)}


def test_aggregate_never_emits_a_style_key():
    scores = [DraftScore(format=1.0, faithfulness=1.0,
                         placeholder_integrity=1.0, residual_clean=1.0)]
    assert "style_match" not in aggregate(scores)


def test_the_module_no_longer_exports_style_match():
    import finetune.eval.metrics as m

    assert not hasattr(m, "style_match")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest finetune/tests/test_no_style_metric.py -v`
Expected: FAIL — `style_match` is still a field and still exported.

- [ ] **Step 3: Implement**

In `finetune/eval/metrics.py`: delete `_HEADING_RE`, `_headings`, `_order_agreement`, `_lexical_overlap` and `style_match`; remove `style_match` from `DraftScore`, from `as_dict`, from `score_draft`'s signature and return, and from `aggregate` (delete the `styled` list and the trailing `if styled:` block); remove `"style_match"` from `__all__`. Replace the last docstring paragraph with:

```
`style_match` was withdrawn: it was reported over a corpus in which no pair was
styled, so it measured a dimension that never varied. It returns when
`datagen/vignettes/styles/` exists and styled pairs are in the corpus.
```

In `finetune/eval/report.py`, delete the two-line block:

```python
    if "style_match" in base.metrics or "style_match" in tuned.metrics:
        lines.append(_row("style_match", base.metrics, tuned.metrics, "style_match"))
```

and change the trailing gate sentence to `"Ship gate: tuned ≥ base on every metric above, no regression on the regression set, and latency ratio ≤ 1.15."`

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest finetune/tests/ -v`
Expected: PASS. Fix any `test_eval.py` assertion still referencing style by deleting it.

- [ ] **Step 5: Commit**

```bash
git add finetune/eval/metrics.py finetune/eval/report.py finetune/tests/
git commit -m "fix(finetune): withdraw style_match, which scored a dimension the corpus never varied (D3)"
```

---

### Task 7: An independent LLM judge (fixes D2)

The fact-aligned validator scores a draft against the same `EncounterFacts` the target was rendered from. The judge sees the **source note and the draft only** — never the facts — so it cannot reward reproduction of the scaffold.

**Files:**
- Create: `finetune/eval/judge.py`
- Test: `finetune/tests/test_judge.py`
- Modify: `finetune/tests/test_prompt_template.py` (extend the import-boundary assertion)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `JudgeVerdict(supported: bool, unsupported_claims: list[str], raw: str)`; `judge_draft(source: str, draft: str, *, complete: Callable[[str, str], str]) -> JudgeVerdict`; `OllamaJudge(model="qwen3.8:27b").complete(system, user) -> str`.

- [ ] **Step 1: Write the failing test**

```python
# finetune/tests/test_judge.py
"""The judge grades against the source note, never against EncounterFacts."""
import inspect

from finetune.eval.judge import JudgeVerdict, judge_draft


def _canned(payload):
    return lambda system, user: payload


def test_a_clean_draft_is_supported():
    v = judge_draft("Chest pain. BP 140/90.", "**Objective**\nBP 140/90.",
                    complete=_canned('{"supported": true, "unsupported_claims": []}'))
    assert v.supported is True
    assert v.unsupported_claims == []


def test_an_invented_claim_is_caught():
    v = judge_draft(
        "Chest pain. BP 140/90.",
        "**Objective**\nBP 140/90. Troponin raised.",
        complete=_canned('{"supported": false, "unsupported_claims": ["Troponin raised"]}'),
    )
    assert v.supported is False
    assert "Troponin raised" in v.unsupported_claims


def test_unparseable_output_is_not_silently_a_pass():
    v = judge_draft("x", "y", complete=_canned("I think it looks fine, mostly."))
    assert v.supported is None
    assert v.raw == "I think it looks fine, mostly."


def test_the_judge_is_never_handed_the_facts():
    """Its whole value is that it cannot see the scaffold's source of truth."""
    params = inspect.signature(judge_draft).parameters
    assert "facts" not in params
    assert set(params) == {"source", "draft", "complete"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest finetune/tests/test_judge.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'finetune.eval.judge'`.

- [ ] **Step 3: Implement**

```python
# finetune/eval/judge.py
"""A second, independent grader for faithfulness.

`assemble.validators` scores a draft by aligning it back to the same
`EncounterFacts` that `build_target` rendered the target from — model, target
and grader all derive from one artefact, so a perfect score is consistent with
"reproduced the scaffold" and says nothing about faithfulness.

This grader sees the SOURCE NOTE and the DRAFT only. It never receives
`EncounterFacts`, and `judge_draft` has no parameter through which they could be
passed. Disagreement between the two graders is the signal worth reporting.

Evaluation-only: this module opens a socket to the local Ollama daemon and must
never be importable from `carescribe/`.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Callable

JUDGE_SYSTEM = (
    "You grade clinical documents for faithfulness. You are given a SOURCE note "
    "and a DRAFT written from it. Decide whether every clinical claim in the "
    "DRAFT is supported by the SOURCE.\n"
    "Bracketed placeholders such as [PATIENT] or [DATE_2] are redacted "
    "identifiers, not claims — ignore them.\n"
    'Reply with JSON only: {"supported": true|false, "unsupported_claims": [...]}'
)

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


@dataclass(frozen=True)
class JudgeVerdict:
    supported: bool | None      # None => the judge's reply could not be parsed
    unsupported_claims: list[str]
    raw: str


def judge_draft(
    source: str, draft: str, *, complete: Callable[[str, str], str]
) -> JudgeVerdict:
    """Grade ``draft`` against ``source``. ``complete(system, user) -> str``."""
    user = f"SOURCE:\n{source}\n\nDRAFT:\n{draft}"
    raw = complete(JUDGE_SYSTEM, user)
    match = _JSON_RE.search(raw or "")
    if not match:
        return JudgeVerdict(None, [], raw)
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        return JudgeVerdict(None, [], raw)
    supported = payload.get("supported")
    return JudgeVerdict(
        supported if isinstance(supported, bool) else None,
        [str(c) for c in payload.get("unsupported_claims", [])],
        raw,
    )


class OllamaJudge:
    """The default grader: a larger, different model on the local daemon.

    Different family and size from the model under test, and it reads a
    different artefact than the scaffold was built from.
    """

    def __init__(self, model: str = "qwen3.8:27b",
                 host: str = "http://127.0.0.1:11434") -> None:
        self.model, self.host = model, host

    def complete(self, system: str, user: str) -> str:
        import urllib.request

        body = json.dumps({
            "model": self.model,
            "prompt": f"{system}\n\n{user}",
            "stream": False,
            "think": False,
            "options": {"temperature": 0.0},
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{self.host}/api/generate", data=body,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read().decode("utf-8")).get("response", "")


__all__ = ["JUDGE_SYSTEM", "JudgeVerdict", "OllamaJudge", "judge_draft"]
```

Add to `finetune/tests/test_prompt_template.py` (the existing boundary test file):

```python
def test_carescribe_never_imports_the_judge():
    """The judge opens a socket. It must stay outside the app's import graph."""
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[2] / "carescribe"
    offenders = [
        str(p) for p in root.rglob("*.py")
        if "eval.judge" in p.read_text(encoding="utf-8", errors="ignore")
        or "eval import judge" in p.read_text(encoding="utf-8", errors="ignore")
    ]
    assert offenders == []
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest finetune/tests/test_judge.py finetune/tests/test_prompt_template.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add finetune/eval/judge.py finetune/tests/test_judge.py finetune/tests/test_prompt_template.py
git commit -m "feat(finetune): independent LLM judge for faithfulness (D2)"
```

---

### Task 8: Adversarial gap probe and confabulation rate

"Not documented." is the product's main anti-confabulation behaviour. It is trained on 47% of pairs and currently never probed.

**Files:**
- Create: `finetune/eval/gap_probe.py`
- Test: `finetune/tests/test_gap_probe.py`

**Interfaces:**
- Consumes: `EncounterFacts.vignette_id` (Task 1); `EvalItem` from `run_eval`.
- Produces: `make_gap_probes(n, *, seed=2000, forms=...) -> list[EvalItem]` (every item has non-empty `documented_gaps`); `confabulation_rate(items, drafts) -> float | None`.

- [ ] **Step 1: Write the failing test**

```python
# finetune/tests/test_gap_probe.py
"""A required field is absent. The model must say so, not invent."""
from finetune.eval.gap_probe import confabulation_rate, gap_headings, make_gap_probes


def test_every_probe_has_at_least_one_gap():
    probes = make_gap_probes(6, seed=2000)
    assert probes
    assert all(p.facts.documented_gaps for p in probes)


def test_probes_are_deterministic_for_a_seed():
    a = [p.facts.documented_gaps for p in make_gap_probes(4, seed=99)]
    b = [p.facts.documented_gaps for p in make_gap_probes(4, seed=99)]
    assert a == b


def test_saying_not_documented_is_not_confabulation():
    probes = make_gap_probes(2, seed=2000)
    drafts = [p.target for p in probes]           # the target already says it
    assert confabulation_rate(probes, drafts) == 0.0


def test_asserting_content_under_a_gapped_heading_is_confabulation():
    probes = make_gap_probes(1, seed=2000)
    heading = gap_headings(probes[0])[0]
    drafts = [f"**{heading}**\nPenicillin allergy, rash.\n"]
    assert confabulation_rate(probes, drafts) == 1.0


def test_no_probes_reports_absent_not_zero():
    assert confabulation_rate([], []) is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest finetune/tests/test_gap_probe.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'finetune.eval.gap_probe'`.

- [ ] **Step 3: Implement**

```python
# finetune/eval/gap_probe.py
"""Adversarial probes for the "Not documented." behaviour.

Every probe is an encounter in which a field the form requires is deliberately
absent. The metric is the confabulation rate: how often the model asserts
content under a heading whose facts were removed. This is the failure that
matters clinically, and the four v1 metrics did not measure it.
"""

from __future__ import annotations

import re
from typing import Sequence

from finetune.assemble.build_target import build_target
from finetune.assemble.deidentify_notes import deidentify_note, leaked_values
from finetune.datagen.render_note import render
from finetune.datagen.sampler import sample_encounters
from finetune.datagen.schema import FormType
from finetune.eval.run_eval import EvalItem, _DEFAULT_FORMS

NOT_DOCUMENTED = "not documented"

# EncounterFacts field -> the heading its content appears under in a rendered form.
_FIELD_HEADINGS: dict[str, tuple[str, ...]] = {
    "history": ("Subjective", "History", "Background"),
    "pmh": ("Subjective", "History", "Background"),
    "meds": ("Medications", "Current Medications", "Interventions"),
    "allergies": ("Allergies",),
    "examination": ("Objective", "Examination"),
    "investigations": ("Objective", "Investigations", "Results"),
    "impression": ("Assessment", "Impression", "Problem List"),
    "plan": ("Plan", "Interventions"),
    "follow_up": ("Follow-up", "Follow up"),
}

_HEADING_RE = re.compile(r"\*\*\s*(.+?)\s*\*\*\s*\n(.*?)(?=\n\*\*|\Z)", re.DOTALL)


def gap_headings(item: EvalItem) -> list[str]:
    """Headings whose backing facts were removed from this probe."""
    out: list[str] = []
    for field in item.facts.documented_gaps:
        out.extend(_FIELD_HEADINGS.get(field, ()))
    return out or ["Plan"]


def make_gap_probes(
    n: int,
    *,
    seed: int = 2000,
    forms: tuple[FormType, ...] = _DEFAULT_FORMS,
) -> list[EvalItem]:
    """``n`` eval items, every one with at least one documented gap."""
    from finetune.datagen.identifiers import inject

    items: list[EvalItem] = []
    drawn = 0
    # gap_probability=1.0 blanks every gappable field the vignette allows.
    for facts in sample_encounters(n * 4, seed=seed, gap_probability=1.0):
        if len(items) >= n:
            break
        if not facts.documented_gaps:
            continue
        form = forms[drawn % len(forms)]
        drawn += 1
        identified, placed = inject(render(facts, seed=seed + drawn), seed=seed + drawn)
        deid = deidentify_note(identified)
        if leaked_values(deid, [p.value for p in placed]):
            continue
        items.append(
            EvalItem(
                facts=facts,
                form=form,
                document=deid.placeholdered_text,
                known_placeholders=deid.known_placeholders,
                target=build_target(facts, form),
            )
        )
    return items


def _section_text(draft: str, heading: str) -> str | None:
    for match in _HEADING_RE.finditer(draft):
        if match.group(1).strip().lower() == heading.strip().lower():
            return match.group(2)
    return None


def confabulated(item: EvalItem, draft: str) -> bool:
    """True when a gapped section asserts content instead of admitting absence."""
    for heading in gap_headings(item):
        body = _section_text(draft, heading)
        if body is None:
            continue
        stripped = body.strip()
        if stripped and NOT_DOCUMENTED not in stripped.lower():
            return True
    return False


def confabulation_rate(
    items: Sequence[EvalItem], drafts: Sequence[str]
) -> float | None:
    """Fraction of probes that invented content. ``None`` when there are none."""
    if not items or not drafts:
        return None
    pairs = list(zip(items, drafts))
    return sum(confabulated(i, d) for i, d in pairs) / len(pairs)


__all__ = [
    "NOT_DOCUMENTED",
    "confabulated",
    "confabulation_rate",
    "gap_headings",
    "make_gap_probes",
]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest finetune/tests/test_gap_probe.py -v`
Expected: PASS. If `_FIELD_HEADINGS` does not match the headings `build_target` actually emits, print one `build_target(facts, FormType.SOAP)` and correct the mapping — **fix the mapping, not the test**.

- [ ] **Step 5: Commit**

```bash
git add finetune/eval/gap_probe.py finetune/tests/test_gap_probe.py
git commit -m "feat(finetune): adversarial gap probe and confabulation rate"
```

---

### Task 9: Rebuild the dataset and re-score v1 honestly

The deliverable of this milestone: real numbers, published beside the old ones.

**Files:**
- Modify: `finetune/eval/run_eval.py` (`main` — wire overlap, judge and gap probe into the report)
- Create: `finetune/runs/phi35-v1/EVAL_REPORT_v2harness.md` (generated)
- Modify: `finetune/runs/phi35-v1/EVAL_REPORT.md` (prepend the correction notice)

**Interfaces:**
- Consumes: everything from Tasks 1–8.
- Produces: no new API. Generates the honest report.

- [ ] **Step 1: Rebuild the dataset with vignette-disjoint splits**

Run:
```bash
python -m finetune.assemble.build_dataset --n 4000 --out finetune/data/full_v2
```
Expected: succeeds, and `finetune/data/full_v2/dataset_manifest.json` contains `"split_mode": "vignette_disjoint"` with disjoint `split_vignettes` lists.

**If it raises `ValueError: 10 vignettes cannot yield a disjoint train/dev/test split`**, that is Task 3's guard doing its job and it is the expected outcome at 10 vignettes with `test_frac=0.1`. Rerun with explicit fractions that 10 vignettes can support:
```bash
python -c "
from finetune.assemble.build_dataset import build
from finetune.assemble.pairs import split_by_vignette, write_jsonl
from finetune.assemble.manifest import build_manifest, write_manifest
r = build(4000, seed=0)
s = split_by_vignette(r['pairs'], dev_frac=0.2, test_frac=0.2, seed=0)
for k, v in s.items(): write_jsonl(v, f'finetune/data/full_v2/{k}.jsonl')
write_manifest(build_manifest(s, generator_backend='template', generator_model=None, seed=0),
               'finetune/data/full_v2/dataset_manifest.json')
print({k: len(v) for k, v in s.items()})
"
```
Record in the report that 2 of 10 vignettes are held out — a thin holdout, and one of the reasons V2 raises the vignette count.

- [ ] **Step 2: Wire the new signals into the report**

In `run_eval.main()`, after `base_run, tuned_run = run(base, items), run(tuned, items)`, add:

```python
    from finetune.eval.gap_probe import confabulation_rate, make_gap_probes
    from finetune.eval.overlap import overlap_report

    train_targets = [i.target for i in load_eval_items(
        args.test_jsonl.replace("test.jsonl", "train.jsonl"))]
    ov = overlap_report(train_targets, [i.target for i in items])

    probes = make_gap_probes(args.gap_probes, seed=2000)
    base_conf = confabulation_rate(
        probes, [base.complete(*p.messages_pair()) for p in probes])
    tuned_conf = confabulation_rate(
        probes, [tuned.complete(*p.messages_pair()) for p in probes])
    print(f"confabulation rate — base {base_conf}, tuned {tuned_conf}")
```

Add the argument `ap.add_argument("--gap-probes", type=int, default=40)`, and pass `overlap=ov` to `write_report`.

Add this helper to `EvalItem` in `run_eval.py` so a completer can be called directly:

```python
    def messages_pair(self) -> tuple[str, str]:
        """(system, user) for a Completer.complete call."""
        msgs = self.messages()
        return msgs[0]["content"], msgs[1]["content"]
```

- [ ] **Step 3: Run the honest evaluation**

Run (entry point is `finetune.eval`; `finetune.eval.run_eval` had no `__main__` guard and exited 0 having done nothing -- a guard has since been added, but this is the documented entry point):
```bash
python -m finetune.eval \
  --base-gguf finetune/runs/base-gguf/Phi-3.5-mini-instruct-Q4_K_M.gguf \
  --tuned-gguf models/carescribe-clinical-phi35-v1.Q4_K_M.gguf \
  --test-jsonl finetune/data/full_v2/test.jsonl \
  --out finetune/runs/phi35-v1/v2harness
```
Expected: completes and writes `EVAL_REPORT.md` + `eval_report.json` under `v2harness/`. **Scores are expected to fall substantially. That is the deliverable, not a regression.**

- [ ] **Step 4: Publish the correction**

Prepend to `finetune/runs/phi35-v1/EVAL_REPORT.md`:

```markdown
> **Superseded 2026-09-09.** The numbers below were produced by a harness with
> four defects (D1–D4 in `docs/superpowers/specs/2026-09-09-clinical-finetune-v2-design.md`):
> the test split shared vignette skeletons with training, the evaluator never
> read that split at all, faithfulness was scored against the same facts the
> target was rendered from, and `style_match` scored a dimension no pair varied.
> Honest re-scoring: `v2harness/EVAL_REPORT.md`.
```

Copy the generated report to `finetune/runs/phi35-v1/EVAL_REPORT_v2harness.md` and add a short table putting old and new numbers side by side, with one sentence per metric explaining the movement.

- [ ] **Step 5: Verify nothing else broke, then commit**

Run: `python -m pytest finetune/tests/ -q && python -m pytest tests -q`
Expected: both suites pass.

```bash
git add finetune/ docs/
git commit -m "eval(finetune): re-score v1 on the honest harness and publish the correction"
git push origin feat/retrieval-augmented-clinical-forms
```

---

## Self-review

**Spec coverage.** §3.1 → Tasks 1, 3. §3.2 → Task 5. §3.3 → Task 7. §3.4 → Task 6. §3.5 → Task 8. §3.6 → Task 9. Spec §4 (V2 corpus), §5 (V3 roll-up), §6 (ship gate), §8 (integration) are out of scope for this plan by design and get their own plans. **Gap found and closed:** the spec does not mention D4 — that `run_eval` never reads the held-out split — because it was found while writing this plan; Task 4 covers it and the spec's D-list should be updated to match.

**Type consistency.** `EncounterFacts.vignette_id: str` (Task 1) is read by `Pair.meta["vignette_id"]` (Task 1), `split_by_vignette` (Task 3) and `gap_probe` (Task 8). `EvalItem` field names (`facts`, `form`, `document`, `known_placeholders`, `target`) match the existing dataclass at `run_eval.py:43-48` and are used identically in Tasks 4 and 8. `overlap_report`'s keys (`median`, `p95`, `n_above_0_6`, `n`) are produced in Task 5 and consumed by the same task's report block and by Task 9.

**Placeholder scan.** No TBD/TODO; every code step carries runnable code; Task 8's fallback instruction names the concrete corrective action rather than "handle edge cases".
