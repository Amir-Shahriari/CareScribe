"""
Turn vignettes into `EncounterFacts` instances with a seeded RNG.

`expand` resolves one vignette's sampling markers and builds the facts.
`sample_encounters` draws a whole corpus, weighting by vignette weight and an
optional per-specialty multiplier from `datagen.yaml`.
"""

from __future__ import annotations

import random
from typing import Iterable, Iterator

from finetune.datagen.sampling import resolve
from finetune.datagen.schema import (
    Demographics,
    EncounterFacts,
    EncounterType,
    Finding,
    HistoryItem,
    Medication,
    PlanItem,
    Result,
)
from finetune.datagen.vignettes import VIGNETTES, Vignette

_EMPTY = {None: None, "list": [], "str": ""}


def _blank_for(field_name: str) -> object:
    if field_name == "follow_up":
        return None
    return []


def expand(
    vignette: Vignette,
    rng: random.Random,
    *,
    gap_probability: float = 0.0,
) -> EncounterFacts:
    """Build one `EncounterFacts` from a vignette.

    With ``gap_probability`` > 0, each field listed in ``vignette.gappable`` is
    independently blanked and recorded in ``documented_gaps`` — this is how the
    model learns to write "Not documented" instead of inventing content.
    """
    enc_type = resolve(vignette.encounter_type, rng)
    if not isinstance(enc_type, EncounterType):
        enc_type = EncounterType(enc_type)

    demo = resolve(vignette.demographics, rng)
    history = [HistoryItem(**h) for h in resolve(vignette.history, rng)]
    meds = [Medication(**m) for m in resolve(vignette.meds, rng)]
    examination = [Finding(**f) for f in resolve(vignette.examination, rng)]
    investigations = [
        Result(**{**r, "value": str(r["value"])})
        for r in resolve(vignette.investigations, rng)
    ]
    plan = [PlanItem(**p) for p in resolve(vignette.plan, rng)]

    fields: dict[str, object] = dict(
        specialty=vignette.specialty,
        encounter_type=enc_type,
        demographics=Demographics(**demo),
        presenting_complaint=resolve(vignette.presenting_complaint, rng),
        history=history,
        pmh=list(resolve(vignette.pmh, rng)),
        meds=meds,
        allergies=list(resolve(vignette.allergies, rng)),
        examination=examination,
        investigations=investigations,
        impression=list(resolve(vignette.impression, rng)),
        plan=plan,
        follow_up=resolve(vignette.follow_up, rng),
    )

    gaps: list[str] = []
    for name in vignette.gappable:
        if gap_probability and rng.random() < gap_probability:
            fields[name] = _blank_for(name)
            gaps.append(name)
    fields["documented_gaps"] = gaps

    return EncounterFacts(**fields)


def _weighted_pool(
    vignettes: Iterable[Vignette],
    specialty_weights: dict[str, float] | None,
) -> tuple[list[Vignette], list[float]]:
    pool, weights = [], []
    for v in vignettes:
        mult = (specialty_weights or {}).get(v.specialty, 1.0)
        if v.weight * mult <= 0:
            continue
        pool.append(v)
        weights.append(v.weight * mult)
    return pool, weights


def sample_encounters(
    n: int,
    *,
    seed: int = 0,
    vignettes: Iterable[Vignette] | None = None,
    specialty_weights: dict[str, float] | None = None,
    gap_probability: float = 0.25,
) -> Iterator[EncounterFacts]:
    """Yield ``n`` `EncounterFacts`, deterministic for a given ``seed``."""
    rng = random.Random(seed)
    pool, weights = _weighted_pool(list(vignettes or VIGNETTES), specialty_weights)
    if not pool:
        raise ValueError("no vignettes to sample from")
    for _ in range(n):
        vignette = rng.choices(pool, weights=weights, k=1)[0]
        yield expand(vignette, rng, gap_probability=gap_probability)


__all__ = ["expand", "sample_encounters"]
