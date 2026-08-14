import pytest

from carescribe.core import clinical_forms, mapping


def test_combine_sources_prefixes_placeholders_per_document():
    sources = [
        ("intake.txt", "Patient: [PATIENT], seen on [DATE_1].", {"[PATIENT]": "A", "[DATE_1]": "1 Jan"}),
        ("referral.txt", "Re: [PATIENT], referred by [CLINICIAN_1].", {"[PATIENT]": "A", "[CLINICIAN_1]": "Dr B"}),
    ]
    combined_text, merged_map = clinical_forms.combine_sources(sources)

    assert "[DOC1_PATIENT]" in combined_text
    assert "[DOC2_PATIENT]" in combined_text
    assert "[PATIENT]" not in combined_text  # no un-prefixed survivor

    assert merged_map["[DOC1_PATIENT]"] == "A"
    assert merged_map["[DOC1_DATE_1]"] == "1 Jan"
    assert merged_map["[DOC2_PATIENT]"] == "A"
    assert merged_map["[DOC2_CLINICIAN_1]"] == "Dr B"


def test_combine_sources_reidentifies_without_collision():
    sources = [
        ("a.txt", "[PATIENT] attended.", {"[PATIENT]": "Alice Chen"}),
        ("b.txt", "[PATIENT] was discussed.", {"[PATIENT]": "Someone Else Entirely"}),
    ]
    combined_text, merged_map = clinical_forms.combine_sources(sources)
    resolved, unresolved = mapping.reidentify_document(combined_text, merged_map)
    assert unresolved == []
    assert "Alice Chen attended." in resolved
    assert "Someone Else Entirely was discussed." in resolved


def test_combine_sources_rejects_an_empty_list():
    with pytest.raises(clinical_forms.ClinicalFormError):
        clinical_forms.combine_sources([])
