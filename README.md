# CareScribe

A local, privacy-preserving Streamlit app that **de-identifies patient documents** with a
local LLM, then **drafts care notes** from the de-identified text.

Everything runs on your machine. No cloud services, no API keys, no telemetry.

---

## ⚠ Privacy caveat — read this first

**LLM-based de-identification is not a guarantee of HIPAA compliance.**

This tool is a drafting aid, not a compliance control. Specifically:

- A language model **will** miss identifiers, and *which* ones it misses changes between
  runs on the same document. In local testing with `llama3.1:8b`, one run dropped the
  hospital name in the letterhead entirely; the next run dropped two of three clinicians.
  The deterministic regex layer exists precisely because the model's recall is not
  dependable, and it in turn only covers the categories a regex can express.
- Recall degrades further on unusual formatting, handwriting-derived OCR text, and long
  documents that overflow the context window.
- It can also produce false positives, redacting clinical content that matters.
- **Every output requires human review** before it is used or shared. The app forces you
  to read and confirm the redacted text before it will generate notes — do not click
  through that step.
- Before using this on real patient data you must **validate it on your own documents**:
  measure recall and precision against a manually-annotated gold-standard set, and decide
  whether the residual risk is acceptable under your governance framework.
- HIPAA Safe Harbor requires the removal of all 18 identifier categories. This app targets
  them, but targeting is not the same as achieving. Expert Determination or a formal
  validation study is what makes a de-identification claim defensible — not this README.

The app never writes PHI to disk. It also cannot stop *you* from downloading a
PHI-containing file and putting it somewhere inappropriate.

---

## What it does

A four-step wizard:

1. **Upload** — read a PDF, DOCX, or TXT document into memory.
2. **De-identify** — a local LLM detects identifiers; you review, correct, and confirm
   them in an editable table; replacement happens deterministically in Python.
3. **Generate care notes** — SOAP note, care plan, progress note, or your own prompt,
   streamed live. Optionally map real names back into the finished note.
4. **Export** — download the de-identified text and the care note as `.txt` or `.md`.

### The hybrid de-identification pipeline

De-identification runs in four layers. No layer is sufficient alone, and the stack as a
whole is still not a guarantee — see the caveat above.

1. **Deterministic regex pass** (`deidentify.presidio_prepass`) — pure Python, no
   dependencies, runs before the LLM. Catches the formats a regex gets right and a
   language model routinely drops: NHS numbers, emails, UK phone numbers and postcodes,
   record numbers anchored to a label ("Hospital No: 4471982"), organisation names ending
   in a known descriptor ("... General Hospital"), clinician names introduced by a
   clinical title ("Dr Patel"), and optionally in-prose dates.

2. **LLM pass** — the local model reads the whole document and returns identifiers as
   strict JSON. This covers what regex cannot: free-text names in unusual positions,
   relatives and next of kin, facilities without a descriptor, contextual dates.

3. **Variant expansion** (`mapping.surface_forms`) — each detected name and organisation
   is expanded into every plausible written form *before* matching. One person's forms all
   collapse onto that person's single placeholder:

   | Detected | Also redacted |
   |---|---|
   | `Margaret Elizabeth Chen` | `Margaret Chen`, `Mrs Chen`, `Chen`, `M.E.C.`, `MEC`, `M.C.`, plus any "Known as" alias |
   | `Fiona Docherty` | `Sister Docherty`, `Dr. Docherty`, `Docherty` |
   | `St. Aidan's General Hospital` | `St. Aidan's General`, `St. Aidan's` |

   Matching is whitespace-tolerant, so a name split across a line break
   (`"Margaret\nChen"`) still matches, and overlapping matches resolve longest-span-first
   so `14 Leeds Road` is consumed whole and `David Chen` beats a bare `Chen`.

4. **Human review** — the reviewer edits the identifier table, sees every derived surface
   form in the "Surface forms covered" panel, and must click **Confirm** before anything
   reaches the care-note stage. This step is load-bearing, not decorative. The layers
   above raise recall; they do not remove the need for someone to read the redacted text.

Two module-level flags in `core/deidentify.py` turn off the higher-false-positive parts of
layer 1 if they misfire on your documents: `REDACT_INPROSE_DATES`, `DETECT_ORG_NAMES`,
and `DETECT_TITLED_NAMES`.

