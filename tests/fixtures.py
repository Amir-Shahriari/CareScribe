"""
Synthetic test data for the de-identification regression suite.

EVERYTHING HERE IS FABRICATED. No real patient, clinician, facility, NHS
number, address, or telephone number appears in it. The names, identifiers, and
clinical details were invented to exercise the redaction logic. The phone number
uses Ofcom's 01632 960xxx drama range and the email uses example.co.uk, both
reserved for fiction.

The document lives in ``synthetic_patient_discharge_summary.txt`` next to this
file. Line breaks in it are load-bearing — "Margaret\\nChen" is the regression
target for the whitespace-tolerant matcher, so do not reflow it.
"""

from pathlib import Path

FIXTURE_PATH = Path(__file__).resolve().parent / "synthetic_patient_discharge_summary.txt"

DISCHARGE_SUMMARY = FIXTURE_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# RECALL — none of these may survive de-identification.
# ---------------------------------------------------------------------------
MUST_NOT_SURVIVE = [
    "943 476 5919",                # NHS number — structured regex layer
    "Mrs Chen",                    # title + surname in prose — name variant
    "Margaret\nChen",              # name split across a line break — \s+ matcher
    "M.E.C.",                      # initials — name variant
    "David Chen",                  # relative's name — own entity
    "Dr O'Sullivan",               # clinician short form — name variant
    "Sister Docherty",             # clinician short form — name variant
    "Dr Patel",                    # clinician short form — name variant
    "01632 960 188",               # loose in-prose phone — structured regex layer
    "St. Aidan's",                 # facility short form — org variant
    "Riverside Medical Practice",  # facility — NER layer
]

# Extra identifiers the layered pipeline is expected to catch. Kept separate
# from the list above so a failure says which guarantee broke.
ALSO_MUST_NOT_SURVIVE = [
    "4471982",                     # hospital number — context-anchored MRN
    "m.chen48@example.co.uk",      # email
    "LS9 4TT",                     # postcode
    "14 Leeds Road",               # street address
    "12/03/1948",                  # DOB — identity-anchored date
    "Peggy",                       # "Known as" alias
    "Margaret Elizabeth Chen",     # full patient name
    "Aoife O'Sullivan",            # clinician full name
]

# ---------------------------------------------------------------------------
# PRECISION — these must be PRESERVED. Over-redaction damages the document's
# clinical meaning, which is a worse failure than an untidy redaction.
# ---------------------------------------------------------------------------

# "Leeds" as a place of care / where she visited family, not as an address.
# It also appears inside "14 Leeds Road", which IS redacted — the standalone
# mention is the one that must survive.
PRESERVED_PLACES = ["Leeds"]

PRESERVED_DOSAGES = ["Aspirin 75mg", "Ticagrelor 90mg", "Bisoprolol 2.5mg", "Atorvastatin 80mg"]

PRESERVED_CLINICAL = [
    "LAD", "NSTEMI", "ECG", "ST depression", "troponin", "stent", "chest pain",
    "drug-eluting", "stenosis", "anterior leads", "nocte", "once daily",
]

MUST_SURVIVE = PRESERVED_PLACES + PRESERVED_DOSAGES + PRESERVED_CLINICAL
