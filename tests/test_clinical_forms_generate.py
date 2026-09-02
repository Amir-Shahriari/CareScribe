import pytest

from carescribe.core import carenotes, clinical_forms


class RecordingBackend:
    """Captures exactly what generation handed the model — mirrors the
    fixture in tests/test_generation.py, kept local so this file has no
    cross-file test dependency."""

    def __init__(self, reply: str = ""):
        self.reply = reply
        self.system = ""
        self.prompt = ""

    def generate(self, system, prompt, stream=True, *, grammar=None):
        self.system = system
        self.prompt = prompt
        yield self.reply


def test_generate_form_document_sends_the_field_marker_prompt():
    spec = clinical_forms.get_form_spec("client_session_notes")
    reply = "".join(f"<<FIELD:{f.key}>>\ntext for {f.key}\n" for f in spec.fields)
    backend = RecordingBackend(reply)

    chunks = clinical_forms.generate_form_document(
        "Patient: [PATIENT]\nSeen in clinic.", spec, backend, stream=False,
    )
    output = "".join(chunks)

    assert f"<<FIELD:{spec.fields[0].key}>>" in backend.system
    assert "Patient: [PATIENT]" in backend.prompt
    assert output == reply


def test_generate_form_document_refuses_a_real_identifier():
    spec = clinical_forms.get_form_spec("client_session_notes")
    backend = RecordingBackend("output")
    with pytest.raises(carenotes.CareNoteError):
        list(clinical_forms.generate_form_document(
            "Mariam Rahman attended clinic.", spec, backend, stream=False,
            phi_values=["Mariam Rahman"],
        ))


def test_refine_form_document_preserves_markers_instruction():
    spec = clinical_forms.get_form_spec("client_session_notes")
    backend = RecordingBackend("revised")
    draft = "".join(f"<<FIELD:{f.key}>>\noriginal\n" for f in spec.fields)

    list(clinical_forms.refine_form_document(
        "source text", draft, "make it shorter", spec, backend, stream=False,
    ))
    assert "<<FIELD:" in backend.prompt
    assert "make it shorter" in backend.prompt


def test_render_preview_shows_every_field_label_and_value():
    spec = clinical_forms.get_form_spec("client_session_notes")
    values = {f.key: f"value-{f.key}" for f in spec.fields}
    preview = clinical_forms.render_preview(spec, values)
    for field in spec.fields:
        assert field.label in preview
        assert f"value-{field.key}" in preview


def test_render_preview_defaults_missing_value():
    spec = clinical_forms.get_form_spec("client_session_notes")
    preview = clinical_forms.render_preview(spec, {})
    assert "Not documented" in preview
