"""
`EncounterFacts` -> a realistic, messy clinician note (the INPUT side of a pair).

Deterministic and model-free: it stitches the facts into prose with surface
variation chosen by a seeded RNG. Two axes:

* **style**  — ``terse`` ward note · ``letter`` dictated referral · ``proforma``
  headed template · ``prose`` near-continuous paragraph.
* **noise**  — inconsistent casing, dropped headers, run-together lines,
  OCR-ish substitutions — sampled per note.

Identifier slots (``[[NAME]]``, ``[[DOB]]``, ``[[DATE]]``, ``[[NHS]]``,
``[[MRN]]``, ``[[PROVIDER]]``) are left as literal tokens for
``identifiers.inject`` to fill; that keeps this module free of any fake-PHI
dependency.

An optional model polish (`generator_backend`) can rewrite the result for
fluency — the caller re-validates and keeps the scaffold if polish drifts.
"""

from __future__ import annotations

import random

from finetune.datagen.schema import EncounterFacts

STYLES = ("terse", "letter", "proforma", "prose")


def _med(m) -> str:
    return " ".join(x for x in (m.name, m.dose or "", m.frequency or "") if x).strip()


def _lines(facts: EncounterFacts) -> list[tuple[str, list[str]]]:
    """(section label, lines) in a fixed clinical order, skipping empty sections."""
    out: list[tuple[str, list[str]]] = []
    out.append(("Presenting complaint", [facts.presenting_complaint]))
    if facts.history:
        out.append(
            ("History", [f"{h.label} — {h.detail}" if h.detail else h.label for h in facts.history])
        )
    if facts.pmh:
        out.append(("Past history", list(facts.pmh)))
    if facts.meds:
        out.append(("Medications", [_med(m) for m in facts.meds]))
    if facts.allergies:
        out.append(("Allergies", list(facts.allergies)))
    if facts.examination:
        out.append(
            ("Examination", [f"{f.system}: {f.finding}" + (f" {f.value}" if f.value else "") for f in facts.examination])
        )
    if facts.investigations:
        out.append(
            ("Investigations", [f"{r.test} {r.value}" + (f" [{r.flag}]" if r.flag else "") for r in facts.investigations])
        )
    if facts.impression:
        out.append(("Impression", list(facts.impression)))
    if facts.plan:
        out.append(("Plan", [f"{p.action}: {p.detail}" if p.detail else p.action for p in facts.plan]))
    if facts.follow_up:
        out.append(("Follow-up", [facts.follow_up]))
    return out


def _degrade(text: str, rng: random.Random) -> str:
    """A little OCR/casing/spacing noise, sampled."""
    if rng.random() < 0.35:
        text = text.replace(". ", ".  ")
    if rng.random() < 0.25:
        text = text.replace(" — ", " - ")
    if rng.random() < 0.15:
        # lower-case some lines, but never one carrying an identifier slot —
        # those tokens must survive verbatim for identifiers.inject to fill.
        text = "\n".join(
            ln.lower() if (rng.random() < 0.3 and "[[" not in ln) else ln
            for ln in text.splitlines()
        )
    if rng.random() < 0.1:
        text = text.replace("0", "O", 1)
    return text


def _header(rng: random.Random) -> str:
    bits = [
        f"Name: [[NAME]]   DOB: [[DOB]]   NHS: [[NHS]]",
        f"Date: [[DATE]]   MRN: [[MRN]]",
        f"Seen by: [[PROVIDER]]",
    ]
    rng.shuffle(bits)
    return "\n".join(bits)


def render(facts: EncounterFacts, *, style: str | None = None, seed: int = 0) -> str:
    """Render one messy source note. Deterministic for a given ``seed``."""
    rng = random.Random(seed)
    style = style or rng.choice(STYLES)
    sections = _lines(facts)

    if style == "terse":
        body = "\n".join(
            f"{label}: " + "; ".join(lines) for label, lines in sections
        )
    elif style == "proforma":
        body = "\n\n".join(
            f"{label.upper()}\n" + "\n".join(f"  - {ln}" for ln in lines)
            for label, lines in sections
        )
    elif style == "letter":
        para = " ".join(
            f"{label}: " + "; ".join(lines) + "." for label, lines in sections
        )
        body = f"Dear Colleague,\n\n{para}\n\nWith best wishes,\n[[PROVIDER]]"
    else:  # prose
        body = " ".join(
            "; ".join(lines).rstrip(".") + "." for _label, lines in sections
        )

    note = f"{_header(rng)}\n\n{body}" if style != "letter" else f"{_header(rng)}\n\n{body}"
    return _degrade(note, rng)


__all__ = ["STYLES", "render"]
