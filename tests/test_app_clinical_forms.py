"""Pure-logic pieces of the clinical-form UI: the session-state key used to
key a multi-document draft (not tied to one Document.name, unlike the
free-form path), and header-field completeness checking before Generate is
enabled.
"""

from carescribe import app


def test_form_draft_key_is_stable_for_the_same_selection():
    key1 = app._form_draft_key(["b.txt", "a.txt"], "client_session_notes")
    key2 = app._form_draft_key(["a.txt", "b.txt"], "client_session_notes")
    assert key1 == key2  # order of selection shouldn't matter


def test_form_draft_key_differs_by_form_or_selection():
    base = app._form_draft_key(["a.txt"], "client_session_notes")
    assert base != app._form_draft_key(["a.txt", "b.txt"], "client_session_notes")
    assert base != app._form_draft_key(["a.txt"], "client_treatment_review")


def test_invalidate_form_export_drops_stale_resolved_values():
    # A refine or regenerate must never leave a previously re-identified
    # export sitting around next to freshly-generated draft text — the UI
    # decides whether to show "Re-identified" and render the download
    # button purely off resolved_field_values, so a stale one there means
    # the practitioner reviews revision N but downloads revision N-1.
    draft = {
        "resolved_field_values": {"x": "y"},
        "unresolved": ["stale"],
        "deidentified": "some draft text",
    }
    app._invalidate_form_export(draft)
    assert "resolved_field_values" not in draft
    assert draft["unresolved"] == []
    # Unrelated draft state is left alone.
    assert draft["deidentified"] == "some draft text"


def test_header_values_complete_requires_every_non_reason_field():
    from carescribe.core import clinical_forms
    spec = clinical_forms.get_form_spec("client_session_notes")
    incomplete = {"date": "12/08/2026"}
    complete = {
        "date": "12/08/2026", "practitioner": "A. Nguyen",
        "client_name": "J. Smith", "client_dob": "01/01/1990",
        "session_number": "4", "item_code": "80010",
    }
    assert app._header_values_complete(spec, incomplete) is False
    assert app._header_values_complete(spec, complete) is True
    # "Reason for referral" is optional — a blank answer is a valid clinical fact.
    assert app._header_values_complete(spec, {**complete, "reason_for_referral": ""}) is True
