"""
Run the real CareScribe de-identifier over a synthetic note.

The fine-tune must see exactly the text distribution production produces: the
output of `carescribe.core.deidentify.deidentify`, with real `[TOKEN_n]`
placeholders and de-id's own artefacts. Generating clean placeholdered text
directly would miss those. So the round trip is:

    render note  ->  inject fake identifiers  ->  DE-IDENTIFY HERE  ->  train

This module imports only `carescribe.core.deidentify`, which is CPU-only and
opens no socket. A test asserts that.
"""

from __future__ import annotations

from dataclasses import dataclass

from carescribe.core.deidentify import deidentify


@dataclass(frozen=True)
class DeidentifiedNote:
    placeholdered_text: str
    phi_map: dict[str, str]          # placeholder -> real value
    entities: list[dict]

    @property
    def known_placeholders(self) -> list[str]:
        return list(self.phi_map)


def deidentify_note(note_text: str) -> DeidentifiedNote:
    """De-identify one rendered+identified synthetic note."""
    result = deidentify(note_text)
    return DeidentifiedNote(
        placeholdered_text=result.redacted_text,
        phi_map=dict(result.phi_map),
        entities=list(result.entities),
    )


def leaked_values(note: DeidentifiedNote, expected_values: list[str]) -> list[str]:
    """Injected identifier values that de-id did NOT remove from the text.

    A non-empty result means the synthetic note is too hard for the real
    pipeline — a useful datagen signal, and a sample to drop rather than train
    on.
    """
    hay = " ".join(note.placeholdered_text.split()).casefold()
    missed = []
    for value in expected_values:
        needle = " ".join(str(value).split()).casefold()
        if len(needle) >= 3 and needle in hay:
            missed.append(value)
    return missed


__all__ = ["DeidentifiedNote", "deidentify_note", "leaked_values"]
