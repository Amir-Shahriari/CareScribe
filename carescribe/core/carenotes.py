"""
Care note generation — local, on approved de-identified text only.

The contract this module honours is the one the stub declared: it takes
de-identified text and nothing else. There is no parameter for the original
document and none for the identity mapping, so there is nowhere for PHI to
enter from. Re-identification happens afterwards, in
:func:`carescribe.core.mapping.reidentify_document`, entirely in Python.

That split is deliberate and worth stating plainly: the model's view of the
document is identical whether it runs on this laptop or, one day, somewhere
else. Swapping :class:`OllamaBackend` for a cloud one changes where the tokens
go, not what they contain.

The backend is a Protocol rather than a hard dependency for the same reason —
the seam where a provider gets swapped is one method wide.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Iterator, Protocol

from . import deidentify, mapping, ollama_client

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"

DISABLED_MESSAGE = (
    "Available after de-identification is approved — approve the document first."
)

# The banner every generated document carries. Prepended in Python rather than
# asked of the model, because a rule the model can forget is not a guarantee.
DRAFT_BANNER = (
    "> **DRAFT — requires clinician review.** Generated locally from "
    "de-identified text. Verify every clinical detail against the source "
    "document before use."
)

TEMPLATES: dict[str, str] = {
    "SOAP care note": "care_notes_soap.txt",
    "GP clinic letter": "clinic_letter.txt",
    "Discharge summary": "discharge_summary.txt",
    "Custom (your own template)": "custom.txt",
}

CUSTOM_TEMPLATE = "Custom (your own template)"


class CareNoteError(RuntimeError):
    """Raised when care note generation can't proceed."""


class Backend(Protocol):
    """One method wide: the seam a different provider would be swapped in at.

    ``grammar`` is an optional GBNF string (see :mod:`carescribe.core.grammar`);
    a backend that cannot use it ignores it.
    """

    def generate(
        self, system: str, prompt: str, stream: bool = True, *, grammar: str | None = None
    ) -> Iterator[str]:
        ...


class OllamaBackend:
    """Local generation through the loopback-pinned Ollama daemon."""

    def __init__(self, model: str, temperature: float = 0.0) -> None:
        self.model = model
        self.temperature = temperature

    def generate(
        self, system: str, prompt: str, stream: bool = True, *, grammar: str | None = None
    ) -> Iterator[str]:
        # Ollama's HTTP API has no first-class GBNF field across the versions
        # CareScribe supports, so the grammar is accepted and ignored here; the
        # local GGUF backend is where constrained decoding runs.
        try:
            yield from ollama_client.generate(
                self.model, system, prompt, stream, temperature=self.temperature
            )
        except ollama_client.OllamaError as exc:
            raise CareNoteError(str(exc)) from exc


# future: CloudBackend — same Protocol, different transport. It would receive
# exactly what OllamaBackend receives: de-identified text with placeholders.


def load_prompt(name: str) -> str:
    """Read one prompt file from ``carescribe/prompts``."""
    path = PROMPT_DIR / name
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise CareNoteError(f"Prompt template '{name}' could not be read: {exc}") from exc


def system_prompt() -> str:
    """The shared preamble — role, anti-fabrication rules, placeholder rules."""
    return load_prompt("system.txt")


def template_names() -> list[str]:
    return list(TEMPLATES)


def render_prompt(
    deidentified_text: str, template: str, custom_instruction: str = ""
) -> str:
    """Build the user prompt for one template with the source text embedded."""
    filename = TEMPLATES.get(template)
    if filename is None:
        raise CareNoteError(
            f"Unknown template '{template}'. Available: {', '.join(TEMPLATES)}"
        )
    body = load_prompt(filename)
    if template == CUSTOM_TEMPLATE and not custom_instruction.strip():
        raise CareNoteError(
            "The custom template needs your own instructions or house format."
        )
    return body.replace("{document}", deidentified_text).replace(
        "{instruction}", custom_instruction.strip()
    )


def _value_present(needle: str, haystack: str) -> bool:
    """True only when ``needle`` occurs in ``haystack`` as a whole token run.

    Both are already casefolded and whitespace-collapsed. The match must not be
    flanked by another alphanumeric character, so a real leaked identifier —
    which is always delimited by spaces or punctuation — is caught, while a
    short mapping value that is merely a fragment of an ordinary word is not
    (``"mm"`` inside ``"community"``, ``"sr"`` inside ``"disorder"``). Without
    this, a 2–3 character mapping value (an honorific, a set of initials, a room
    code, a token a reviewer added by hand) refuses generation on text that is
    perfectly clean.
    """
    return re.search(rf"(?<![0-9a-z]){re.escape(needle)}(?![0-9a-z])", haystack) is not None


