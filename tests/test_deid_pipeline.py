"""
Regression suite for the layered de-identification pipeline.

Two guarantees, tested separately because they fail in opposite directions:

* **Recall** — no identifier survives. A miss here leaks PHI.
* **Precision** — clinical content survives. A miss here silently damages the
  document's meaning, and the reviewer has no way to notice from the preview.

Everything runs on the CPU with no network access, using the synthetic fixture
in ``synthetic_patient_discharge_summary.txt``.
"""

import re

import pytest

from carescribe.core import deidentify, mapping
from tests.fixtures import (
    ALSO_MUST_NOT_SURVIVE,
    MUST_NOT_SURVIVE,
    PRESERVED_CLINICAL,
    PRESERVED_DOSAGES,
    PRESERVED_PLACES,
)


# ==========================================================================
# RECALL
# ==========================================================================

@pytest.mark.parametrize("identifier", MUST_NOT_SURVIVE, ids=repr)
def test_identifier_does_not_survive(redacted, identifier):
    assert identifier not in redacted


@pytest.mark.parametrize("identifier", ALSO_MUST_NOT_SURVIVE, ids=repr)
def test_additional_identifier_does_not_survive(redacted, identifier):
    assert identifier not in redacted


def test_nhs_number_gone_in_every_spacing(redacted):
    """The NHS number must not survive under any spacing or hyphenation."""
    for spelling in ("943 476 5919", "9434765919", "943-476-5919", "943476 5919"):
        assert spelling not in redacted
    # And no bare 10-digit run is left anywhere.
    assert not re.search(r"\b\d{3}[\s-]?\d{3}[\s-]?\d{4}\b", redacted)


def test_line_broken_name_collapses_to_one_placeholder(redacted):
    """"Margaret\\nChen" must redact to the SAME placeholder as the header name."""
    assert "Margaret" not in redacted
    assert "Chen" not in redacted
    assert redacted.count("[PATIENT]") >= 3  # header, "Mrs Chen", the split name


def test_every_surname_form_maps_to_one_clinician(deid, redacted):
    """"Dr Patel", "Dr Raj Patel" and a bare "Patel" are one person, one placeholder."""
    patel = [e for e in deid.entities if "Patel" in e["value"]]
    assert len(patel) == 1, f"clinician split across rows: {patel}"
    assert patel[0]["placeholder"] not in ("", None)
    assert "Patel" not in redacted


