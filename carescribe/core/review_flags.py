"""
Residual-candidate highlighter — where the reviewer's eye should go first.

This is deliberately **not** :func:`~carescribe.core.deidentify.residual_scan`.
That function is the blocking gate and has to be precise, because a false
positive there trains reviewers to click past a real one. This module is the
opposite trade: permissive, non-blocking, and tuned for recall. It points at
spans in the *already-redacted* text that could still be hiding an identifier
and asks a human to look.

The class it exists for is the one that actually leaked in testing — a
capitalised token no layer claimed. ``Adeyinka`` left behind when a wrapped name
was only half caught, ``Harrogate`` in a letterhead, ``Kirkstall Lane Surgery``
split over a line. Every one of those is invisible to a scan looking for
structured formats, and obvious to an eye that is told where to look.

Nothing here blocks a write on its own. The UI requires each flag to be either
redacted or explicitly dismissed, which is the point: the reviewer has to have
*seen* each one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from . import deidentify, mapping

# Capitalised words that open sentences and clinical lines, plus the field and
# section labels a form is built from. Flagging these would bury the real
# candidates in noise, and a highlighter nobody reads is worse than none: a
# label is never the identifier — the value beside it is — so reporting "Birth"
# out of "Date of Birth:" costs attention and buys nothing.
#
# Kept as a plain word list rather than a regex so it stays easy to extend.
# Comments must sit outside the literal: anything inside it is split on
# whitespace and becomes a suppressed word.
_COMMON_OPENERS = frozenset(
    """
    the this that these those a an and but or if then when while during after
    before both either neither also however therefore because since although
    he she they it her his their we you i there here what which who whom whose
    her him them us me my our your its
    patient patients client resident service user mr mrs ms miss dr sister nurse
    no yes not none nil all any each per via due from with within without under
    over into onto about above below between across through
    admitted admission discharged discharge diagnosis diagnoses history plan
    plans impression findings investigations results bloods observations
    examination assessment management treatment therapy allergies allergy social
    family background presenting complaint problem problems referral referred
    seen attended attends attending reviewed review medication medications meds
    next kin ward department dept summary follow followup follow-up nursing
    handover contact contacted telephone tel phone email fax address date dob
    born name known typed dictated signed countersigned prepared authorised
    yours sincerely faithfully regards dear re cc copy
    he's she's it's there's
    case number ref id unit hospital record chart nhs no case-no mrn dob
    detained reported described denied continued commenced started stopped
    arranged agreed discussed noted assessed prescribed remains attends
    presented complained requested declined offered advised planned booked
    thank thanks earlier later further
    birth appointment appt present attendees attendance escalation log
    coordinator co-ordinator keyworker amhp consultant cardiologist registrar
    physiotherapist pharmacist surgeon anaesthetist psychologist psychiatrist
    brother sister son daughter wife husband partner mother father carer
    relative relatives nok guardian friend neighbour spouse
    team department unit service crisis resolution home treatment community
    mental health medicine psychological nursing outpatient inpatient
    """.split()
)

# Month names are date material, reported by the date rule rather than as names.
_MONTHS = frozenset(
    """
    january february march april may june july august september october november
    december jan feb mar apr jun jul aug sep sept oct nov dec
    monday tuesday wednesday thursday friday saturday sunday
    """.split()
)

_CAPITALISED_RUN = re.compile(r"\b[A-Z][a-z'’\-]+(?:[ \t]+[A-Z][a-z'’\-]+){0,3}\b")
_ALL_CAPS_RUN = re.compile(r"\b[A-Z][A-Z'’\-]{2,}(?:[ \t]+[A-Z][A-Z'’\-]{2,}){0,3}\b")
_DIGIT_RUN = re.compile(r"(?<![\w-])\d[\d\s-]{3,}\d(?![\w-])")
_INITIALS = re.compile(r"\b(?:[A-Z]\.){2,}")

_MONTH_ALTERNATION = (
    "January|February|March|April|May|June|July|August|September|October|"
    "November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
)
_DATE_SHAPED = re.compile(
    rf"\b(?:\d{{1,2}}[/-]\d{{1,2}}[/-]\d{{2,4}}"
    rf"|\d{{1,2}}(?:st|nd|rd|th)?(?:\s+of)?\s+(?:{_MONTH_ALTERNATION})\b(?:\s+\d{{4}})?"
    rf"|(?:{_MONTH_ALTERNATION})\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,?\s+\d{{4}})?"
    rf"|(?:[01]?\d|2[0-3]):[0-5]\d(?:\s*(?:am|pm|hrs))?)",
    re.IGNORECASE,
)

KIND_NAME = "name"
KIND_ID = "id"
KIND_DATE = "date"
KIND_INITIALS = "initials"

_WHY = {
    KIND_NAME: "looks like a name, place, or organisation",
    KIND_ID: "looks like an ID number",
    KIND_DATE: "looks like a date or time",
    KIND_INITIALS: "looks like a person's initials",
}


@dataclass(frozen=True)
class Flag:
    """One span worth a second look, with its offsets in the redacted text."""

    text: str
    char_start: int
    char_end: int
    kind: str
    why: str

    @property
    def key(self) -> str:
        """Identity for dismissal — per value, so one decision covers repeats."""
        return f"{self.kind}:{self.text.casefold()}"


def _placeholder_ranges(text: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for m in mapping.PLACEHOLDER_RE.finditer(text)]


def _is_common(value: str) -> bool:
    """True if every word in the run is ordinary English or a month name."""
    words = [w.strip(".,;:'’\"()-").casefold() for w in value.split()]
    words = [w for w in words if w]
    if not words:
        return True
    # The detector already knows the clinical abbreviations ("LAD", "CXR",
    # "NSTEMI") and drug-name shapes; reusing that list here keeps the two from
    # drifting apart and costs nothing to maintain.
    return all(
        w in _COMMON_OPENERS
        or w in _MONTHS
        or w in deidentify._CLINICAL_TERMS
        or deidentify._DRUG_SUFFIX.search(w)
        for w in words
    )


def candidate_residuals(deidentified_text: str) -> list[Flag]:
    """Spans in already-redacted text that could still hide an identifier.

    Permissive by design. Ordered by position so the highlighter can render them
    in reading order, and de-duplicated by (kind, value) so a name appearing
    five times is one decision rather than five.
    """
    text = deidentified_text or ""
    if not text.strip():
        return []

    protected = deidentify.protected_ranges(text)
    placeholders = _placeholder_ranges(text)

    def blocked(start: int, end: int) -> bool:
        return any(
            start < p_end and end > p_start
            for p_start, p_end in (*protected, *placeholders)
        )

    found: list[Flag] = []
    claimed: list[tuple[int, int]] = []

    def add(start: int, end: int, kind: str) -> None:
        value = text[start:end].strip()
        if len(value) < 2 or blocked(start, end):
            return
        if any(start < c_end and end > c_start for c_start, c_end in claimed):
            return
        claimed.append((start, end))
        found.append(Flag(value, start, end, kind, _WHY[kind]))

    # Order matters: the most specific shapes claim their span first, so a date
    # is not also reported as a bare digit run.
    for match in _DATE_SHAPED.finditer(text):
        add(match.start(), match.end(), KIND_DATE)

    for match in _INITIALS.finditer(text):
        add(match.start(), match.end(), KIND_INITIALS)

    for match in _DIGIT_RUN.finditer(text):
        digits = re.sub(r"\D", "", match.group(0))
        if len(digits) >= 5:
            add(match.start(), match.end(), KIND_ID)

    for pattern in (_CAPITALISED_RUN, _ALL_CAPS_RUN):
        for match in pattern.finditer(text):
            if _is_common(match.group(0)):
                continue
            add(match.start(), match.end(), KIND_NAME)

    found.sort(key=lambda flag: flag.char_start)

    # One decision per distinct value: the reviewer judges "Adeyinka", not each
    # of its four occurrences.
    seen: set[str] = set()
    unique: list[Flag] = []
    for flag in found:
        if flag.key in seen:
            continue
        seen.add(flag.key)
        unique.append(flag)
    return unique


def outstanding(flags: list[Flag], dismissed: list[str] | tuple[str, ...] = ()) -> list[Flag]:
    """Flags the reviewer has neither redacted away nor dismissed."""
    cleared = {str(value) for value in dismissed}
    return [flag for flag in flags if flag.key not in cleared]


__all__ = [
    "Flag",
    "KIND_DATE",
    "KIND_ID",
    "KIND_INITIALS",
    "KIND_NAME",
    "candidate_residuals",
    "outstanding",
]
