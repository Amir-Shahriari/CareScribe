"""
Wizard UI checks via Streamlit's AppTest, with Ollama faked. No server needed.

Run:  python tests/test_app.py
"""

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest  # noqa: E402

from carescribe.core import mapping, ollama_client  # noqa: E402

APP = str(ROOT / "carescribe" / "app.py")
failures = []
passes = 0


def check(name, cond, detail=""):
    global passes
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -> {detail}"))
    if cond:
        passes += 1
    else:
        failures.append(name)


def report(at, label):
    exc = [e.value for e in at.exception]
    check(f"{label}: no exception", not exc, exc)
    return at


# ---- 1. Ollama DOWN: must render an error, not crash ----
# Forced regardless of whether a real server happens to be running locally.
_real_available = ollama_client.is_available
_real_list = ollama_client.list_models
ollama_client.is_available = lambda: False
ollama_client.list_models = lambda: []

at = AppTest.from_file(APP, default_timeout=60).run()
report(at, "step1 (ollama down)")
errs = " ".join(e.value for e in at.error)
check("ollama-down shows red status", any("unreachable" in e.value for e in at.error), errs)
check("ollama-down shows the pull hint",
      any("ollama pull llama3.1:8b" in i.value for i in at.info), [i.value for i in at.info])


# AppTest runs the script in-process, so patching the imported module object
# here is what the app sees.
def fake_ollama(models):
    ollama_client.is_available = lambda: True
    ollama_client.list_models = lambda: list(models)


def run_with_fake(models, state=None, label=""):
    fake_ollama(models)
    at = AppTest.from_file(APP, default_timeout=90)
    for key, value in (state or {}).items():
        at.session_state[key] = value
    at.run()
    return report(at, label)


# ---- 2. Ollama UP but no models ----
at = run_with_fake([], label="step1 (no models)")
check("no-models warning shown",
      any("no models are installed" in w.value for w in at.warning),
      [w.value for w in at.warning])

MODELS = ["llama3.1:8b", "qwen2.5:7b"]

# ---- 3. Step 1 with a document loaded ----
DOC = "Patient: Margaret Chen (DOB 03/14/1952), MRN A-99812. Seen by Dr. Alan Reyes."
at = run_with_fake(MODELS, {"step": 0, "raw_text": DOC, "file_name": "note.txt"},
                   "step1 (doc loaded)")
check("model dropdowns present", len(at.sidebar.selectbox) >= 1, len(at.sidebar.selectbox))
check("step1 success banner", any("note.txt" in s.value for s in at.success),
      [s.value for s in at.success])

# ---- 4. Step 2 with entities present ----
ents = mapping.assign_placeholders(mapping.dedupe_entities([
    {"type": "PATIENT_NAME", "value": "Margaret Chen"},
    {"type": "DOB", "value": "03/14/1952"},
    {"type": "MRN", "value": "A-99812"},
    {"type": "PROVIDER_NAME", "value": "Alan Reyes"},
]))
red = mapping.redact(DOC, ents)
phi_map = mapping.build_map(ents)
state2 = {"step": 1, "raw_text": DOC, "file_name": "note.txt",
          "entities": ents, "redacted_text": red, "phi_map": phi_map}

at = run_with_fake(MODELS, state2, "step2 (entities)")
# AppTest has no DataEditor accessor; st.data_editor surfaces as arrow_data_frame.
editors = [e for e in at.main if type(e).__name__ == "Dataframe"]
check("data_editor rendered", len(editors) == 1, len(editors))
check("editor holds the 4 identifiers", len(editors[0].value) == 4 if editors else False,
      (len(editors[0].value) if editors else None))
check("editor columns correct",
      list(editors[0].value.columns) == ["type", "value", "placeholder"] if editors else False,
      (list(editors[0].value.columns) if editors else None))
check("human-review warning shown",
      any("Human review required" in w.value for w in at.warning), [w.value for w in at.warning])
check("redacted preview holds placeholders",
      any("[PATIENT]" in t.value for t in at.text_area), [t.value[:60] for t in at.text_area])

# Task 5: derived surface forms are visible to the reviewer, not just table rows.
expander_labels = [getattr(b, "label", "") for b in at.main if hasattr(b, "label")]
check("surface-forms expander present",
      any("Surface forms covered" in str(label) for label in expander_labels),
      expander_labels)
check("surface-forms lists derived variants",
      any("Mrs Chen" in m.value for m in at.markdown), "not found")
