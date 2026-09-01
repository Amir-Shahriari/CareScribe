"""
Small seeded-sampling primitives shared by the vignette sampler.

A vignette is a declarative skeleton: most of its leaves are ``Choice`` /
``Range`` / ``Weighted`` markers that :func:`resolve` turns into concrete values
using a single ``random.Random``. One seed in ``datagen.yaml`` therefore fixes
the entire corpus.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Sequence


@dataclass(frozen=True)
class Choice:
    """Pick one of ``options`` uniformly."""

    options: Sequence[Any]

    def draw(self, rng: random.Random) -> Any:
        return rng.choice(list(self.options))


@dataclass(frozen=True)
class Weighted:
    """Pick one of ``options`` by matching ``weights``."""

    options: Sequence[Any]
    weights: Sequence[float]

    def draw(self, rng: random.Random) -> Any:
        return rng.choices(list(self.options), weights=list(self.weights), k=1)[0]


@dataclass(frozen=True)
class Range:
    """An integer in ``[low, high]``, optionally rendered with ``unit``."""

    low: int
    high: int
    unit: str | None = None

    def draw(self, rng: random.Random) -> str | int:
        value = rng.randint(self.low, self.high)
        return f"{value} {self.unit}" if self.unit else value


@dataclass(frozen=True)
class Subset:
    """Pick between ``k_low`` and ``k_high`` distinct items from ``options``."""

    options: Sequence[Any]
    k_low: int = 0
    k_high: int | None = None

    def draw(self, rng: random.Random) -> list[Any]:
        pool = list(self.options)
        hi = self.k_high if self.k_high is not None else len(pool)
        k = rng.randint(self.k_low, min(hi, len(pool)))
        return rng.sample(pool, k)


_MARKERS = (Choice, Weighted, Range, Subset)


def resolve(value: Any, rng: random.Random) -> Any:
    """Recursively turn sampling markers into concrete values."""
    if isinstance(value, _MARKERS):
        return resolve(value.draw(rng), rng)
    if isinstance(value, dict):
        return {k: resolve(v, rng) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve(v, rng) for v in value]
    if isinstance(value, tuple):
        return tuple(resolve(v, rng) for v in value)
    return value


__all__ = ["Choice", "Range", "Subset", "Weighted", "resolve"]
