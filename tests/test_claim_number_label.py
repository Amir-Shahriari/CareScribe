from unittest import mock

from carescribe.core import deidentify as D


def deid_rules_only(text):
    """De-identify with no NER model — the supported no-spaCy machine."""
    with mock.patch.object(D, "get_analyzer", return_value=None):
        return D.deidentify(text).redacted_text


def test_bare_claim_without_no_or_number():
    """The Cc-line form "(claim WC-2025-118342)" is anchored."""
    out = deid_rules_only(
        "Cc: Marcus Delaney, Statewide Workers Insurance (claim WC-2025-118342)"
    )
    assert "WC-2025-118342" not in out
    assert "[MRN]" in out


def test_claim_number_label_still_works():
    """The labelled form is unchanged."""
    assert "WC-2025-118342" not in deid_rules_only("Claim number: WC-2025-118342")


def test_claim_no_label_still_works():
    """The abbreviated label is unchanged."""
    assert "WC-2025-118342" not in deid_rules_only("Claim No: WC-2025-118342")


def test_bare_claim_in_prose_is_not_an_anchor():
    """Without a digit-shaped value there is nothing to take."""
    for line in (
        "The claim was denied.",
        "Her claim remains open.",
        "He submitted a claim last year.",
    ):
        assert deid_rules_only(line) == line


def test_neighbouring_labels_still_work():
    """Accession, Clinic file and UR No are untouched by this change."""
    assert "RAD-2025-77120" not in deid_rules_only("Accession number: RAD-2025-77120")
    assert "CPC-4471" not in deid_rules_only("Clinic file: CPC-4471")
    assert "4471982" not in deid_rules_only("UR No: 4471982")
