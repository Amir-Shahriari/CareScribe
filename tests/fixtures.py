"""
Synthetic test data for the de-identification regression suite.

EVERYTHING IN THIS FILE IS FABRICATED. No real patient, clinician, facility,
NHS number, address, or telephone number appears here. The names, identifiers,
and clinical details were invented to exercise the redaction logic. The phone
number uses Ofcom's 01632 960xxx drama range and the email uses example.co.uk,
both reserved for fiction.

The document deliberately contains every identifier form that leaked in the
reported test run, plus the clinical strings that must survive untouched.
"""

# Line breaks matter here: "Margaret\nChen" on lines 24-25 is a regression target
# for the whitespace-tolerant matcher. Do not reflow this string.
DISCHARGE_SUMMARY = """\
ST. AIDAN'S GENERAL HOSPITAL
Department of Cardiology — Discharge Summary

Patient:        Margaret Elizabeth Chen
Known as:       "Peggy"
DOB:            12/03/1948
NHS No:         943 476 5919
Hospital No:    4471982
Address:        14 Leeds Road, Harrogate, LS9 4TT
Telephone:      01632 960 188
Email:          m.chen48@example.co.uk
GP Practice:    Riverside Medical Practice

Admitted 4 June 2026 under Dr Aoife O'Sullivan (Consultant Cardiologist).
Discharged 21 July 2026.

HISTORY
Mrs Chen presented on the 2nd of June with central chest pain radiating to the
left arm. She had returned two days earlier from visiting family in Leeds.
ECG showed ST depression in the anterior leads and troponin was elevated. A
diagnosis of NSTEMI was made.

Angiography on 06/06/2026 demonstrated a 90% stenosis of the LAD. A drug-eluting
stent was deployed. Margaret
Chen tolerated the procedure well and Peggy was mobilising independently by day
three.

Dr O'Sullivan reviewed the angiogram. Sister Docherty confirmed the discharge
medication list, and Dr Patel countersigned the summary.

Nursing handover was completed by Sister Fiona Docherty. Follow-up bloods were
reviewed by Dr Raj Patel.

MEDICATION ON DISCHARGE
  Aspirin 75mg once daily
  Ticagrelor 90mg twice daily
  Bisoprolol 2.5mg once daily
  Atorvastatin 80mg nocte

NEXT OF KIN
  David Chen (son) — the ward can be reached on 01632 960 188.

The patient is referred to in earlier correspondence as M.E.C.
Follow-up at Riverside Medical Practice in six weeks; cardiology review at
St. Aidan's in three months.
"""

# What a competent local model returns for the document above. Note what it
# MISSES — the NHS number, hospital number, phone, postcode and email are all
# absent, which is exactly what the deterministic regex pass exists to catch.
LLM_ENTITIES = [
    {"type": "PATIENT_NAME", "value": "Margaret Elizabeth Chen"},
    {"type": "DOB", "value": "12/03/1948"},
    {"type": "ADDRESS", "value": "14 Leeds Road"},
    {"type": "ADDRESS", "value": "Harrogate"},
    {"type": "PROVIDER_NAME", "value": "Aoife O'Sullivan"},
    {"type": "PROVIDER_NAME", "value": "Fiona Docherty"},
    {"type": "PROVIDER_NAME", "value": "Raj Patel"},
    {"type": "FACILITY", "value": "St. Aidan's General Hospital"},
    {"type": "FACILITY", "value": "Riverside Medical Practice"},
    {"type": "PATIENT_NAME", "value": "David Chen"},
]

# Identifiers that leaked in the reported run. None may survive redaction.
MUST_NOT_SURVIVE = [
    "943 476 5919",              # NHS number — regex pass
    "Mrs Chen",                  # title + surname in prose — name variant
    "Margaret\nChen",            # name split across a line break — \s+ matcher
    "M.E.C.",                    # initials — name variant
    "David Chen",                # relative's name — own entity, longest-span wins
    "Dr O'Sullivan",             # provider short form — name variant
    "Sister Docherty",           # provider short form — name variant
    "Dr Patel",                  # provider short form — name variant
    "01632 960 188",             # loose in-prose phone — regex pass
    "St. Aidan's",               # facility short form — facility variant
    "Riverside Medical Practice",  # facility — LLM entity
]

# Clinical content that must survive intact. Over-redaction here would damage
# the note's meaning, which is worse than an untidy redaction.
MUST_SURVIVE = [
    "Leeds",        # standalone city (she visited family there)
    "75mg",
    "90mg",
    "2.5mg",
    "80mg",
    "LAD",
    "NSTEMI",
    "ECG",
    "troponin",
    "stent",
    "chest pain",
]
