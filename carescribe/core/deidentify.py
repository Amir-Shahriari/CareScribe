"""
Layered, CPU-only de-identification.

No network, no GPU, no LLM. Every layer runs locally against the document text
and contributes character spans; the layers are merged, resolved
longest-match-wins, and turned into reviewable entities with stable
placeholders.

Layers
------
1. **Structured regex** (:func:`structured_spans`) — deterministic, highest
   precision. NHS numbers, UK phones, emails, UK postcodes, label-anchored
   record numbers, address lines, organisation names ending in a known
   descriptor, and names introduced by a clinical title.
2. **Presidio + spaCy NER** (:func:`ner_spans`) — recall for free-text entities.
   PERSON / LOCATION / ORGANIZATION / DATE_TIME plus Presidio's own pattern
   recognisers. This is the layer that catches a name sitting in the middle of a
   paragraph, where no label or title vouches for it.
3. **GLiNER** (:func:`gliner_spans`) — optional. Only runs if the package
   imported; the pipeline is fully functional without it.
4. **Variant expansion** — at redaction time, in :mod:`.mapping`. Every entity
   fans out into the forms the document might actually use ("Mrs Chen",
   "M.E.C.", "St. Aidan's"), all mapped onto that entity's single placeholder.
5. **Line-break-tolerant matching** — also in :mod:`.mapping`: form tokens are
   joined with ``\\s+``, so "Margaret\\nChen" still matches "Margaret Chen".

Recall is the union of the layers. Precision is bought back by the filters in
:func:`_span_is_plausible` — NER on clinical prose will happily label "ECG" an
organisation and "Leeds" an address, and blindly trusting it would damage the
document's clinical meaning, which is a worse failure than an untidy redaction.

None of this is a guarantee. The reviewer's approval step in the UI, and the
:func:`residual_scan` gate behind it, are load-bearing.
"""

from __future__ import annotations

import os
import re
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

from . import applog, mapping

# ---------------------------------------------------------------------------
# Protected terms — the allow-list that outranks every detection layer
# ---------------------------------------------------------------------------

PROTECTED_TERMS_PATH = Path(__file__).with_name("protected_terms.txt")


def load_protected_terms(path: Path | None = None) -> list[str]:
    """Read the editable allow-list. Blank lines and ``#`` comments are ignored."""
    source = path or PROTECTED_TERMS_PATH
    try:
        raw = source.read_text(encoding="utf-8")
    except OSError:
        return []
    terms = []
    for line in raw.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            terms.append(line)
    return terms


def _build_protected_pattern(terms: list[str]) -> re.Pattern[str] | None:
    if not terms:
        return None
    # Longest first so "Mental Health Act" wins over a bare "Act" if both listed.
    ordered = sorted(terms, key=len, reverse=True)
    body = "|".join(r"\s+".join(re.escape(t) for t in term.split()) for term in ordered)
    return re.compile(rf"(?<!\w)(?:{body})(?!\w)", re.IGNORECASE)


PROTECTED_TERMS = load_protected_terms()
_PROTECTED_RE = _build_protected_pattern(PROTECTED_TERMS)


def protected_ranges(text: str) -> list[tuple[int, int]]:
    """Character ranges of every allow-listed term occurrence in ``text``."""
    if _PROTECTED_RE is None or not text:
        return []
    return [(m.start(), m.end()) for m in _PROTECTED_RE.finditer(text)]


def reload_protected_terms(path: Path | None = None) -> list[str]:
    """Re-read the allow-list from disk (the file is meant to be edited by hand)."""
    global PROTECTED_TERMS, _PROTECTED_RE
    PROTECTED_TERMS = load_protected_terms(path)
    _PROTECTED_RE = _build_protected_pattern(PROTECTED_TERMS)
    return PROTECTED_TERMS

# Rough guard: very long documents are slower to review, not unsafe. The UI
# warns past this so a reviewer knows what they are taking on.
SOFT_CHAR_LIMIT = 20_000


# ---------------------------------------------------------------------------
# Policy flags
# ---------------------------------------------------------------------------

# In-prose dates are the highest-false-positive category in the whole pipeline.
# Clinical text is dense with date-shaped numbers, and a wrong hit here damages
# the note's clinical meaning rather than merely leaving an identifier behind.
#
# False (the default): only dates carrying an identity anchor are redacted —
# "DOB: 12/03/1948", "Admitted 4 June 2026". A procedure date buried in prose
# ("Angiography on 06/06/2026") is left alone, as are durations ("six weeks"),
# dosing frequencies ("once daily"), and every lab value that looks date-shaped.
#
# True: every date-shaped span is redacted, minus the dosage/lab-value guard.
REDACT_INPROSE_DATES = False

# Layer switches. Turning a layer off costs recall, never correctness.
USE_STRUCTURED = True
USE_NER = True
USE_GLINER = True  # no-op unless the gliner package is importable

# ---------------------------------------------------------------------------
# Offline enforcement
#
# De-identification must never touch the network. Left to itself, a spaCy or
# HuggingFace component that cannot find a local resource will try to fetch it —
# which on a clinic network behind a captive portal does not fail, it *hangs*,
# and the clinician sees a frozen app with no explanation.
#
# These flags turn that hang into an immediate, legible error. Set at import,
# before any of those libraries initialise.
# ---------------------------------------------------------------------------
for _var, _value in (
    ("HF_HUB_OFFLINE", "1"),
    ("TRANSFORMERS_OFFLINE", "1"),
    ("HF_DATASETS_OFFLINE", "1"),
    ("NO_PROXY", "*"),
):
    os.environ.setdefault(_var, _value)

# Which spaCy model to use, tried in order.
#
# The packaged app defaults to the small model: en_core_web_lg is ~750 MB and
# slow to load on the laptops this is aimed at, and a first-run stall reads as a
# broken app. `md` and `lg` are better on free-text names and are preferred when
# installed. Override with CARESCRIBE_SPACY_MODEL.
SPACY_MODEL_PREFERENCE = ("en_core_web_lg", "en_core_web_md", "en_core_web_sm")
PACKAGED_DEFAULT_MODEL = "en_core_web_sm"


def _model_preference() -> tuple[str, ...]:
    override = (os.environ.get("CARESCRIBE_SPACY_MODEL") or "").strip()
    if override:
        return (override,)
    return SPACY_MODEL_PREFERENCE


SPACY_MODELS = _model_preference()


def resolve_model_path(name: str) -> str | None:
    """Where a spaCy model package actually lives, or ``None`` if absent.

    Resolved explicitly rather than trusting ``spacy.load`` to find it, so a
    model missing from a frozen build is a clear message instead of a download
    attempt.
    """
    try:
        import importlib.util

        spec = importlib.util.find_spec(name)
    except Exception:  # noqa: BLE001
        return None
    if spec is None or not spec.submodule_search_locations:
        return None
    return str(list(spec.submodule_search_locations)[0])


def available_models() -> list[str]:
    """Every spaCy model importable in this environment."""
    return [name for name in SPACY_MODEL_PREFERENCE if resolve_model_path(name)]

# GLiNER labels, per the pipeline spec. Only used when the package is present.
GLINER_MODEL = "urchade/gliner_small-v2.1"
GLINER_LABELS = ("person", "organization", "address", "id")
GLINER_THRESHOLD = 0.5

# Presidio results below this confidence are noise. US_DRIVER_LICENSE fires on
# any 7-digit run at score 0.01, which in a clinical document means every lab
# value and every dosage.
NER_MIN_SCORE = 0.35

# Presidio entity types we act on. Everything else it can produce (URL, CRYPTO,
# IBAN, US_DRIVER_LICENSE, NRP...) is either irrelevant to a UK clinical record
# or too noisy to be worth the false positives.
NER_ACCEPTED = {
    "PERSON": "PERSON",
    "LOCATION": "ADDRESS",
    "ORGANIZATION": "FACILITY",
    "DATE_TIME": "DATE",
    "EMAIL_ADDRESS": "EMAIL",
    "PHONE_NUMBER": "PHONE",
    "UK_NHS": "NHS_NUMBER",
    "US_SSN": "SSN",
    "CREDIT_CARD": "OTHER_ID",
    "MEDICAL_LICENSE": "OTHER_ID",
}

# Layer precedence when two layers claim the same span. Lower sorts first.
_SOURCE_RANK = {"regex": 0, "gliner": 1, "ner": 2, "wrapped": 3}


class DeidentificationError(RuntimeError):
    """Raised when de-identification can't run at all."""


@dataclass
class Span:
    """One detection, in character offsets over the source text."""

    start: int
    end: int
    entity_type: str
    source: str = "regex"
    score: float = 1.0


@dataclass
class DeidResult:
    """Everything the de-identification stage produces for one document."""

    entities: list[dict] = field(default_factory=list)  # {type,value,placeholder,action}
    redacted_text: str = ""
    phi_map: dict[str, str] = field(default_factory=dict)  # placeholder -> original
    known_as: str | None = None


# ---------------------------------------------------------------------------
# Engine loading — lazy, cached, and never fatal
# ---------------------------------------------------------------------------

_ENGINE_LOCK = threading.Lock()
_ANALYZER: object | None = None
_ANALYZER_MODEL: str | None = None
_ANALYZER_ERROR: str | None = None
_ANALYZER_TRIED = False

_GLINER: object | None = None
_GLINER_ERROR: str | None = None
_GLINER_TRIED = False


def _build_analyzer() -> tuple[object | None, str | None, str | None]:
    """Build a Presidio ``AnalyzerEngine`` over spaCy. Returns (engine, model, error)."""
    try:
        from presidio_analyzer import AnalyzerEngine
        from presidio_analyzer.nlp_engine import NlpEngineProvider
    except ImportError as exc:
        return None, None, f"presidio-analyzer is not installed ({exc})."

    errors: list[str] = []
    for model_name in SPACY_MODELS:
        # Resolve the package before asking Presidio for it. If it is not on
        # disk, say so — do not hand the name to a loader that would try to
        # fetch it and hang on a captive-portal network.
        model_path = resolve_model_path(model_name)
        if model_path is None:
            errors.append(f"{model_name}: not installed in this build")
            applog.warn("NER model %s: not installed", model_name)
            continue

        applog.log("loading NER model %s from %s", model_name, model_path)
        started = time.monotonic()
        try:
            provider = NlpEngineProvider(
                nlp_configuration={
                    "nlp_engine_name": "spacy",
                    "models": [{"lang_code": "en", "model_name": model_name}],
                }
            )
            engine = AnalyzerEngine(
                nlp_engine=provider.create_engine(), supported_languages=["en"]
            )
            applog.log(
                "NER model %s loaded in %.1fs", model_name, time.monotonic() - started
            )
            return engine, model_name, None
        except Exception as exc:  # noqa: BLE001 — any failure means "try the next model"
            applog.exception("NER model %s failed to load", model_name)
            errors.append(f"{model_name}: {exc}")

    detail = "\n".join(errors)
    applog.warn("no NER model could be loaded:\n%s", detail)
    if is_frozen_build():
        # In a packaged build there is no pip to run, and no network fetch is
        # permitted, so this is a broken build rather than a setup step.
        return None, None, (
            "The de-identification model is not installed in this build.\n\n"
            "This is a packaging fault, not something you can fix here — the "
            "app needs rebuilding with the language model included.\n\n"
            f"Details:\n{detail}"
        )
    return None, None, (
        "No spaCy model could be loaded. Install one with:\n"
        f"    python -m spacy download {PACKAGED_DEFAULT_MODEL}\n\n" + detail
    )


