"""
In-memory PII <-> placeholder mapping.

This module is deliberately pure: it takes text and entity dicts and returns new
strings. It never touches disk, never touches ``st.session_state``, and holds no
module-level state. The app owns the map and clears it on "Wipe PHI".

Two-layer model
---------------
An *entity* is a reviewable row: ``{type, value, placeholder}``. A *surface form*
is any string in the document that should collapse to that entity's placeholder —
the entity's own value plus derived variants ("Mrs Chen", "M.E.C.", "St. Aidan's").

Variants are derived at redaction time rather than added as entity rows, so one
person keeps exactly one placeholder no matter how many ways the document spells
their name. :func:`surface_forms` exposes the derived set so the UI can show the
reviewer what will actually be matched.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Iterable

logger = logging.getLogger(__name__)

# Canonical entity types the de-identification prompt is allowed to emit.
ENTITY_TYPES: tuple[str, ...] = (
    "PATIENT_NAME",
    "DOB",
    "MRN",
    "NHS_NUMBER",
    "ADDRESS",
    "PHONE",
    "FAX",
    "EMAIL",
    "SSN",
    "PROVIDER_NAME",
    "FACILITY",
    "DATE",
    "OTHER_ID",
)

# Shorter, friendlier placeholder stems for a few verbose types.
_PLACEHOLDER_STEMS = {
    "PATIENT_NAME": "PATIENT",
    "PROVIDER_NAME": "PROVIDER",
}

# Types whose values name a person — these get name-variant expansion.
PERSON_TYPES = frozenset({"PATIENT_NAME", "PROVIDER_NAME"})

# Types whose values name an organisation — these get org-variant expansion.
FACILITY_TYPES = frozenset({"FACILITY"})

# Types vague enough that a colliding, more specific type should win on merge.
GENERIC_TYPES = frozenset({"DATE", "OTHER_ID"})

# Values shorter than this are too risky to blanket-replace (a two-letter
# "value" would shred the document), so we skip them during redaction.
MIN_VALUE_LENGTH = 2

# Titles recognised both as prefixes to strip and as prefixes to generate.
TITLES = ["Mr", "Mrs", "Ms", "Miss", "Dr", "Sister", "Nurse", "Prof", "Professor", "Sr", "Mx"]
_TITLE_LOOKUP = frozenset(t.lower().rstrip(".") for t in TITLES)

# Trailing organisation descriptors stripped to produce facility short forms.
# Longest first so "General Hospital" is tried before "Hospital".
ORG_DESCRIPTORS = (
    "General Hospital",
    "Medical Practice",
    "Medical Centre",
    "Medical Center",
    "Health Centre",
    "Health Center",
    "Hospital",
    "Practice",
    "Clinic",
    "Trust",
    "Surgery",
    "Centre",
    "Center",
)

# Facility short forms below this length are dropped — a two-letter fragment
# would fire all over the document.
MIN_FACILITY_FORM_LENGTH = 3


def normalise_type(raw: str | None) -> str:
    """Coerce a model-supplied type string onto the canonical list."""
    if not raw:
        return "OTHER_ID"
    candidate = str(raw).strip().upper().replace(" ", "_").replace("-", "_")
    if candidate in ENTITY_TYPES:
        return candidate
    # A few aliases the models (and the regex pre-pass) reach for.
    aliases = {
        "NAME": "PATIENT_NAME",
        "PATIENT": "PATIENT_NAME",
        "PERSON": "PATIENT_NAME",
        "DATE_OF_BIRTH": "DOB",
        "BIRTHDATE": "DOB",
        "MEDICAL_RECORD_NUMBER": "MRN",
        "RECORD_NUMBER": "MRN",
        "HOSPITAL_NUMBER": "MRN",
        "NHS_NO": "NHS_NUMBER",
        "NHS": "NHS_NUMBER",
        "DOCTOR": "PROVIDER_NAME",
        "PROVIDER": "PROVIDER_NAME",
        "PHYSICIAN": "PROVIDER_NAME",
        "HOSPITAL": "FACILITY",
        "CLINIC": "FACILITY",
        "ORG": "FACILITY",
        "PRACTICE": "FACILITY",
        "FACILITY_NAME": "FACILITY",
        "TELEPHONE": "PHONE",
        "PHONE_NUMBER": "PHONE",
        "UK_PHONE": "PHONE",
        "EMAIL_ADDRESS": "EMAIL",
        "ZIP": "ADDRESS",
        "POSTCODE": "ADDRESS",
        "UK_POSTCODE": "ADDRESS",
        "LOCATION": "ADDRESS",
        "ID": "OTHER_ID",
    }
    return aliases.get(candidate, "OTHER_ID")


def dedupe_entities(entities: Iterable[dict]) -> list[dict]:
    """Drop blank and duplicate entities, keeping first-seen order and casing.

    Duplicates are matched case-insensitively on the value; the first spelling
    encountered wins, so re-identification restores the document's own casing.
    """
    seen: dict[str, dict] = {}
    for entity in entities:
        value = str(entity.get("value", "") or "").strip()
        if len(value) < MIN_VALUE_LENGTH:
            continue
        key = value.casefold()
        if key in seen:
            continue
        seen[key] = {"type": normalise_type(entity.get("type")), "value": value}
    return list(seen.values())


def assign_placeholders(entities: Iterable[dict]) -> list[dict]:
    """Attach a stable placeholder to each unique entity.

    A type with exactly one value gets a bare placeholder (``[PATIENT]``); a
    type with several gets numbered ones (``[MRN_1]``, ``[MRN_2]``). Any
    placeholder already present on an entity (e.g. the user edited it in the
    UI) is preserved.
    """
    entities = list(entities)

    # Count how many unique values each type has, to decide bare vs numbered.
    totals: dict[str, int] = {}
    for entity in entities:
        entity_type = normalise_type(entity.get("type"))
        totals[entity_type] = totals.get(entity_type, 0) + 1

    counters: dict[str, int] = {}
    result: list[dict] = []
    for entity in entities:
        entity_type = normalise_type(entity.get("type"))
        stem = _PLACEHOLDER_STEMS.get(entity_type, entity_type)

        existing = str(entity.get("placeholder", "") or "").strip()
        if existing:
            placeholder = existing
        else:
            counters[entity_type] = counters.get(entity_type, 0) + 1
            if totals[entity_type] == 1:
                placeholder = f"[{stem}]"
            else:
                placeholder = f"[{stem}_{counters[entity_type]}]"

        result.append(
            {
                "type": entity_type,
                "value": str(entity.get("value", "")).strip(),
                "placeholder": placeholder,
            }
        )
    return result


# --------------------------------------------------------------------------
# Surface-form expansion
# --------------------------------------------------------------------------

def expand_name_variants(full_name: str, known_as: str | None = None) -> set[str]:
    """Return every plausible written form of one person's name.

    Covers: the full name, each name part standalone, title+surname
    ("Mrs Chen", "Dr. O'Sullivan"), first+surname, and initials ("MEC",
    "M.E.C.", "M.C."), plus an optional "known as" alias.

    A leading title is stripped before deriving parts. Without that, a value the
    model returns as "Dr Patel" would emit "Dr" as a standalone form and redact
    every "Dr" in the document — catastrophic over-redaction. The full original
    string is still kept as a form.

    Future enhancement: a local NER pass could catch name forms this doesn't
    anticipate (nicknames, transliterations). Deliberately not added — it would
    mean a spaCy/GLiNER dependency, and this stays pure-Python regex.
    """
    parts = [p for p in re.split(r"\s+", full_name.strip()) if p]
    if not parts:
        return set()

    variants = {full_name.strip()}

    # Derive from the name proper, not from an honorific.
    core = parts
    if len(parts) > 1 and parts[0].strip(".,").lower() in _TITLE_LOOKUP:
        core = parts[1:]

    for part in core:
        cleaned = part.strip(".,'")
        if len(cleaned) >= 2:
            variants.add(cleaned)  # first / middle / surname standalone

    surname = core[-1].strip(".,")
    first = core[0].strip(".,")

    for title in TITLES:
        variants.add(f"{title} {surname}")
        variants.add(f"{title}. {surname}")

    # "Margaret Chen" for "Margaret Elizabeth Chen" — by far the commonest form
    # in prose, and the one that lets a line-broken "Margaret\nChen" collapse to
    # a single placeholder instead of two.
    if len(core) > 2:
        variants.add(f"{first} {surname}")

    initials = [p[0].upper() for p in core if p[:1].isalpha()]
    if len(initials) >= 2:
        variants.add("".join(initials))
        variants.add(".".join(initials) + ".")
        variants.add(f"{initials[0]}.{initials[-1]}.")

    if known_as:
        variants.add(known_as.strip().strip('"').strip("'"))

    return {v for v in variants if len(v.strip()) >= MIN_VALUE_LENGTH}


def expand_facility_variants(name: str) -> set[str]:
    """Return the full organisation name plus short forms.

    "St. Aidan's General Hospital" -> {"St. Aidan's General Hospital",
    "St. Aidan's General", "St. Aidan's"}. Short forms below
    :data:`MIN_FACILITY_FORM_LENGTH` are dropped to avoid over-redaction.
    """
    name = name.strip()
    if not name:
        return set()

    variants = {name}
    lowered = name.lower()

    for descriptor in ORG_DESCRIPTORS:
        suffix = " " + descriptor.lower()
        if lowered.endswith(suffix):
            short = name[: len(name) - len(suffix)].strip(" ,-")
            if len(short) >= MIN_FACILITY_FORM_LENGTH:
                variants.add(short)

    return {v for v in variants if len(v) >= MIN_FACILITY_FORM_LENGTH}


_KNOWN_AS_RE = re.compile(
    r"\b(?:known\s+as|preferred\s+name|goes\s+by)\b\s*[:\-]?\s*[\"“']?([A-Za-z][\w'\-]{1,30})",
    re.IGNORECASE,
)


def find_known_as(text: str) -> str | None:
    """Pull a patient's preferred name out of a "Known as:" field, if present."""
    match = _KNOWN_AS_RE.search(text or "")
    return match.group(1) if match else None


