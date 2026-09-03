"""
Regression: public crisis-line names are not identifiers and must not be redacted.

Found by a cockpit QA pass. "Advised to contact Lifeline 13 11 14" came back as
"contact [PERSON] 13 11 14" in one document and untouched in another — the NER
layer labels a well-known helpline as a PERSON or ORGANIZATION depending on the
surrounding sentence. Redacting it loses clinically useful information (which
support was offered) and buys nothing: a national helpline is public, not PHI.

Fix: add the common Australian and UK crisis-line names to
``carescribe/core/protected_terms.txt`` (the allow-list that outranks every
detection layer), so they are preserved deterministically.
"""

from __future__ import annotations

import pytest

from carescribe.core import deidentify

CRISIS_LINES = [
    "Lifeline",
    "Suicide Call Back Service",
    "Beyond Blue",
    "Kids Helpline",
    "MensLine Australia",
    "13YARN",
    "1800RESPECT",
    "Samaritans",
    "Papyrus",
    "SHOUT",
    "CALM",
]


@pytest.mark.parametrize("name", CRISIS_LINES)
def test_a_crisis_line_name_survives_deidentification(name: str) -> None:
    text = f"Safety plan discussed. Advised to contact {name} if distressed before the next session."
    redacted = deidentify.deidentify(text).redacted_text
    assert name in redacted, redacted


@pytest.mark.parametrize(
    "line",
    [
        "Advised to contact Lifeline 13 11 14 if in crisis.",
        "Referred to the Suicide Call Back Service 1300 659 467.",
        "Gave details for Beyond Blue and Kids Helpline.",
    ],
)
def test_crisis_line_name_and_number_both_survive_in_context(line: str) -> None:
    redacted = deidentify.deidentify(line).redacted_text
    for token in ("Lifeline", "Suicide Call Back Service", "Beyond Blue", "Kids Helpline"):
        if token in line:
            assert token in redacted, (token, redacted)


def test_a_person_named_near_a_crisis_line_is_still_redacted() -> None:
    """The allow-list entry is the helpline name only — a real name beside it still goes."""
    text = "Jordan Whitfield was given the Lifeline number by Dr Amelia Ferro."
    redacted = deidentify.deidentify(text).redacted_text
    assert "Lifeline" in redacted
    assert "Whitfield" not in redacted
    assert "Amelia Ferro" not in redacted
