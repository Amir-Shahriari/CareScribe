"""
Hybrid de-identification: deterministic regex + LLM + variant expansion.

Flow
----
1. Deterministic structured pre-pass — see :func:`presidio_prepass`. Pure regex,
   no dependencies. Catches the formats a regex nails and an LLM drops: NHS
   numbers, emails, UK phones and postcodes, context-anchored record numbers,
   and (optionally) in-prose dates.
2. Ask the local model for STRICT JSON listing the identifiers it found. The LLM
   covers what regex can't: free-text names, facilities, relatives, roles.
3. Parse defensively; on failure retry ONCE with a stricter prompt.
4. Merge both sources, deduplicate, assign stable placeholders.
5. Redact in Python, expanding each entity into its surface forms
   (``mapping.surface_forms``) so "Mrs Chen" and "M.E.C." collapse onto the same
   placeholder as "Margaret Elizabeth Chen".

Step 5 being pure Python matters: the model never rewrites the document, so it
cannot hallucinate clinical content into the redacted text.

Neither layer is sufficient alone, and the pair is still not a guarantee — the
reviewer's confirmation step in the UI is load-bearing, not decorative.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from ..prompts.deid_prompt import (
    DEID_RETRY_SYSTEM,
    DEID_RETRY_USER_TEMPLATE,
    DEID_SYSTEM,
    DEID_USER_TEMPLATE,
)
from . import mapping
from .ollama_client import OllamaError, chat

# Rough guard: ~4 chars/token, and we want prompt + document inside an 8k window
# alongside the reply. Beyond this the UI warns the reviewer.
SOFT_CHAR_LIMIT = 20_000

# ---------------------------------------------------------------------------
# In-prose date redaction.
#
# This is the highest-false-positive category in the whole pipeline. Clinical
# text is dense with numbers that look date-shaped, and a wrong hit here damages
# the note's clinical meaning rather than merely leaving an identifier behind.
# Set this to False to disable in-prose date detection entirely; explicit dates
# the LLM reports (DOB, admission, discharge) are unaffected either way.
# ---------------------------------------------------------------------------
REDACT_INPROSE_DATES = True

# Detect organisation names ending in a known descriptor ("... General Hospital")
# and clinician names introduced by a clinical title ("Dr Patel"). Both exist
# because live testing showed the LLM's recall on these two categories is
# unreliable run to run — it dropped a letterhead hospital in one run and two of
# three clinicians in the next. Set either to False to rely on the model alone.
DETECT_ORG_NAMES = True
DETECT_TITLED_NAMES = True


class DeidentificationError(RuntimeError):
    """Raised when the model's output can't be turned into an entity list."""


@dataclass
class DeidResult:
    """Everything the de-identification stage produces."""

    entities: list[dict] = field(default_factory=list)  # {type, value, placeholder}
    redacted_text: str = ""
    phi_map: dict[str, str] = field(default_factory=dict)  # placeholder -> original
    retried: bool = False  # True if the first JSON parse failed


# --------------------------------------------------------------------------
# JSON parsing — models wrap JSON in fences, prose, or both, despite the prompt
# --------------------------------------------------------------------------

_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)


def _strip_fences(raw: str) -> str:
    """Remove leading/trailing markdown code fences."""
    text = raw.strip()
    text = _FENCE_RE.sub("", text)
    return text.strip()


def _first_json_object(text: str) -> str | None:
    """Extract the first balanced ``{...}`` block, ignoring braces inside strings.

    A plain regex can't do this correctly (nested objects, braces in values), so
    we scan with a depth counter and a string-state flag.
    """
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(text)):
        char = text[index]

        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    return None


def parse_entities_json(raw: str) -> list[dict]:
    """Parse a model reply into a list of ``{"type", "value"}`` dicts.

    Tolerates code fences and surrounding prose. Raises
    :class:`DeidentificationError` if no usable JSON object is present.
    """
    if not raw or not raw.strip():
        raise DeidentificationError("The model returned an empty response.")

    cleaned = _strip_fences(raw)

    payload = None
    for candidate in (cleaned, _first_json_object(cleaned)):
        if not candidate:
            continue
        try:
            payload = json.loads(candidate)
            break
        except json.JSONDecodeError:
            continue

    if payload is None:
        raise DeidentificationError(
            "The model did not return valid JSON.\n\nIt replied:\n"
            + raw[:500].strip()
        )

    # Accept {"entities": [...]} and, leniently, a bare [...] list.
    if isinstance(payload, list):
        entities = payload
    elif isinstance(payload, dict):
        entities = payload.get("entities")
        if entities is None:
            # Some models use a different key; take the first list of dicts.
            for value in payload.values():
                if isinstance(value, list):
                    entities = value
                    break
    else:
        entities = None

    if entities is None:
        raise DeidentificationError(
            "The model's JSON had no 'entities' list. It returned:\n"
            + json.dumps(payload)[:500]
        )
    if not isinstance(entities, list):
        raise DeidentificationError("The 'entities' field was not a list.")

    result: list[dict] = []
    for item in entities:
        if not isinstance(item, dict):
            continue
        value = item.get("value")
        if not isinstance(value, str) or not value.strip():
            continue
        result.append({"type": item.get("type"), "value": value.strip()})

    return result


# --------------------------------------------------------------------------
# Deterministic structured pre-pass (pure regex, no dependencies)
# --------------------------------------------------------------------------

# Formats a regex gets right and a language model routinely drops.
STRUCTURED = {
    "NHS_NUMBER": r"\b\d{3}[\s-]?\d{3}[\s-]?\d{4}\b",
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "UK_PHONE": r"\b0\d{2,4}[\s-]?\d{3,4}[\s-]?\d{2,4}\b",
    "UK_POSTCODE": r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b",
}

# Postcodes are matched case-sensitively; case-insensitive would fire on ordinary
# lowercase words that happen to share the letter/digit shape.
_CASE_SENSITIVE = {"UK_POSTCODE"}

_STRUCTURED_COMPILED = {
    name: re.compile(pattern, 0 if name in _CASE_SENSITIVE else re.IGNORECASE)
    for name, pattern in STRUCTURED.items()
}

# Record numbers are only taken when a label vouches for them — a bare 5-10 digit
# run in clinical text is far more likely to be a lab value or a dosage.
MRN_CONTEXT = re.compile(
    r"\b(?:MRN|Hospital\s*(?:No|Number)|Record\s*(?:No|Number)|"
    r"Chart\s*(?:No|Number)|Patient\s*(?:No|Number))\b\.?\s*[:#]?\s*(\d{5,10})\b",
    re.IGNORECASE,
)

# Organisation names, anchored on the same trailing descriptors Task 3 strips to
# build short forms. A live run showed llama3.1:8b silently dropping the hospital
# in a letterhead entirely, which meant no FACILITY entity existed to expand and
# "St. Aidan's" survived. Detecting the long form deterministically is what makes
# the short-form expansion reliable rather than dependent on the model noticing.
_ORG_ALTERNATION = "|".join(
    descriptor.replace(" ", r"\s+") for descriptor in mapping.ORG_DESCRIPTORS
)

# Leading words that make the match a label rather than a name ("GP Practice:").
_ORG_STOPWORDS = frozenset({"gp", "the", "this", "our", "your", "a", "an", "local", "same", "his", "her"})

# Capitalised run + descriptor. The descriptor is matched case-insensitively so
# an ALL-CAPS letterhead works, but the preceding tokens must still be
# capitalised, which keeps it off ordinary prose.
FACILITY_PATTERN = re.compile(
    rf"\b(?:[A-Z][\w'’.\-]*\s+){{1,4}}(?i:{_ORG_ALTERNATION})\b"
)


def _facility_spans(text: str) -> list[tuple[int, int, str]]:
    """Find organisation names ending in a known org descriptor."""
    spans: list[tuple[int, int, str]] = []
    for match in FACILITY_PATTERN.finditer(text):
        first_token = match.group(0).split()[0].strip(".,'").lower()
        if first_token in _ORG_STOPWORDS:
            continue
        spans.append((match.start(), match.end(), "FACILITY"))
    return spans


# Names introduced by a *clinical* title. Personal titles (Mr/Mrs/Ms/Miss) are
# deliberately excluded: they usually introduce the patient, and detecting
# "Mrs Chen" as a separate entity would split one person across two placeholders
# instead of collapsing onto the patient's, which is what Task 2 guarantees.
PERSON_TITLE_PATTERN = re.compile(
    r"\b(?:Dr|Doctor|Sister|Matron|Nurse|Prof|Professor)\b\.?\s+"
    r"((?:[A-Z][\w'’\-]+)(?:\s+[A-Z][\w'’\-]+){0,2})"
)

# Words that make the capture a role, not a name ("Nurse Practitioner").
_ROLE_STOPWORDS = frozenset({
    "practitioner", "specialist", "manager", "team", "station", "ward", "unit",
    "led", "in", "on", "charge", "consultant", "registrar", "bank", "staff",
    "of", "and", "the", "at", "for",
})


def _titled_person_spans(text: str) -> list[tuple[int, int, str]]:
    """Find clinician names following a clinical title.

    The span covers the *name only*, not the title, so the value dedupes against
    whatever the LLM returned and variant expansion regenerates every title form
    from it ("Docherty" -> "Sister Docherty", "Dr. Docherty", ...).
    """
    spans: list[tuple[int, int, str]] = []
    for match in PERSON_TITLE_PATTERN.finditer(text):
        name = match.group(1)
        if name.split()[0].strip(".,'").lower() in _ROLE_STOPWORDS:
            continue
        spans.append((match.start(1), match.end(1), "PROVIDER_NAME"))
    return spans


_MONTHS = (
    "January|February|March|April|May|June|July|August|September|October|"
    "November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
)

# "12/03/1948", "06-06-2026"
NUMERIC_DATE = re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b")

# "4 June", "2nd of June", "21 July 2026"
PROSE_DATE = re.compile(
    rf"\b\d{{1,2}}(?:st|nd|rd|th)?(?:\s+of)?\s+(?:{_MONTHS})\b(?:\s+\d{{4}})?",
    re.IGNORECASE,
)

# Guards against dosages and lab values being read as dates.
_UNIT_AFTER = re.compile(r"^\s*(?:mg|mcg|ug|ml|l|g|kg|mmol|mol|%|bpm|units?)\b", re.IGNORECASE)
_DOSE_BEFORE = re.compile(r"(?:level|levels|dose|dosage|reading|count|score)\s*[:=]?\s*$", re.IGNORECASE)


def _is_clinical_measurement(text: str, start: int, end: int) -> bool:
    """True if a date-shaped span is really a dosage or lab value.

    Rejects a match immediately followed by a unit ("2.5mg", "90 bpm") or
    immediately preceded by a measurement word ("troponin level 12/03").
    """
    if _UNIT_AFTER.match(text[end : end + 12]):
        return True
    if _DOSE_BEFORE.search(text[max(0, start - 24) : start]):
        return True
    return False


def _date_spans(text: str) -> list[tuple[int, int, str]]:
    """Find in-prose date spans, skipping clinical measurements."""
    spans: list[tuple[int, int, str]] = []
    for pattern in (NUMERIC_DATE, PROSE_DATE):
        for match in pattern.finditer(text):
            if _is_clinical_measurement(text, match.start(), match.end()):
                continue
            spans.append((match.start(), match.end(), "DATE"))
    return spans


def presidio_prepass(text: str) -> list[dict]:
    """### STRUCTURED-ID HOOK (formerly the Presidio stub) ###

    Deterministic regex pass over ``text``, run *before* the LLM. Returns
    entities in exactly the shape the LLM returns — ``{"type", "value"}`` — so
    they merge into the review table and get redacted through the same path.

    Covers: NHS numbers, emails, UK phones and postcodes, label-anchored record
    numbers, organisation names, and (when :data:`REDACT_INPROSE_DATES` is set)
    in-prose dates.

    The name is kept for continuity with the original Phase 2 hook, but this is
    pure Python: no Presidio, no spaCy, no GLiNER, no model download. A local NER
    model would improve recall on unstructured identifiers (person names in
    unusual positions, organisation names) and remains a possible future
    enhancement — it is not wired in, by design, to keep the dependency
    footprint small and the behaviour fully deterministic.

    Overlapping matches are resolved longest-span-first, so a phone number is
    never also reported as an NHS number.
    """
    if not text:
        return []

    spans: list[tuple[int, int, str]] = []

    for entity_type, pattern in _STRUCTURED_COMPILED.items():
        for match in pattern.finditer(text):
            spans.append((match.start(), match.end(), entity_type))

    # Label-anchored record numbers: capture the digits, not the label.
    for match in MRN_CONTEXT.finditer(text):
        spans.append((match.start(1), match.end(1), "MRN"))

    if DETECT_ORG_NAMES:
        spans.extend(_facility_spans(text))

    if DETECT_TITLED_NAMES:
        spans.extend(_titled_person_spans(text))

    if REDACT_INPROSE_DATES:
        spans.extend(_date_spans(text))

    # Longest span wins; ties leftmost. Keeps "01632 960 188" as one UK_PHONE
    # rather than also emitting an NHS_NUMBER for an overlapping digit run.
    spans.sort(key=lambda span: (-(span[1] - span[0]), span[0]))

    occupied = bytearray(len(text))
    entities: list[dict] = []
    seen: set[str] = set()

    for start, end, entity_type in spans:
        if any(occupied[start:end]):
            continue
        occupied[start:end] = b"\x01" * (end - start)

        value = text[start:end].strip()
        key = value.casefold()
        if len(value) < mapping.MIN_VALUE_LENGTH or key in seen:
            continue
        seen.add(key)
        entities.append({"type": entity_type, "value": value})

    return entities


def _collapse_person_subsets(entities: list[dict]) -> list[dict]:
    """Drop a person entity whose name is a trailing part of a longer one.

    The regex pass finds "Docherty" (from "Sister Docherty") while the LLM finds
    "Fiona Docherty". Keeping both would split one clinician across two
    placeholders. The longer name's variant expansion already covers the shorter
    form, so dropping the short one loses no recall.

    Matching is on whole tokens: "Chen" collapses into "Margaret Chen", but
    "Aiden" never collapses into "Braiden".
    """
    people = [
        (index, entity)
        for index, entity in enumerate(entities)
        if entity["type"] in mapping.PERSON_TYPES
    ]

    redundant: set[int] = set()
    for index, entity in people:
        tokens = entity["value"].casefold().split()
        for other_index, other in people:
            if other_index == index or other_index in redundant:
                continue
            other_tokens = other["value"].casefold().split()
            if len(other_tokens) <= len(tokens):
                continue
            # Whole-token suffix match: "docherty" inside "fiona docherty".
            if other_tokens[-len(tokens):] == tokens:
                redundant.add(index)
                break

    return [entity for index, entity in enumerate(entities) if index not in redundant]


def merge_entities(*entity_lists: list[dict]) -> list[dict]:
    """Merge entity lists from multiple detectors, de-duplicating by value.

    Earlier lists win on type conflicts, so pass the higher-precision detector
    first (the regex pre-pass before the LLM's guesses).

    Two exceptions:

    * A later list may *upgrade* a generic type. The regex pass reports
      "12/03/1948" as a plain DATE; if the LLM recognises the same string as a
      DOB, the reviewer should see DOB. Specific always beats generic.
    * Partial names collapse into the fuller name for the same person, so one
      person keeps one placeholder.
    """
    combined: list[dict] = []
    for entities in entity_lists:
        combined.extend(entities or [])

    merged = mapping.dedupe_entities(combined)
    by_value = {entity["value"].casefold(): entity for entity in merged}

    for entity in combined:
        value = str(entity.get("value", "") or "").strip().casefold()
        existing = by_value.get(value)
        if existing is None:
            continue
        incoming_type = mapping.normalise_type(entity.get("type"))
        if existing["type"] in mapping.GENERIC_TYPES and incoming_type not in mapping.GENERIC_TYPES:
            existing["type"] = incoming_type

    return _collapse_person_subsets(merged)


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------

def detect_entities(model: str, text: str, timeout: float = 600.0) -> tuple[list[dict], bool]:
    """Ask the model for identifiers. Returns ``(entities, retried)``.

    Retries once with a stricter prompt if the first reply doesn't parse.
    Propagates :class:`OllamaError` (server problems) and
    :class:`DeidentificationError` (parsing problems) to the caller.
    """
    first_error: DeidentificationError | None = None

    try:
        raw = chat(
            model=model,
            system=DEID_SYSTEM,
            user=DEID_USER_TEMPLATE.format(document=text),
            stream=False,
            timeout=timeout,
            temperature=0.0,  # detection should be as deterministic as possible
        )
        return parse_entities_json(str(raw)), False
    except DeidentificationError as exc:
        first_error = exc

    # --- single stricter retry ---
    try:
        raw = chat(
            model=model,
            system=DEID_RETRY_SYSTEM,
            user=DEID_RETRY_USER_TEMPLATE.format(document=text),
            stream=False,
            timeout=timeout,
            temperature=0.0,
        )
        return parse_entities_json(str(raw)), True
    except DeidentificationError as exc:
        raise DeidentificationError(
            f"De-identification failed after a retry.\n\n"
            f"First attempt: {first_error}\n\nRetry: {exc}\n\n"
            f"Try a different model — some small models struggle to emit strict "
            f"JSON. llama3.1:8b is a reliable choice."
        ) from exc


def deidentify(
    model: str,
    text: str,
    use_structured_pass: bool = True,
    use_presidio: bool | None = None,
) -> DeidResult:
    """Run the full de-identification stage over ``text``.

    The structured regex pre-pass is on by default — it is local, instant, and
    costs nothing. ``use_presidio`` is accepted as a deprecated alias for
    ``use_structured_pass`` so older call sites keep working.
    """
    if not text.strip():
        raise DeidentificationError("There is no text to de-identify.")

    if use_presidio is not None:
        use_structured_pass = use_presidio

    llm_entities, retried = detect_entities(model, text)

    # Regex first so its precise structured types take precedence in the merge.
    prepass = presidio_prepass(text) if use_structured_pass else []
    entities = merge_entities(prepass, llm_entities)

    entities = mapping.assign_placeholders(entities)

    # Detected once here and reused, so the map and the preview agree.
    known_as = mapping.find_known_as(text)

    return DeidResult(
        entities=entities,
        redacted_text=mapping.redact(text, entities, known_as),
        phi_map=mapping.build_map(entities),
        retried=retried,
    )


def rebuild(text: str, entities: list[dict]) -> DeidResult:
    """Re-derive redacted text and the PHI map from a user-edited entity table.

    Called after every edit in the Step 2 data editor, so the preview and the
    map always reflect exactly what the reviewer approved — no stale state.

    The structured pre-pass deliberately does NOT re-run here. Its findings are
    already rows in the table by this point, and re-running it would resurrect
    every false positive the reviewer just deleted.
    """
    cleaned = mapping.dedupe_entities(entities)

    # dedupe_entities drops placeholders, so re-attach the ones the user set.
    # First non-empty placeholder per value wins: a later duplicate row with a
    # blank placeholder must not wipe out the one the user typed above it.
    by_value: dict[str, str] = {}
    for entity in entities:
        key = str(entity.get("value", "")).strip().casefold()
        placeholder = str(entity.get("placeholder", "") or "").strip()
        if key and placeholder and not by_value.get(key):
            by_value[key] = placeholder

    for entity in cleaned:
        entity["placeholder"] = by_value.get(entity["value"].casefold(), "")

    with_placeholders = mapping.assign_placeholders(cleaned)

    return DeidResult(
        entities=with_placeholders,
        redacted_text=mapping.redact(text, with_placeholders),
        phi_map=mapping.build_map(with_placeholders),
    )