def is_frozen_build() -> bool:
    return bool(getattr(sys, "frozen", False))


def get_analyzer() -> object | None:
    """Return the shared Presidio analyzer, or ``None`` if it can't be built.

    First call pays the model load (a few seconds on CPU); the result is cached
    for the life of the process.
    """
    global _ANALYZER, _ANALYZER_MODEL, _ANALYZER_ERROR, _ANALYZER_TRIED
    if _ANALYZER_TRIED:
        return _ANALYZER
    with _ENGINE_LOCK:
        if not _ANALYZER_TRIED:
            _ANALYZER, _ANALYZER_MODEL, _ANALYZER_ERROR = _build_analyzer()
            _ANALYZER_TRIED = True
    return _ANALYZER


def get_gliner() -> object | None:
    """Return the shared GLiNER model, or ``None`` if it isn't available.

    Guarded end to end: a missing package, a missing weights download, or a load
    failure all degrade to ``None`` and the pipeline runs on layers 1-2.
    """
    global _GLINER, _GLINER_ERROR, _GLINER_TRIED
    if _GLINER_TRIED:
        return _GLINER
    with _ENGINE_LOCK:
        if _GLINER_TRIED:
            return _GLINER
        _GLINER_TRIED = True
        try:
            from gliner import GLiNER  # type: ignore[import-not-found]
        except Exception as exc:  # noqa: BLE001
            _GLINER_ERROR = f"gliner not installed ({exc}). Optional — layers 1-2 still run."
            return None
        try:
            _GLINER = GLiNER.from_pretrained(GLINER_MODEL)
        except Exception as exc:  # noqa: BLE001
            _GLINER_ERROR = f"gliner failed to load {GLINER_MODEL}: {exc}"
            _GLINER = None
    return _GLINER


def engine_status() -> dict:
    """Report which layers are live, for the sidebar. Loads nothing by itself."""
    return {
        "structured": USE_STRUCTURED,
        "ner": _ANALYZER is not None,
        "ner_model": _ANALYZER_MODEL,
        "ner_error": _ANALYZER_ERROR,
        "gliner": _GLINER is not None,
        "gliner_error": _GLINER_ERROR,
        "inprose_dates": REDACT_INPROSE_DATES,
    }


def warm_up() -> dict:
    """Load every enabled engine now, so the first document isn't the slow one."""
    if USE_NER:
        get_analyzer()
    if USE_GLINER:
        get_gliner()
    return engine_status()


# ---------------------------------------------------------------------------
# Layer 1 — structured regex
# ---------------------------------------------------------------------------

STRUCTURED = {
    "NHS_NUMBER": r"\b\d{3}[\s-]?\d{3}[\s-]?\d{4}\b",
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "PHONE": r"\b0\d{2,4}[\s-]?\d{3,4}[\s-]?\d{2,4}\b",
    "ADDRESS": r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b",  # UK postcode
}

# Postcodes are matched case-sensitively; case-insensitive would fire on ordinary
# lowercase words that happen to share the letter/digit shape.
_CASE_SENSITIVE = {"ADDRESS"}

_STRUCTURED_COMPILED = {
    name: re.compile(pattern, 0 if name in _CASE_SENSITIVE else re.IGNORECASE)
    for name, pattern in STRUCTURED.items()
}

# Record numbers are only taken when a label vouches for them — a bare 5-10 digit
# run in clinical text is far more likely to be a lab value or a dosage.
#
# The label may carry a parenthetical gloss ("Hospital No (MRN): 4471982" is
# what document #2 used, and the old pattern stopped dead at the bracket), and
# the value may be grouped with spaces or hyphens ("33-201-45"). Both are
# separator noise around the same thing: a labelled 5-10 digit identifier.
#
# "Trust ID"/"Trust No" is a UK trust's own local patient identifier, distinct
# from the national NHS number — document #11's corpus sibling used "Local
# Trust ID: TR-2026-00458" and the old label list had no entry for it at all,
# so a letter-prefixed local ID sailed through untouched. GMC/NMC/HCPC numbers
# are a different identifier again: not the patient's, but the treating
# clinician's public professional-register number, which is at least as
# identifying as their name and was likewise never anchored.
_MRN_LABELS = (
    r"MRN|Hospital\s*(?:No|Number)|Record\s*(?:No|Number)|Case\s*(?:No|Number)|"
    r"Chart\s*(?:No|Number)|Patient\s*(?:No|Number)|Unit\s*(?:No|Number)|"
    r"Patient\s*ID|Hosp\s*No|NHS\s*Trust\s*No|Trust\s*(?:No|Number|ID)|"
    r"GMC\s*(?:No|Number)?|NMC\s*(?:No|Number|PIN)?|HCPC\s*(?:No|Number|Registration)?"
)

MRN_CONTEXT = re.compile(
    rf"\b(?:{_MRN_LABELS})\b"
    r"(?:[ \t]*\([^)\n]{0,24}\))?"   # optional gloss: "(MRN)", "(hospital)"
    # "Case No.:" carries both a full stop and a colon, so the separator run has
    # to allow several punctuation marks, not one.
    r"[ \t]*[:#.]*[ \t]*"
    r"([A-Z]{0,3}[\s-]?\d(?:[ \t-]?\d){4,9})\b",
    re.IGNORECASE,
)

# Kinship words, shared by the labelled-relative field below and the role
# classifier further down.
_KINSHIP = (
    r"son|daughter|wife|husband|partner|mother|father|mum|mother|dad|brother|"
    r"sister|spouse|carer|next\s+of\s+kin|nephew|niece|grandson|granddaughter|"
    r"grandmother|grandfather|guardian|friend|neighbour"
)

# Labelled identity fields. The value is whatever follows the label on that line,
# which is exactly where a field value ends — the property NER does not know.
_NAME_VALUE = r"([A-Z][\w'’\-]*(?:[ \t]+[A-Z][\w'’\-]*){0,3})"

