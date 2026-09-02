"""The four gates catch the failure modes that matter."""

from __future__ import annotations

from finetune.assemble.build_target import build_target
from finetune.assemble.validators import (
    check_faithfulness,
    check_format,
    check_placeholders,
    check_residual,
    validate,
)
from finetune.datagen.sampler import sample_encounters
from finetune.datagen.schema import FormType

FACTS = next(sample_encounters(1, seed=99, gap_probability=0.0))
SOAP = build_target(FACTS, FormType.SOAP)


def test_format_flags_a_missing_heading():
    ok, problems = check_format(SOAP.replace("**A — Assessment**", "**Notes**"), FormType.SOAP)
    assert not ok
    assert any("A — Assessment" in p for p in problems)


def test_format_flags_text_before_the_first_heading():
    ok, _ = check_format("Here is your note.\n\n" + SOAP, FormType.SOAP)
    assert not ok


def test_faithfulness_flags_an_invented_number():
    tampered = SOAP + "\n- BP was 187/112 today"
    ok, problems = check_faithfulness(tampered, FACTS, FormType.SOAP)
    assert not ok
    assert any("187" in p or "112" in p for p in problems)


def test_faithfulness_accepts_the_untouched_scaffold():
    ok, problems = check_faithfulness(SOAP, FACTS, FormType.SOAP)
    assert ok, problems


def test_placeholder_check_flags_a_mangled_token():
    ok, problems = check_placeholders("[PATIENT] seen by [MATIENT_2].", ["[PATIENT]", "[PATIENT_2]"])
    assert not ok
    assert problems


def test_residual_check_flags_a_phone_number_but_not_a_placeholder():
    ok_clean, _ = check_residual("[PATIENT] was reviewed on the ward.")
    assert ok_clean
    ok_leak, problems = check_residual("Call 0161 496 0245 for the ward.")
    assert not ok_leak and problems


def test_residual_check_honours_acknowledged_findings():
    ok, _ = check_residual("Seen at the community clinic in Harrogate.", acknowledged=["Harrogate"])
    assert ok


def test_validate_aggregates():
    report = validate(SOAP, FACTS, FormType.SOAP, known_placeholders=[])
    assert report.ok
    assert report.problems == []
