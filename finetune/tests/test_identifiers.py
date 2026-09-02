"""Injected identifiers must look real, sit at the right offsets, be repeatable."""

from __future__ import annotations

import random

from finetune.datagen.identifiers import Placed, inject, nhs_number, strip_answer_key


def _check_digit_ok(formatted: str) -> bool:
    d = [int(c) for c in formatted if c.isdigit()]
    assert len(d) == 10
    total = sum(x * w for x, w in zip(d[:9], range(10, 1, -1)))
    check = 11 - (total % 11)
    check = 0 if check == 11 else check
    return check == d[9]


def test_nhs_number_shape_and_check_digit():
    for seed in range(20):
        n = nhs_number(random.Random(seed))
        assert len(n) == 12 and n[3] == " " and n[7] == " "
        assert _check_digit_ok(n)


def test_slots_are_filled_and_offsets_are_exact():
    text = "Patient [[NAME]] seen, DOB [[dob]], NHS [[NHS]], ring [[phone]]."
    out, placed = inject(text, seed=7)
    assert "[[" not in out
    assert {p.kind for p in placed} == {"name", "dob", "nhs_number", "phone"}
    for p in placed:
        assert out[p.start : p.end] == p.value


def test_no_tokens_appends_an_admin_block():
    out, placed = inject("A short clinical note with no slots.", seed=3)
    assert "Administrative details" in out
    assert len(placed) >= 4
    for p in placed:
        assert out[p.start : p.end] == p.value
    assert any(p.kind == "nhs_number" for p in placed)


def test_injection_is_deterministic():
    text = "Seen by [[PROVIDER]] on [[DATE]] at [[POSTCODE]]."
    assert inject(text, seed=11) == inject(text, seed=11)
    assert inject(text, seed=11) != inject(text, seed=12)


def test_strip_answer_key_dedupes_in_order():
    placed = [
        Placed("name", "A B", 0, 3),
        Placed("name", "A B", 10, 13),
        Placed("dob", "1 May 1970", 20, 30),
    ]
    assert strip_answer_key(placed) == ["A B", "1 May 1970"]