check("surface-forms count exceeds row count",
      any("from 4 rows" in str(label) for label in expander_labels), expander_labels)

# ---- 5. Step 3 blocked until confirmation ----
at = run_with_fake(MODELS, {**state2, "step": 2, "deid_confirmed": False}, "step3 (unconfirmed)")
check("step3 blocked when unconfirmed",
      any("Confirm de-identification" in e.value for e in at.error), [e.value for e in at.error])

# ---- 6. Step 3 confirmed, with a generated note ----
NOTE = "**S — Subjective**\n[PATIENT] reports chest pain. Seen by [PROVIDER]."
state3 = {**state2, "step": 2, "deid_confirmed": True, "note_text": NOTE,
          "note_reidentified": mapping.reidentify(NOTE, phi_map)}
at = run_with_fake(MODELS, state3, "step3 (confirmed)")
check("template radio rendered", len(at.radio) == 1, len(at.radio))
check("4 templates offered", len(at.radio[0].options) == 4, at.radio[0].options)
check("re-insert checkbox present", len(at.checkbox) >= 1, len(at.checkbox))
check("note displayed with placeholders",
      any("[PATIENT]" in m.value for m in at.markdown), "not found")

# ---- 6b. re-insert toggled on ----
at = AppTest.from_file(APP, default_timeout=90)
for k, v in state3.items():
    at.session_state[k] = v
fake_ollama(MODELS)
at.run()
at.checkbox[0].set_value(True).run()
report(at, "step3 (reinsert on)")
check("reinsert shows real name", any("Margaret Chen" in m.value for m in at.markdown), "not found")
check("reinsert shows PHI warning", any("real PHI" in e.value for e in at.error),
      [e.value for e in at.error])

# ---- 6c. Task 7: a corrupted placeholder is repaired and reported in the UI ----
MANGLED = "[MATIENT] reports chest pain. Seen by [GHOST_9]."
state3c = {**state3, "note_text": MANGLED,
           "note_reidentified": mapping.reidentify(MANGLED, phi_map),
           "placeholder_repairs": [("[MATIENT]", "[PATIENT]")]}
at = run_with_fake(MODELS, state3c, "step3 (mangled placeholders)")
check("repair reported to reviewer",
      any("repaired automatically" in i.value for i in at.info), [i.value for i in at.info])
check("unrepairable placeholder still warned",
      any("[GHOST_9]" in w.value for w in at.warning), [w.value for w in at.warning])

# ---- 7. Step 4 export ----
at = run_with_fake(MODELS, {**state3, "step": 3}, "step4 (export)")
buttons = [b.label for b in at.get("download_button")]
check("4 de-id/note download buttons", len(buttons) == 4, buttons)
check("no PHI download until opted in",
      not any("PHI" in b for b in buttons), buttons)

at = AppTest.from_file(APP, default_timeout=90)
for k, v in {**state3, "step": 3}.items():
    at.session_state[k] = v
fake_ollama(MODELS)
at.run()
at.checkbox[0].set_value(True).run()      # "Include a PHI version"
report(at, "step4 (PHI opt-in)")
phi_buttons = [b.label for b in at.get("download_button")]
check("PHI downloads appear on opt-in", len(phi_buttons) == 6, phi_buttons)

# ---- 8. Wipe PHI clears state ----
at = AppTest.from_file(APP, default_timeout=90)
for k, v in state3.items():
    at.session_state[k] = v
at.session_state["placeholder_repairs"] = [("[MATIENT]", "[PATIENT]")]
fake_ollama(MODELS)
at.run()
wipe = [b for b in at.sidebar.button if "wipe" in b.label.lower()]
check("wipe button exists", len(wipe) == 1, [b.label for b in at.sidebar.button])
if wipe:
    wipe[0].click().run()
    report(at, "after wipe")
    check("wipe cleared raw_text", at.session_state["raw_text"] == "")
    check("wipe cleared entities", at.session_state["entities"] == [])
    check("wipe cleared phi_map", at.session_state["phi_map"] == {})
    check("wipe cleared note", at.session_state["note_text"] == "")
    check("wipe cleared placeholder repairs", at.session_state["placeholder_repairs"] == [])
    check("wipe reset step", at.session_state["step"] == 0)

ollama_client.is_available = _real_available
ollama_client.list_models = _real_list

print("\n" + "=" * 60)
print(f"{passes} passed, {len(failures)} failed")
if failures:
    print("FAILURES: " + ", ".join(failures))
sys.exit(1 if failures else 0)
