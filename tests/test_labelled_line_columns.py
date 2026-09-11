"""Labelled name fields separated from the next field by whitespace only.

`Name: Jonathan Blake   DOB: 26 July 1996` is an ordinary letterhead line, and
before this fix it matched none of the value terminators — so the DOB and the
NHS number beside it were redacted while the patient's own name rode out.
Measured rules-only over these shapes, the three rules caught 7 of 17.

Every case runs with `get_analyzer` patched to `None`. That is the supported
state of a machine with no spaCy model, and it is the only way to see a hole in
the regex layer: with the model loaded, NER covers these and the suite stays
green over the gap.
"""

from unittest import mock

import pytest

from carescribe.core import deidentify

NAME = "Jonathan Blake"
KIN = "Priya Whitfield"


def rules_only(text):
    """De-identify with the analyzer forced off."""
    with mock.patch.object(deidentify, "get_analyzer", return_value=None):
        return deidentify.deidentify(text).redacted_text


# (line, value that must not survive) — the shapes the old terminator missed.
COLUMN_SHAPES = [
    (f"Name: {NAME}   DOB: 26 July 1996   NHS: 186 085 6845", NAME),
    (f"Patient: {NAME}   DOB: 26 July 1996", NAME),
    (f"Patient:  {NAME}\tDOB: 26/07/1996", NAME),
    (f"Full name: {NAME}   MRN: 9894263", NAME),
    (f"Worker: {NAME}   Claim No: 22/1234", NAME),
    (f"Client name: {NAME}     Ward: Ashdown", NAME),
    (f"NOK: {KIN}   Relationship: wife", KIN),
    (f"Emergency contact: {KIN}   Phone: 0433 990 214", KIN),
    (f"Carer: {KIN}  |  0433 990 214", KIN),
    (f"Re: {NAME}   DOB: 26 July 1996", NAME),
    (f"Re: Mr {NAME}, DOB 26/07/1996", NAME),
]

# Shapes that already worked — they must keep working.
ALREADY_HELD = [
    (f"Patient: {NAME}", NAME),
    (f"Client: {NAME} (DOB 12/04/1985, Medicare 2934 5671 0)", NAME),
    (f"Patient: {NAME}  |  DOB 12/04/1985  |  Medicare 2934 5671 0", NAME),
    (f"Name: {NAME}, DOB: 26 July 1996", NAME),
    (f"Next of kin: {KIN} (spouse) - 0433 990 214", KIN),
    (f"Re: Mr {NAME}", NAME),
]

# Clinical text that must survive. A widened rule shows up here first.
MUST_PRESERVE = [
    ("Drug name: Sertraline", "Sertraline"),
    ("File name: report.docx", "report.docx"),
    ("Re: medication review", "medication review"),
    ("Referral for medication review", "medication review"),
    ("Impression: Stable angina   Plan: CT coronary angiography",
     "CT coronary angiography"),
    ("Plan: Increase Sertraline to 100mg OD   Review: 3 weeks",
     "Increase Sertraline"),
    ("Diagnosis: Chronic Obstructive Pulmonary Disease",
     "Chronic Obstructive Pulmonary Disease"),
    ("Allergies: Penicillin   Reaction: rash", "Penicillin"),
]


@pytest.mark.parametrize("line,value", COLUMN_SHAPES, ids=lambda v: str(v)[:40])
def test_a_name_in_a_whitespace_column_is_redacted(line, value):
    assert value not in rules_only(line)


@pytest.mark.parametrize("line,value", ALREADY_HELD, ids=lambda v: str(v)[:40])
def test_the_shapes_that_already_worked_still_work(line, value):
    assert value not in rules_only(line)


@pytest.mark.parametrize("line,value", MUST_PRESERVE, ids=lambda v: str(v)[:40])
def test_clinical_text_is_not_over_redacted(line, value):
    assert value in rules_only(line)


def test_the_neighbouring_field_is_still_redacted_too():
    """The DOB was never the problem — check the fix did not cost it."""
    out = rules_only(f"Name: {NAME}   DOB: 26 July 1996   NHS: 186 085 6845")
    assert NAME not in out
    assert "26 July 1996" not in out
    assert "186 085 6845" not in out


def test_a_double_space_ends_the_value_rather_than_sitting_inside_a_name():
    """Two spaces are a column gap, deliberately, even mid-value.

    The alternative was letting a name span a run of whitespace, and that made
    `Worker: Jonathan Blake   Claim No: 22/1234` capture "Jonathan Blake   Claim"
    — swallowing the next field's label into the placeholder. A form separates
    fields with a column gap; a person does not spell their own name with one.
    So "Jonathan" is taken here and "Blake" is not, and that is the intended
    reading of an ambiguous line.
    """
    out = rules_only("Patient: Jonathan  Blake")
    assert "Jonathan" not in out
    assert "Blake" in out


def test_a_name_the_rule_cannot_bound_is_left_whole_not_half_redacted():
    """Four tokens is the cap `_trim_span` also enforces. Past it, take none.

    Redacting the part that fits leaves the real surname beside a placeholder —
    `Patient: [PATIENT] Windsor` — which reads as handled and so survives
    review. A name left plainly in the clear does not.
    """
    out = rules_only("Patient: Jonathan James Alexander Blake Windsor  DOB: 26/07/1996")
    assert "[PATIENT] Windsor" not in out
    assert "Jonathan James Alexander Blake Windsor" in out
    assert "26/07/1996" not in out  # the rest of the line still redacts


PLACEHOLDER_VALUES = [
    ("Patient: Unknown  Status: Discharged", "Unknown"),
    ("Carer: Self  Phone: 0433 990 214", "Self"),
    ("Next of kin: Deceased  Updated: 12/04/2024", "Deceased"),
    ("Name: See Above  DOB: 26/07/1996", "See Above"),
    ("Worker: Injured  Status: Open", "Injured"),
    ("Client: Active  Status: Reviewed", "Active"),
    ("Full name: Not Provided  DOB: 26 July 1996", "Not Provided"),
    ("Next of kin: Not Applicable  Phone: N/A", "Not Applicable"),
    ("Worker: Case Manager  Status: Active", "Case Manager"),
]


@pytest.mark.parametrize("line,value", PLACEHOLDER_VALUES, ids=lambda v: str(v)[:40])
def test_a_field_holding_no_name_is_not_redacted(line, value):
    """What real forms put in an identity field when there is no name.

    None of these matched before the terminator was widened — the line had to
    END at the value, and these lines do not. They are clinical content:
    "Next of kin: Deceased" is a fact, and "Worker: Case Manager" a role.
    """
    assert value in rules_only(line)


def test_one_bad_match_does_not_rewrite_the_whole_document():
    """`mapping.redact` replaces every occurrence of a matched value.

    So redacting "Unknown" in a header once rewrote every other "unknown" in the
    note — turning "cause of fall unknown" into "[PATIENT]".
    """
    out = rules_only(
        "Patient: Unknown  DOB: 26/07/1996\n"
        "History: Found collapsed, cause of fall unknown.\n"
        "Known allergies: Unknown."
    )
    assert "cause of fall unknown" in out
    assert out.count("Unknown") == 2
    assert "26/07/1996" not in out


def test_the_label_must_still_start_the_line():
    """A bare `Name` label is only safe because it is line-anchored."""
    assert "Sertraline" in rules_only("Drug name: Sertraline   Dose: 50mg")
