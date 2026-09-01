"""
The four gates every training pair must pass, reused verbatim by the eval
harness (workstream D). A pair — scaffold or polished — is kept only if
:func:`validate` returns ``ok``.

- **format**   — the output has the form's required headings, in order, with
  nothing but whitespace before the first.
- **faithfulness** — no number in the body that is absent from the encounter
  facts; any section whose source facts are all empty reads "Not documented.".
- **placeholder integrity** — `carescribe.core.mapping.check_placeholder_integrity`
  finds no mangled / unknown / missing token.
- **residual clean** — `carescribe.core.deidentify.residual_scan` finds nothing
  the reviewer had not already cleared.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from carescribe.core import deidentify, mapping

from finetune.assemble.build_target import NOT_DOCUMENTED
from finetune.datagen.schema import EncounterFacts, FormType

_HEADINGS: dict[FormType, list[str]] = {
    FormType.SOAP: ["S — Subjective", "O — Objective", "A — Assessment", "P — Plan"],
    FormType.PROGRESS_NOTE: [
        "Interval History",
        "Current Status",
        "Response to Treatment",
        "Assessment",
        "Plan / Next Steps",
    ],
    FormType.CARE_PLAN: [
        "Problem List",
        "Interventions",
        "Safety & Risk Considerations",
        "Patient / Carer Education",
        "Follow-up",
    ],
    FormType.HANDOVER: ["Situation", "Background", "Assessment", "Recommendation"],
}

# Which encounter-fact fields feed each heading, per form. Used to decide when a
# section is legitimately empty ("Not documented.").
_SECTION_SOURCES: dict[FormType, dict[str, tuple[str, ...]]] = {
    FormType.SOAP: {
        "S — Subjective": ("presenting_complaint", "history"),
        "O — Objective": ("examination", "investigations", "meds"),
        "A — Assessment": ("impression",),
        "P — Plan": ("plan", "follow_up"),
    },
    FormType.PROGRESS_NOTE: {
        "Interval History": ("history", "presenting_complaint"),
        "Current Status": ("examination", "investigations", "meds"),
        "Response to Treatment": ("history",),
        "Assessment": ("impression",),
        "Plan / Next Steps": ("plan", "follow_up"),
    },
    FormType.HANDOVER: {
        "Situation": ("presenting_complaint",),
        "Background": ("pmh", "history"),
        "Assessment": ("impression", "examination", "investigations", "meds"),
        "Recommendation": ("plan", "follow_up"),
    },
}

_NUM_RE = re.compile(r"\d+(?:\.\d+)?")
_ORDINAL_LINE_RE = re.compile(r"^\s*(\d+)[.)]", re.MULTILINE)


@dataclass
class Report:
    format_ok: bool = True
    faithful_ok: bool = True
    placeholder_ok: bool = True
    residual_ok: bool = True
    problems: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return (
            self.format_ok
            and self.faithful_ok
            and self.placeholder_ok
            and self.residual_ok
        )


def _field_is_empty(facts: EncounterFacts, name: str) -> bool:
    return getattr(facts, name) in (None, [], "")


def _numbers_in_facts(facts: EncounterFacts) -> set[str]:
    blob = " ".join(_flatten_strings(facts.model_dump()))
    return set(_NUM_RE.findall(blob))


def _flatten_strings(obj) -> list[str]:
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, dict):
        return [s for v in obj.values() for s in _flatten_strings(v)]
    if isinstance(obj, (list, tuple)):
        return [s for v in obj for s in _flatten_strings(v)]
    if obj is None:
        return []
    return [str(obj)]


def _sections(output: str, headings: list[str]) -> dict[str, str]:
    """Split ``output`` into ``{heading: body}`` for the known headings."""
    positions = []
    for h in headings:
        m = re.search(rf"\*\*\s*{re.escape(h)}\s*\*\*", output)
        if m:
            positions.append((m.start(), m.end(), h))
    positions.sort()
    bodies: dict[str, str] = {}
    for i, (_start, end, h) in enumerate(positions):
        stop = positions[i + 1][0] if i + 1 < len(positions) else len(output)
        bodies[h] = output[end:stop].strip()
    return bodies


def check_format(output: str, form: FormType) -> tuple[bool, list[str]]:
    headings = _HEADINGS.get(form)
    if headings is None:
        return False, [f"no heading spec for {form}"]
    problems: list[str] = []
    last = -1
    first_at = None
    for h in headings:
        m = re.search(rf"\*\*\s*{re.escape(h)}\s*\*\*", output)
        if not m:
            problems.append(f"missing heading: {h}")
            continue
        if first_at is None:
            first_at = m.start()
        if m.start() < last:
            problems.append(f"heading out of order: {h}")
        last = m.start()
    if first_at is not None and output[:first_at].strip():
        problems.append("text before the first heading")
    return not problems, problems


def check_faithfulness(
    output: str, facts: EncounterFacts, form: FormType
) -> tuple[bool, list[str]]:
    problems: list[str] = []
    allowed = _numbers_in_facts(facts)
    # ordinals used to number a problem/plan list are structural, not claims
    allowed |= {m.group(1) for m in _ORDINAL_LINE_RE.finditer(output)}
    for num in _NUM_RE.findall(output):
        if num not in allowed:
            problems.append(f"unsupported number in draft: {num}")

    sources = _SECTION_SOURCES.get(form, {})
    bodies = _sections(output, _HEADINGS.get(form, []))
    for heading, fields in sources.items():
        if all(_field_is_empty(facts, f) for f in fields):
            body = bodies.get(heading, "")
            if NOT_DOCUMENTED not in body:
                problems.append(
                    f"section {heading!r} has no supporting facts but is not "
                    f"marked '{NOT_DOCUMENTED}'"
                )
    return not problems, problems


def check_placeholders(draft: str, known_placeholders) -> tuple[bool, list[str]]:
    """Fail on a mangled or invented bracket token; ignore ``missing``.

    A filled form built from structured facts legitimately does not cite every
    identifier the source held — an NHS number or MRN rarely appears in a SOAP
    narrative — so a known placeholder simply being absent is not a defect.
    What must never happen is a token that resolves to nothing (``unknown``,
    possibly invented) or one corrupted from a real placeholder (``mangled``);
    either breaks re-identification.
    """
    issues = [
        i
        for i in mapping.check_placeholder_integrity(draft, list(known_placeholders))
        if i.kind != mapping.ISSUE_MISSING
    ]
    return not issues, [i.detail for i in issues]


def check_residual(draft: str, acknowledged=()) -> tuple[bool, list[str]]:
    cleared = {" ".join(a.split()).casefold() for a in acknowledged}
    leaked = [
        v
        for v in deidentify.residual_scan(draft or "")
        if " ".join(v.split()).casefold() not in cleared
    ]
    return not leaked, [f"residual identifier: {v!r}" for v in leaked]


def validate(
    output: str,
    facts: EncounterFacts,
    form: FormType,
    *,
    known_placeholders=(),
    acknowledged=(),
) -> Report:
    r = Report()
    r.format_ok, p1 = check_format(output, form)
    r.faithful_ok, p2 = check_faithfulness(output, facts, form)
    r.placeholder_ok, p3 = check_placeholders(output, known_placeholders)
    r.residual_ok, p4 = check_residual(output, acknowledged)
    r.problems = [*p1, *p2, *p3, *p4]
    return r


__all__ = [
    "Report",
    "check_faithfulness",
    "check_format",
    "check_placeholders",
    "check_residual",
    "validate",
]