def assert_deidentified(text: str, phi_values: Iterable[str] | None = None) -> None:
    """Refuse to send anything carrying a value from the identity mapping.

    A cheap, blunt check, and deliberately so: it compares the outgoing text
    against the real values the mapping holds. It cannot prove the text is free
    of PHI — the review gate upstream is what does that — but it turns the one
    failure that would matter most, a mapping value reaching the model, into a
    crash rather than a silent send.

    The comparison is token-bounded, not a raw substring test: a value counts as
    present only when it appears delimited by non-alphanumeric characters, so a
    genuine leak still crashes but a short value coinciding with a fragment of
    an ordinary word does not.
    """
    if not phi_values:
        return
    haystack = " ".join((text or "").split()).casefold()
    for value in phi_values:
        needle = " ".join(str(value or "").split()).casefold()
        if len(needle) < mapping.MIN_VALUE_LENGTH:
            continue
        if _value_present(needle, haystack):
            raise CareNoteError(
                "Refusing to generate: the text handed to the model still "
                "contains a value from the identity mapping. This is a bug — "
                "generation must only ever receive approved de-identified text."
            )


def assert_no_residual_identifiers(text: str, acknowledged: Iterable[str] = ()) -> None:
    """Refuse to send text the residual sweep still flags.

    :func:`assert_deidentified` only catches values that are in the identity
    mapping — something a detector found. This is the complementary check: an
    identifier *no* layer ever detected is not in the mapping and not a
    placeholder, so only a re-scan of the outgoing text can catch it. Runs
    :func:`carescribe.core.deidentify.residual_scan` and raises unless every
    finding is one the reviewer explicitly cleared at approval (``acknowledged``
    — the document's ``dismissed`` list, e.g. a town used as a place of care).

    Approval already runs this sweep; reaching here with a fresh finding means
    the approved text and the text handed to the model have diverged, or a
    dismissal was lost. The crash is deliberate — a leak becomes a stop, not a
    send.
    """

    def norm(value: str) -> str:
        return " ".join(str(value or "").split()).casefold()

    cleared = {norm(value) for value in acknowledged}
    leaked = [
        value
        for value in deidentify.residual_scan(text or "")
        if norm(value) not in cleared
    ]
    if leaked:
        raise CareNoteError(
            "Refusing to generate: the text handed to the model still contains "
            "what look like identifiers the review did not clear — "
            + ", ".join(repr(value) for value in leaked[:10])
            + ". Generation must only ever receive approved de-identified text; "
            "treat this as a bug in the approval path."
        )


def generate_document(
    deidentified_text: str,
    template: str,
    backend: Backend,
    stream: bool = True,
    *,
    custom_instruction: str = "",
    phi_values: Iterable[str] | None = None,
    acknowledged: Iterable[str] = (),
    system: str | None = None,
    user_prompt: str | None = None,
    grammar: str | None = None,
) -> Iterator[str]:
    """Stream a drafted document from approved de-identified text.

    ``phi_values`` is the mapping's real values, passed **only** so this
    function can assert they are absent. They are never forwarded to a backend.

    ``acknowledged`` is the document's ``dismissed`` list — residual-sweep
    findings the reviewer looked at and cleared. It carries no PHI (every
    string in it is one the reviewer read in the de-identified text) and is
    used only to keep :func:`assert_no_residual_identifiers` from tripping on
    a finding approval already accepted.

    ``system``/``user_prompt`` let a caller (the clinical-form pipeline)
    supply a fully-built prompt instead of looking one up by ``template``
    label — ``template`` is then unused but still required positionally for
    backward compatibility with existing callers.
    """
    if not deidentified_text or not deidentified_text.strip():
        raise CareNoteError("There is no de-identified text to work from.")

    assert_deidentified(deidentified_text, phi_values)
    assert_no_residual_identifiers(deidentified_text, acknowledged)
    prompt = user_prompt if user_prompt is not None else render_prompt(
        deidentified_text, template, custom_instruction
    )
    assert_deidentified(prompt, phi_values)

    # Only pass `grammar` when there is one, so a backend (or a test stub) whose
    # generate() predates the keyword still works for the unconstrained path.
    extra = {"grammar": grammar} if grammar else {}
    return _without_reasoning(
        backend.generate(system or system_prompt(), prompt, stream, **extra)
    )


