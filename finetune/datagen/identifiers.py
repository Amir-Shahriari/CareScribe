"""
Inject realistic-looking **fake** UK identifiers into a rendered note.

Nothing here is real. Names come from small built-in word lists, NHS numbers
carry a valid mod-11 check digit, dates and postcodes are plausible but random.
The point is only that the CareScribe de-identifier has something shaped like
PHI to catch on the round trip:

    render note (with [[TOKEN]] slots)  ->  INJECT HERE  ->  real de-id  ->  train

Pure standard library, deterministic for a given ``seed``.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass

_FIRST = [
    "Aisha", "Mohammed", "Grace", "Oliver", "Priya", "Wei", "Tomas", "Amara",
    "Jack", "Sofia", "Ravi", "Chloe", "Ade", "Noor", "Liam", "Yuki", "Hassan",
    "Freya", "Kwame", "Elena", "Sam", "Jordan", "Maryam", "George", "Ingrid",
]
_LAST = [
    "Whitfield", "Okafor", "Nasser", "Brandt", "Ilic", "Mercer", "Doyle",
    "Patel", "O'Brien", "Zhang", "Kowalski", "Abebe", "Rahman", "Fletcher",
    "Nguyen", "Santos", "Bianchi", "Odedra", "Campbell", "Haddad",
]
_TITLES = ["Dr", "Mr", "Mrs", "Ms", "Miss", "Mx"]
_POSTCODE_AREAS = ["M", "BL", "OL", "SK", "WA", "PR", "L", "LS", "S", "B"]
_MONTHS = [
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
]

_KIND_TOKENS = {
    "[[NAME]]": "name",
    "[[DOB]]": "dob",
    "[[DATE]]": "date",
    "[[NHS]]": "nhs_number",
    "[[POSTCODE]]": "postcode",
    "[[MRN]]": "mrn",
    "[[PHONE]]": "phone",
    "[[PROVIDER]]": "provider",
}


@dataclass(frozen=True)
class Placed:
    kind: str
    value: str
    start: int
    end: int


def nhs_number(rng: random.Random) -> str:
    """A fake 10-digit NHS number, ``'NNN NNN NNNN'``, valid mod-11 check digit."""
    while True:
        digits = [rng.randint(0, 9) for _ in range(9)]
        total = sum(d * w for d, w in zip(digits, range(10, 1, -1)))
        check = 11 - (total % 11)
        if check == 11:
            check = 0
        if check == 10:
            continue  # invalid — regenerate
        digits.append(check)
        s = "".join(map(str, digits))
        return f"{s[:3]} {s[3:6]} {s[6:]}"


def _name(rng: random.Random) -> str:
    return f"{rng.choice(_FIRST)} {rng.choice(_LAST)}"


def _provider(rng: random.Random) -> str:
    return f"{rng.choice(_TITLES)} {rng.choice(_FIRST)[0]}. {rng.choice(_LAST)}"


def _dob(rng: random.Random) -> str:
    return f"{rng.randint(1, 28)} {rng.choice(_MONTHS)} {rng.randint(1938, 2013)}"


def _date(rng: random.Random) -> str:
    return f"{rng.randint(1, 28):02d}/{rng.randint(1, 12):02d}/{rng.randint(2023, 2026)}"


def _postcode(rng: random.Random) -> str:
    return (
        f"{rng.choice(_POSTCODE_AREAS)}{rng.randint(1, 30)} "
        f"{rng.randint(1, 9)}{rng.choice('ABDEFGHJLNPQRSTUWXYZ')}"
        f"{rng.choice('ABDEFGHJLNPQRSTUWXYZ')}"
    )


def _mrn(rng: random.Random) -> str:
    return f"{rng.randint(100000, 9999999)}"


def _phone(rng: random.Random) -> str:
    return f"07{rng.randint(100, 999)} {rng.randint(100000, 999999)}"


_GENERATORS = {
    "name": _name,
    "provider": _provider,
    "dob": _dob,
    "date": _date,
    "nhs_number": nhs_number,
    "postcode": _postcode,
    "mrn": _mrn,
    "phone": _phone,
}


def _make(kind: str, rng: random.Random) -> str:
    return _GENERATORS[kind](rng)


def _collect(text: str) -> list[Placed]:
    """Re-scan a finished string for the values placed in it (offsets included)."""
    # Not used directly; inject builds offsets as it goes. Kept for symmetry.
    return []


def inject(
    text: str, *, seed: int, n_names: int = 2, extra: int = 4
) -> tuple[str, list[Placed]]:
    """Fill ``[[TOKEN]]`` slots, or append an admin block if there are none.

    Returns the rewritten text and a list of :class:`Placed` sorted by offset,
    with ``text[p.start:p.end] == p.value``. Deterministic for a given ``seed``.
    """
    rng = random.Random(seed)

    token_re = re.compile("|".join(re.escape(t) for t in _KIND_TOKENS), re.IGNORECASE)
    if token_re.search(text):
        out: list[str] = []
        placed: list[Placed] = []
        pos = 0
        cursor = 0
        for m in token_re.finditer(text):
            kind = _KIND_TOKENS[m.group(0).upper()]
            value = _make(kind, rng)
            out.append(text[cursor:m.start()])
            pos += m.start() - cursor
            placed.append(Placed(kind, value, pos, pos + len(value)))
            out.append(value)
            pos += len(value)
            cursor = m.end()
        out.append(text[cursor:])
        return "".join(out), placed

    # No slots — append an administrative block so every note has PHI to catch.
    lines = ["", "Administrative details", "-" * 21]
    entries: list[tuple[str, str]] = []
    for _ in range(max(1, n_names)):
        entries.append(("name", _name(rng)))
    entries.append(("nhs_number", nhs_number(rng)))
    entries.append(("dob", _dob(rng)))
    pool = ["date", "postcode", "mrn", "phone", "provider"]
    for _ in range(max(0, extra)):
        kind = rng.choice(pool)
        entries.append((kind, _make(kind, rng)))

    labels = {
        "name": "Patient",
        "nhs_number": "NHS number",
        "dob": "Date of birth",
        "date": "Appointment",
        "postcode": "Postcode",
        "mrn": "Hospital number",
        "phone": "Contact",
        "provider": "Seen by",
    }
    base = text if text.endswith("\n") else text + "\n"
    placed: list[Placed] = []
    rendered = base + "\n".join(lines) + "\n"
    for kind, value in entries:
        line = f"{labels[kind]}: {value}"
        start = len(rendered) + len(f"{labels[kind]}: ")
        placed.append(Placed(kind, value, start, start + len(value)))
        rendered += line + "\n"

    return rendered, sorted(placed, key=lambda p: p.start)


def strip_answer_key(placed: list[Placed]) -> list[str]:
    """The placed values, deduped, order preserved."""
    seen: set[str] = set()
    out: list[str] = []
    for p in placed:
        if p.value not in seen:
            seen.add(p.value)
            out.append(p.value)
    return out


__all__ = ["Placed", "inject", "nhs_number", "strip_answer_key"]
