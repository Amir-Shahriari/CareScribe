"""
The ideal filled form for an encounter — the assistant side of a training pair.

This is a **deterministic scaffold**: it maps `EncounterFacts` into the exact
heading structure the form's system prompt asks for, and nothing else. Because
every line is placed from a known fact, the scaffold alone satisfies three of
the four validators — format, faithfulness, placeholder integrity — by
construction. A field whose facts are in `documented_gaps` renders as
"Not documented.", which is what teaches the model to do the same.

An optional prose-polish pass (workstream B.2 stage 2) can rewrite this for
fluency and is then re-validated; if polish fails, the scaffold is kept.
"""

from __future__ import annotations

from finetune.datagen.schema import EncounterFacts, FormType

NOT_DOCUMENTED = "Not documented."


# --------------------------------------------------------------------------- #
# Fact -> line helpers
# --------------------------------------------------------------------------- #


def _med_line(m) -> str:
    bits = [m.name]
    if m.dose:
        bits.append(m.dose)
    if m.route:
        bits.append(f"({m.route})")
    if m.frequency:
        bits.append(m.frequency)
    return " ".join(bits)


def _history_lines(facts: EncounterFacts) -> list[str]:
    out = [facts.presenting_complaint.strip().rstrip(".") + "."]
    out += [
        f"{h.label}: {h.detail}" if h.detail else h.label for h in facts.history
    ]
    return out


def _objective_lines(facts: EncounterFacts) -> list[str]:
    out: list[str] = []
    for f in facts.examination:
        line = f"{f.system}: {f.finding}"
        if f.value:
            line += f" — {f.value}"
        out.append(line)
    for r in facts.investigations:
        line = f"{r.test}: {r.value}"
        if r.flag:
            line += f" ({r.flag})"
        out.append(line)
    if facts.meds:
        out.append("Medications: " + "; ".join(_med_line(m) for m in facts.meds))
    return out


def _plan_lines(facts: EncounterFacts, *, with_follow_up: bool = True) -> list[str]:
    out = [
        f"{p.action}: {p.detail}" if p.detail else p.action for p in facts.plan
    ]
    if with_follow_up and facts.follow_up:
        out.append(f"Follow-up: {facts.follow_up}")
    return out


def _section(heading: str, lines: list[str]) -> str:
    body = "\n".join(f"- {ln}" for ln in lines) if lines else NOT_DOCUMENTED
    return f"**{heading}**\n{body}"


# --------------------------------------------------------------------------- #
# Per-form scaffolds
# --------------------------------------------------------------------------- #


def _soap(facts: EncounterFacts) -> str:
    subjective = _history_lines(facts)
    objective = _objective_lines(facts)
    assessment = list(facts.impression)
    plan = _plan_lines(facts)
    return "\n\n".join(
        [
            _section("S — Subjective", subjective),
            _section("O — Objective", objective),
            _section("A — Assessment", assessment),
            _section("P — Plan", plan),
        ]
    )


def _progress_note(facts: EncounterFacts) -> str:
    interval = [
        f"{h.label}: {h.detail}" if h.detail else h.label for h in facts.history
    ] or [facts.presenting_complaint.strip().rstrip(".") + "."]
    status = _objective_lines(facts)
    response = [
        h.detail for h in facts.history if h.detail and "response" in h.label.lower()
    ]
    assessment = list(facts.impression)
    plan = _plan_lines(facts)
    return "\n\n".join(
        [
            _section("Interval History", interval),
            _section("Current Status", status),
            _section("Response to Treatment", response),
            _section("Assessment", assessment),
            _section("Plan / Next Steps", plan),
        ]
    )


def _care_plan(facts: EncounterFacts) -> str:
    problems = list(facts.impression) or [facts.presenting_complaint]
    problem_lines = [f"{i}. {p}" for i, p in enumerate(problems, start=1)]
    risk = [
        f.value or f.finding
        for f in facts.examination
        if "risk" in f.system.lower() or "risk" in f.finding.lower()
    ]
    return "\n\n".join(
        [
            "**Problem List**\n" + "\n".join(problem_lines),
            _section("Interventions", _plan_lines(facts, with_follow_up=False)),
            _section("Safety & Risk Considerations", risk),
            _section("Patient / Carer Education", []),
            _section("Follow-up", [facts.follow_up] if facts.follow_up else []),
        ]
    )


def _handover(facts: EncounterFacts) -> str:
    situation = [facts.presenting_complaint.strip().rstrip(".") + "."]
    background = list(facts.pmh) + [
        f"{h.label}: {h.detail}" if h.detail else h.label for h in facts.history
    ]
    assessment = list(facts.impression) + _objective_lines(facts)
    recommendation = _plan_lines(facts)
    return "\n\n".join(
        [
            _section("Situation", situation),
            _section("Background", background),
            _section("Assessment", assessment),
            _section("Recommendation", recommendation),
        ]
    )


