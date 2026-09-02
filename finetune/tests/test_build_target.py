"""The deterministic scaffold must satisfy its own validators for every form."""

from __future__ import annotations

import pytest

from finetune.assemble.build_target import NOT_DOCUMENTED, build_target
from finetune.assemble.validators import validate
from finetune.datagen.sampler import sample_encounters
from finetune.datagen.schema import Demographics, EncounterFacts, EncounterType, FormType

_FORMS = [FormType.SOAP, FormType.PROGRESS_NOTE, FormType.HANDOVER, FormType.CARE_PLAN]


@pytest.mark.parametrize("form", _FORMS, ids=lambda f: f.value)
def test_scaffold_passes_its_own_validators(form):
    for i, facts in enumerate(sample_encounters(40, seed=11, gap_probability=0.35)):
        target = build_target(facts, form)
        report = validate(target, facts, form, known_placeholders=[])
        assert report.ok, f"{form}: {report.problems}\n---\n{target}"


def test_scaffold_is_deterministic():
    facts = next(sample_encounters(1, seed=5))
    assert build_target(facts, FormType.SOAP) == build_target(facts, FormType.SOAP)


def test_a_gapped_section_reads_not_documented():
    facts = EncounterFacts(
        specialty="general practice",
        encounter_type=EncounterType.FOLLOW_UP,
        demographics=Demographics(age_band="40-49", sex="F", occupation="teacher"),
        presenting_complaint="routine review, no new concerns",
        examination=[],
        impression=[],
        documented_gaps=["examination", "investigations", "meds", "impression"],
    )
    soap = build_target(facts, FormType.SOAP)
    objective = soap.split("**O — Objective**", 1)[1].split("**A — Assessment**", 1)[0]
    assessment = soap.split("**A — Assessment**", 1)[1].split("**P — Plan**", 1)[0]
    assert NOT_DOCUMENTED in objective
    assert NOT_DOCUMENTED in assessment
    assert validate(soap, facts, FormType.SOAP, known_placeholders=[]).ok


def test_uploaded_template_fills_every_field_marker():
    from carescribe.core import clinical_forms

    from finetune.assemble.validators import validate

    spec = clinical_forms.get_form_spec("client_session_notes")
    facts = next(sample_encounters(1, seed=1))

    with pytest.raises(ValueError):
        build_target(facts, FormType.UPLOADED_TEMPLATE)  # needs a spec

    target = build_target(facts, FormType.UPLOADED_TEMPLATE, form_spec=spec)
    for field in spec.fields:
        assert f"<<FIELD:{field.key}>>" in target
    report = validate(
        target, facts, FormType.UPLOADED_TEMPLATE, known_placeholders=[], form_spec=spec
    )
    assert report.ok, report.problems