### How the privacy model actually works

- **The model never rewrites your document.** It only returns a JSON list of the strings
  it thinks are identifiers. Redaction is plain Python string replacement
  (`core/mapping.py`), so the model cannot hallucinate content into the redacted text or
  silently drop a paragraph.
- **Re-identification survives a mangled placeholder.** Note models sometimes corrupt a
  placeholder while rewriting (`[MATIENT_2]` for `[PATIENT_2]`). Re-identification matches
  placeholders with a tolerant pattern and repairs near-misses by edit distance, refusing
  to guess when two candidates are equally close. Anything it can't resolve is left
  untouched and reported in the UI — it never crashes and never silently attaches the
  wrong identity.
- **The care note stage only ever sees redacted text.** `carenotes.generate_stream()`
  takes the de-identified string and nothing else — there is no parameter it could use to
  leak the original.
- **Re-identification happens after generation**, in Python, on the output string. Real
  names are never sent to the model at any point.
- **Nothing is persisted.** The document, the identifier table, and the
  placeholder→name map live in `st.session_state` (server-side RAM) and are dropped by
  the **Clear session / wipe PHI** button. Files hit disk only when you click a download
  button.
- **The Ollama host is hard-pinned to `127.0.0.1`.** The `OLLAMA_HOST` environment
  variable is deliberately ignored, so a stray value there can't redirect PHI to a remote
  machine.

---

## Setup

### 1. Install Ollama

Download from <https://ollama.com/download> and install. Then pull a model:

```bash
ollama pull llama3.1:8b
```

Verify it's running — Ollama starts a local server on `127.0.0.1:11434`:

```bash
ollama list
```

### 2. Python environment

This project ships with a conda environment named **`medgpt`**:

```bash
conda create -n medgpt python=3.11 -y     # already created if you followed setup
conda activate medgpt
pip install -r requirements.txt
```

### 3. Run

From the project root (`medgpt/`):

```bash
streamlit run carescribe/app.py
```

The app opens at <http://127.0.0.1:8501>. `.streamlit/config.toml` disables Streamlit's
usage statistics and binds the server to loopback only.

---

## Recommended models for 8GB VRAM (RTX 3070)

All of these are Q4_K_M quantised by default in Ollama and fit in 8GB alongside an 8k
context window.

| Model | Pull command | Notes |
|---|---|---|
| **Llama 3.1 8B** | `ollama pull llama3.1:8b` | **Best default.** Most reliable at emitting strict JSON, which is what the de-identification stage depends on. |
| **Qwen 2.5 7B** | `ollama pull qwen2.5:7b` | Strong instruction-following; good alternative if Llama's recall disappoints on your documents. A newer Qwen 7–9B release works equally well — check `ollama.com/library/qwen3` for the current tag. |
| **Gemma 3 4B** | `ollama pull gemma3:4b` | Much faster and lighter, but noticeably weaker at structured output. Use it for the care-note stage if you want speed, not for de-identification. |

### On a single 8GB GPU, use one model for both stages

The sidebar has a *"Use a separate model for care notes"* toggle. **Leave it off.** With
8GB of VRAM, only one 7–9B model fits at a time, so selecting a different model for stage
3 forces Ollama to evict the first model and load the second — adding tens of seconds per
run, and again on every re-run. One model for both stages is meaningfully faster.

If a model fails to load, close other GPU applications (browsers with hardware
acceleration are the usual culprit) or drop to `gemma3:4b`.

### Performance notes

- Context is set to 8k tokens (`num_ctx` in `core/ollama_client.py`). Documents longer
  than roughly 20,000 characters trigger a warning in step 1 — identifiers past the
  cutoff will not be detected. Split long records into sections.
- De-identification runs at `temperature=0.0` for determinism; care notes at `0.3`.
- The first call after starting Ollama is slow (model load). Subsequent calls are fast.

---

## Project structure

