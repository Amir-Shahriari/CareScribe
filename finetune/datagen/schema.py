"""
`EncounterFacts` — the single source of truth for one synthetic clinical
encounter.

Every training example in this project is generated *from* an `EncounterFacts`
instance, never from prose. Because the facts are ground truth, the three
properties the fine-tune must guarantee — format adherence, faithfulness, and
placeholder integrity — are checkable at data-build time: a rendered target
that does not match its facts is discarded, never trained on.

No identifiers live here. Age is a band, not a date of birth; there is no name,
no NHS number, no address. Real-looking identifiers are injected later, at
render time (`datagen/identifiers.py`), and stripped again by the real
CareScribe de-identifier before a pair is assembled.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

# --------------------------------------------------------------------------- #
# Enums
# --------------------------------------------------------------------------- #


class FormType(str, Enum):
    """The output form a training example asks the model to fill."""

    SOAP = "soap"
    CARE_PLAN = "care_plan"
    PROGRESS_NOTE = "progress_note"
    HANDOVER = "handover"
    UPLOADED_TEMPLATE = "uploaded_template"


class EncounterType(str, Enum):
    """The clinical shape of the encounter the source note describes."""

    NEW = "new"
    FOLLOW_UP = "follow_up"
    DISCHARGE = "discharge"
    HANDOVER = "handover"
    CRISIS = "crisis"


# --------------------------------------------------------------------------- #
# Leaf models
# --------------------------------------------------------------------------- #

_FORBIDDEN_HINT = (
    "no identifiers in EncounterFacts — inject them at render time instead"
)


def _looks_like_identifier(value: str) -> str | None:
    """Return a reason string if ``value`` looks like a leaked identifier."""
    stripped = value.strip()
    digit_run = 0
    for char in stripped:
        if char.isdigit():
            digit_run += 1
            if digit_run >= 4:
                return "contains a 4+ digit run"
        else:
            digit_run = 0
    words = [w for w in stripped.replace(",", " ").split() if w]
    if len(words) >= 2 and all(w[:1].isupper() and w[1:].islower() for w in words[:2]):
        # "John Smith", "Jane Doe" — two consecutive Capitalised words.
        return "looks like a person name"
    return None


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Medication(_Base):
    name: str
    dose: str | None = None
    route: str | None = None
    frequency: str | None = None


class HistoryItem(_Base):
    label: str
    detail: str | None = None


class Finding(_Base):
    system: str
    finding: str
    value: str | None = None


class Result(_Base):
    test: str
    value: str
    flag: str | None = None


class PlanItem(_Base):
    action: str
    detail: str | None = None


class Demographics(_Base):
    age_band: str
    sex: str
    occupation: str | None = None

    @field_validator("age_band", "sex", "occupation")
    @classmethod
    def _no_identifier_shapes(cls, value: str | None) -> str | None:
        if value is None:
            return value
        reason = _looks_like_identifier(value)
        if reason is not None:
            raise ValueError(f"{value!r} {reason}: {_FORBIDDEN_HINT}")
        return value


# --------------------------------------------------------------------------- #
# EncounterFacts
# --------------------------------------------------------------------------- #


class EncounterFacts(_Base):
    """A complete, ground-truth synthetic encounter.

    Every leaf is either a concrete value or explicitly ``None`` / ``[]``. A
    field named in :attr:`documented_gaps` MUST be empty on the instance — that
    is what lets a rendered target legitimately say "Not documented" and what
    teaches the model to do the same instead of inventing content.
    """

    specialty: str
    encounter_type: EncounterType
    demographics: Demographics
    presenting_complaint: str
    history: list[HistoryItem] = []
    pmh: list[str] = []
    meds: list[Medication] = []
    allergies: list[str] = []
    examination: list[Finding] = []
    investigations: list[Result] = []
    impression: list[str] = []
    plan: list[PlanItem] = []
    follow_up: str | None = None
    documented_gaps: list[str] = []

    # Fields a `documented_gaps` entry is allowed to name. `presenting_complaint`
    # is deliberately excluded — an encounter with no complaint is not a valid
    # sample.
    _GAPPABLE = frozenset(
        {
            "history",
            "pmh",
            "meds",
            "allergies",
            "examination",
            "investigations",
            "impression",
            "plan",
            "follow_up",
        }
    )

    @field_validator("specialty", "presenting_complaint")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be empty")
        return value

    @model_validator(mode="after")
    def _gaps_are_real_and_empty(self) -> EncounterFacts:
        for name in self.documented_gaps:
            if name not in FIELD_NAMES:
                raise ValueError(
                    f"documented_gaps names {name!r}, which is not a field of "
                    f"EncounterFacts"
                )
            if name not in self._GAPPABLE:
                raise ValueError(
                    f"documented_gaps names {name!r}, which cannot be a "
                    f"documented gap"
                )
            current = getattr(self, name)
            if current not in (None, [], ""):
                raise ValueError(
                    f"documented_gaps names {name!r} but the field is "
                    f"populated ({current!r}); a gap must be empty"
                )
        return self


# The EncounterFacts field set, for validators and downstream workstreams to
# import rather than re-deriving.
FIELD_NAMES: frozenset[str] = frozenset(EncounterFacts.model_fields)

GAPPABLE_FIELDS: frozenset[str] = EncounterFacts._GAPPABLE


__all__ = [
    "FIELD_NAMES",
    "GAPPABLE_FIELDS",
    "Demographics",
    "EncounterFacts",
    "EncounterType",
    "Finding",
    "FormType",
    "HistoryItem",
    "Medication",
    "PlanItem",
    "Result",
]
