"""House-style exemplar store + BM25 retrieval, and its hook into the
clinical-form prompt. Storage is a monkeypatched temp dir; retrieval is pure
Python and never touches the network.
"""

import pytest

from carescribe.core import clinical_forms, exemplars


@pytest.fixture(autouse=True)
def _store(tmp_path, monkeypatch):
    monkeypatch.setattr(exemplars.desktop, "app_data_dir", lambda: tmp_path)
    exemplars._CACHE.clear()
    yield tmp_path
    exemplars._CACHE.clear()


def test_add_then_count_and_persist(_store):
    assert exemplars.count("client_session_notes") == 0
    exemplars.add_exemplar(
        "client_session_notes",
        {"session_summary.plan": "Reviewed goals with [PATIENT]. Continue CBT.",
         "session_summary.homework": "Not documented"},
    )
    assert exemplars.count("client_session_notes") == 1
    assert (_store / "exemplars" / "client_session_notes.jsonl").is_file()


def test_add_refuses_a_value_that_still_holds_an_identifier(_store):
    with pytest.raises(exemplars.ExemplarError):
        exemplars.add_exemplar(
            "f", {"a": "Patient rang the clinic on 01632 960 188 to reschedule."}
        )
    assert exemplars.count("f") == 0


def test_add_refuses_when_everything_is_blank_or_not_documented(_store):
    with pytest.raises(exemplars.ExemplarError):
        exemplars.add_exemplar("f", {"a": "  ", "b": "Not documented"})


def test_retrieve_ranks_by_bm25_overlap_with_the_query(_store):
    for plan in (
        "Sleep hygiene handout given. Caffeine reduction advised.",
        "Graded exposure hierarchy built for social situations.",
        "Medication review with GP requested; continue sertraline.",
    ):
        exemplars.add_exemplar("f", {"plan": plan})

    hits = exemplars.retrieve("f", "plan", "patient reports poor sleep and high caffeine", k=1)
    assert hits == ["Sleep hygiene handout given. Caffeine reduction advised."]


def test_retrieve_dedupes_and_ignores_records_without_the_field(_store):
    exemplars.add_exemplar("f", {"plan": "Continue weekly sessions."})
    exemplars.add_exemplar("f", {"plan": "Continue weekly sessions."})  # dup
    exemplars.add_exemplar("f", {"plan": "Not documented", "other": "kept"})  # 'plan' dropped
    exemplars.add_exemplar("f", {"other": "x"})  # no 'plan' key
    assert exemplars.retrieve("f", "plan", "anything", k=5) == ["Continue weekly sessions."]


def test_retrieve_respects_k(_store):
    for i in range(6):
        exemplars.add_exemplar("f", {"plan": f"distinct plan text number {i}"})
    assert len(exemplars.retrieve("f", "plan", "plan text", k=3)) == 3


def test_retrieve_all_omits_fields_with_no_exemplars(_store):
    exemplars.add_exemplar("f", {"a": "alpha note"})
    out = exemplars.retrieve_all("f", ["a", "b"], "alpha", k=2)
    assert set(out) == {"a"}


def test_cache_refreshes_when_the_file_grows(_store):
    exemplars.add_exemplar("f", {"plan": "first"})
    assert exemplars.count("f") == 1
    exemplars.add_exemplar("f", {"plan": "second"})
    assert exemplars.count("f") == 2
    assert set(exemplars.retrieve("f", "plan", "first second", k=5)) == {"first", "second"}


# --- prompt hook ---------------------------------------------------------

def test_build_prompt_injects_house_style_lines_and_the_caveat():
    spec = clinical_forms.get_form_spec("client_session_notes")
    key = spec.fields[0].key
    system, _user = clinical_forms.build_prompt(
        spec, "[PATIENT] attended.", {key: ["Prior wording for this field."]}
    )
    assert "house-style example: Prior wording for this field." in system
    assert "STYLE from them only, never facts" in system


def test_build_prompt_without_exemplars_is_unchanged():
    spec = clinical_forms.get_form_spec("client_session_notes")
    system, _ = clinical_forms.build_prompt(spec, "src")
    assert "house-style example: " not in system  # the injected line format
    for field in spec.fields:
        assert f"<<FIELD:{field.key}>>" in system


class _RecordingBackend:
    def __init__(self):
        self.system = None

    def generate(self, system, prompt, stream=True, *, grammar=None):
        self.system = system
        yield "<<FIELD:x>>\nok\n"


def test_generate_form_document_threads_exemplars_into_the_prompt():
    spec = clinical_forms.get_form_spec("client_session_notes")
    key = spec.fields[0].key
    backend = _RecordingBackend()
    list(
        clinical_forms.generate_form_document(
            "[PATIENT] seen today.", spec, backend, stream=True,
            exemplars={key: ["Clinic house wording."]},
        )
    )
    assert "house-style example: Clinic house wording." in backend.system