PATIENT_LINE = re.compile(
    r"^[ \t]*(?:Patient(?:[ \t]+name)?|Client(?:[ \t]+name)?|Service[ \t]+user|"
    r"Resident|Referral[ \t]+for)[ \t]*:[ \t]*" + _NAME_VALUE + r"[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)

RELATIVE_LINE = re.compile(
    rf"^[ \t]*(?:Next[ \t]+of[ \t]+kin|NOK|Emergency[ \t]+contact|Carer|"
    rf"Nearest[ \t]+relative|{_KINSHIP})[ \t]*:[ \t]*" + _NAME_VALUE + r"[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)

# Ward names. Anchored either on a "Ward:" field or on the "<Name> Ward" form, so
# the bare word "ward" in prose ("reviewed on the ward") is never touched.
WARD_PATTERN = re.compile(
    r"(?:^[ \t]*Ward[ \t]*:[ \t]*(?P<field>[A-Z][\w'’\-]*(?:[ \t]+[A-Z][\w'’\-]*){0,3})"
    r"(?:[ \t]+Ward)?[ \t]*$)"
    r"|(?P<named>\b[A-Z][\w'’\-]+(?:[ \t]+[A-Z][\w'’\-]+){0,2}[ \t]+Ward\b)",
    re.MULTILINE,
)

# Care Programme Approach identifier. Anchored to a label so the bare acronym
# "CPA" — the care approach itself, which is on the protected list — survives.
CPA_NUMBER = re.compile(
    r"\bCPA(?:[ \t]*(?:number|no|ref|id))?[ \t]*[:#.]*[ \t]*"
    r"(CPA[-\s]?\d{2,6}(?:[-\s]?[A-Z0-9]{1,4})?)\b",
    re.IGNORECASE,
)
CPA_BARE = re.compile(r"\b(CPA[-\s]\d{2,6}(?:[-\s]?[A-Z0-9]{1,4})?)\b")

# A labelled address line is taken whole: "14 Leeds Road, Harrogate, LS9 4TT".
# Grabbing the entire value is what lets the NER layer stay strict about bare
# place names, which is how "visiting family in Leeds" survives.
ADDRESS_LINE = re.compile(
    r"^[ \t]*(?:Home\s+|Postal\s+|Correspondence\s+)?Addr(?:ess)?"
    r"(?:\s*(?:line)?\s*\d)?[ \t]*:[ \t]*(\S.*?)[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)

_ORG_ALTERNATION = "|".join(
    descriptor.replace(" ", r"\s+") for descriptor in mapping.ORG_DESCRIPTORS
)

# Leading words that make the match a label rather than a name ("GP Practice:").
_ORG_STOPWORDS = frozenset(
    {
        "gp", "the", "this", "our", "your", "a", "an", "local", "same", "his", "her",
        "to", "at",
        # Section-heading words NER hands back as part of an organisation:
        # "Next review" became a clinic, which then redacted "NEXT OF KIN".
        "next", "ward", "bloods", "medication", "nursing", "handover", "present",
        "referral", "diagnosis", "history", "plan", "impression", "summary",
    }
)

# Capitalised run + descriptor. The descriptor is matched case-insensitively so
# an ALL-CAPS letterhead works, but the preceding tokens must still be
# capitalised, which keeps it off ordinary prose.
FACILITY_PATTERN = re.compile(
    rf"\b(?:[A-Z][\w'’.\-]*[ \t]+){{1,4}}(?i:{_ORG_ALTERNATION})\b"
)

# Names introduced by a *clinical* title. Personal titles (Mr/Mrs/Ms/Miss) are
# deliberately excluded: they usually introduce the patient, and detecting
# "Mrs Chen" as a separate entity would split one person across two placeholders
# instead of collapsing onto the patient's.
PERSON_TITLE_PATTERN = re.compile(
    r"\b(?:Dr|Doctor|Sister|Matron|Nurse|Prof|Professor|Consultant|Registrar)\b\.?[ \t]+"
    r"((?:[A-Z][\w'’\-]+)(?:[ \t]+[A-Z][\w'’\-]+){0,2})"
)

# --- Header / footer place names -----------------------------------------
#
# A letterhead carries the site's town and county on a line of their own
# ("Harrogate, North Yorkshire"). No street word and no postcode follows, so the
# address gate that protects "visiting family in Leeds" correctly declines it —
# and it sailed through in the clear on document #2.
#
# The rule is narrow on purpose: a line consisting of *nothing but* two
# capitalised phrases separated by a comma, in the first or last few lines of
# the document. Clinical prose never takes that shape, so the precision cost is
# close to nil while the letterhead case is caught deterministically.
HEADER_FOOTER_LINES = 6

_PLACE_PHRASE = r"[A-Z][\w'’\-]*(?:[ \t]+[A-Z][\w'’\-]*){0,3}"

HEADER_LOCATION = re.compile(
    rf"^[ \t]*({_PLACE_PHRASE},[ \t]*{_PLACE_PHRASE})[ \t]*$"
)

# A clinician sign-off in a footer ("Dr Adaeze Chukwuemeka, Consultant
# Psychiatrist") has exactly the same two-phrases-joined-by-a-comma shape as a
# letterhead town/county line, and it sits in the same footer zone. Document
# #15's corpus sibling caught this: the whole sign-off line — name and role
# both — was swallowed as one LOCATION, when the name belongs to
# PERSON_TITLE_PATTERN and the role ("Consultant Psychiatrist") is clinical
# content that must survive. A line opening with a personal/clinical title, or
# whose second phrase is a known clinical role, is a person, never a place.
_HEADER_LOCATION_PERSON_GUARD = re.compile(
    r"^(?:Dr|Doctor|Mr|Mrs|Ms|Miss|Mx|Prof|Professor|Sister|Nurse|Matron|Sr)\b"
    r"|,[ \t]*(?:Consultant|Registrar|SHO|SpR|FY1|FY2|GP|Nurse|Sister|Matron|"
    r"CPN|OT|SALT|Physio(?:therapist)?|Pharmacist|Surgeon|Anaesthetist|"
    r"Psychologist|Psychiatrist|Social\s+worker|Care\s*co-?ordinator|Specialist)\b",
    re.IGNORECASE,
)


def _header_footer_bounds(text: str) -> list[tuple[int, int]]:
    """Character ranges of the document's opening and closing lines."""
    lines = text.splitlines(keepends=True)
    if not lines:
        return []
    offsets: list[tuple[int, int]] = []
    position = 0
    for line in lines:
        offsets.append((position, position + len(line)))
        position += len(line)

    head = offsets[:HEADER_FOOTER_LINES]
    tail = offsets[-HEADER_FOOTER_LINES:]
    zones = []
    if head:
        zones.append((head[0][0], head[-1][1]))
    if tail and (not zones or tail[0][0] > zones[0][1]):
        zones.append((tail[0][0], tail[-1][1]))
    return zones


# --- Staff names written as initial + surname -----------------------------
#
# "A. Whitfield" in a Typed-by line, "R. Ellis (OT)" in an attendee list. NER
# catches these only sometimes — it caught them in the fixture and missed them
# in document #2 — so layer 1 has to carry the guarantee itself.
#
# Initials are separated from the surname by spaces or tabs only, never a
# newline: allowing a line break is how "M.E.C.\nFollow-up" would become the
# name "M.E.C. Follow".
INITIAL_SURNAME = re.compile(
    r"\b((?:[A-Z]\.){1,3}[ \t]*[A-Z][\w'’\-]+)\b"
)

# Role words that vouch for an initial+surname being staff. Broader than the
# clinical titles in PERSON_TITLE_PATTERN — a community team signs off with job
# titles ("Care coordinator", "CPN", "OT") rather than "Dr".
_STAFF_ROLE_BEFORE = re.compile(
    r"(?:\b(?:Dr|Doctor|Sister|Matron|Nurse|Prof|Professor|Consultant|Registrar|"
    r"CPN|OT|SALT|Physio|Physiotherapist|Pharmacist|Surgeon|Anaesthetist|"
    r"Psychologist|Psychiatrist|Social\s+worker|Support\s+worker|Key\s+worker|"
    r"Care\s+coordinator|Care\s+co-ordinator|Named\s+nurse|Keyworker)"
    r"\b[\s:.]*|"
    r"\b(?:typed|dictated|signed|countersigned|prepared|authorised|reviewed|"
    r"seen|assessed|checked)\s+by[\s:]*|"
    r"\b(?:Present|Attendees?|In\s+attendance|Copy\s+to|Cc)\s*:[^\n]*?)$",
    re.IGNORECASE,
)

# A parenthetical job title straight after the name does the same job.
_STAFF_ROLE_AFTER = re.compile(
    r"^[ \t]*[(,][ \t]*(?:Consultant|Registrar|SHO|SpR|FY1|FY2|GP|Nurse|Sister|"
    r"Matron|CPN|OT|SALT|Physio|Physiotherapist|Pharmacist|Surgeon|Anaesthetist|"
    r"Psychologist|Psychiatrist|Social\s+worker|Care\s+coordinator|Specialist)",
    re.IGNORECASE,
)


# Words that make the capture a role, not a name ("Nurse Practitioner").
_ROLE_STOPWORDS = frozenset(
    {
        "practitioner", "specialist", "manager", "team", "station", "ward", "unit",
        "led", "in", "on", "charge", "consultant", "registrar", "bank", "staff",
        "of", "and", "the", "at", "for", "review", "reviewed", "cardiologist",
        "physician", "surgeon", "anaesthetist", "practice",
    }
)

_MONTHS = (
    "January|February|March|April|May|June|July|August|September|October|"
    "November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
)

NUMERIC_DATE = re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b")

PROSE_DATE = re.compile(
    rf"\b\d{{1,2}}(?:st|nd|rd|th)?(?:\s+of)?\s+(?:{_MONTHS})\b(?:\s+\d{{4}})?",
    re.IGNORECASE,
)

# Guards against dosages and lab values being read as dates.
_UNIT_AFTER = re.compile(
    r"^\s*(?:mg|mcg|ug|ml|l|g|kg|mmol|mol|%|bpm|units?|iu|/kg)\b", re.IGNORECASE
)
_DOSE_BEFORE = re.compile(
    r"(?:level|levels|dose|dosage|reading|count|score|bp|inr|hb|ratio)\s*[:=]?\s*$",
    re.IGNORECASE,
)

# Labels that mark a date as part of someone's identity rather than part of the
# clinical narrative. A date carrying one of these is ALWAYS redacted, whatever
# REDACT_INPROSE_DATES says — the flag governs unlabelled prose dates only.
#
# "Date typed" and "Next review" are here because document #2 had them and they
# were not anchors, so the same date was redacted in one field and left standing
# in the next.
_DATE_ANCHORS = (
    r"D\.?O\.?B|Date\s+of\s+Birth|Birth\s*date|Born|Admitted|Admission|"
    r"Discharged|Discharge\s+date|Date\s+of\s+discharge|Appointment|Appt|"
    r"Follow[\s-]?up\s+(?:on|date)|Seen\s+on|Attended|Next\s+visit|"
    r"Reviewed\s+on|Clinic\s+date|Visit\s+date|"
    r"Date\s+typed|Typed\s+on|Typed|Dictated(?:\s+on)?|Transcribed(?:\s+on)?|"
    r"Next\s+review|Review\s+date|Date\s+seen|Letter\s+date|Date\s+of\s+letter|"
    r"Date\s+of\s+admission|Date\s+of\s+assessment|Assessment\s+date"
)

# The subset that specifically means "this is a birth date". A numeric date is
# only typed DOB under one of these; "Appointment: 12/09/2026" is an ordinary
# DATE, and typing it DOB put an [DOB] placeholder on a clinic appointment.
_BIRTH_ANCHORS = r"D\.?O\.?B|Date\s+of\s+Birth|Birth\s*date|Born"
_BIRTH_ANCHOR_BEFORE = re.compile(
    rf"\b(?:{_BIRTH_ANCHORS})\b[\s:.,\-–—]*(?:on|at)?[\s:]*$", re.IGNORECASE
)
_DATE_ANCHOR_BEFORE = re.compile(
    rf"\b(?:{_DATE_ANCHORS})\b[\s:.,\-–—]*(?:on|at)?[\s:]*$", re.IGNORECASE
)
_DATE_ANCHOR_WINDOW = 60

# Appointment and contact dates. For a psychiatrist these are identifying — when
# a patient was seen, called, or admitted places them somewhere at a time — so
# they are redacted even with REDACT_INPROSE_DATES off. The anchor may sit
# either side of the date ("arranged to see her on 21 July", "the 3 August
# crisis call"), so both directions are checked, and the window is a clause
# rather than a whole sentence to keep durations out of range.
_CONTACT_ANCHORS = (
    r"appointment|appt|review(?:ed)?|seen|see|seeing|arranged\s+to\s+see|"
    r"attend(?:ed|s|ance)?|visit(?:ed|s)?|call(?:ed|s)?|contact(?:ed|s)?|"
    r"rang|phoned|telephoned|spoke|admitted|admission|discharged?|"
    r"assessed|assessment|clinic|crisis|follow[\s-]?up|booked|scheduled"
)
# The window stops at a full stop, not at a line break: a soft wrap is still the
# same sentence, and "arranged for 6 August 2026\nat 14:30" put the anchor and
# the time on opposite sides of a newline, so the time stayed in the clear.
_CONTACT_BEFORE = re.compile(
    rf"\b(?:{_CONTACT_ANCHORS})\b[^.]{{0,40}}$", re.IGNORECASE
)
_CONTACT_AFTER = re.compile(
    rf"^[^.]{{0,24}}\b(?:{_CONTACT_ANCHORS})\b", re.IGNORECASE
)
_CONTACT_WINDOW = 60

# A time of day attached to an appointment ("21 July 2026 at 10:15").
CLOCK_TIME = re.compile(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\s*(?:am|pm|hrs)?\b", re.IGNORECASE)


# A real calendar date or clock time, as opposed to the durations and
# frequencies Presidio also returns as DATE_TIME ("three-day", "six weeks",
# "twice daily"). The contact rule below only ever applies to these: without the
# shape test, "admitted on [DATE] following a three-day history" put an anchor
# within reach of the duration and redacted the clinical detail.
_CALENDAR_SHAPE = re.compile(
    rf"^(?:\d{{1,2}}[/-]\d{{1,2}}[/-]\d{{2,4}}"
    rf"|\d{{1,2}}(?:st|nd|rd|th)?(?:\s+of)?\s+(?:{_MONTHS})(?:\s+\d{{4}})?"
    rf"|(?:{_MONTHS})\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,?\s+\d{{4}})?"
    rf"|(?:[01]?\d|2[0-3]):[0-5]\d\s*(?:am|pm|hrs)?)$",
    re.IGNORECASE,
)


def _looks_like_calendar_date(value: str) -> bool:
    return bool(_CALENDAR_SHAPE.match(value.strip()))


def _has_contact_anchor(text: str, start: int, end: int) -> bool:
    """True if a real date sits in an appointment or contact clause."""
    if not _looks_like_calendar_date(text[start:end]):
        return False
    before = text[max(0, start - _CONTACT_WINDOW) : start]
    after = text[end : end + _CONTACT_WINDOW]
    return bool(_CONTACT_BEFORE.search(before) or _CONTACT_AFTER.match(after))


def _is_clinical_measurement(text: str, start: int, end: int) -> bool:
    """True if a date-shaped span is really a dosage or lab value."""
    if _UNIT_AFTER.match(text[end : end + 12]):
        return True
    if _DOSE_BEFORE.search(text[max(0, start - 24) : start]):
        return True
    return False


# A labelled date *field* — the whole line up to the date is a label ending in a
# colon. "Admission date:" reads as one label, which the anchor list could not
# express: it matches "Admission" and then chokes on the word "date" before the
# colon. Any "<something> date:" field is an identity field by construction.
_DATE_FIELD_LABEL = re.compile(
    r"^[ \t]*(?:[A-Za-z][\w'’\-]*[ \t]+){0,3}"
    r"(?:date|dates|dob|d\.o\.b\.?|born|birth|admitted|admission|discharged|"
    r"discharge|appointment|appt|review|reviewed|typed|dictated|transcribed|"
    r"seen|attended|assessment|letter)"
    r"[ \t]*(?:\([^)\n]{0,24}\))?[ \t]*:[ \t]*$",
    re.IGNORECASE,
)


def _is_labelled_date_field(text: str, start: int) -> bool:
    """True if the date sits in a labelled field ("Admission date: 11 May 2026")."""
    line_start, _ = _line_bounds(text, start)
    return bool(_DATE_FIELD_LABEL.match(text[line_start:start]))


def _has_identity_anchor(text: str, start: int) -> bool:
    """True if an identity label ("DOB:", "Admitted") sits just before ``start``."""
    if _is_labelled_date_field(text, start):
        return True
    return bool(_DATE_ANCHOR_BEFORE.search(text[max(0, start - _DATE_ANCHOR_WINDOW) : start]))


def _time_span_wanted(text: str, start: int, end: int) -> bool:
    """A clock time is identifying only when it belongs to an appointment."""
    return _has_contact_anchor(text, start, end)


def date_span_wanted(text: str, start: int, end: int) -> bool:
    """Policy gate for one date-shaped span.

    Clinical measurements are never dates. Beyond that, when
    :data:`REDACT_INPROSE_DATES` is False only identity-anchored dates qualify.
    """
    if _is_clinical_measurement(text, start, end):
        return False
    if REDACT_INPROSE_DATES:
        return True
    if _has_identity_anchor(text, start):
        return True
    # An appointment or contact date is identifying whatever the flag says.
    return _has_contact_anchor(text, start, end)


def flatten_lines(text: str) -> tuple[str, list[int]]:
    """Return ``text`` with every line break collapsed to one space, plus an
    offset map back to the original.

    ``index_map[i]`` is the offset in ``text`` of the character that produced
    ``flat[i]``, so a span found on the flattened copy maps straight back.

    A whitespace run containing a break becomes exactly one space regardless of
    whether the file uses LF or CRLF. Substituting in place instead — one space
    per character — turned "\\r\\n" into two spaces, and spaCy tokenises the
    double space differently, so the same document detected differently
    depending on which machine had written it.
    """
    flat: list[str] = []
    index_map: list[int] = []
    position = 0
    length = len(text)
    while position < length:
        char = text[position]
        if char.isspace():
            run_end = position
            while run_end < length and text[run_end].isspace():
                run_end += 1
            run = text[position:run_end]
            if "\n" in run or "\r" in run:
                flat.append(" ")
                index_map.append(position)
            else:
                flat.append(run)
                index_map.extend(range(position, run_end))
            position = run_end
            continue
        flat.append(char)
        index_map.append(position)
        position += 1
    return "".join(flat), index_map


# A blank line — two or more newlines with only spaces/tabs between them — is
# a paragraph or section boundary. flatten_lines() (above) collapses it to a
# single space like any other line break, on purpose: it exists to reconnect
# a name split by ONE line wrap ("Oluwaseun\nAdeyinka"), and that flattened
# copy is exactly what the "wrapped" detection pass in analyze() runs NER
# over. A wrapped name never has a blank paragraph in the middle of it, so a
# wrapped-pass span whose original-text range crosses one is never a genuine
# reconnection — corpus document #15 caught this exact shape: "Overall risk
# rating: Medium" was immediately followed by a blank line and then an
# unrelated paragraph ("Bloods showed..."), and the flattened copy joined
# them into what read as a two-word name, later trimmed down to "Medium"
# alone. _crosses_paragraph_break lets analyze() reject that class of
# cross-section artefact without touching flatten_lines() itself, which
# other, genuine same-paragraph wraps still depend on.
_BLANK_LINE = re.compile(r"\n[ \t]*\r?\n")


def _crosses_paragraph_break(text: str, start: int, end: int) -> bool:
    """True if the ORIGINAL-text span ``text[start:end]`` contains a blank line."""
    return bool(_BLANK_LINE.search(text[start:end]))


def _is_staff_context(text: str, start: int, end: int) -> bool:
    """True if an initial+surname sits somewhere that vouches for it being staff.

    Scoped to the name's own line: a "Present:" heading vouches for every name
    on that line, and a role word vouches for the name that follows it. Looking
    further afield would let one "Dr" three lines up bless an unrelated token.
    """
    line_start, _ = _line_bounds(text, start)
    before = text[line_start:start]
    after = text[end : end + 40]
    return bool(_STAFF_ROLE_BEFORE.search(before) or _STAFF_ROLE_AFTER.match(after))


def _plausible_surname(value: str) -> bool:
    """True if the trailing token of an initial+surname reads like a real name.

    Rejects the clinical shapes that share the pattern: "T3/T4" never reaches
    here, but "S. aureus" would if the surname test were only "is it a word".
    """
    surname = value.split()[-1] if value.split() else value
    surname = surname.strip(".,;:'’\"()-")
    if len(surname) < 3 or not surname[:1].isupper():
        return False
    key = surname.casefold()
    return not (key in _NOT_A_NAME or key in _CLINICAL_TERMS or _DRUG_SUFFIX.search(key))


def structured_spans(text: str) -> list[Span]:
    """Layer 1: deterministic regex detections over ``text``."""
    spans: list[Span] = []

    for entity_type, pattern in _STRUCTURED_COMPILED.items():
        for match in pattern.finditer(text):
            spans.append(Span(match.start(), match.end(), entity_type))

    for match in MRN_CONTEXT.finditer(text):
        spans.append(Span(match.start(1), match.end(1), "MRN"))

    # Labelled identity fields, taken deterministically. Leaving these to NER
    # meant a "Brother: David Chen" line whose value ran into the next line came
    # back as one person covering two people, and the brother lost his role.
    for pattern, entity_type in (
        (PATIENT_LINE, "PATIENT_NAME"),
        (RELATIVE_LINE, "RELATIVE_NAME"),
    ):
        for match in pattern.finditer(text):
            value = match.group(1)
            if value.split()[0].strip(".,'").lower() in _ROLE_STOPWORDS:
                continue
            spans.append(Span(match.start(1), match.end(1), entity_type))

    for match in WARD_PATTERN.finditer(text):
        group = "field" if match.group("field") else "named"
        spans.append(Span(match.start(group), match.end(group), "WARD"))

    for pattern in (CPA_NUMBER, CPA_BARE):
        for match in pattern.finditer(text):
            spans.append(Span(match.start(1), match.end(1), "CPA_NO"))

    for match in ADDRESS_LINE.finditer(text):
        spans.append(Span(match.start(1), match.end(1), "ADDRESS"))

    for zone_start, zone_end in _header_footer_bounds(text):
        for line in re.finditer(r"[^\n]*", text[zone_start:zone_end]):
            match = HEADER_LOCATION.match(line.group(0))
            if not match:
                continue
            value = match.group(1)
            # A letterhead line naming the organisation is a FACILITY, and the
            # facility pattern below has the better span for it.
            if FACILITY_PATTERN.search(value):
                continue
            # A clinician sign-off ("Dr X, Consultant Psychiatrist") is a
            # person, not a place — see _HEADER_LOCATION_PERSON_GUARD above.
            if _HEADER_LOCATION_PERSON_GUARD.search(value):
                continue
            offset = zone_start + line.start() + match.start(1)
            spans.append(Span(offset, offset + len(value), "LOCATION"))

    for match in INITIAL_SURNAME.finditer(text):
        value = match.group(1)
        if not _plausible_surname(value):
            continue
        if _is_staff_context(text, match.start(1), match.end(1)):
            spans.append(Span(match.start(1), match.end(1), "PROVIDER_NAME"))
        else:
            # Still a person, but nothing vouches for the role — leave it
            # generic so classify_person and the NER layer can refine it.
            spans.append(Span(match.start(1), match.end(1), "PERSON"))

    for match in FACILITY_PATTERN.finditer(text):
        if match.group(0).split()[0].strip(".,'").lower() in _ORG_STOPWORDS:
            continue
        spans.append(Span(match.start(), match.end(), "FACILITY"))

    for match in PERSON_TITLE_PATTERN.finditer(text):
        name = match.group(1)
        if name.split()[0].strip(".,'").lower() in _ROLE_STOPWORDS:
            continue
        # The span covers the name only, not the title, so it dedupes against
        # what NER returns and variant expansion regenerates every title form.
        spans.append(Span(match.start(1), match.end(1), "PROVIDER_NAME"))

    for pattern in (NUMERIC_DATE, PROSE_DATE):
        for match in pattern.finditer(text):
            if not date_span_wanted(text, match.start(), match.end()):
                continue
            # A numeric date is only a birth date when a birth label says so.
            # Everything else — an appointment, a review date — is a DATE, and
            # shares the DATE placeholder run with its prose twin.
            window = text[max(0, match.start() - _DATE_ANCHOR_WINDOW) : match.start()]
            is_dob = bool(_BIRTH_ANCHOR_BEFORE.search(window))
            spans.append(Span(match.start(), match.end(), "DOB" if is_dob else "DATE"))

    for match in CLOCK_TIME.finditer(text):
        if _time_span_wanted(text, match.start(), match.end()):
            spans.append(Span(match.start(), match.end(), "DATE"))

    return spans


# ---------------------------------------------------------------------------
# Precision filters — what NER gets wrong on clinical prose
# ---------------------------------------------------------------------------

# Acronyms and abbreviations spaCy routinely mislabels as ORG or PERSON. Not
# exhaustive and not meant to be: the all-caps heuristic below catches the rest.
_CLINICAL_TERMS = frozenset(
    """
    ecg ekg echo cxr ct mri mra us doppler nstemi stemi mi acs lad rca lcx lima
    pci cabg lvef tte toe inr fbc ue lft crp esr bnp hba1c egfr bp hr rr spo2
    copd ckd aki tia cva dvt pe af svt vt vf chf hf pcp dnacpr tpn ng iv im sc
    po prn od bd tds qds nocte stat gtn ppi nsaid dm t1dm t2dm uti lrti urti
    obs sob nad nka dnar itu icu hdu aande ed gp sho spr fy1 fy2 mdt
    mg mcg ug ml kg mmol mol bpm iu units unit mmhg cm mm kcal
    hb wcc plt mcv rbc wbc alt ast alp ggt tsh ft4 ft3 psa ldl hdl
    spirometry fev1 fvc peak flow audiometry ecog gcs mmse phq gad
    """.split()
)

# Capitalised words that start clinical lines and sentences. NER hands these
# back inside PERSON and ORGANIZATION spans; they must be trimmed off or the
# entity value swallows real clinical text.
_NOT_A_NAME = frozenset(
    """
    follow followup the this that these those she he they it her his their patient
    patients client resident discharge discharged admitted admission admit nursing
    nurse history medication medications meds next kin ward department dept summary
    diagnosis diagnoses review reviewed reviewing consultant cardiologist cardiology
    respiratory neurology oncology surgery surgical medical general practice clinic
    hospital trust known name address telephone tel phone email fax dob date born
    plan plans impression findings investigations results bloods observations
    examination assessment management treatment therapy allergies allergy social
    physician surgeon anaesthetist practitioner pharmacist physiotherapist
    psychologist psychiatrist paramedic midwife radiographer dietitian
    family background presenting complaint problem problems referral referred
    seen attended attends attending under with and but for from on at in of to
    was were is are has have had been being will would should may might can could
    no none nil not yes all any each per via due if then than when while during
    after before both either neither also however therefore because since although
    angiography angiogram echocardiogram procedure operation theatre recovery
    outpatient inpatient community district safeguarding capacity mobility
    continence nutrition hydration skin pressure falls risk care plan handover
    level levels value values range ranges count counts score scores reading
    readings dose doses units unit result baseline target trend
    """.split()
)

# Street descriptors that make a place name part of an address rather than a
# bare mention of a town.
_STREET_WORDS = re.compile(
    r"\b(?:road|rd|street|st|lane|ln|avenue|ave|close|drive|dr|way|court|ct|"
    r"place|pl|terrace|crescent|cres|gardens|grove|row|walk|hill|park|square|"
    r"mews|rise|view|villas|buildings|house|flat|apartment)\b",
    re.IGNORECASE,
)

_POSTCODE = _STRUCTURED_COMPILED["ADDRESS"]

# "Label:" at the head of a line — the value that follows ends at the line end.
_FIELD_LABEL_LINE = re.compile(r"^[ \t]*[A-Za-z][\w \t/'’-]{0,30}:[ \t]*$")

# The trailing words an organisation name may legitimately wrap onto.
_WRAPPABLE_DESCRIPTORS = frozenset(
    [d.casefold() for d in mapping.ORG_DESCRIPTORS] + ["ward", "unit", "team", "house"]
)

# A capitalised token immediately followed by a dose is a drug, not a name.
_DOSE_AFTER = re.compile(
    r"^[\s,]*\d+(?:\.\d+)?\s*(?:mg|mcg|ug|g|ml|l|units?|iu|%)\b", re.IGNORECASE
)

# The same dose, but inside the span rather than after it.
_DOSE_INSIDE = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:mg|mcg|ug|ml|units?|iu)\b", re.IGNORECASE
)

# Common drug-name endings — a backstop for medications with no dose attached.
_DRUG_SUFFIX = re.compile(
    r"(?:statin|pril|sartan|olol|azole|cillin|mycin|parin|grelor|oxaban|"
    r"tidine|prazole|dipine|semide|formin|codone|morphine|azepam|pramine)$",
    re.IGNORECASE,
)

# Dotted initials: "M.E.C." is a legitimate identifier, unlike "ECG".
_DOTTED_INITIALS = re.compile(r"^(?:[A-Z]\.){2,}$")

_TITLE_TOKEN = frozenset(
    t.lower().rstrip(".") for t in mapping.TITLES + ["Doctor", "Matron", "Consultant", "Registrar"]
)


def _is_acronym(value: str) -> bool:
    """True for a short all-caps token like "ECG" or "LS9" — never a name here."""
    stripped = value.strip(".,'’- ")
    if _DOTTED_INITIALS.match(stripped):
        return False
    return len(stripped) <= 6 and stripped.upper() == stripped and any(c.isalpha() for c in stripped)


def _looks_clinical(value: str) -> bool:
    """True if the value is a known clinical abbreviation or a drug name."""
    key = value.strip(".,'’- ").casefold()
    if key in _CLINICAL_TERMS:
        return True
    return bool(_DRUG_SUFFIX.search(key))


def _trim_span(text: str, start: int, end: int, entity_type: str) -> tuple[int, int] | None:
    """Shrink a NER span to its identifying core.

    Drops leading titles ("Sister Fiona Docherty" -> "Fiona Docherty", so the
    name collapses onto one placeholder rather than two) and edge tokens that
    are ordinary English or section headings ("M.E.C.\\nFollow" -> "M.E.C.").
    Returns ``None`` if nothing identifying is left.
    """
    value = text[start:end]
    leading = len(value) - len(value.lstrip())
    trailing = len(value) - len(value.rstrip())
    start, end = start + leading, end - trailing
    if start >= end:
        return None

    # An unclosed bracket means the span ran into a parenthetical that isn't
    # part of the name: "T. Adeyemi (Physio" replaced the name *and* half the
    # job title, leaving a stray ")" in the redacted text.
    value = text[start:end]
    if "(" in value and ")" not in value:
        end = start + value.index("(")
        while end > start and text[end - 1].isspace():
            end -= 1
        if start >= end:
            return None

    # A date never runs past the end of its own line. NER hands back
    # "14 June 2026\nDate" for a discharge field whose next line starts with
    # "Date typed:", and carrying that newline into the entity value both
    # mangles the following line on replacement and stops the value matching
    # the same date written in prose.
    if entity_type in ("DATE", "DOB"):
        newline = text.find("\n", start, end)
        if newline != -1:
            end = newline
        while end > start and not text[end - 1].isalnum():
            end -= 1
        return (start, end) if end > start else None

    is_person = entity_type in mapping.PERSON_TYPES
    if not is_person and entity_type != "FACILITY":
        return (start, end)

    # Walk tokens with their offsets so trimming stays exact.
    tokens = [(m.start(), m.end()) for m in re.finditer(r"\S+", text[start:end])]
    if not tokens:
        return None

    def bare(index: int) -> str:
        token_start, token_end = tokens[index]
        return text[start + token_start : start + token_end].strip(".,;:'’\"()-").casefold()

    if is_person:
        # Names: strip honorifics off the front and ordinary English off both
        # ends, so "Sister Fiona Docherty" and "M.E.C.\nFollow" both reduce to
        # the identifying core.
        while tokens and (not bare(0) or bare(0) in _TITLE_TOKEN or bare(0) in _NOT_A_NAME):
            tokens.pop(0)
        while tokens and (not bare(-1) or bare(-1) in _NOT_A_NAME):
            tokens.pop()
        # A person's name is at most four tokens; anything longer is a mis-span.
        if len(tokens) > 4:
            return None
    else:
        # Organisations: only the leading article or label is droppable. The
        # trailing descriptor is *part of the name* — trimming "Riverside
        # Medical Practice" down to "Riverside" would leave "Medical Practice"
        # standing in the redacted text, which is worse than not detecting it.
        while tokens and (not bare(0) or bare(0) in _ORG_STOPWORDS):
            tokens.pop(0)

    if not tokens:
        return None

    return (start + tokens[0][0], start + tokens[-1][1])


def _location_is_address(text: str, start: int, end: int) -> bool:
    """True if a LOCATION span is part of a postal address, not a bare place name.

    "14 Leeds Road" and anything on an ``Address:`` line qualify. "visiting
    family in Leeds" does not — redacting that would strip clinical context for
    no privacy gain, and the address line itself is already covered by layer 1.
    """
    value = text[start:end]
    # The street word must follow something ("Leeds Road", not a bare "St"):
    # several of them double as ordinary abbreviations in clinical prose.
    street = _STREET_WORDS.search(value)
    if street and street.start() > 0:
        return True
    if _POSTCODE.search(text[end : end + 60]):
        return True
    line_start, line_end = _line_bounds(text, start)
    return bool(ADDRESS_LINE.match(text[line_start:line_end]))


# Bare risk-rating and risk-category words ("Low", "Medium", "High", "Falls",
# "Absconding") that a risk-assessment grid renders as plain-text pipe-table
# cells. spaCy reliably mislabels them as PERSON/ORGANIZATION there — corpus
# document #15 caught "Falls" (raw NER) and "Absconding" (the line-flattened
# pass merging a table row into its neighbour) becoming a facility.
#
# This is deliberately NOT a global allow-list entry (protected_terms.txt):
# "Low" and "Falls" are both attested English surnames, so exempting them
# everywhere would silently under-redact a real patient or clinician who
# happens to be named one. Scoping the exemption to "this exact word, AND it
# is the entire trimmed content of an isolated pipe-table cell" keeps every
# other occurrence — free prose, a labelled field, a name that merely shares
# a line with a "|" — fully subject to ordinary detection.
_RISK_GRID_WORDS = frozenset({"low", "medium", "high", "falls", "absconding"})


def _is_isolated_table_cell(text: str, start: int, end: int) -> bool:
    """True if ``text[start:end]`` is one whole pipe-table cell's content.

    The line must contain a "|" at all — ordinary prose never qualifies —
    and the span must be bounded by a "|" (or the line's own start/end) on
    both sides, with nothing but whitespace filling the gap. A name that
    merely sits somewhere on a line with a pipe character, or that runs into
    other text before reaching the next "|", does not qualify.
    """
    line_start, line_end = _line_bounds(text, start)
    line = text[line_start:line_end]
    if "|" not in line:
        return False
    before = text[line_start:start]
    after = text[end:line_end]
    before_ok = before.strip(" \t") == "" or before.rstrip(" \t").endswith("|")
    after_ok = after.strip(" \t") == "" or after.lstrip(" \t").startswith("|")
    return before_ok and after_ok


def _span_is_plausible(text: str, span: Span) -> bool:
    """Reject the false positives NER reliably produces on clinical documents."""
    value = text[span.start : span.end].strip()
    if len(value) < mapping.MIN_VALUE_LENGTH:
        return False

    # Names, organisations, and NER-guessed places are all vulnerable to the
    # same two mistakes: a clinical acronym ("ECG", "ST", "LAD") and a drug name
    # read as a proper noun. The regex layer is exempt on ADDRESS because a
    # postcode legitimately looks like an acronym.
    if span.entity_type in mapping.PERSON_TYPES or span.entity_type == "FACILITY" or (
        span.entity_type == "ADDRESS" and span.source != "regex"
    ):
        if _is_acronym(value) or _looks_clinical(value):
            return False
        # A risk-grid rating/category word standing alone as a whole
        # pipe-table cell — see _RISK_GRID_WORDS above. Scoped to that exact
        # shape, so the same word in free prose is unaffected.
        if (
            value.casefold() in _RISK_GRID_WORDS
            and _is_isolated_table_cell(text, span.start, span.end)
        ):
            return False
        # "Aspirin 75mg" — a capitalised token followed by a dose is a drug.
        if _DOSE_AFTER.match(text[span.end : span.end + 16]):
            return False
        # ...and one that swallowed the dose ("Salbutamol 100mcg" returned whole
        # as a PERSON) is the same drug with a worse span.
        if _DOSE_INSIDE.search(value):
            return False
        # Names and organisations are capitalised in clinical documents. A
        # lowercase span is a unit or a mis-span ("500mg" -> ORGANIZATION "mg").
        if not value[0].isupper() and not value[0].isdigit():
            return False
        # ...and a span glued to the end of a number is part of that number.
        if span.start > 0 and text[span.start - 1].isdigit():
            return False

    if span.entity_type in mapping.PERSON_TYPES and "\n" in value:
        # A name may wrap onto the next line, but a *field* value ends where its
        # line does. Without this, "Brother: David Chen\nWei Chen attended" came
        # back as one four-token person and merged the brother with the patient.
        line_start, _ = _line_bounds(text, span.start)
        if _FIELD_LABEL_LINE.match(text[line_start : span.start]):
            return False
        if value.count("\n") > 1:
            return False
        # The continuation has to read like the rest of a name. Flattening the
        # line break put "M.E.C." next to the "Follow-up" heading below it and
        # the pair came back as one person, which redacted the heading.
        tail = value.partition("\n")[2].strip().split()
        if tail:
            token = tail[0].strip(".,;:'’\"()-").casefold()
            # "Follow-up" is the heading below a line ending in initials; check
            # the leading component too, or the hyphen hides it from the list.
            if token in _NOT_A_NAME or token.split("-")[0] in _NOT_A_NAME:
                return False

    if span.entity_type == "FACILITY" and "\n" in value:
        # A multi-line ORG span is a mis-span — except for the one shape a
        # genuinely wrapped organisation takes, where the line break falls right
        # before the descriptor that ends its name ("Kirkstall Lane\nSurgery").
        # Anything else joins the letterhead to whatever follows it: spaCy
        # returned "...MENTAL HEALTH TEAM\nHarrogate" as one organisation and it
        # then outranked the town on length alone.
        head, _, tail = value.partition("\n")
        if "\n" in tail or not head.strip():
            return False
        if tail.strip().casefold() not in _WRAPPABLE_DESCRIPTORS:
            return False

    if span.entity_type == "ADDRESS" and span.source != "regex":
        if not _location_is_address(text, span.start, span.end):
            return False

    if span.entity_type in ("DATE", "DOB"):
        if not date_span_wanted(text, span.start, span.end):
            return False

    return True


# ---------------------------------------------------------------------------
# Person role classification
# ---------------------------------------------------------------------------

_CLINICIAN_BEFORE = re.compile(
    r"(?:\b(?:Dr|Doctor|Sister|Matron|Nurse|Prof|Professor|Consultant|Registrar|"
    r"Physiotherapist|Pharmacist|Surgeon|Anaesthetist)\b\.?\s*|"
    r"\b(?:reviewed|completed|countersigned|signed|dictated|seen|assessed|"
    r"prepared|authorised)\s+by\s+|\bunder\s+(?:the\s+care\s+of\s+)?)$",
    re.IGNORECASE,
)
_CLINICIAN_AFTER = re.compile(
    r"^\s*[(,]\s*(?:Consultant|Registrar|SHO|SpR|FY1|FY2|GP|Nurse|Sister|Matron|"
    r"Physiotherapist|Pharmacist|Surgeon|Anaesthetist|Specialist)",
    re.IGNORECASE,
)

_RELATIVE_AFTER = re.compile(rf"^\s*[(,]\s*(?:her\s+|his\s+|their\s+)?(?:{_KINSHIP})\b", re.IGNORECASE)
_RELATIVE_BEFORE = re.compile(rf"\b(?:{_KINSHIP})\s*[,:]?\s*$", re.IGNORECASE)
_RELATIVE_HEADING = re.compile(
    r"^\s*(?:NEXT\s+OF\s+KIN|FAMILY|RELATIVES?|EMERGENCY\s+CONTACT|CARER)\b", re.IGNORECASE
)

_PATIENT_LABEL = re.compile(
    r"^[ \t]*(?:Patient(?:\s+name)?|Name|Client(?:\s+name)?|Resident|"
    r"Service\s+user|Referral\s+for|Regarding|Re)[ \t]*:[ \t]*",
    re.IGNORECASE,
)

# A labelled relative field. Explicit and unambiguous, unlike the kinship
# heuristics, so it is checked straight after the patient label.
_RELATIVE_LABEL = re.compile(
    rf"^[ \t]*(?:Next\s+of\s+kin|NOK|Emergency\s+contact|Carer|Nearest\s+relative|"
    rf"{_KINSHIP})[ \t]*:[ \t]*",
    re.IGNORECASE,
)


def _line_bounds(text: str, index: int) -> tuple[int, int]:
    start = text.rfind("\n", 0, index) + 1
    end = text.find("\n", index)
    return start, (len(text) if end == -1 else end)


def _under_relative_heading(text: str, start: int) -> bool:
    """True if ``start`` sits within three lines of a NEXT OF KIN-style heading."""
    line_start, _ = _line_bounds(text, start)
    head = text[:line_start].splitlines()
    for line in reversed(head[-3:]):
        if _RELATIVE_HEADING.match(line):
            return True
        if line.strip() and line.strip().isupper() and not _RELATIVE_HEADING.match(line):
            return False  # a different section heading intervened
    return False


def classify_person(text: str, start: int, end: int) -> str:
    """Decide whether a detected name is a clinician, a relative, or the patient.

    Order matters: a clinical title beats everything (a "Sister" in a nursing
    handover is staff, not a sibling), then explicit kinship, then a patient
    label. Anything unclassified stays the generic ``PERSON`` type — honest
    about the uncertainty, and the reviewer can retype it in the table.
    """
    before = text[max(0, start - 40) : start]
    after = text[end : end + 40]

    # An explicit patient label is the strongest evidence in the document and is
    # checked first. It used to be checked last, so a patient whose sibling was
    # listed three lines above under NEXT OF KIN inherited the kinship heading
    # and was relabelled a relative — the report then had no patient at all.
    line_start, _ = _line_bounds(text, start)
    label = _PATIENT_LABEL.match(text[line_start:start])
    if label and label.end() == start - line_start:
        return "PATIENT_NAME"

    relative_label = _RELATIVE_LABEL.match(text[line_start:start])
    if relative_label and relative_label.end() == start - line_start:
        return "RELATIVE_NAME"

    if _CLINICIAN_BEFORE.search(before) or _CLINICIAN_AFTER.match(after):
        return "PROVIDER_NAME"
    if _RELATIVE_AFTER.match(after) or _RELATIVE_BEFORE.search(before):
        return "RELATIVE_NAME"
    if _under_relative_heading(text, start):
        return "RELATIVE_NAME"

    return "PERSON"


# ---------------------------------------------------------------------------
# Layer 2 — Presidio + spaCy NER
# ---------------------------------------------------------------------------

def ner_spans(text: str) -> list[Span]:
    """Layer 2: Presidio/spaCy detections, mapped onto CareScribe entity types.

    Returns an empty list — not an error — if no spaCy model could be loaded, so
    the structured layer still protects the document.
    """
    analyzer = get_analyzer()
    if analyzer is None or not text:
        return []

    try:
        results = analyzer.analyze(text=text, language="en")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001 — a NER failure must not take the app down
        return []

    spans: list[Span] = []
    for result in results:
        if result.score < NER_MIN_SCORE:
            continue
        entity_type = NER_ACCEPTED.get(result.entity_type)
        if entity_type is None:
            continue
        spans.append(Span(result.start, result.end, entity_type, "ner", float(result.score)))
    return spans


# ---------------------------------------------------------------------------
# Layer 3 — GLiNER (optional)
# ---------------------------------------------------------------------------

_GLINER_TYPES = {
    "person": "PERSON",
    "organization": "FACILITY",
    "address": "ADDRESS",
    "id": "OTHER_ID",
}


def gliner_spans(text: str) -> list[Span]:
    """Layer 3: GLiNER detections, or an empty list when it isn't installed."""
    model = get_gliner()
    if model is None or not text:
        return []

    try:
        found = model.predict_entities(  # type: ignore[attr-defined]
            text, list(GLINER_LABELS), threshold=GLINER_THRESHOLD
        )
    except Exception:  # noqa: BLE001
        return []

    spans: list[Span] = []
    for item in found:
        entity_type = _GLINER_TYPES.get(str(item.get("label", "")).lower())
        if entity_type is None:
            continue
        spans.append(
            Span(
                int(item["start"]),
                int(item["end"]),
                entity_type,
                "gliner",
                float(item.get("score", 0.5)),
            )
        )
    return spans


# ---------------------------------------------------------------------------
# Merging
# ---------------------------------------------------------------------------

def _collapse_person_subsets(entities: list[dict]) -> list[dict]:
    """Drop a person entity whose name is contained in a longer one.

    NER returns "Chen", "Margaret\\nChen" and "Margaret Elizabeth Chen" for the
    same person. Keeping all three would split one patient across three
    placeholders; the longest name's variant expansion already covers the
    shorter forms, so dropping them loses no recall.

    Matching is on whole tokens in order, and the surname must agree: "Chen"
    collapses into "Margaret Chen", but "Aiden" never collapses into "Braiden",
    and "David Chen" never collapses into "Margaret Elizabeth Chen".
    """
    people = [
        (index, entity)
        for index, entity in enumerate(entities)
        if entity["type"] in mapping.PERSON_TYPES
    ]

    def is_subname(short: list[str], long: list[str]) -> bool:
        if len(short) >= len(long) or short[-1] != long[-1]:
            return False  # different surname, or not actually shorter
        position = 0
        for token in short:
            try:
                position = long.index(token, position) + 1
            except ValueError:
                return False
        return True

    redundant: set[int] = set()
    for index, entity in people:
        tokens = entity["value"].casefold().split()
        for other_index, other in people:
            if other_index == index or other_index in redundant:
                continue
            if is_subname(tokens, other["value"].casefold().split()):
                redundant.add(index)
                break

    return [entity for index, entity in enumerate(entities) if index not in redundant]


def _specific_person_type(entity: dict) -> bool:
    """True for a person row whose role is known (patient / relative / clinician)."""
    return entity["type"] in mapping.PERSON_TYPES and entity["type"] not in mapping.GENERIC_TYPES


def _collapse_person_identities(entities: list[dict], known_as: str | None = None) -> list[dict]:
    """Collapse every written form of one person onto a single entity row.

    :func:`_collapse_person_subsets` only merges forms that share a surname, so
    a document calling the patient "Mohammed Al-Rashid" in the header and plain
    "Mohammed" in the body ended up with two rows and two placeholders for one
    human being.

    The identity key is surname + first initial (:func:`mapping.canonical_person_key`),
    which merges "Margaret Elizabeth Chen" with "Margaret Chen" while keeping
    "David Chen" separate. Rows carrying only a first name, a bare surname or
    initials have no key of their own; they are attached to a full-name anchor
    only when exactly one anchor's variant expansion already covers them, so an
    ambiguous "Chen" across two people stays its own reviewable row rather than
    being silently bound to the wrong identity.

    Merging is refused across two *different* known roles: a patient and a
    clinician who share a surname and an initial are two people, not one.
    """
    people = [
        (index, entity)
        for index, entity in enumerate(entities)
        if entity["type"] in mapping.PERSON_TYPES
    ]
    if len(people) < 2:
        return entities

    anchors: list[tuple[int, dict, str]] = []
    loose: list[tuple[int, dict]] = []
    for index, entity in people:
        core = mapping.name_core(entity["value"])
        if len(core) >= 2:
            anchors.append((index, entity, mapping.canonical_person_key(entity["value"])))
        else:
            loose.append((index, entity))

    redundant: set[int] = set()

    def compatible(a: dict, b: dict) -> bool:
        if _specific_person_type(a) and _specific_person_type(b):
            return a["type"] == b["type"]
        return True

    # Full names sharing an identity key: keep the most informative spelling.
    # Keys match exactly, or as an initial standing in for a given name, so
    # "W. Chen" folds into "Wei Chen" while "Mei Chen" stays a separate person.
    by_key: dict[str, tuple[int, dict]] = {}
    for index, entity, key in anchors:
        if not key:
            continue
        existing_key = next(
            (k for k in by_key if mapping.keys_are_compatible(k, key)), None
        )
        winner = by_key.get(existing_key) if existing_key else None
        if winner is None:
            by_key[key] = (index, entity)
            continue
        key = existing_key or key
        if not compatible(winner[1], entity):
            continue
        keep, drop = winner, (index, entity)
        if len(mapping.name_core(entity["value"])) > len(mapping.name_core(winner[1]["value"])):
            keep, drop = (index, entity), winner
        # The surviving row must carry the more specific role.
        if _specific_person_type(drop[1]) and not _specific_person_type(keep[1]):
            keep[1]["type"] = drop[1]["type"]
        by_key[key] = keep
        redundant.add(drop[0])

    # First names, bare surnames and initials fold into the one anchor whose
    # variant expansion already produces them.
    surviving = [(index, entity) for index, entity, _ in anchors if index not in redundant]
    for index, entity in loose:
        value = entity["value"].strip().casefold()
        matches = []
        for anchor_index, anchor in surviving:
            if not compatible(anchor, entity):
                continue
            alias = known_as if anchor["type"] == "PATIENT_NAME" else None
            forms = {f.casefold() for f in mapping.expand_name_variants(anchor["value"], alias)}
            if value in forms:
                matches.append((anchor_index, anchor))
        if len(matches) == 1:
            if _specific_person_type(entity) and not _specific_person_type(matches[0][1]):
                matches[0][1]["type"] = entity["type"]
            redundant.add(index)

    return [entity for index, entity in enumerate(entities) if index not in redundant]


def _collapse_facility_subsets(entities: list[dict]) -> list[dict]:
    """Drop a facility whose name is a short form of a longer one.

    The letterhead gives "ST. AIDAN'S GENERAL HOSPITAL" and the sign-off gives
    "St. Aidan's". They are one organisation and must share one placeholder;
    the long name's variant expansion already covers the short form.

    A generically-typed entity collapses in too. NER sometimes returns a short
    organisation name as a PERSON, and leaving it as one is not just untidy:
    person expansion would derive standalone forms from an organisation's
    tokens, which is how "St. Aidan's" ends up redacting "ST depression".
    """
    candidates = [
        (index, entity)
        for index, entity in enumerate(entities)
        if entity["type"] in mapping.FACILITY_TYPES or entity["type"] in mapping.GENERIC_TYPES
    ]
    facilities = [
        (index, entity) for index, entity in candidates if entity["type"] in mapping.FACILITY_TYPES
    ]

    redundant: set[int] = set()
    for index, entity in candidates:
        value = " ".join(entity["value"].casefold().split())
        for other_index, other in facilities:
            if other_index == index or other_index in redundant:
                continue
            if len(other["value"]) <= len(entity["value"]):
                continue
            variants = {
                " ".join(form.casefold().split())
                for form in mapping.expand_org_variants(other["value"])
            }
            if value in variants:
                redundant.add(index)
                break

    return [entity for index, entity in enumerate(entities) if index not in redundant]


def merge_spans(text: str, *span_lists: list[Span], known_as: str | None = None) -> list[dict]:
    """Resolve every layer's spans into a de-duplicated entity list.

    Overlaps are settled longest-match-wins, ties going to the
    higher-precision layer (regex before GLiNER before NER). The surviving
    spans are then de-duplicated by value, so a name appearing five times is one
    reviewable row.
    """
    spans: list[Span] = []
    for span_list in span_lists:
        spans.extend(span_list or [])

    # Strings that some layer read as part of a place. spaCy labels town names
    # PERSON as readily as LOCATION ("Bolton", "Leeds"), so a bare mention of
    # one gets redacted as a name while the identical token inside the address
    # is governed by the stricter address gate. Collecting the address's own
    # tokens makes that one decision instead of two contradictory ones.
    place_names: set[str] = set()
    for span in spans:
        if span.entity_type not in ("ADDRESS", "LOCATION"):
            continue
        value = text[span.start : span.end]
        if span.source != "regex":
            place_names.add(value.strip().casefold())
        for token in re.findall(r"[A-Za-z][\w'’\-]{2,}", value):
            place_names.add(token.casefold())

    # The allow-list outranks every layer. A candidate overlapping a protected
    # term is dropped before anything else looks at it, so "Mental Health Act"
    # cannot become a clinic and "HoNOS" cannot become an organisation — a note
    # with those redacted is useless to the clinician reading it, even though
    # nothing leaked.
    protected = protected_ranges(text)

    def is_protected(span: Span) -> bool:
        for p_start, p_end in protected:
            if p_start <= span.start and span.end <= p_end:
                return True  # the candidate IS an allow-listed term
            if span.start <= p_start and p_end <= span.end and span.source != "regex":
                # A guessed span that swallowed a protected term ("Mental Health
                # Act Assessment Record"). A deterministic regex hit is exempt:
                # "CPA-4471-B" legitimately contains the protected word "CPA",
                # and the label is what makes it an identifier.
                return True
        return False

    # The line-flattened pass exists only to see entities a wrap hid. Where the
    # normal pass already found something in that region it has the better span,
    # because it still had the line structure: flattening joined a letterhead
    # organisation to the town on the next line and produced one span covering
    # both, which then outranked the town on length alone.
    # Same entity type only. A wrapped name sat at exactly the same offsets as an
    # ORGANIZATION mis-span the facility rule then threw away, and comparing
    # across types let the discarded span suppress the good one — the wrapped
    # name vanished and half of it stayed in the clear.
    seen_ranges: dict[str, list[tuple[int, int]]] = {}
    for span in spans:
        if span.source != "wrapped":
            seen_ranges.setdefault(span.entity_type, []).append((span.start, span.end))

    spans = [
        span
        for span in spans
        if span.source != "wrapped"
        or not any(
            s <= span.start and span.end <= e
            for s, e in seen_ranges.get(span.entity_type, ())
        )
    ]

    # Trim, classify, and filter before overlap resolution, so a rejected
    # mis-span doesn't block the good span underneath it.
    prepared: list[Span] = []
    for span in spans:
        if is_protected(span):
            continue
        trimmed = _trim_span(text, span.start, span.end, span.entity_type)
        if trimmed is None:
            continue
        start, end = trimmed
        entity_type = span.entity_type
        if entity_type == "PERSON":
            entity_type = classify_person(text, start, end)
            # Only an *unclassified* person is dropped as a place. A title, a
            # kinship marker, or a "Patient:" label is stronger evidence than
            # a gazetteer collision, so those are kept.
            if entity_type == "PERSON" and text[start:end].strip().casefold() in place_names:
                continue
        candidate = Span(start, end, entity_type, span.source, span.score)
        if not _span_is_plausible(text, candidate):
            continue
        prepared.append(candidate)

    prepared.sort(
        key=lambda s: (
            -(s.end - s.start),
            _SOURCE_RANK.get(s.source, 9),
            -s.score,
            s.start,
        )
    )

    occupied = bytearray(len(text))
    kept: list[Span] = []
    for span in prepared:
        if any(occupied[span.start : span.end]):
            continue
        occupied[span.start : span.end] = b"\x01" * (span.end - span.start)
        kept.append(span)

    kept.sort(key=lambda s: s.start)

    def _confidence(span: Span) -> str:
        """"auto" if this span is safe to redact with no manual decision.

        Layer 1 (regex) is pattern-certain by construction. Anything else is
        "auto" only if a second, independent layer's candidate also covered
        this exact region while spans were still being resolved — real
        corroboration, not just one layer's guess. Checked against
        ``prepared`` (every candidate, before the occupied-bytearray dedup
        above threw the losers away), because ``kept`` only has the single
        surviving span per region and has already lost that information.
        """
        if span.source == "regex":
            return "auto"
        sources = {
            other.source
            for other in prepared
            if other.start < span.end and span.start < other.end
        }
        return "auto" if len(sources) >= 2 else "review"

    entities = mapping.dedupe_entities(
        {
            "type": span.entity_type,
            "value": text[span.start : span.end],
            "confidence": _confidence(span),
        }
        for span in kept
    )

    # A later, more specific type upgrades a generic one for the same value:
    # a bare NER "PERSON" gives way to "PROVIDER_NAME" from the title regex.
    by_value = {entity["value"].casefold(): entity for entity in entities}
    for span in kept:
        existing = by_value.get(text[span.start : span.end].strip().casefold())
        if existing is None:
            continue
        if (
            existing["type"] in mapping.GENERIC_TYPES
            and span.entity_type not in mapping.GENERIC_TYPES
        ):
            existing["type"] = span.entity_type

    collapsed = _collapse_person_identities(_collapse_person_subsets(entities), known_as)
    return _collapse_facility_subsets(collapsed)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze(text: str) -> list[dict]:
    """Run every enabled layer over ``text`` and return reviewable entities.

    Each entity is ``{type, value, placeholder, action}``, ready to drop into
    the review table.
    """
    if not text or not text.strip():
        return []

    # A name or an organisation broken by a line wrap ("Oluwaseun\nAdeyinka",
    # "Kirkstall Lane\nSurgery") is invisible to NER, which sees two unrelated
    # fragments. Detection therefore runs a second time over a copy with every
    # line break flattened to a space. The substitution is length-preserving —
    # one character out for one character in, "\r\n" becoming two spaces — so
    # spans found on the flattened copy carry straight back to the original
    # offsets with no mapping table. The first pass still runs on the real text,
    # because the line structure is what the address, ward, date-field and
    # letterhead rules key on.
    flattened, index_map = flatten_lines(text)

    layers: list[list[Span]] = []
    if USE_STRUCTURED:
        layers.append(structured_spans(text))
    if USE_NER:
        layers.append(ner_spans(text))
    if USE_GLINER:
        layers.append(gliner_spans(text))

    if flattened != text:
        wrapped: list[Span] = []
        if USE_STRUCTURED:
            wrapped.extend(structured_spans(flattened))
        if USE_NER:
            wrapped.extend(ner_spans(flattened))
        if USE_GLINER:
            wrapped.extend(gliner_spans(flattened))
        # Only the span types a line wrap can hide are taken from this pass;
        # anything line-anchored keeps the first pass's answer. A span whose
        # original-text range crosses a blank line is a cross-paragraph
        # artefact of the flattening, not a genuine wrapped name or
        # organisation — see _crosses_paragraph_break.
        layers.append([
            Span(
                index_map[span.start],
                index_map[span.end - 1] + 1,
                span.entity_type,
                "wrapped",
                span.score,
            )
            for span in wrapped
            if (span.entity_type in mapping.PERSON_TYPES
                or span.entity_type in mapping.FACILITY_TYPES)
            and 0 <= span.start < span.end <= len(index_map)
            and not _crosses_paragraph_break(
                text, index_map[span.start], index_map[span.end - 1] + 1
            )
        ])

    known_as = mapping.find_known_as(text)
    entities = merge_spans(text, *layers, known_as=known_as)

    # A "Known as" alias is folded into the patient's placeholder by variant
    # expansion, so it must not also stand as an entity of its own.
    if known_as:
        entities = [e for e in entities if e["value"].casefold() != known_as.casefold()]

    return mapping.assign_placeholders(entities)


# A document this app is asked to handle should take seconds. Past this, the
# honest thing is to stop and point at the log rather than spin forever.
DEID_TIMEOUT_SECONDS = 180


def deidentify(text: str) -> DeidResult:
    """Run the full local pipeline over one document.

    CPU-only and offline: no model is called over a socket, and nothing is
    written to disk.
    """
    if not text or not text.strip():
        raise DeidentificationError("There is no text to de-identify.")

    started = time.monotonic()
    applog.log("de-identify: start chars=%d", len(text))
    entities = analyze(text)
    elapsed = time.monotonic() - started
    if elapsed > DEID_TIMEOUT_SECONDS:
        applog.warn("de-identify: exceeded budget %.0fs chars=%d", elapsed, len(text))
        raise DeidentificationError(
            f"De-identification took longer than {DEID_TIMEOUT_SECONDS // 60} "
            f"minutes on a {len(text):,}-character document and was stopped.\n\n"
            f"If the document really is that large, try splitting it. If not, "
            f"the log has the detail: {applog.log_path()}"
        )
    applog.log(
        "de-identify: done in %.1fs chars=%d entities=%d",
        elapsed, len(text), len(entities),
    )
    known_as = mapping.find_known_as(text)

    return DeidResult(
        entities=entities,
        redacted_text=mapping.redact(text, entities, known_as),
        phi_map=mapping.build_map(entities),
        known_as=known_as,
    )


def rebuild(text: str, entities: list[dict]) -> DeidResult:
    """Re-derive redacted text and the PHI map from a reviewer-edited table.

    Called after every edit in the review panel, so the preview always reflects
    exactly what the reviewer is looking at — no stale state.

    The detection layers deliberately do NOT re-run here. Their findings are
    already rows in the table, and re-running them would resurrect every false
    positive the reviewer just deleted or marked Keep.
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
    known_as = mapping.find_known_as(text)

    return DeidResult(
        entities=with_placeholders,
        redacted_text=mapping.redact(text, with_placeholders, known_as),
        phi_map=mapping.build_map(with_placeholders),
        known_as=known_as,
    )


def add_manual_entity(
    text: str, entities: list[dict], value: str, entity_type: str = "OTHER_ID"
) -> DeidResult:
    """Add an identifier the tools missed and immediately re-redact.

    The new value goes through the same variant expansion as a detected one, so
    typing a full name also covers "Mrs Surname" and the initials.
    """
    value = (value or "").strip()
    if len(value) < mapping.MIN_VALUE_LENGTH:
        raise DeidentificationError(
            f"'{value}' is too short to redact safely — it would match all over the document."
        )

    rows = list(entities)
    if any(str(e.get("value", "")).strip().casefold() == value.casefold() for e in rows):
        raise DeidentificationError(f"'{value}' is already in the table.")

    rows.append({
        "type": mapping.normalise_type(entity_type),
        "value": value,
        "placeholder": "",
        "confidence": "auto",
    })
    return rebuild(text, rows)


# ---------------------------------------------------------------------------
# Pre-handoff safety sweep
# ---------------------------------------------------------------------------

# Findings that are only a placeholder are not leaks — "[NHS_NO]" contains no
# digits, but "Address: [ADDRESS]" would otherwise be re-reported by the
# address-line regex.
_PLACEHOLDER_SPAN = mapping.PLACEHOLDER_RE


def residual_scan(deidentified_text: str) -> list[str]:
    """Re-scan ALREADY-REDACTED text for anything that still looks identifying.

    Runs the structured regex layer plus a PERSON-only NER check, and returns
    the surviving strings. This is the gate in front of approval: a non-empty
    result blocks the write and shows the reviewer what is still there.

    Anything that is merely a placeholder, or overlaps one, is not a finding.
    """
    if not deidentified_text or not deidentified_text.strip():
        return []

    text = deidentified_text
    protected = [(m.start(), m.end()) for m in _PLACEHOLDER_SPAN.finditer(text)]

    def overlaps_placeholder(start: int, end: int) -> bool:
        return any(start < p_end and end > p_start for p_start, p_end in protected)

    # Structured formats, plus a PERSON-only NER check. Organisations are
    # deliberately excluded: the ORG recogniser flags department and ward names
    # the pipeline never redacts, so including it would block every approval on
    # a finding the reviewer has no action to take on.
    candidates: list[Span] = list(structured_spans(text))
    candidates.extend(span for span in ner_spans(text) if span.entity_type == "PERSON")

    findings: list[str] = []
    seen: set[str] = set()
    for span in candidates:
        trimmed = _trim_span(text, span.start, span.end, span.entity_type)
        if trimmed is None:
            continue
        start, end = trimmed
        if overlaps_placeholder(start, end):
            continue
        candidate = Span(start, end, span.entity_type, span.source, span.score)
        if not _span_is_plausible(text, candidate):
            continue
        value = text[start:end].strip()
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key)
        findings.append(value)

    return findings


__all__ = [
    "DeidResult",
    "DeidentificationError",
    "REDACT_INPROSE_DATES",
    "SOFT_CHAR_LIMIT",
    "Span",
    "add_manual_entity",
    "analyze",
    "deidentify",
    "engine_status",
    "gliner_spans",
    "merge_spans",
    "ner_spans",
    "rebuild",
    "residual_scan",
    "structured_spans",
    "warm_up",
]
