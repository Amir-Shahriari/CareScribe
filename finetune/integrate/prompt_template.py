"""
The prompt construction shared by training and production.

Training pairs MUST be built with the exact system/user strings the shipping
app sends at inference time, or the fine-tune is optimising for a prompt the
app never uses. Rather than copy the text, this module imports it from
``carescribe.prompts.carenotes_prompt`` and only adds the mapping from
:class:`~finetune.datagen.schema.FormType` to the right pieces.

``carescribe`` never imports this module (or anything else under ``finetune/``);
the dependency is one-way.
"""

from __future__ import annotations

from carescribe.prompts import carenotes_prompt as _cp

from finetune.datagen.schema import FormType

# Re-exported so callers touch one name, not the carescribe internals.
SHARED_RULES: str = _cp._SHARED_RULES
USER_TEMPLATE: str = _cp.USER_TEMPLATE

# FormType -> (system prompt, default instruction line).
_BY_FORM: dict[FormType, tuple[str, str]] = {
    FormType.SOAP: (_cp.SOAP_SYSTEM, "Write the SOAP note."),
    FormType.CARE_PLAN: (_cp.CARE_PLAN_SYSTEM, "Write the nursing care plan."),
    FormType.PROGRESS_NOTE: (
        _cp.PROGRESS_NOTE_SYSTEM,
        "Write the interval progress note.",
    ),
    FormType.HANDOVER: (
        _cp.CUSTOM_SYSTEM,
        "Write the shift handover summary (SBAR: Situation, Background, "
        "Assessment, Recommendation).",
    ),
    FormType.UPLOADED_TEMPLATE: (
        _cp.CUSTOM_SYSTEM,
        "Fill in the clinical form below using only the source document.",
    ),
}


def system_prompt(form: FormType) -> str:
    """The system string for a form type."""
    return _BY_FORM[form][0]


def default_instruction(form: FormType) -> str:
    """The instruction line paired with a form type when none is supplied."""
    return _BY_FORM[form][1]


def build_messages(
    form: FormType,
    placeholdered_document: str,
    *,
    instruction: str | None = None,
    style_exemplar: str | None = None,
) -> list[dict[str, str]]:
    """A chat message list: system, then user.

    ``placeholdered_document`` is the output of the real CareScribe
    de-identifier — text with ``[PATIENT]`` / ``[DATE_1]`` style tokens. An
    optional ``style_exemplar`` is prepended to the user turn, matching how the
    app conditions on a clinic's house style.
    """
    user = USER_TEMPLATE.format(
        document=placeholdered_document,
        instruction=instruction or default_instruction(form),
    )
    if style_exemplar:
        user = f"House-style example to match:\n{style_exemplar}\n\n{user}"
    return [
        {"role": "system", "content": system_prompt(form)},
        {"role": "user", "content": user},
    ]


__all__ = [
    "SHARED_RULES",
    "USER_TEMPLATE",
    "build_messages",
    "default_instruction",
    "system_prompt",
]
