"""RELATIVE_LINE must keep matching when a relationship, phone or age
follows the name -- the old "$" anchor only matched a bare "Label: Name".
"""

from unittest import mock

from carescribe.core import deidentify as D


def deid_rules_only(text):
    """De-identify with no NER model -- the supported no-spaCy machine."""
    with mock.patch.object(D, "get_analyzer", return_value=None):
        return D.deidentify(text).redacted_text


def test_no_false_positives_on_unlabelled_text():
    """Lines that are not a labelled field naming a person pass through unchanged."""
    for line in (
        "Next of kin details were not recorded.",
        "The carer reported increased strain.",
    ):
        assert deid_rules_only(line) == line


def test_sample_document_shape_next_of_kin():
    """This exact line appears in sample_documents/01_gp_referral_letter.docx and the name leaked."""
    text = "Next of kin: Priya Whitfield (spouse) — 0433 990 214"
    assert "Priya Whitfield" not in deid_rules_only(text)


def test_people_who_can_help_shape():
    """The strengths-based phrasing names the same spouse with the same trailing detail."""
    text = "People who can help: Priya Whitfield (spouse) — 0433 990 214"
    assert "Priya Whitfield" not in deid_rules_only(text)


def test_nok_with_bracketed_relationship():
    """A NOK line with a bracketed relationship still redacts the name."""
    text = "NOK: Sarah Blake (wife)"
    assert "Sarah Blake" not in deid_rules_only(text)


def test_emergency_contact_with_phone():
    """An emergency contact followed by a phone number (ASCII hyphen) still redacts."""
    text = "Emergency contact: Sarah Blake - 0412 345 678"
    assert "Sarah Blake" not in deid_rules_only(text)


def test_next_of_kin_with_trailing_age():
    """A trailing comma-separated age after the name still redacts."""
    text = "Next of kin: Priya Whitfield, 38"
    assert "Priya Whitfield" not in deid_rules_only(text)


def test_carer_with_bracketed_relationship():
    """A carer line with a bracketed relationship still redacts the name."""
    text = "Carer: Denise Whitfield (mother)"
    assert "Denise Whitfield" not in deid_rules_only(text)


def test_bare_shapes_still_work():
    """The bare "Label: Name" shapes that always worked still redact, unchanged."""
    for text in (
        "Next of kin: Priya Whitfield",
        "Wife: Sarah Blake",
    ):
        assert "Priya Whitfield" not in deid_rules_only(text)
        assert "Sarah Blake" not in deid_rules_only(text)