@dataclass
class SurfaceForms:
    """All strings that redact to a placeholder, plus collisions worth flagging."""

    forms: dict[str, str] = field(default_factory=dict)  # form -> placeholder
    ambiguous: list[tuple[str, str, str]] = field(default_factory=list)  # form, kept, dropped
    by_placeholder: dict[str, list[str]] = field(default_factory=dict)


def surface_forms(entities: Iterable[dict], known_as: str | None = None) -> SurfaceForms:
    """Expand entities into every surface form that should be redacted.

    Entity values are registered first and are authoritative: an explicit row
    always outranks a variant derived from someone else's name. Where two people
    genuinely share a form ("Chen" for both Margaret Chen and David Chen), the
    first entity in table order keeps it and the collision is reported — the
    string still gets redacted either way, which is what matters for recall.
    """
    result = SurfaceForms()

    def register(form: str, placeholder: str) -> None:
        form = (form or "").strip()
        if len(form) < MIN_VALUE_LENGTH or not placeholder:
            return
        existing = result.forms.get(form.casefold())
        if existing is None:
            result.forms[form.casefold()] = placeholder
            result.by_placeholder.setdefault(placeholder, []).append(form)
        elif existing != placeholder:
            result.ambiguous.append((form, existing, placeholder))

    ordered = [e for e in entities if str(e.get("placeholder", "") or "").strip()]

    # Pass 1 — exact entity values.
    for entity in ordered:
        register(str(entity.get("value", "")), str(entity["placeholder"]).strip())

    # Pass 2 — derived variants.
    for entity in ordered:
        entity_type = normalise_type(entity.get("type"))
        value = str(entity.get("value", "")).strip()
        placeholder = str(entity["placeholder"]).strip()

        if entity_type in PERSON_TYPES:
            alias = known_as if entity_type == "PATIENT_NAME" else None
            derived = expand_name_variants(value, alias)
        elif entity_type in FACILITY_TYPES:
            derived = expand_facility_variants(value)
        else:
            continue

        for form in derived:
            register(form, placeholder)

    return result


