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


def test_a_name_containing_a_double_space_is_taken_in_full():
    """The column-gap terminator must not truncate the value it is bounding."""
    assert "Blake" not in rules_only("Patient: Jonathan  Blake")


def test_the_label_must_still_start_the_line():
    """A bare `Name` label is only safe because it is line-anchored."""
    assert "Sertraline" in rules_only("Drug name: Sertraline   Dose: 50mg")
