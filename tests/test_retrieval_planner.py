"""Per-field retrieval planning (roadmap item E). The shipped planner is
rule-based over field labels; a guard test keeps it (like the reference
library) out of the generation path.
"""

import inspect

from carescribe.core import clinical_forms, retrieval_planner


def _field(spec, needle):
    return next(f for f in spec.fields if needle.lower() in f.label.lower())


def test_medication_field_wants_sentence_level_reference():
    spec = clinical_forms.get_form_spec("biopsychosocial_assessment")
    plans = retrieval_planner.plan(spec, "source text")
    plan = plans[_field(spec, "medication").key]
    assert plan.want_reference is True
    assert plan.granularity == "sentence"


def test_mood_field_wants_no_reference():
    spec = clinical_forms.get_form_spec("biopsychosocial_assessment")
    plans = retrieval_planner.plan(spec, "src")
    assert plans[_field(spec, "Mood").key].want_reference is False


def test_risk_field_wants_paragraph_reference():
    spec = clinical_forms.get_form_spec("biopsychosocial_assessment")
    plans = retrieval_planner.plan(spec, "src")
    plan = plans[_field(spec, "Suicidal ideation").key]
    assert plan.want_reference is True
    assert plan.granularity == "paragraph"


def test_diagnoses_field_wants_section_reference():
    spec = clinical_forms.get_form_spec("client_treatment_review")
    plans = retrieval_planner.plan(spec, "src")
    plan = plans[_field(spec, "diagnoses").key]
    assert plan.want_reference is True
    assert plan.granularity == "section"


def test_plan_covers_every_field_and_wants_exemplars_for_all():
    spec = clinical_forms.get_form_spec("client_session_notes")
    plans = retrieval_planner.plan(spec, "patient reports low mood and poor sleep")
    assert set(plans) == {f.key for f in spec.fields}
    assert all(p.want_exemplars for p in plans.values())


def test_query_is_field_label_plus_salient_source_terms_without_stopwords():
    spec = clinical_forms.get_form_spec("client_session_notes")
    plans = retrieval_planner.plan(
        spec, "The patient reported ongoing insomnia and anhedonia this week."
    )
    query = next(iter(plans.values())).query
    assert "insomnia" in query and "anhedonia" in query
    assert " the " not in f" {query} "


def test_planner_is_pluggable():
    spec = clinical_forms.get_form_spec("client_session_notes")

    class _Empty:
        def plan(self, form_spec, deidentified_text):
            return {}

    assert retrieval_planner.plan(spec, "x", planner=_Empty()) == {}


def test_planner_is_not_wired_into_generation():
    from carescribe.core import carenotes

    assert "retrieval_planner" not in inspect.getsource(clinical_forms)
    assert "retrieval_planner" not in inspect.getsource(carenotes)