# --------------------------------------------------------------------------
# Matching and redaction
# --------------------------------------------------------------------------

def _form_pattern(form: str) -> re.Pattern[str] | None:
    """Whitespace-tolerant, case-insensitive pattern for one surface form.

    Tokens are joined with ``\\s+`` so a name split across a line break
    ("Margaret\\nChen") still matches, and non-word guards stop a form firing
    inside a longer word.
    """
    tokens = [t for t in form.split() if t]
    if not tokens:
        return None
    body = r"\s+".join(re.escape(token) for token in tokens)
    return re.compile(r"(?<![\w])" + body + r"(?![\w])", re.IGNORECASE)


def find_spans(text: str, forms: dict[str, str]) -> list[tuple[int, int, str]]:
    """Find non-overlapping ``(start, end, placeholder)`` spans for every form.

    All candidate matches are collected, then resolved longest-span-first so
    "David Chen" beats a bare "Chen" and "14 Leeds Road" is consumed whole. An
    occupancy mask makes the overlap check linear in matched characters.
    """
    candidates: list[tuple[int, int, str]] = []
    for form, placeholder in forms.items():
        pattern = _form_pattern(form)
        if pattern is None:
            continue
        for match in pattern.finditer(text):
            candidates.append((match.start(), match.end(), placeholder))

    # Longest first; ties broken leftmost for determinism.
    candidates.sort(key=lambda span: (-(span[1] - span[0]), span[0]))

    occupied = bytearray(len(text))
    kept: list[tuple[int, int, str]] = []
    for start, end, placeholder in candidates:
        if any(occupied[start:end]):
            continue
        occupied[start:end] = b"\x01" * (end - start)
        kept.append((start, end, placeholder))

    return kept


