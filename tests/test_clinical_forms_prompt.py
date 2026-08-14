from carescribe.core import clinical_forms


def test_build_prompt_lists_every_field_marker_in_order():
    spec = clinical_forms.get_form_spec("client_session_notes")
    system, user = clinical_forms.build_prompt(spec, "Patient: [PATIENT]\nSeen in clinic.")

    for field in spec.fields:
        assert f"<<FIELD:{field.key}>>" in system

    order = [system.index(f"<<FIELD:{f.key}>>") for f in spec.fields]
    assert order == sorted(order)

    assert "Not documented" in system
    assert "Preserve every bracketed placeholder" in system or "placeholder" in system.lower()
    assert "[PATIENT]" in user
    assert "Seen in clinic." in user


def test_build_prompt_never_echoes_a_real_identifier_pattern():
    spec = clinical_forms.get_form_spec("client_session_notes")
    system, _ = clinical_forms.build_prompt(spec, "irrelevant")
    assert "Mariam" not in system  # sanity: system prompt is static, not source-derived