def refine_document(
    deidentified_text: str,
    draft: str,
    instruction: str,
    backend: Backend,
    stream: bool = True,
    *,
    history: list[tuple[str, str]] | None = None,
    phi_values: Iterable[str] | None = None,
    acknowledged: Iterable[str] = (),
    system: str | None = None,
    refine_prompt_name: str = "refine.txt",
) -> Iterator[str]:
    """Revise an existing draft against a follow-up instruction.

    Operates on the same de-identified source plus the running draft — both
    already free of PHI — so the refinement loop carries exactly the privacy
    properties of the first pass. ``history`` is a short list of
    ``(instruction, note)`` pairs, included so the model does not undo an
    earlier request while satisfying the current one.

    ``system``/``refine_prompt_name`` let a caller supply a different system
    prompt and refine-instruction template (the clinical-form pipeline uses
    ``refine_form.txt``, which adds a field-marker-preservation rule).
    """
    if not draft or not draft.strip():
        raise CareNoteError("There is no draft to refine yet.")
    if not instruction or not instruction.strip():
        raise CareNoteError("Say what you would like changed.")

    assert_deidentified(draft, phi_values)
    assert_deidentified(instruction, phi_values)
    assert_no_residual_identifiers(deidentified_text, acknowledged)

    steer = instruction.strip()
    if history:
        earlier = "\n".join(f"- {item}" for item, _ in history[-4:])
        steer = (
            f"{steer}\n\nEarlier instructions already applied — keep them "
            f"satisfied:\n{earlier}"
        )

    prompt = (
        load_prompt(refine_prompt_name)
        .replace("{document}", deidentified_text)
        .replace("{draft}", draft)
        .replace("{instruction}", steer)
    )
    assert_deidentified(prompt, phi_values)

    return _without_reasoning(backend.generate(system or system_prompt(), prompt, stream))


# --------------------------------------------------------------------------
# Dropping the model's own reasoning
# --------------------------------------------------------------------------
#
# A reasoning-capable model narrates its planning before (and sometimes after)
# the answer: "The user wants a SOAP note. Let's analyse... Wait, check the
# rules...". It arrives three ways — a well-formed ``<think>...</think>`` block,
# a bare ``</think>`` with the planning text in front of it and no opening tag,
# or (a truncated stream) an unclosed ``<think>``. None of it is the document.
# ``ollama_client`` also asks Ollama to disable thinking; this is the belt to
# that braces, and it covers the GGUF and cloud backends too.

_REASON_TAGS = "think|thinking|reasoning|thought|scratchpad"
_THINK_BLOCK_RE = re.compile(
    rf"<\s*({_REASON_TAGS})\s*>.*?<\s*/\s*\1\s*>\s*",
    re.DOTALL | re.IGNORECASE,
)
_OPEN_TAG_RE = re.compile(rf"<\s*(?:{_REASON_TAGS})\s*>", re.IGNORECASE)
_CLOSE_TAG_RE = re.compile(rf"<\s*/\s*(?:{_REASON_TAGS})\s*>", re.IGNORECASE)
_ORPHAN_CLOSE_RE = re.compile(
    rf"\A.*?<\s*/\s*(?:{_REASON_TAGS})\s*>\s*",
    re.DOTALL | re.IGNORECASE,
)

# How much answer text to buffer before concluding no reasoning prefix is
# coming and releasing it. Real planning monologues run to thousands of
# characters, so this only delays the first render of a genuinely long,
# reasoning-free draft — never drops any of it.
_REASON_STREAM_FLUSH = 4000

_TAG_FRAGMENTS = tuple(
    f"<{slash}{name}"
    for name in _REASON_TAGS.split("|")
    for slash in ("", "/")
)