_SCAFFOLDS = {
    FormType.SOAP: _soap,
    FormType.PROGRESS_NOTE: _progress_note,
    FormType.CARE_PLAN: _care_plan,
    FormType.HANDOVER: _handover,
}


# --------------------------------------------------------------------------
# Uploaded clinic template — <<FIELD:key>> markers, one per FormSpec field
# --------------------------------------------------------------------------

_FIELD_MARKER = "<<FIELD:{key}>>"


def _field_content(label: str, facts: EncounterFacts) -> str:
    """Map an arbitrary clinic-form field to the encounter fact that fits it, or
    NOT_DOCUMENTED. Deliberately conservative — a field with no clear source
    trains the model to write 'Not documented', which is the point."""
    low = label.lower()

    def any_of(*words: str) -> bool:
        return any(w in low for w in words)

    if any_of("diagnos", "prognos", "impression", "formulation") and facts.impression:
        return "; ".join(facts.impression)
    if any_of("presenting problem", "presenting issue", "main issue", "session agenda",
              "reason for referral"):
        return facts.presenting_complaint.strip().rstrip(".") + "."
    if any_of("risk", "suicidal", "self-harm", "self harm", "homicidal", "violence",
              "vulnerab", "abscond", "impulsivit"):
        risk = [
            f.value or f.finding for f in facts.examination
            if "risk" in f.system.lower() or "risk" in f.finding.lower()
        ]
        return "; ".join(risk) if risk else NOT_DOCUMENTED
    if any_of("medication", "current medications", "daily dose"):
        return "; ".join(_med_line(m) for m in facts.meds) if facts.meds else NOT_DOCUMENTED
    if any_of("goal", "treatment plan", "plan for treatment", "intervention applied",
              "next phase", "relapse prevention", "discharge"):
        lines = _plan_lines(facts, with_follow_up=False)
        return "; ".join(lines) if lines else NOT_DOCUMENTED
    if any_of("review date", "follow-up", "follow up"):
        return facts.follow_up or NOT_DOCUMENTED
    if any_of("mood", "affect"):
        hits = [f.value or f.finding for f in facts.examination
                if "mood" in (f.finding + f.system).lower() or "affect" in f.finding.lower()]
        return "; ".join(hits) if hits else NOT_DOCUMENTED
    if any_of("mental state", "symptom"):
        hits = [f"{f.finding}: {f.value}" if f.value else f.finding
                for f in facts.examination if "mental state" in f.system.lower()]
        return "; ".join(hits) if hits else NOT_DOCUMENTED
    if any_of("history of presenting", "psychiatric history", "medical history",
              "previous assessment"):
        hist = list(facts.pmh) + [
            f"{h.label}: {h.detail}" if h.detail else h.label for h in facts.history
        ]
        return "; ".join(hist) if hist else NOT_DOCUMENTED
    if any_of("progress", "obstacle", "setback", "response to treatment"):
        hits = [h.detail for h in facts.history
                if h.detail and any(w in h.label.lower() for w in ("progress", "response", "mood", "status"))]
        return "; ".join(hits) if hits else NOT_DOCUMENTED
    if any_of("outcome measure", "psychometric", "scoring"):
        hits = [f"{r.test} {r.value}" for r in facts.investigations
                if any(c.isdigit() for c in r.value)]
        return "; ".join(hits) if hits else NOT_DOCUMENTED
    return NOT_DOCUMENTED


def uploaded_template_target(facts: EncounterFacts, form_spec) -> str:
    """<<FIELD:key>> content, one line per field, in the spec's field order."""
    parts = []
    for field in form_spec.fields:
        parts.append(
            _FIELD_MARKER.format(key=field.key) + "\n" + _field_content(field.label, facts)
        )
    return "\n".join(parts)


def build_target(facts: EncounterFacts, form: FormType, form_spec=None) -> str:
    """The ideal filled form for ``facts`` — deterministic, fact-placed only.

    ``form_spec`` is required for ``FormType.UPLOADED_TEMPLATE`` (a
    ``carescribe.core.clinical_forms.FormSpec``)."""
    if form == FormType.UPLOADED_TEMPLATE:
        if form_spec is None:
            raise ValueError("UPLOADED_TEMPLATE needs a form_spec")
        return uploaded_template_target(facts, form_spec)
    try:
        scaffold = _SCAFFOLDS[form]
    except KeyError:
        raise NotImplementedError(
            f"no deterministic scaffold for {form}"
        )
    return scaffold(facts)


__all__ = ["NOT_DOCUMENTED", "build_target"]
