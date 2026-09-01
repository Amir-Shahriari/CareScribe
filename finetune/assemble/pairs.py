"""
Assemble validated SFT pairs and split them, stratified.

A pair is one chat example: the real CareScribe system/user prompt (imported,
never re-spelled) plus a validated target form. Only pairs whose target passes
all four validators reach this module.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

from finetune.datagen.schema import EncounterFacts, FormType
from finetune.integrate.prompt_template import build_messages


@dataclass(frozen=True)
class Pair:
    messages: list[dict[str, str]]
    meta: dict[str, object] = field(default_factory=dict)

    def to_json_line(self) -> str:
        return json.dumps(
            {"messages": self.messages, "meta": self.meta},
            ensure_ascii=False,
            sort_keys=True,
        )


def make_pair(
    facts: EncounterFacts,
    form: FormType,
    placeholdered_document: str,
    target: str,
    *,
    style_exemplar: str | None = None,
    polished: bool = False,
) -> Pair:
    messages = build_messages(
        form, placeholdered_document, style_exemplar=style_exemplar
    )
    messages.append({"role": "assistant", "content": target})
    return Pair(
        messages=messages,
        meta={
            "form_type": form.value,
            "specialty": facts.specialty,
            "encounter_type": facts.encounter_type.value,
            "styled": style_exemplar is not None,
            "polished": polished,
            "documented_gaps": list(facts.documented_gaps),
        },
    )


def _stratum(pair: Pair) -> tuple:
    m = pair.meta
    return (m["form_type"], m["specialty"], m["styled"])


def stratified_split(
    pairs: Sequence[Pair],
    *,
    dev_frac: float = 0.1,
    test_frac: float = 0.1,
    seed: int = 0,
) -> dict[str, list[Pair]]:
    """Split into train/dev/test, keeping each stratum's proportions.

    Deterministic: the same pairs and seed always give the same split. A
    stratum too small to contribute to dev/test puts all its pairs in train.
    """
    import random

    buckets: dict[tuple, list[Pair]] = {}
    for p in pairs:
        buckets.setdefault(_stratum(p), []).append(p)

    out: dict[str, list[Pair]] = {"train": [], "dev": [], "test": []}
    for key in sorted(buckets, key=repr):
        group = buckets[key]
        random.Random((seed, key).__hash__()).shuffle(group)
        n = len(group)
        n_test = int(n * test_frac)
        n_dev = int(n * dev_frac)
        out["test"].extend(group[:n_test])
        out["dev"].extend(group[n_test : n_test + n_dev])
        out["train"].extend(group[n_test + n_dev :])
    return out


def write_jsonl(pairs: Iterable[Pair], path: str | Path) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as fh:
        for pair in pairs:
            fh.write(pair.to_json_line() + "\n")
            count += 1
    return count


__all__ = ["Pair", "make_pair", "stratified_split", "write_jsonl"]
