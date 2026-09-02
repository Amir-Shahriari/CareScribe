"""
The `Vignette` skeleton and the formulary the domain modules draw on.

A vignette is a declarative shape for one kind of encounter. Its leaves may be
plain values or `sampling` markers (`Choice`, `Range`, `Subset`, `Weighted`);
`finetune.datagen.sampler.expand` resolves them against a seeded RNG and builds
an `EncounterFacts`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from finetune.datagen.schema import EncounterType

# A tiny UK-ish formulary: name -> (doses, route, frequencies). Domain modules
# reference these so doses stay plausible without every vignette re-declaring
# them.
FORMULARY: dict[str, tuple[list[str], str, list[str]]] = {
    "salbutamol": (["100mcg", "200mcg"], "inhaled", ["PRN", "QDS PRN"]),
    "beclometasone": (["100mcg", "200mcg", "400mcg"], "inhaled", ["BD"]),
    "amlodipine": (["5mg", "10mg"], "oral", ["OD"]),
    "ramipril": (["2.5mg", "5mg", "10mg"], "oral", ["OD"]),
    "atorvastatin": (["20mg", "40mg", "80mg"], "oral", ["ON"]),
    "bisoprolol": (["1.25mg", "2.5mg", "5mg"], "oral", ["OD"]),
    "furosemide": (["20mg", "40mg"], "oral", ["OD", "BD"]),
    "sertraline": (["50mg", "100mg", "150mg"], "oral", ["OD"]),
    "mirtazapine": (["15mg", "30mg", "45mg"], "oral", ["ON"]),
    "metformin": (["500mg", "1g"], "oral", ["BD"]),
    "donepezil": (["5mg", "10mg"], "oral", ["ON"]),
    "paracetamol": (["1g"], "oral", ["QDS PRN"]),
    "apixaban": (["2.5mg", "5mg"], "oral", ["BD"]),
}


def med(name: str, dose: str, freq: str) -> dict[str, str]:
    """A medication dict for a vignette, using the formulary's route."""
    route = FORMULARY.get(name, ([], "oral", []))[1]
    return {"name": name, "dose": dose, "route": route, "frequency": freq}


@dataclass(frozen=True)
class Vignette:
    id: str
    specialty: str
    encounter_type: EncounterType | Any  # plain or a sampling marker
    demographics: dict[str, Any]
    presenting_complaint: Any
    weight: float = 1.0
    history: Any = field(default_factory=list)
    pmh: Any = field(default_factory=list)
    meds: Any = field(default_factory=list)
    allergies: Any = field(default_factory=list)
    examination: Any = field(default_factory=list)
    investigations: Any = field(default_factory=list)
    impression: Any = field(default_factory=list)
    plan: Any = field(default_factory=list)
    follow_up: Any = None
    # Fields the sampler is allowed to blank into `documented_gaps`.
    gappable: tuple[str, ...] = ()


__all__ = ["FORMULARY", "Vignette", "med"]