```
medgpt/
  requirements.txt
  README.md
  .streamlit/config.toml       # telemetry off, loopback-only binding
  carescribe/
    app.py                     # Streamlit entry point, 4-step wizard
    core/
      ollama_client.py         # server probe, model list, chat() with timeouts
      ingest.py                # extract_text() for pdf/docx/txt
      deidentify.py            # regex pre-pass, LLM pass, defensive parse, merge
      carenotes.py             # care note generation from de-identified text only
      mapping.py               # variant expansion, span matching, re-identification
    prompts/
      deid_prompt.py           # de-identification system + user templates
      carenotes_prompt.py      # SOAP / care plan / progress note / custom
  tests/
    fixtures.py                # synthetic discharge summary (no real PHI)
    test_logic.py              # de-id logic, recall + precision regressions
    test_app.py                # wizard UI via Streamlit AppTest
    run_all.py                 # runs both suites
```

### Tests

```bash
conda activate medgpt
python tests/run_all.py
```

Neither suite needs Ollama running. `test_logic.py` covers the regex pre-pass, variant
expansion, the span matcher, in-prose date guards, and placeholder-corruption recovery,
including a recall/precision regression set built on a synthetic discharge summary: every
identifier that has ever leaked must be absent from the redacted output, and clinical
strings (`75mg`, `LAD`, `NSTEMI`, a standalone city name) must survive untouched.

### Identifier categories covered

`PATIENT_NAME`, `DOB`, `MRN`, `NHS_NUMBER`, `ADDRESS`, `PHONE`, `FAX`, `EMAIL`, `SSN`,
`PROVIDER_NAME`, `FACILITY`, `DATE`, `OTHER_ID`.

Placeholders are assigned per unique value: a type with one value gets `[PATIENT]`, a
type with several gets `[MRN_1]`, `[MRN_2]`. Replacement is case-insensitive, guarded by
word boundaries, and applied longest-span-first so "John Q. Smith" is consumed before a
bare "Smith" can fragment it.

### Known limitations

- A **bare forename with no surname and no title** ("David was present") is invisible to
  both layers unless the LLM happens to catch it. Regex cannot express it without a name
  gazetteer or NER.
- When two people share a surname, the bare surname is bound to whichever entity appears
  first in the table. It is still redacted, but re-identification may restore the wrong
  full name for that one form. The UI flags these collisions explicitly.
- If the model reports a patient's alias as its own entity, it gets its own placeholder
  rather than folding into the patient's. Merge them by editing the placeholder column.
- Detection quality depends on the model. `llama3.1:8b` is the most consistent of the
  8GB-class options tested.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| 🔴 *Ollama unreachable* | Start Ollama, then click **Refresh connection**. Confirm with `ollama list`. |
| *Running but no models installed* | `ollama pull llama3.1:8b` |
| *De-identification failed after a retry* | The model won't emit valid JSON. Switch to `llama3.1:8b` — small models often fail this. |
| *Listed forms still appear in the redacted text* | The table's value doesn't match the document verbatim. Fix the spelling in the table and click **Apply table edits**. |
| *Placeholders that can't be re-identified* | The model invented a placeholder too corrupted to match. Near-misses are repaired automatically; anything reported here needs a regenerate or a manual edit. |
| *Something clinical got redacted* | Delete the row and click **Apply table edits** — deletions stick, the regex pass does not re-run and resurrect them. If a whole category misfires, turn off `REDACT_INPROSE_DATES`, `DETECT_ORG_NAMES`, or `DETECT_TITLED_NAMES` in `core/deidentify.py`. |
| *No text could be extracted* | Scanned PDF with no text layer. CareScribe does not run OCR — OCR it first. |

---

## Phase 2 status

The deterministic pre-pass described here originally is **implemented and on by default**,
but as pure-Python regex rather than Microsoft Presidio — `core/deidentify.py` →
`presidio_prepass()` (the name is kept for continuity). No Presidio, no spaCy, no GLiNER,
no model download, no added dependency.

Remaining future enhancement: **a local NER model.** It would raise recall on the one
category regex genuinely cannot express — person names with no title, no surname, and no
structural anchor. It is not wired in, to keep the dependency footprint small and the
behaviour fully deterministic and auditable. The merge path (`merge_entities`) already
accepts an arbitrary number of detector outputs, so adding a third layer is a one-line
change at the call site in `deidentify()`. Pinned versions stay commented out in
`requirements.txt`.

---

## License / disclaimer

Provided as-is, with no warranty. Not a medical device. Not a compliance control. You are
responsible for validating it before any use involving real patient data.