def redact(text: str, entities: Iterable[dict], known_as: str | None = None) -> str:
    """Replace every surface form of every entity with its placeholder.

    Replacement runs back-to-front so earlier spans keep their indices.
    ``known_as`` is auto-detected from the document when not supplied.
    """
    entities = list(entities)
    if known_as is None:
        known_as = find_known_as(text)

    forms = surface_forms(entities, known_as).forms
    spans = find_spans(text, forms)

    redacted = text
    for start, end, placeholder in sorted(spans, key=lambda span: span[0], reverse=True):
        redacted = redacted[:start] + placeholder + redacted[end:]

    return redacted


def build_map(entities: Iterable[dict]) -> dict[str, str]:
    """Build the placeholder -> original-value map used for re-identification.

    If two entities share a placeholder (possible after manual edits), the first
    one wins — re-identification stays deterministic.
    """
    mapping: dict[str, str] = {}
    for entity in entities:
        placeholder = str(entity.get("placeholder", "") or "").strip()
        value = str(entity.get("value", "") or "").strip()
        if placeholder and value and placeholder not in mapping:
            mapping[placeholder] = value
    return mapping


def residual_values(text: str, entities: Iterable[dict], known_as: str | None = None) -> list[str]:
    """Return surface forms that still appear in ``text`` after redaction.

    Used by the UI as a cheap self-check — a non-empty result means a
    replacement didn't take, which the reviewer needs to know about. Checks
    derived variants too, not just the literal entity values.
    """
    if known_as is None:
        known_as = find_known_as(text)

    leftovers: list[str] = []
    seen: set[str] = set()
    expanded = surface_forms(list(entities), known_as)

    # Report the longest leaking form per placeholder; the short variants of a
    # name that leaked would otherwise bury the signal.
    for form in sorted(expanded.forms, key=len, reverse=True):
        pattern = _form_pattern(form)
        if pattern and pattern.search(text) and form.casefold() not in seen:
            seen.add(form.casefold())
            leftovers.append(form)

    return leftovers


# --------------------------------------------------------------------------
# Re-identification — tolerant of placeholders the note model mangled
# --------------------------------------------------------------------------

# Deliberately loose: matches [PATIENT], [MRN_1], and corrupted forms like
# [MATIENT_2] so they can be repaired rather than silently left in the output.
PLACEHOLDER_RE = re.compile(r"\[[A-Z][A-Z_]*_?\d*\]")

