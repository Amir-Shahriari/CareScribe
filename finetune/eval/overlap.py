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
