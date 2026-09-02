"""
Optional Phase 2 — DPO to sharpen faithfulness and placeholder integrity beyond
what SFT gives.

Gated on the Phase-D eval showing residual failures worth an extra run. For
each kept SFT pair, a *rejected* variant is synthesised by one targeted
corruption: drop a required section, inject one unsupported finding, or mangle
one placeholder. `trl`'s DPOTrainer then learns (chosen > rejected).

This module is a documented stub: `make_rejected` is implemented and tested
(it is pure); `train_dpo` mirrors `sft.train` and is wired but unverified.
"""

from __future__ import annotations

import random
import re

_HEADING_RE = re.compile(r"\*\*.+?\*\*")
_PLACEHOLDER_RE = re.compile(r"\[[A-Z][A-Z0-9_]*\]")


def make_rejected(chosen: str, *, seed: int) -> str:
    """One targeted corruption of a good draft — never more than one."""
    rng = random.Random(seed)
    strategies = ["drop_section", "unsupported_finding", "mangle_placeholder"]
    rng.shuffle(strategies)

    for strategy in strategies:
        if strategy == "drop_section":
            headings = list(_HEADING_RE.finditer(chosen))
            if len(headings) >= 2:
                cut = rng.choice(headings[1:])
                nxt = next(
                    (m for m in headings if m.start() > cut.start()), None
                )
                end = nxt.start() if nxt else len(chosen)
                return (chosen[: cut.start()] + chosen[end:]).strip()
        elif strategy == "unsupported_finding":
            return chosen.rstrip() + "\n- BP 188/121, new AF on ECG today"
        elif strategy == "mangle_placeholder":
            tokens = list(_PLACEHOLDER_RE.finditer(chosen))
            if tokens:
                t = rng.choice(tokens)
                bad = "[" + t.group(0)[2:]  # drop first letter of the name
                return chosen[: t.start()] + bad + chosen[t.end():]
    # nothing applied (very short draft) — fall back to the unsupported finding
    return chosen.rstrip() + "\n- unsupported: patient reports chest pain"


def build_preference_rows(pairs: list[dict], *, seed: int = 0) -> list[dict]:
    """SFT chat rows -> DPO rows ``{prompt, chosen, rejected}``."""
    rows = []
    for i, pair in enumerate(pairs):
        msgs = pair["messages"]
        chosen = msgs[-1]["content"]
        rows.append(
            {
                "prompt": msgs[:-1],
                "chosen": chosen,
                "rejected": make_rejected(chosen, seed=seed + i),
            }
        )
    return rows


def train_dpo(*args, **kwargs):  # pragma: no cover - unverified, needs a GPU
    raise NotImplementedError(
        "DPO phase is wired but not yet verified; enable only if Phase-D eval "
        "shows residual failures after SFT."
    )


__all__ = ["build_preference_rows", "make_rejected", "train_dpo"]
