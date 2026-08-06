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

from pathlib import Path
from typing import Iterable, Iterator, Protocol

from . import mapping, ollama_client

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
    """One method wide: the seam a different provider would be swapped in at."""

    def generate(self, system: str, prompt: str, stream: bool = True) -> Iterator[str]:
        ...


class OllamaBackend:
    """Local generation through the loopback-pinned Ollama daemon."""

    def __init__(self, model: str, temperature: float = 0.2) -> None:
        self.model = model
        self.temperature = temperature

    def generate(self, system: str, prompt: str, stream: bool = True) -> Iterator[str]:
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


def assert_deidentified(text: str, phi_values: Iterable[str] | None = None) -> None:
    """Refuse to send anything carrying a value from the identity mapping.

    A cheap, blunt check, and deliberately so: it compares the outgoing text
    against the real values the mapping holds. It cannot prove the text is free
    of PHI — the review gate upstream is what does that — but it turns the one
    failure that would matter most, a mapping value reaching the model, into a
    crash rather than a silent send.
    """
    if not phi_values:
        return
    haystack = " ".join((text or "").split()).casefold()
    for value in phi_values:
        needle = " ".join(str(value or "").split()).casefold()
        if len(needle) >= mapping.MIN_VALUE_LENGTH and needle in haystack:
            raise CareNoteError(
                "Refusing to generate: the text handed to the model still "
                "contains a value from the identity mapping. This is a bug — "
                "generation must only ever receive approved de-identified text."
            )


def generate_document(
    deidentified_text: str,
    template: str,
    backend: Backend,
    stream: bool = True,
    *,
    custom_instruction: str = "",
    phi_values: Iterable[str] | None = None,
) -> Iterator[str]:
    """Stream a drafted document from approved de-identified text.

    ``phi_values`` is the mapping's real values, passed **only** so this
    function can assert they are absent. They are never forwarded to a backend.
    """
    if not deidentified_text or not deidentified_text.strip():
        raise CareNoteError("There is no de-identified text to work from.")

    assert_deidentified(deidentified_text, phi_values)
    prompt = render_prompt(deidentified_text, template, custom_instruction)
    assert_deidentified(prompt, phi_values)

    return backend.generate(system_prompt(), prompt, stream)


def refine_document(
    deidentified_text: str,
    draft: str,
    instruction: str,
    backend: Backend,
    stream: bool = True,
    *,
    history: list[tuple[str, str]] | None = None,
    phi_values: Iterable[str] | None = None,
) -> Iterator[str]:
    """Revise an existing draft against a follow-up instruction.

    Operates on the same de-identified source plus the running draft — both
    already free of PHI — so the refinement loop carries exactly the privacy
    properties of the first pass. ``history`` is a short list of
    ``(instruction, note)`` pairs, included so the model does not undo an
    earlier request while satisfying the current one.
    """
    if not draft or not draft.strip():
        raise CareNoteError("There is no draft to refine yet.")
    if not instruction or not instruction.strip():
        raise CareNoteError("Say what you would like changed.")

    assert_deidentified(draft, phi_values)
    assert_deidentified(instruction, phi_values)

    steer = instruction.strip()
    if history:
        earlier = "\n".join(f"- {item}" for item, _ in history[-4:])
        steer = (
            f"{steer}\n\nEarlier instructions already applied — keep them "
            f"satisfied:\n{earlier}"
        )

    prompt = (
        load_prompt("refine.txt")
        .replace("{document}", deidentified_text)
        .replace("{draft}", draft)
        .replace("{instruction}", steer)
    )
    assert_deidentified(prompt, phi_values)

    return backend.generate(system_prompt(), prompt, stream)


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
    return with_banner("".join(chunks))


__all__ = [
    "Backend",
    "CUSTOM_TEMPLATE",
    "CareNoteError",
    "DISABLED_MESSAGE",
    "DRAFT_BANNER",
    "OllamaBackend",
    "TEMPLATES",
    "assert_deidentified",
    "finalise",
    "generate_care_note",
    "generate_document",
    "load_prompt",
    "refine_document",
    "render_prompt",
    "system_prompt",
    "template_names",
    "with_banner",
]
