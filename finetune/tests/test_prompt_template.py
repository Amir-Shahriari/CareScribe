"""The training prompt must be byte-identical to what the app sends."""

from __future__ import annotations

from carescribe.prompts import carenotes_prompt as cp

from finetune.datagen.schema import FormType
from finetune.integrate import prompt_template as pt


def test_system_prompts_come_verbatim_from_carescribe():
    assert pt.system_prompt(FormType.SOAP) == cp.SOAP_SYSTEM
    assert pt.system_prompt(FormType.CARE_PLAN) == cp.CARE_PLAN_SYSTEM
    assert pt.system_prompt(FormType.PROGRESS_NOTE) == cp.PROGRESS_NOTE_SYSTEM
    assert pt.SHARED_RULES == cp._SHARED_RULES
    assert pt.USER_TEMPLATE == cp.USER_TEMPLATE


def test_every_form_type_has_a_prompt():
    for form in FormType:
        assert pt.system_prompt(form)
        assert pt.default_instruction(form)


def test_build_messages_shape():
    msgs = pt.build_messages(FormType.SOAP, "[PATIENT] seen today. BP [VALUE].")
    assert [m["role"] for m in msgs] == ["system", "user"]
    assert msgs[0]["content"] == cp.SOAP_SYSTEM
    assert "[PATIENT] seen today" in msgs[1]["content"]
    assert "Write the SOAP note." in msgs[1]["content"]


def test_style_exemplar_is_prepended_to_the_user_turn():
    msgs = pt.build_messages(
        FormType.PROGRESS_NOTE,
        "[PATIENT] reviewed.",
        style_exemplar="Terse. Bullet points. No sign-off.",
    )
    assert msgs[1]["content"].startswith("House-style example to match:")
    assert "Terse. Bullet points." in msgs[1]["content"]


def test_custom_instruction_overrides_the_default():
    msgs = pt.build_messages(
        FormType.SOAP, "[PATIENT] seen.", instruction="Write only the Plan section."
    )
    assert "Write only the Plan section." in msgs[1]["content"]
    assert "Write the SOAP note." not in msgs[1]["content"]
