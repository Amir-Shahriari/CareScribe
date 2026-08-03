"""
Offline logic checks for CareScribe. No Ollama required.

Run:  python tests/test_logic.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from carescribe.core import carenotes, deidentify, ingest, mapping, ollama_client  # noqa: E402
from carescribe.prompts import carenotes_prompt  # noqa: E402
from tests.fixtures import (  # noqa: E402
    DISCHARGE_SUMMARY,
    LLM_ENTITIES,
    MUST_NOT_SURVIVE,
    MUST_SURVIVE,
)

failures = []
passes = 0


def check(name, cond, detail=""):
    global passes
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -> {detail}"))
    if cond:
        passes += 1
    else:
        failures.append(name)


# ==========================================================================
# SECTION A — original suite (behaviour that must not regress)
# ==========================================================================
print("=== A. baseline ===")

# --- 1. ollama_client degrades gracefully ---
avail = ollama_client.is_available()
print(f"      (ollama reachable: {avail})")
check("is_available returns bool", isinstance(avail, bool))
check("list_models returns list", isinstance(ollama_client.list_models(), list))

# --- 2. JSON parsing, defensive ---
cases = {
    "plain": '{"entities":[{"type":"PATIENT_NAME","value":"Margaret Chen"}]}',
    "fenced": '```json\n{"entities":[{"type":"MRN","value":"A-99812"}]}\n```',
    "prose_wrapped": 'Sure! Here you go:\n{"entities":[{"type":"DOB","value":"03/14/1952"}]}\nHope that helps.',
    "brace_in_value": '{"entities":[{"type":"OTHER_ID","value":"ID{7}"}]}',
    "bare_list": '[{"type":"PHONE","value":"(555) 123-4567"}]',
    "empty_entities": '{"entities":[]}',
}
for name, raw in cases.items():
    try:
        out = deidentify.parse_entities_json(raw)
        check(f"parse {name}", isinstance(out, list), out)
    except Exception as e:
        check(f"parse {name}", False, repr(e))

for name, raw in {"garbage": "I cannot help with that.", "empty": "  "}.items():
    try:
        deidentify.parse_entities_json(raw)
        check(f"parse {name} raises", False, "no exception")
    except deidentify.DeidentificationError:
        check(f"parse {name} raises", True)

# --- 3. redact / reidentify round trip ---
doc = ("Patient: Margaret Chen (DOB 03/14/1952), MRN A-99812, alt MRN B-11220.\n"
       "Contact: 555-123-4567, margaret.chen@example.com, 14 Leeds Road, Springfield.\n"
       "Seen by Dr. Alan Reyes at Springfield General. Margaret reports chest pain.\n"
       "Note: Leeds is a city; MARGARET CHEN also appears in caps.\n")
ents = [
    {"type": "PATIENT_NAME", "value": "Margaret Chen"},
    {"type": "DOB", "value": "03/14/1952"},
    {"type": "MRN", "value": "A-99812"},
    {"type": "MRN", "value": "B-11220"},
    {"type": "PHONE", "value": "555-123-4567"},
    {"type": "EMAIL", "value": "margaret.chen@example.com"},
    {"type": "ADDRESS", "value": "14 Leeds Road"},
    {"type": "PROVIDER_NAME", "value": "Alan Reyes"},
    {"type": "FACILITY", "value": "Springfield General"},
]
ents = mapping.assign_placeholders(mapping.dedupe_entities(ents))
ph = {e["value"]: e["placeholder"] for e in ents}
check("single-value type -> bare placeholder", ph["Margaret Chen"] == "[PATIENT]", ph)
check("multi-value type -> numbered", ph["A-99812"] == "[MRN_1]" and ph["B-11220"] == "[MRN_2]", ph)
check("provider stem shortened", ph["Alan Reyes"] == "[PROVIDER]", ph)

red = mapping.redact(doc, ents)
check("no residual values", mapping.residual_values(red, ents) == [],
      mapping.residual_values(red, ents))
check("case-insensitive match hit", "MARGARET CHEN" not in red)
check("standalone 'Leeds' untouched", "Leeds is a city" in red, red)
check("longest-first: address consumed whole", "[ADDRESS]" in red)

phi_map = mapping.build_map(ents)
restored = mapping.reidentify(red, phi_map)
check("MRN_1 not eaten by MRN rule", "A-99812" in restored and "B-11220" in restored)
for value in ph:
    check(f"round-trip restores '{value[:18]}'", value in restored)

# --- 4. rebuild() from an edited table ---
edited = [
    {"type": "PATIENT_NAME", "value": "Margaret Chen", "placeholder": "[PT]"},
    {"type": "OTHER_ID", "value": "A-99812", "placeholder": ""},
    {"type": "", "value": "", "placeholder": ""},           # blank row from data_editor
    {"type": "PATIENT_NAME", "value": "margaret chen", "placeholder": ""},  # dup
]
res = deidentify.rebuild(doc, edited)
check("rebuild drops blank rows", len(res.entities) == 2, res.entities)
check("rebuild keeps manual placeholder", res.entities[0]["placeholder"] == "[PT]", res.entities)
check("rebuild auto-assigns blank", res.entities[1]["placeholder"].startswith("["), res.entities)
check("rebuild redacts", "[PT]" in res.redacted_text, res.redacted_text[:120])

# --- 5. type normalisation ---
check("alias doctor->PROVIDER_NAME", mapping.normalise_type("doctor") == "PROVIDER_NAME")
check("unknown->OTHER_ID", mapping.normalise_type("weird thing") == "OTHER_ID")
check("None->OTHER_ID", mapping.normalise_type(None) == "OTHER_ID")

# --- 6. prompts + carenotes helpers ---
sysmsg, usermsg = carenotes_prompt.build_messages("SOAP note", red)
check("SOAP system prompt built", "Subjective" in sysmsg)
check("document embedded in user msg", "[PATIENT]" in usermsg)
sysmsg2, usermsg2 = carenotes_prompt.build_messages("Custom prompt", red, "Write a haiku.")
check("custom instruction honoured", "Write a haiku." in usermsg2)
check("template labels exposed", len(carenotes.TEMPLATE_LABELS) == 4, carenotes.TEMPLATE_LABELS)
check("unknown placeholder detected",
      carenotes.find_unknown_placeholders("Hi [PATIENT] and [GHOST_3]", phi_map) == ["[GHOST_3]"],
      carenotes.find_unknown_placeholders("Hi [PATIENT] and [GHOST_3]", phi_map))
check("no false unknown", carenotes.find_unknown_placeholders("Hi [PATIENT]", phi_map) == [])

# --- 7. guards raise, don't crash ---
for fn, args in [(carenotes.generate, ("", "text", "SOAP note")),
                 (carenotes.generate, ("m", "   ", "SOAP note"))]:
    try:
        fn(*args); check("carenotes guard", False, "no raise")
    except carenotes.CareNoteError:
        check("carenotes guard raises", True)

# --- 8. ingest: txt + bad type + empty ---
class Fake:
    def __init__(self, name, data): self.name, self._d = name, data
    def getvalue(self): return self._d

check("txt ingest", ingest.extract_text(Fake("a.txt", "Hello PHI".encode())) == "Hello PHI")
check("cp1252 fallback", "café" in ingest.extract_text(Fake("b.txt", "café".encode("cp1252"))))
for name, data, label in [("x.jpg", b"data", "bad ext"), ("x.txt", b"", "empty"),
                          ("x.doc", b"data", "legacy doc"), ("x.txt", b"   ", "whitespace only")]:
    try:
        ingest.extract_text(Fake(name, data)); check(f"ingest {label} raises", False, "no raise")
    except ingest.IngestError:
        check(f"ingest {label} raises", True)

# --- 9. structured pre-pass is live (was: asserted the no-op stub) ---
prepass_baseline = deidentify.presidio_prepass(doc)
check("prepass finds structured IDs",
      any(e["value"] == "margaret.chen@example.com" for e in prepass_baseline),
      prepass_baseline)
check("merge with empty prepass", len(deidentify.merge_entities([], ents)) == len(ents))


# ==========================================================================
# SECTION B — Task 1: deterministic structured pre-pass
# ==========================================================================
print("\n=== B. structured regex pre-pass ===")

prepass = deidentify.presidio_prepass(DISCHARGE_SUMMARY)
found = {e["value"]: e["type"] for e in prepass}

check("prepass: NHS number", found.get("943 476 5919") == "NHS_NUMBER", found)
check("prepass: UK phone", found.get("01632 960 188") == "UK_PHONE", found)
check("prepass: email", found.get("m.chen48@example.co.uk") == "EMAIL", found)
check("prepass: postcode", found.get("LS9 4TT") == "UK_POSTCODE", found)
check("prepass: context-anchored MRN", found.get("4471982") == "MRN", found)
check("prepass: ALL-CAPS letterhead facility",
      found.get("ST. AIDAN'S GENERAL HOSPITAL") == "FACILITY", found)
check("prepass: title-case facility",
      found.get("Riverside Medical Practice") == "FACILITY", found)
check("prepass: 'GP Practice:' label not taken as a facility",
      not any(e["value"].lower().startswith("gp ") for e in prepass), found)
titled = {e["value"] for e in prepass if e["type"] == "PROVIDER_NAME"}
check("prepass: titled clinician, full name", "Aoife O'Sullivan" in titled, titled)
check("prepass: titled clinician, surname only", "Docherty" in titled, titled)
check("prepass: 'Dr Patel' short form caught", "Patel" in titled, titled)
check("prepass: title itself excluded from the value",
      not any(v.split()[0] in mapping.TITLES for v in titled), titled)
check("prepass: role words not taken as names",
      not any(e["value"].lower().startswith(("practitioner", "consultant"))
              for e in deidentify.presidio_prepass("Seen by the Nurse Practitioner and Consultant Cardiologist.")),
      deidentify.presidio_prepass("Seen by the Nurse Practitioner and Consultant Cardiologist."))
check("prepass: personal titles are NOT person-detected (patient collision)",
      not any(e["type"] == "PROVIDER_NAME"
              for e in deidentify.presidio_prepass("Mrs Chen attended.")),
      deidentify.presidio_prepass("Mrs Chen attended."))

# Partial names must fold into the fuller name, not split the person in two.
collapsed = deidentify.merge_entities(
    [{"type": "PROVIDER_NAME", "value": "Docherty"}],
    [{"type": "PROVIDER_NAME", "value": "Fiona Docherty"}],
)
check("subset collapse keeps the fuller name",
      [e["value"] for e in collapsed] == ["Fiona Docherty"], collapsed)
check("subset collapse is token-wise, not substring",
      len(deidentify.merge_entities(
          [{"type": "PROVIDER_NAME", "value": "Aiden"}],
          [{"type": "PROVIDER_NAME", "value": "Braiden Cole"}])) == 2)
check("subset collapse ignores non-person types",
      len(deidentify.merge_entities(
          [{"type": "MRN", "value": "123456"}],
          [{"type": "MRN", "value": "99 123456"}])) == 2)

_flags = (deidentify.DETECT_ORG_NAMES, deidentify.DETECT_TITLED_NAMES)
try:
    deidentify.DETECT_ORG_NAMES = False
    deidentify.DETECT_TITLED_NAMES = False
    off = deidentify.presidio_prepass(DISCHARGE_SUMMARY)
    check("DETECT_ORG_NAMES=False disables facility detection",
          not any(e["type"] == "FACILITY" for e in off))
    check("DETECT_TITLED_NAMES=False disables titled-name detection",
          not any(e["type"] == "PROVIDER_NAME" for e in off))
    check("toggles leave structured IDs alone",
          any(e["type"] == "NHS_NUMBER" for e in off))
finally:
    deidentify.DETECT_ORG_NAMES, deidentify.DETECT_TITLED_NAMES = _flags

check("prepass: plain prose yields no facility",
      not any(e["type"] == "FACILITY"
              for e in deidentify.presidio_prepass("She attends a clinic near the practice.")),
      deidentify.presidio_prepass("She attends a clinic near the practice."))
check("prepass: phone not double-tagged as NHS",
      len([v for v in found if v == "01632 960 188"]) == 1, found)
check("prepass: no bare digit run picked up as MRN",
      "5919" not in found and "960" not in found, found)
check("prepass: empty text is safe", deidentify.presidio_prepass("") == [])
check("prepass: no-identifier text yields nothing",
      deidentify.presidio_prepass("Patient stable. Chest clear. No new symptoms.") == [],
      deidentify.presidio_prepass("Patient stable. Chest clear. No new symptoms."))

# MRN must not fire without a label vouching for it.
check("prepass: unlabelled 7-digit run ignored",
      not any(e["type"] == "MRN" for e in deidentify.presidio_prepass("Result was 4471982 units.")),
      deidentify.presidio_prepass("Result was 4471982 units."))
check("prepass: labelled variants match",
      all(any(e["type"] == "MRN" for e in deidentify.presidio_prepass(t))
          for t in ["MRN: 123456", "Hospital No 998877", "Record No. 4471982",
                    "Chart Number: 55512345"]))


# ==========================================================================
# SECTION C — Tasks 2 & 3: variant expansion
# ==========================================================================
print("\n=== C. name and facility variants ===")

patient_variants = mapping.expand_name_variants("Margaret Elizabeth Chen", known_as='"Peggy"')
for want in ["Margaret Elizabeth Chen", "Margaret Chen", "Mrs Chen", "Mrs. Chen",
             "Chen", "Margaret", "M.E.C.", "MEC", "M.C.", "Peggy"]:
    check(f"name variant '{want}'", want in patient_variants, sorted(patient_variants))

check("known_as strips quotes", '"Peggy"' not in patient_variants, sorted(patient_variants))

# The title guard: without it, "Dr" becomes a redaction form and shreds the note.
dr_patel = mapping.expand_name_variants("Dr Patel")
check("title not emitted as standalone form", "Dr" not in dr_patel, sorted(dr_patel))
check("title-prefixed value still yields surname", "Patel" in dr_patel, sorted(dr_patel))
check("title-prefixed value keeps full form", "Dr Patel" in dr_patel, sorted(dr_patel))
sister = mapping.expand_name_variants("Sister Docherty")
check("Sister not emitted as standalone form", "Sister" not in sister, sorted(sister))

check("apostrophe surname survives",
      "Dr O'Sullivan" in mapping.expand_name_variants("Aoife O'Sullivan"),
      sorted(mapping.expand_name_variants("Aoife O'Sullivan")))
check("empty name -> empty set", mapping.expand_name_variants("   ") == set())
check("single-token name safe",
      mapping.expand_name_variants("Chen") >= {"Chen", "Mrs Chen"},
      sorted(mapping.expand_name_variants("Chen")))

aidans = mapping.expand_facility_variants("St. Aidan's General Hospital")
check("facility: full form kept", "St. Aidan's General Hospital" in aidans, sorted(aidans))
check("facility: 'General Hospital' stripped", "St. Aidan's" in aidans, sorted(aidans))
riverside = mapping.expand_facility_variants("Riverside Medical Practice")
check("facility: 'Medical Practice' stripped", "Riverside" in riverside, sorted(riverside))
check("facility: short fragments dropped",
      all(len(v) >= mapping.MIN_FACILITY_FORM_LENGTH for v in mapping.expand_facility_variants("St Hospital")),
      sorted(mapping.expand_facility_variants("St Hospital")))
check("facility: no descriptor -> just the name",
      mapping.expand_facility_variants("Bramwell House") == {"Bramwell House"})

check("known_as detected from document",
      mapping.find_known_as(DISCHARGE_SUMMARY) == "Peggy",
      mapping.find_known_as(DISCHARGE_SUMMARY))
check("known_as absent -> None", mapping.find_known_as("No alias here.") is None)


# ==========================================================================
# SECTION D — Tasks 4 & 5: full pipeline, recall and precision
# ==========================================================================
print("\n=== D. pipeline: recall + precision ===")

# Exactly what deidentify() does, minus the LLM call.
pipeline_entities = deidentify.merge_entities(
    deidentify.presidio_prepass(DISCHARGE_SUMMARY), LLM_ENTITIES
)
pipeline_entities = mapping.assign_placeholders(pipeline_entities)
REDACTED = mapping.redact(DISCHARGE_SUMMARY, pipeline_entities)

print("--- redacted ---\n" + REDACTED + "----------------")

# RECALL
for leaked in MUST_NOT_SURVIVE:
    check(f"recall: {leaked!r} removed", leaked not in REDACTED)

# PRECISION
for kept in MUST_SURVIVE:
    check(f"precision: {kept!r} survives", kept in REDACTED)

check("precision: address consumed as one unit",
      "Leeds Road" not in REDACTED and "[ADDRESS" in REDACTED, REDACTED[:200])
check("precision: standalone city survives",
      "family in Leeds" in REDACTED, REDACTED)
check("precision: 'Dr' honorific not shredded",
      REDACTED.count("[PROVIDER") >= 3, REDACTED)
check("precision: no empty-bracket artefacts", "[]" not in REDACTED)

# Task 4 specifics
check("line-break-tolerant match",
      "Margaret\nChen" not in REDACTED and "Chen tolerated" not in REDACTED, REDACTED)
check("all patient variants share one placeholder",
      len({p for p, forms in mapping.surface_forms(pipeline_entities).by_placeholder.items()
           if "Mrs Chen" in forms or "M.E.C." in forms}) == 1)

expanded = mapping.surface_forms(pipeline_entities, "Peggy")
check("surface forms exceed entity rows",
      len(expanded.forms) > len(pipeline_entities),
      (len(expanded.forms), len(pipeline_entities)))
check("shared surname reported as ambiguous",
      any(form.casefold() == "chen" for form, _, _ in expanded.ambiguous),
      expanded.ambiguous)
check("ambiguous form still redacted", "Chen" not in REDACTED)

# Task 5: every finding is a reviewable row
values = {e["value"] for e in pipeline_entities}
check("review table includes regex findings",
      {"943 476 5919", "01632 960 188", "LS9 4TT", "4471982"} <= values, sorted(values))
check("review table includes LLM findings",
      {"Margaret Elizabeth Chen", "David Chen"} <= values, sorted(values))
check("identical values collapse to one row",
      len(values) == len(pipeline_entities), (len(values), len(pipeline_entities)))
check("merge upgrades generic type to specific",
      next(e["type"] for e in pipeline_entities if e["value"] == "12/03/1948") == "DOB",
      [e for e in pipeline_entities if e["value"] == "12/03/1948"])

check("no residual forms after redaction",
      mapping.residual_values(REDACTED, pipeline_entities, "Peggy") == [],
      mapping.residual_values(REDACTED, pipeline_entities, "Peggy"))

# rebuild() must not resurrect reviewer-deleted rows
trimmed = [e for e in pipeline_entities if e["value"] != "943 476 5919"]
rebuilt = deidentify.rebuild(DISCHARGE_SUMMARY, trimmed)
check("rebuild does not re-run the prepass",
      all(e["value"] != "943 476 5919" for e in rebuilt.entities),
      [e["value"] for e in rebuilt.entities])
check("rebuild preserves placeholders across edits",
      rebuilt.entities[0]["placeholder"] == trimmed[0]["placeholder"],
      (rebuilt.entities[0], trimmed[0]))


# ==========================================================================
# SECTION E — Task 6: in-prose dates
# ==========================================================================
print("\n=== E. in-prose dates ===")

date_values = {e["value"] for e in prepass if e["type"] == "DATE"}
for want in ["4 June 2026", "21 July 2026", "2nd of June", "06/06/2026", "12/03/1948"]:
    check(f"date caught: {want!r}", want in date_values, sorted(date_values))

check("dates removed from output",
      not any(d in REDACTED for d in ["4 June 2026", "21 July 2026", "2nd of June", "06/06/2026"]),
      REDACTED)

# Dosage / lab guards
for safe in ["Aspirin 75mg once daily", "Bisoprolol 2.5mg once daily",
             "heart rate 90 bpm", "troponin level 12/03", "sodium 140 mmol"]:
    hits = [e for e in deidentify.presidio_prepass(safe) if e["type"] == "DATE"]
    check(f"date guard: {safe!r}", hits == [], hits)

check("month word alone is not a date",
      not any(e["type"] == "DATE" for e in deidentify.presidio_prepass("Reviewed in June.")),
      deidentify.presidio_prepass("Reviewed in June."))

# Toggle
_original_flag = deidentify.REDACT_INPROSE_DATES
try:
    deidentify.REDACT_INPROSE_DATES = False
    off = deidentify.presidio_prepass(DISCHARGE_SUMMARY)
    check("REDACT_INPROSE_DATES=False disables dates",
          not any(e["type"] == "DATE" for e in off),
          [e for e in off if e["type"] == "DATE"])
    check("REDACT_INPROSE_DATES=False keeps other IDs",
          any(e["type"] == "NHS_NUMBER" for e in off))
finally:
    deidentify.REDACT_INPROSE_DATES = _original_flag
check("flag restored", deidentify.REDACT_INPROSE_DATES is _original_flag)


# ==========================================================================
# SECTION F — Task 7: robust re-identification
# ==========================================================================
print("\n=== F. placeholder-corruption safety ===")

fuzzy_map = {"[PATIENT_1]": "Margaret Chen", "[PATIENT_2]": "David Chen",
             "[PROVIDER]": "Raj Patel", "[MRN_1]": "4471982"}

r = mapping.reidentify_detailed("[MATIENT_2] visited today.", fuzzy_map)
check("repairs corrupted placeholder", "David Chen" in r.text, r.text)
check("repair is reported", r.corrected == [("[MATIENT_2]", "[PATIENT_2]")], r.corrected)
check("no unresolved after repair", r.unresolved == [], r.unresolved)

r = mapping.reidentify_detailed("[PROVIDR] signed off.", fuzzy_map)
check("repairs a dropped character", "Raj Patel" in r.text, r.text)

r = mapping.reidentify_detailed("Seen by [GHOST_9].", fuzzy_map)
check("distant token left alone", "[GHOST_9]" in r.text, r.text)
check("distant token reported unresolved", r.unresolved == ["[GHOST_9]"], r.unresolved)

r = mapping.reidentify_detailed("Ref [PATIENT_3].", fuzzy_map)
check("ambiguous token refuses to guess", "[PATIENT_3]" in r.text, r.text)
check("ambiguous token reported unresolved", r.unresolved == ["[PATIENT_3]"], r.unresolved)

for junk in ["[]", "[[]]", "[123]", "[lower_case]", "[", "]", "[UNCLOSED", "[A]"]:
    try:
        mapping.reidentify(f"text {junk} more", fuzzy_map)
        check(f"never crashes on {junk!r}", True)
    except Exception as e:
        check(f"never crashes on {junk!r}", False, repr(e))

check("exact matches still substitute",
      mapping.reidentify("[PATIENT_1] and [MRN_1]", fuzzy_map) == "Margaret Chen and 4471982",
      mapping.reidentify("[PATIENT_1] and [MRN_1]", fuzzy_map))
check("non-regex placeholder still works",
      mapping.reidentify("[Pt] here", {"[Pt]": "Margaret Chen"}) == "Margaret Chen here",
      mapping.reidentify("[Pt] here", {"[Pt]": "Margaret Chen"}))
check("empty map is a no-op", mapping.reidentify("[PATIENT]", {}) == "[PATIENT]")
check("empty text is safe", mapping.reidentify("", fuzzy_map) == "")
check("repaired token not flagged as unknown",
      carenotes.find_unknown_placeholders("[MATIENT_2] here", fuzzy_map) == [],
      carenotes.find_unknown_placeholders("[MATIENT_2] here", fuzzy_map))
check("invented token still flagged as unknown",
      carenotes.find_unknown_placeholders("[GHOST_9] here", fuzzy_map) == ["[GHOST_9]"],
      carenotes.find_unknown_placeholders("[GHOST_9] here", fuzzy_map))

check("edit distance basic", mapping._edit_distance("[MRN_1]", "[MRN_1]") == 0)
check("edit distance caps out", mapping._edit_distance("abc", "xyzqrstuv") > 2)


print("\n" + "=" * 60)
print(f"{passes} passed, {len(failures)} failed")
if failures:
    print("FAILURES: " + ", ".join(failures))
sys.exit(1 if failures else 0)
