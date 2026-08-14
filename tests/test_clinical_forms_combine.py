import pytest

from carescribe.core import clinical_forms, mapping


def test_combine_sources_prefixes_placeholders_per_document():
    sources = [
        ("intake.txt", "Patient: [PATIENT], seen on [DATE_1].", {"[PATIENT]": "A", "[DATE_1]": "1 Jan"}),
        ("referral.txt", "Re: [PATIENT], referred by [CLINICIAN_1].", {"[PATIENT]": "A", "[CLINICIAN_1]": "Dr B"}),
    ]
    combined_text, merged_map = clinical_forms.combine_sources(sources)

    # Verify letter-based prefixes (DOCA_, DOCB_) are used, not digit-based (DOC1_, DOC2_)
    assert "[DOCA_PATIENT]" in combined_text
    assert "[DOCB_PATIENT]" in combined_text
    assert "[PATIENT]" not in combined_text  # no un-prefixed survivor

    assert merged_map["[DOCA_PATIENT]"] == "A"
    assert merged_map["[DOCA_DATE_1]"] == "1 Jan"
    assert merged_map["[DOCB_PATIENT]"] == "A"
    assert merged_map["[DOCB_CLINICIAN_1]"] == "Dr B"


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


def test_combine_sources_rejects_more_than_26_documents():
    """Regression test for Finding 1: cap at 26 documents (A-Z)."""
    sources = [
        (f"doc{i}.txt", "[PATIENT] data.", {"[PATIENT]": f"Person{i}"})
        for i in range(27)
    ]
    with pytest.raises(clinical_forms.ClinicalFormError):
        clinical_forms.combine_sources(sources)


def test_combine_sources_prefixed_placeholders_match_regex():
    """Regression test for Finding 1: prefixed placeholders must match PLACEHOLDER_RE.

    This critical test ensures that letter-based prefixes like [DOCA_PATIENT]
    match mapping.PLACEHOLDER_RE, so the placeholder integrity and unresolved
    token detection mechanisms in mapping.reidentify_document work correctly.
    """
    sources = [
        ("a.txt", "[PATIENT] attended.", {"[PATIENT]": "Alice"}),
        ("b.txt", "[DATE_2] visit.", {"[DATE_2]": "2026-08-14"}),
        ("c.txt", "[MRN] recorded.", {"[MRN]": "12345"}),
    ]
    combined_text, merged_map = clinical_forms.combine_sources(sources)

    # Verify all prefixed placeholders in the text match the regex
    import re
    for match in mapping.PLACEHOLDER_RE.finditer(combined_text):
        placeholder = match.group(0)
        assert placeholder in merged_map, f"Found unresolved placeholder {placeholder}"


def test_combine_sources_non_standard_placeholder_consistency():
    """Regression test for Finding 2: text and map rewrites must be consistent.

    A manually-typed non-standard placeholder (not matching PLACEHOLDER_RE pattern)
    should be prefixed consistently in both the text and the map. Both rewrites
    are driven from phi_map.keys(), so no asymmetry can exist.
    """
    sources = [
        ("a.txt", "Patient [pt] is here.", {"[pt]": "Alice"}),
        ("b.txt", "Patient [pt] not here.", {"[pt]": "Bob"}),
    ]
    combined_text, merged_map = clinical_forms.combine_sources(sources)

    # The non-standard [pt] placeholders must be prefixed in BOTH text and map
    assert "[pt]" not in combined_text  # bare form should not survive
    assert "[DOCA_pt]" in combined_text
    assert "[DOCB_pt]" in combined_text
    assert "[DOCA_pt]" in merged_map
    assert "[DOCB_pt]" in merged_map
    assert merged_map["[DOCA_pt]"] == "Alice"
    assert merged_map["[DOCB_pt]"] == "Bob"

    # Re-identification must succeed without unresolved tokens
    resolved, unresolved = mapping.reidentify_document(combined_text, merged_map)
    assert unresolved == [], f"Unresolved tokens: {unresolved}"
    assert "Alice" in resolved
    assert "Bob" in resolved


def test_combine_sources_no_filename_in_output():
    """Regression test for Finding 3: raw filename must not leak into model-facing text.

    Document names are often actual filenames which may contain PII. The combined
    text is later sent to the model, so filenames must not be interpolated into it.
    Use plain positional separators instead.
    """
    sources = [
        ("Alice_Chen_referral_2026-08-14.pdf", "[PATIENT] needs care.", {"[PATIENT]": "Alice"}),
        ("Private_Medical_Data_Bob_Smith.docx", "[PROVIDER] agreed.", {"[PROVIDER]": "Dr X"}),
    ]
    combined_text, merged_map = clinical_forms.combine_sources(sources)

    # Verify no raw filenames appear in the combined text
    assert "Alice_Chen_referral" not in combined_text
    assert "2026-08-14" not in combined_text  # no date from filename
    assert "Private_Medical_Data" not in combined_text
    assert "Bob_Smith" not in combined_text

    # Verify plain positional separators are used instead
    assert "--- Source 1 ---" in combined_text
    assert "--- Source 2 ---" in combined_text
