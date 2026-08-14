from carescribe.core import clinical_forms


def _spec():
    return clinical_forms.get_form_spec("client_session_notes")


def test_parse_fields_happy_path():
    spec = _spec()
    key0, key1 = spec.fields[0].key, spec.fields[1].key
    raw = (
        f"<<FIELD:{key0}>>\nFirst field text.\n\n"
        f"<<FIELD:{key1}>>\nSecond field text.\n"
    )
    parsed = clinical_forms.parse_fields(spec, raw)
    assert parsed[key0] == "First field text."
    assert parsed[key1] == "Second field text."


def test_parse_fields_defaults_missing_field_to_not_documented():
    spec = _spec()
    key0 = spec.fields[0].key
    raw = f"<<FIELD:{key0}>>\nOnly this one field.\n"
    parsed = clinical_forms.parse_fields(spec, raw)
    assert parsed[key0] == "Only this one field."
    assert all(
        parsed[f.key] == "Only this one field." if f.key == key0 else parsed[f.key] == "Not documented"
        for f in spec.fields
    )


def test_parse_fields_first_occurrence_wins_on_duplicate_marker():
    spec = _spec()
    key0 = spec.fields[0].key
    raw = f"<<FIELD:{key0}>>\nFirst.\n<<FIELD:{key0}>>\nSecond (should be ignored).\n"
    parsed = clinical_forms.parse_fields(spec, raw)
    assert parsed[key0] == "First."


def test_parse_fields_ignores_unknown_marker_without_raising():
    spec = _spec()
    key0 = spec.fields[0].key
    raw = f"<<FIELD:not_a_real_field>>\nStray.\n<<FIELD:{key0}>>\nReal text.\n"
    parsed = clinical_forms.parse_fields(spec, raw)
    assert parsed[key0] == "Real text."
    assert "not_a_real_field" not in parsed


def test_parse_fields_handles_empty_output():
    spec = _spec()
    parsed = clinical_forms.parse_fields(spec, "")
    assert all(value == "Not documented" for value in parsed.values())
    assert set(parsed) == {f.key for f in spec.fields}


def test_parse_fields_treats_whitespace_only_content_as_not_documented():
    # A field body of only \r/\t/\n (no spaces, no dash) must still resolve
    # to "Not documented" rather than surviving as a blank string — the old
    # strip(" \n—-") charset didn't cover \r or \t.
    spec = _spec()
    key0 = spec.fields[0].key
    raw = f"<<FIELD:{key0}>>\r\n\r\t\n"
    parsed = clinical_forms.parse_fields(spec, raw)
    assert parsed[key0] == "Not documented"
