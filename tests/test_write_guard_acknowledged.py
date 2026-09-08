"""
The `acknowledged` override on the write guard, pinned down.

`write_approved` refuses any text that still scans as identifying. The
`acknowledged` list is a deliberate, per-string reviewer override for strings
that only look like identifiers — not a switch that turns the guard off.
Nothing partial, empty or wildcard-shaped can stand in for naming each string
exactly, and the tests below exist so that boundary cannot widen by accident.

Everything here is fabricated.
"""

import pytest

from carescribe.core import batch

NAME, MRN, NHS = "Wilhelmina Featherstonehaugh", "ZZ9987654", "943 476 5919"
POSTCODE, EMAIL = "BL1 4AB", "jane@nhs.net"
RAW = (
    f"Patient: {NAME}\nMRN: {MRN}\nNHS: {NHS}\n"
    f"Postcode {POSTCODE}\nEmail {EMAIL}\n"
)
EVERYTHING = [NAME, MRN, NHS, POSTCODE, EMAIL]


def test_raw_text_is_refused_without_any_acknowledgement(tmp_path):
    with pytest.raises(batch.BatchError) as excinfo:
        batch.write_approved("a.txt", RAW, output_dir=tmp_path)

    message = str(excinfo.value)
    assert "Refusing to write" in message
    assert NAME in message
    assert list(tmp_path.iterdir()) == []


def test_partial_acknowledgement_still_refuses(tmp_path):
    with pytest.raises(batch.BatchError) as excinfo:
        batch.write_approved(
            "a.txt", RAW, acknowledged=[NHS], output_dir=tmp_path
        )

    message = str(excinfo.value)
    assert "Refusing to write" in message
    assert NAME in message
    assert MRN in message
    assert NHS not in message
    assert list(tmp_path.iterdir()) == []


def test_no_wildcard_acknowledgement(tmp_path):
    with pytest.raises(batch.BatchError) as excinfo:
        batch.write_approved(
            "a.txt", RAW, acknowledged=["*"], output_dir=tmp_path
        )

    assert "Refusing to write" in str(excinfo.value)
    assert list(tmp_path.iterdir()) == []


def test_empty_acknowledgement_acknowledges_nothing(tmp_path):
    with pytest.raises(batch.BatchError) as excinfo:
        batch.write_approved(
            "a.txt", RAW, acknowledged=["", " "], output_dir=tmp_path
        )

    assert "Refusing to write" in str(excinfo.value)
    assert list(tmp_path.iterdir()) == []


def test_naming_every_identifier_is_the_one_deliberate_override(tmp_path):
    path = batch.write_approved(
        "a.txt", RAW, acknowledged=EVERYTHING, output_dir=tmp_path
    )

    assert path == tmp_path / "a.deid.txt"
    assert path.exists()
    assert RAW in path.read_text(encoding="utf-8")


def test_properly_deidentified_text_writes_without_override(tmp_path):
    path = batch.write_approved("a.txt", "[PATIENT] is stable.", output_dir=tmp_path)

    assert path == tmp_path / "a.deid.txt"
    assert path.exists()
    assert "[PATIENT] is stable." in path.read_text(encoding="utf-8")