# Maximum edit distance we will accept when repairing a mangled placeholder.
FUZZY_MAX_DISTANCE = 2


def _edit_distance(a: str, b: str, cap: int = FUZZY_MAX_DISTANCE) -> int:
    """Levenshtein distance, short-circuiting once it exceeds ``cap``."""
    if a == b:
        return 0
    if abs(len(a) - len(b)) > cap:
        return cap + 1

    previous = list(range(len(b) + 1))
    for i, char_a in enumerate(a, start=1):
        current = [i]
        for j, char_b in enumerate(b, start=1):
            current.append(
                min(
                    previous[j] + 1,          # deletion
                    current[j - 1] + 1,       # insertion
                    previous[j - 1] + (char_a != char_b),  # substitution
                )
            )
        if min(current) > cap:
            return cap + 1
        previous = current
    return previous[-1]


def resolve_placeholder(token: str, known: Iterable[str]) -> str | None:
    """Map a possibly-corrupted placeholder onto a known one.

    Returns the exact token if it is already known, the nearest known
    placeholder if there is one unambiguously-closest candidate within
    :data:`FUZZY_MAX_DISTANCE`, else ``None``. Ties resolve to ``None`` on
    purpose — guessing between ``[MRN_1]`` and ``[MRN_2]`` would silently
    attach the wrong identity to the text.
    """
    known = list(known)
    if token in known:
        return token

    # A short token gets a tighter budget; 2 edits on "[MRN]" is most of it.
    cap = FUZZY_MAX_DISTANCE if len(token) >= 6 else 1

    scored = sorted((_edit_distance(token, candidate, cap), candidate) for candidate in known)
    if not scored or scored[0][0] > cap:
        return None
    if len(scored) > 1 and scored[1][0] == scored[0][0]:
        return None  # ambiguous — refuse to guess
    return scored[0][1]


@dataclass
class ReidentifyResult:
    """Outcome of a re-identification pass."""

    text: str = ""
    corrected: list[tuple[str, str]] = field(default_factory=list)  # mangled -> repaired
    unresolved: list[str] = field(default_factory=list)


def reidentify_detailed(text: str, mapping: dict[str, str]) -> ReidentifyResult:
    """Swap placeholders back to originals, repairing mangled tokens.

    Never raises on malformed input: an unrecognised bracketed token is left
    exactly as it was found and reported in ``unresolved``.
    """
    if not text:
        return ReidentifyResult(text=text or "")
    if not mapping:
        return ReidentifyResult(text=text)

    result = ReidentifyResult()
    known = list(mapping)

    # Placeholders the tolerant regex can't see (e.g. a user typed "[Pt]") are
    # handled first by plain longest-first replacement, preserving old behaviour.
    restored = text
    for placeholder in sorted(known, key=len, reverse=True):
        if not PLACEHOLDER_RE.fullmatch(placeholder):
            restored = restored.replace(placeholder, mapping[placeholder])

    corrected: list[tuple[str, str]] = []
    unresolved: list[str] = []

    def substitute(match: re.Match[str]) -> str:
        token = match.group(0)
        if token in mapping:
            return mapping[token]

        repaired = resolve_placeholder(token, known)
        if repaired is not None:
            corrected.append((token, repaired))
            return mapping[repaired]

        unresolved.append(token)
        return token  # leave it alone rather than corrupt the note further

    result.text = PLACEHOLDER_RE.sub(substitute, restored)
    result.corrected = corrected
    result.unresolved = unresolved

    for mangled, repaired in corrected:
        # Placeholder names only — no PHI reaches the log.
        logger.warning("Repaired corrupted placeholder %s -> %s", mangled, repaired)
    for token in unresolved:
        logger.warning("Unknown placeholder left unresolved: %s", token)

    return result


def reidentify(text: str, mapping: dict[str, str]) -> str:
    """Swap placeholders back to their original values.

    Thin wrapper over :func:`reidentify_detailed` for callers that only want the
    text. Corrupted placeholders are repaired where a confident match exists.
    """
    return reidentify_detailed(text, mapping).text
