"""
Care note generation.

This stage sees ONLY de-identified text. The original document and the PHI map
are never passed in — the function signature has nowhere to put them, which is
the point. Re-identification, if the user asks for it, happens afterwards on the
generated string via ``mapping.reidentify``.
"""

from __future__ import annotations

from typing import Iterator

from ..prompts.carenotes_prompt import CUSTOM_TEMPLATE_LABEL, TEMPLATES, build_messages
from . import mapping
from .ollama_client import OllamaError, chat

# Re-exported so the UI can build its selector without importing the prompts pkg.
TEMPLATE_LABELS = list(TEMPLATES.keys())

# Shared with the re-identification path so what we warn about and what we can
# actually repair stay in agreement. Tolerant enough to see mangled tokens like
# [MATIENT_2] that the note model produced while rewriting.
PLACEHOLDER_RE = mapping.PLACEHOLDER_RE


class CareNoteError(RuntimeError):
    """Raised when care note generation can't proceed."""


def _guard(deidentified_text: str, model: str) -> None:
    """Refuse to run on empty input or with no model selected."""
    if not model:
        raise CareNoteError("No model selected. Pick one in the sidebar.")
    if not deidentified_text.strip():
        raise CareNoteError("There is no de-identified text to work from.")


def generate_stream(
    model: str,
    deidentified_text: str,
    template: str,
    custom_instruction: str = "",
    temperature: float = 0.3,
    timeout: float = 600.0,
) -> Iterator[str]:
    """Stream a care note, yielding text deltas.

    ``temperature`` is a little above the de-identification stage's 0.0 —
    clinical prose reads better with some freedom, while the prompt's rules keep
    it anchored to the source.
    """
    _guard(deidentified_text, model)

    system, user = build_messages(template, deidentified_text, custom_instruction)

    stream = chat(
        model=model,
        system=system,
        user=user,
        stream=True,
        timeout=timeout,
        temperature=temperature,
    )
    return stream  # type: ignore[return-value]


def generate(
    model: str,
    deidentified_text: str,
    template: str,
    custom_instruction: str = "",
    temperature: float = 0.3,
    timeout: float = 600.0,
) -> str:
    """Non-streaming variant — returns the finished note as one string."""
    _guard(deidentified_text, model)

    system, user = build_messages(template, deidentified_text, custom_instruction)
    return str(
        chat(
            model=model,
            system=system,
            user=user,
            stream=False,
            timeout=timeout,
            temperature=temperature,
        )
    )


def find_unknown_placeholders(note: str, known: dict[str, str]) -> list[str]:
    """Return placeholders in ``note`` that can't be resolved to the PHI map.

    A token the model merely mangled ([MATIENT_2] for [PATIENT_2]) is repaired
    during re-identification, so it is not reported here. What remains is
    genuinely invented — re-identification will leave it in the output, and the
    UI surfaces it as a warning rather than silently shipping a broken note.
    """
    found = set(PLACEHOLDER_RE.findall(note))
    return sorted(
        token
        for token in found
        if mapping.resolve_placeholder(token, known.keys()) is None
    )


__all__ = [
    "CareNoteError",
    "OllamaError",
    "TEMPLATE_LABELS",
    "CUSTOM_TEMPLATE_LABEL",
    "generate",
    "generate_stream",
    "find_unknown_placeholders",
]