def strip_reasoning(text: str) -> str:
    """Remove a model's reasoning monologue from a finished draft.

    Idempotent. Text with no reasoning markers comes back unchanged apart from
    leading whitespace. ``None`` passes through.
    """
    if not text:
        return text
    cleaned = _THINK_BLOCK_RE.sub("", text)
    open_match = _OPEN_TAG_RE.search(cleaned)
    if open_match and not _CLOSE_TAG_RE.search(cleaned):
        # Unclosed block (truncated output): drop from the open tag on.
        cleaned = cleaned[: open_match.start()]
    elif _CLOSE_TAG_RE.search(cleaned) and not _OPEN_TAG_RE.search(cleaned):
        # Bare closing tag: everything ahead of it was pre-answer reasoning.
        cleaned = _ORPHAN_CLOSE_RE.sub("", cleaned, count=1)
    return cleaned.lstrip()


def _ends_mid_tag(text: str) -> bool:
    """True if ``text`` ends part-way through what could be a reasoning tag."""
    tail = text[-12:].lower()
    cut = tail.rfind("<")
    if cut == -1:
        return False
    frag = tail[cut:]
    return any(t.startswith(frag) or frag.startswith(t) for t in _TAG_FRAGMENTS)


def _without_reasoning(chunks: Iterable[str]) -> Iterator[str]:
    """Filter a token stream so a reasoning prefix never reaches the consumer.

    Buffers until it can tell whether the answer is prefixed with reasoning (a
    ``<think>`` block or a lone ``</think>``); once the document proper has
    started, streams the rest through untouched.
    """
    buffer = ""
    streaming = False
    pending_lstrip = False
    for chunk in chunks:
        if streaming:
            if pending_lstrip:
                chunk = chunk.lstrip()
                if not chunk:
                    continue
                pending_lstrip = False
            yield chunk
            continue
        buffer += chunk
        close = _CLOSE_TAG_RE.search(buffer)
        if close:
            rest = buffer[close.end():].lstrip()
            buffer, streaming = "", True
            if rest:
                yield rest
            else:
                pending_lstrip = True
            continue
        if _OPEN_TAG_RE.search(buffer) or _ends_mid_tag(buffer):
            continue  # still inside (or possibly inside) a reasoning block
        if len(buffer) >= _REASON_STREAM_FLUSH:
            yield buffer
            buffer, streaming = "", True
    if buffer and not streaming:
        yield strip_reasoning(buffer)


def with_banner(draft: str) -> str:
    """Prepend the review banner, without duplicating one already there."""
    text = (draft or "").lstrip()
    if text.startswith("> **DRAFT"):
        return text
    return f"{DRAFT_BANNER}\n\n{text}"


def finalise(draft: str, phi_map: dict[str, str], tolerant: bool = True):
    """Re-identify a draft locally and refuse to hand back a leaky document.

    Returns ``(text, unresolved)``. A non-empty ``unresolved`` means at least
    one bracketed token survived, and the caller must block on it: filing a
    report with a literal ``[PATIENT]`` in it is worse than filing nothing.
    """
    return mapping.reidentify_document(draft, phi_map, tolerant=tolerant)


def generate_care_note(
    deidentified_text: str,
    template: str = "SOAP care note",
    custom_instruction: str = "",
    *,
    backend: Backend | None = None,
    model: str | None = None,
) -> str:
    """Draft a care note from ALREADY DE-IDENTIFIED text, returning it whole.

    The stub's signature, now working. Streaming callers should use
    :func:`generate_document` directly.

    :param deidentified_text: approved output of the de-identification stage.
        Must have passed :func:`carescribe.core.deidentify.residual_scan`.
    """
    if backend is None:
        chosen = model or ollama_client.default_model()
        if not chosen:
            raise CareNoteError(
                ollama_client.DAEMON_DOWN_MESSAGE
                if not ollama_client.is_up()
                else "No local model is installed. Try: ollama pull llama3.1:8b"
            )
        backend = OllamaBackend(chosen)

    chunks = generate_document(
        deidentified_text, template, backend, stream=False,
        custom_instruction=custom_instruction,
    )
    return with_banner(strip_reasoning("".join(chunks)))


__all__ = [
    "Backend",
    "CUSTOM_TEMPLATE",
    "CareNoteError",
    "DISABLED_MESSAGE",
    "DRAFT_BANNER",
    "OllamaBackend",
    "TEMPLATES",
    "assert_deidentified",
    "assert_no_residual_identifiers",
    "finalise",
    "generate_care_note",
    "generate_document",
    "load_prompt",
    "refine_document",
    "render_prompt",
    "strip_reasoning",
    "system_prompt",
    "template_names",
    "with_banner",
]