def test_no_email_phone_or_postcode_survives(redacted):
    assert not re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", redacted)
    assert not re.search(r"\b0\d{2,4}[\s-]?\d{3,4}[\s-]?\d{2,4}\b", redacted)
    assert not re.search(r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b", redacted)


# ==========================================================================
# PRECISION
# ==========================================================================

@pytest.mark.parametrize("place", PRESERVED_PLACES, ids=repr)
def test_place_of_care_survives(redacted, place):
    """A bare city name used as context, not as an address, is not an identifier.

    "She had returned two days earlier from visiting family in Leeds." The same
    token inside "14 Leeds Road" IS redacted — this asserts the standalone one.
    """
    assert place in redacted
    assert f"in {place}." in redacted


@pytest.mark.parametrize("dosage", PRESERVED_DOSAGES, ids=repr)
def test_dosage_survives(redacted, dosage):
    assert dosage in redacted


@pytest.mark.parametrize("term", PRESERVED_CLINICAL, ids=repr)
def test_clinical_term_survives(redacted, term):
    assert term in redacted


def test_medication_block_is_untouched(raw_text, redacted):
    """The whole medication list must come through byte-identical."""
    block = raw_text.split("MEDICATION ON DISCHARGE")[1].split("NEXT OF KIN")[0]
    assert block in redacted


def test_in_prose_clinical_date_survives_by_default(redacted):
    """With REDACT_INPROSE_DATES False, a procedure date is clinical, not identity."""
    assert not deidentify.REDACT_INPROSE_DATES
    assert "Angiography on 06/06/2026" in redacted
    assert "the 2nd of June" in redacted
    assert "six weeks" in redacted
    assert "three months" in redacted


def test_identity_anchored_dates_are_still_redacted(redacted):
    """DOB and admission/discharge dates carry identity, so they go."""
    assert "12/03/1948" not in redacted
    assert "4 June 2026" not in redacted
    assert "21 July 2026" not in redacted


def test_no_clinical_acronym_became_an_entity(deid):
    """spaCy labels "ECG" and "NSTEMI" as organisations; the filter must drop them."""
    values = {e["value"].casefold() for e in deid.entities}
    for acronym in ("ecg", "nstemi", "lad", "st", "mi"):
        assert acronym not in values


def test_no_drug_name_became_an_entity(deid):
    values = {e["value"].casefold() for e in deid.entities}
    for drug in ("aspirin", "ticagrelor", "bisoprolol", "atorvastatin"):
        assert drug not in values


# ==========================================================================
# SAFETY SWEEP
# ==========================================================================

def test_residual_scan_is_empty_on_a_clean_document(redacted):
    assert deidentify.residual_scan(redacted) == []


def test_residual_scan_catches_a_leaked_structured_identifier(redacted):
    leaked = redacted + "\nContact the ward on 01632 960 188.\n"
    assert "01632 960 188" in deidentify.residual_scan(leaked)


def test_residual_scan_catches_a_leaked_name(redacted, ner_available):
    if not ner_available:
        pytest.skip("no spaCy model available")
    leaked = redacted + "\nPlease copy Dr Aoife O'Sullivan into the discharge letter.\n"
    findings = " ".join(deidentify.residual_scan(leaked))
    assert "O'Sullivan" in findings


def test_residual_scan_does_not_flag_placeholders(redacted):
    """Placeholders are the point of the exercise, not leaks."""
    findings = deidentify.residual_scan(redacted)
    assert not any(value.startswith("[") for value in findings)


def test_residual_scan_handles_empty_input():
    assert deidentify.residual_scan("") == []
    assert deidentify.residual_scan("   \n  ") == []


# ==========================================================================
# LAYERS
# ==========================================================================

def test_structured_layer_stands_alone(raw_text):
    """Layer 1 alone must still catch every purely structured identifier."""
    spans = deidentify.structured_spans(raw_text)
    found = {raw_text[s.start : s.end] for s in spans}
    assert "943 476 5919" in found
    assert "01632 960 188" in found
    assert "m.chen48@example.co.uk" in found
    assert "4471982" in found
    assert "14 Leeds Road, Harrogate, LS9 4TT" in found


def test_mrn_needs_a_label(raw_text):
    """A bare digit run is a lab value; only a labelled one is a record number."""
    labelled = deidentify.structured_spans("Hospital No: 4471982")
    assert any(s.entity_type == "MRN" for s in labelled)
    unlabelled = deidentify.structured_spans("Platelets were 4471982 at review.")
    assert not any(s.entity_type == "MRN" for s in unlabelled)


def test_ner_layer_finds_a_name_mid_paragraph(raw_text, ner_available):
    """The layer that exists specifically to catch an unlabelled name in prose."""
    if not ner_available:
        pytest.skip("no spaCy model available")
    spans = deidentify.ner_spans(raw_text)
    persons = {raw_text[s.start : s.end] for s in spans if s.entity_type == "PERSON"}
    assert any("Docherty" in value for value in persons)


def test_gliner_layer_degrades_silently(raw_text):
    """Layer 3 is optional: absent or present, it returns a list and never raises."""
    assert isinstance(deidentify.gliner_spans(raw_text), list)


def test_pipeline_runs_without_ner(raw_text, monkeypatch):
    """With no spaCy model, layer 1 must still protect the document."""
    monkeypatch.setattr(deidentify, "USE_NER", False)
    monkeypatch.setattr(deidentify, "USE_GLINER", False)
    result = deidentify.deidentify(raw_text)
    assert "943 476 5919" not in result.redacted_text
    assert "m.chen48@example.co.uk" not in result.redacted_text
    assert "Riverside Medical Practice" not in result.redacted_text


# ==========================================================================
# VARIANT EXPANSION
# ==========================================================================

def test_expand_name_variants_covers_the_forms_the_document_uses():
    variants = mapping.expand_name_variants("Margaret Elizabeth Chen", known_as="Peggy")
    for form in ("Margaret Elizabeth Chen", "Margaret Chen", "Chen", "Margaret",
                 "Mrs Chen", "Dr. Chen", "MEC", "M.E.C.", "M.C.", "Peggy"):
        assert form in variants, form


def test_expand_name_variants_never_emits_a_bare_title():
    """"Dr" as a standalone form would redact every "Dr" in the document."""
    variants = mapping.expand_name_variants("Dr Patel")
    assert "Dr" not in variants
    assert "Patel" in variants


def test_expand_org_variants_strips_trailing_type_words():
    assert "St. Aidan's" in mapping.expand_org_variants("St. Aidan's General Hospital")
    assert "Riverside" in mapping.expand_org_variants("Riverside Medical Practice")
    assert "Beechwood" in mapping.expand_org_variants("Beechwood Surgery")
    assert "Northfield" in mapping.expand_org_variants("Northfield NHS Trust")
    assert "Elmside" in mapping.expand_org_variants("Elmside Clinic")


def test_matcher_tolerates_a_line_break():
    """Form tokens are joined with \\s+, so a name split across lines still matches."""
    text = "Seen by Margaret\nChen today."
    entities = [{"type": "PATIENT_NAME", "value": "Margaret Chen", "placeholder": "[PATIENT]"}]
    assert mapping.redact(text, entities) == "Seen by [PATIENT] today."


def test_matcher_does_not_fire_inside_a_longer_word():
    text = "Braiden was reviewed."
    entities = [{"type": "PERSON", "value": "Aiden", "placeholder": "[PERSON]"}]
    assert mapping.redact(text, entities) == text


def test_longest_match_wins_on_overlap():
    text = "Contact David Chen about this."
    entities = [
        {"type": "PERSON", "value": "Chen", "placeholder": "[P1]"},
        {"type": "RELATIVE_NAME", "value": "David Chen", "placeholder": "[RELATIVE]"},
    ]
    assert mapping.redact(text, entities) == "Contact [RELATIVE] about this."


# ==========================================================================
# PLACEHOLDERS AND THE REVIEW TABLE
# ==========================================================================

def test_same_value_gets_the_same_placeholder_everywhere(deid, redacted):
    """One real value, one placeholder — the whole point of the mapping."""
    for entity in deid.entities:
        assert entity["placeholder"], entity
    placeholders = [e["placeholder"] for e in deid.entities]
    assert len(placeholders) == len(set(placeholders))


def test_placeholder_stems_are_the_expected_ones(deid):
    by_type = {e["type"]: e["placeholder"] for e in deid.entities}
    assert by_type["PATIENT_NAME"] == "[PATIENT]"
    assert by_type["NHS_NUMBER"] == "[NHS_NO]"
    assert by_type["MRN"] == "[MRN]"
    assert by_type["RELATIVE_NAME"].startswith("[RELATIVE")
    assert by_type["PROVIDER_NAME"].startswith("[CLINICIAN")
    assert by_type["FACILITY"].startswith("[CLINIC")


def test_relative_is_typed_from_the_kinship_marker(deid):
    david = [e for e in deid.entities if e["value"] == "David Chen"]
    assert david and david[0]["type"] == "RELATIVE_NAME"


def test_clinicians_are_typed_from_their_title(deid):
    clinicians = {e["value"] for e in deid.entities if e["type"] == "PROVIDER_NAME"}
    assert clinicians == {"Aoife O'Sullivan", "Fiona Docherty", "Raj Patel"}


def test_keep_action_leaves_the_text_alone(raw_text, deid):
    """Marking a row Keep must un-redact exactly that value and nothing else."""
    entities = [dict(e) for e in deid.entities]
    for entity in entities:
        if entity["type"] == "FACILITY" and "Riverside" in entity["value"]:
            entity["action"] = mapping.KEEP
    result = deidentify.rebuild(raw_text, entities)
    assert "Riverside Medical Practice" in result.redacted_text
    assert "943 476 5919" not in result.redacted_text
    assert not any(p.startswith("[CLINIC") and "Riverside" in v
                   for p, v in result.phi_map.items())


def test_add_manual_entity_expands_variants(raw_text, deid):
    """A value the layers missed is expanded like a detected one."""
    entities = [e for e in deid.entities if "O'Sullivan" not in e["value"]]
    partial = deidentify.rebuild(raw_text, entities)
    assert "O'Sullivan" in partial.redacted_text

    result = deidentify.add_manual_entity(
        raw_text, entities, "Aoife O'Sullivan", "PROVIDER_NAME"
    )
    assert "O'Sullivan" not in result.redacted_text  # incl. the "Dr O'Sullivan" form


def test_add_manual_entity_refuses_a_dangerously_short_value(raw_text, deid):
    with pytest.raises(deidentify.DeidentificationError):
        deidentify.add_manual_entity(raw_text, deid.entities, "a", "OTHER_ID")


def test_add_manual_entity_refuses_a_duplicate(raw_text, deid):
    with pytest.raises(deidentify.DeidentificationError):
        deidentify.add_manual_entity(
            raw_text, deid.entities, "Margaret Elizabeth Chen", "PATIENT_NAME"
        )


def test_a_structured_regex_hit_is_auto_confidence():
    """An NHS number is Layer 1 (regex) — pattern-certain, no review needed."""
    text = "NHS number: 943 476 5919"
    entities = deidentify.analyze(text)
    nhs = next(e for e in entities if e["type"] == "NHS_NUMBER")
    assert nhs["confidence"] == "auto"


def test_a_single_layer_ner_only_hit_needs_review():
    """A bare forename with no structural corroboration is single-layer."""
    text = "Zephyrine mentioned she felt better today."
    entities = deidentify.analyze(text)
    person = next(
        (e for e in entities if e["type"] in ("PATIENT_NAME", "PERSON")), None
    )
    assert person is not None
    assert person["confidence"] == "review"


def test_two_layers_agreeing_is_auto_confidence():
    """GLiNER and Presidio/spaCy both firing on the same span is corroboration."""
    try:
        import gliner  # noqa: F401
    except ImportError:
        pytest.skip("requires the gliner package to be installed")
    text = "The patient, Margaret Elizabeth Chen, was reviewed today."
    entities = deidentify.analyze(text)
    person = next(e for e in entities if "Chen" in e["value"])
    assert person["confidence"] == "auto"


def test_a_manually_added_entity_is_auto_confidence():
    """The add action IS the human decision — no second click to confirm it."""
    text = "Seen by the coordinator, Zaphod, today."
    result = deidentify.add_manual_entity(text, [], "Zaphod")
    entity = next(e for e in result.entities if e["value"] == "Zaphod")
    assert entity["confidence"] == "auto"


def test_rebuild_preserves_a_reviewer_edited_placeholder(raw_text, deid):
    entities = [dict(e) for e in deid.entities]
    entities[0]["placeholder"] = "[CUSTOM_1]"
    result = deidentify.rebuild(raw_text, entities)
    assert result.entities[0]["placeholder"] == "[CUSTOM_1]"
    assert "[CUSTOM_1]" in result.redacted_text


def test_rebuild_does_not_resurrect_deleted_rows(raw_text, deid):
    """A false positive the reviewer deleted must stay deleted."""
    entities = [e for e in deid.entities if e["type"] != "FACILITY"]
    result = deidentify.rebuild(raw_text, entities)
    assert "Riverside Medical Practice" in result.redacted_text
    assert not any(e["type"] == "FACILITY" for e in result.entities)


# ==========================================================================
# GUARDS
# ==========================================================================

def test_empty_document_is_rejected():
    with pytest.raises(deidentify.DeidentificationError):
        deidentify.deidentify("   \n  ")


def test_analyze_returns_nothing_for_empty_text():
    assert deidentify.analyze("") == []


def test_crlf_and_lf_documents_behave_identically(raw_text):
    """A .txt file read off a Windows disk arrives with CRLF endings.

    NER tokenises CRLF text slightly differently, which once caused "St. Aidan's"
    to come back as a PERSON — and person expansion then derived a standalone
    "St" that redacted "ST depression". Both guarantees are asserted here.
    """
    crlf = deidentify.deidentify(raw_text.replace("\n", "\r\n")).redacted_text
    lf = deidentify.deidentify(raw_text).redacted_text

    assert crlf.replace("\r\n", "\n") == lf
    assert "ST depression" in crlf
    assert "St. Aidan's" not in crlf
    assert deidentify.residual_scan(crlf) == []


def test_abbreviated_token_is_not_a_standalone_name_form():
    """"St." must never become a bare "St" that matches clinical text."""
    variants = mapping.expand_name_variants("St. Aidan's")
    assert "St" not in variants
    assert "St." not in variants


def test_pipeline_is_deterministic(raw_text):
    """Two runs over the same text must agree, or review is meaningless."""
    first = deidentify.deidentify(raw_text)
    second = deidentify.deidentify(raw_text)
    assert first.redacted_text == second.redacted_text
    assert first.entities == second.entities


def test_the_identity_map_is_returned_not_stored(deid):
    """The map is a return value the caller holds; nothing module-level keeps it."""
    assert deid.phi_map
    assert deid.phi_map["[PATIENT]"] == "Margaret Elizabeth Chen"
    assert all(value not in deid.redacted_text for value in deid.phi_map.values())
