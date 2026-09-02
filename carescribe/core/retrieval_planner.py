"""
Per-field retrieval planning for clinical-form generation.

Roadmap item E imagined "an agent that ranks chunking and retrieval strategies
for each field being filled". This is the deterministic realization: for every
field in the template, decide

* whether house-style **exemplars** are worth retrieving,
* whether clinic **reference material** is relevant, and at what chunk
  granularity (a dose wants a sentence, a formulation wants a whole section),
* the **query** to run — the field's own label plus the salient words of the
  de-identified source, not the whole note.

`RuleBasedPlanner` is the shipped brain: a small keyword taxonomy over field
labels, no model, fully testable. An LLM-driven planner would implement the
same :class:`RetrievalPlanner` protocol and return the same
``{field_key: RetrievalPlan}`` — that is the seam, mirroring
:class:`carescribe.core.backends.CloudBackend`. Nothing here calls a model or
the network, and nothing here feeds reference text into generation — the plan
only decides what to *fetch*; the reference results go to the clinician's
review panel.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .text_search import query_tokens

# Each rule: substrings that may appear in a field label -> chunk granularity
# for reference retrieval on that field. First match wins; no match => the
# field gets no reference retrieval.
_REFERENCE_RULES: list[tuple[tuple[str, ...], str]] = [
    (("medication", "medicine", "dose", "dosage", "dosing", "prescrib", "drug", "titrat"), "sentence"),
    (("diagnos", "prognos", "formulation", "criteria", "classif"), "section"),
    (("risk", "suicid", "self-harm", "self harm", "safeguard", "homicid", "vulnerab"), "paragraph"),
    (("referral", "discharge", "relapse", "care plan", "pathway", "allied health"), "paragraph"),
    (("intervention", "treatment plan", "goals for treatment", "therap"), "paragraph"),
]

_SALIENT_LIMIT = 24


@dataclass(frozen=True)
class RetrievalPlan:
    field_key: str
    field_label: str
    want_exemplars: bool
    want_reference: bool
    granularity: str  # only meaningful when want_reference is True
    query: str


class RetrievalPlanner(Protocol):
    def plan(self, form_spec, deidentified_text: str) -> dict[str, RetrievalPlan]:
        ...


class RuleBasedPlanner:
    """Deterministic planner driven by a keyword taxonomy over field labels."""

    def _salient_terms(self, text: str) -> list[str]:
        seen: list[str] = []
        for token in query_tokens(text):
            if len(token) > 3 and token not in seen:
                seen.append(token)
            if len(seen) >= _SALIENT_LIMIT:
                break
        return seen

    def plan(self, form_spec, deidentified_text: str) -> dict[str, RetrievalPlan]:
        salient = self._salient_terms(deidentified_text)
        plans: dict[str, RetrievalPlan] = {}
        for field in form_spec.fields:
            label_lower = field.label.lower()
            want_reference, granularity = False, "paragraph"
            for stems, gran in _REFERENCE_RULES:
                if any(stem in label_lower for stem in stems):
                    want_reference, granularity = True, gran
                    break
            query = " ".join(query_tokens(field.label) + salient)
            plans[field.key] = RetrievalPlan(
                field_key=field.key,
                field_label=field.label,
                # Form fields are all narrative today (identifiers are separate
                # HeaderFields); the getattr keeps the seam if that changes.
                want_exemplars=(getattr(field, "kind", "narrative") == "narrative"),
                want_reference=want_reference,
                granularity=granularity,
                query=query,
            )
        return plans


def plan(
    form_spec, deidentified_text: str, planner: RetrievalPlanner | None = None
) -> dict[str, RetrievalPlan]:
    return (planner or RuleBasedPlanner()).plan(form_spec, deidentified_text)


__all__ = ["RetrievalPlan", "RetrievalPlanner", "RuleBasedPlanner", "plan"]
