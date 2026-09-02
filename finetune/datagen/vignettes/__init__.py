"""
Hand-authored, non-PHI encounter skeletons, grouped by clinical domain.

`VIGNETTES` is the flat list the sampler draws from; `datagen.yaml` can weight
the mix by specialty. Add a domain by dropping a module here that exposes its
own `VIGNETTES` list and importing it below.
"""

from __future__ import annotations

from .base import Vignette
from . import (
    cardiology,
    elderly_care,
    general_practice,
    mental_health,
    respiratory,
)

_MODULES = (
    general_practice,
    mental_health,
    cardiology,
    respiratory,
    elderly_care,
)

VIGNETTES: list[Vignette] = [v for module in _MODULES for v in module.VIGNETTES]

# Fail loudly on a duplicate id — vignette ids end up in pair metadata.
_seen: set[str] = set()
for _v in VIGNETTES:
    if _v.id in _seen:
        raise ValueError(f"duplicate vignette id: {_v.id}")
    _seen.add(_v.id)

SPECIALTIES: tuple[str, ...] = tuple(sorted({v.specialty for v in VIGNETTES}))

__all__ = ["SPECIALTIES", "VIGNETTES", "Vignette"]
