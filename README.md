https://amir-shahriari.github.io/CareScribe/


# CareScribe

A local, privacy-preserving Streamlit app that **de-identifies clinical documents in
batches**, puts every detection in front of a human reviewer, and writes out only what the
reviewer has approved.

Everything runs on your machine, on the **CPU**. No GPU, no cloud services, no API keys, no
telemetry. The only network traffic of any kind is to a local Ollama daemon on
`127.0.0.1:11434` during report generation — de-identification itself makes no network
calls at all.

> **Report generation is local.** The model receives de-identified text with placeholders
> and never sees a real identifier. Re-identification happens afterwards, in Python, on
> your machine. See [Generating a report](#generating-a-report).

---

## ⚠ Privacy caveat — read this first

**Automated de-identification is not a guarantee of HIPAA or UK GDPR compliance.**

This tool is a drafting aid, not a compliance control. Specifically:

- Every detection layer misses things. Regex only covers what a regex can express; NER
  misses names in unusual positions and invents entities in clinical prose. Their union is
  better than either alone, and still not complete.
- Recall degrades on unusual formatting, OCR-derived text, and heavily abbreviated notes.
- It also produces **false positives** — over-redaction silently damages the document's
  clinical meaning, and the reviewer is the only thing that catches it.
- **Every document requires human review.** The app will not write a file until you have
  looked at the preview and clicked approve, and the safety sweep will block you if
  something still looks like an identifier. Do not click through those steps.
- Before using this on real patient data you must **validate it on your own documents**:
  measure recall and precision against a manually annotated gold-standard set, and decide
  whether the residual risk is acceptable under your governance framework.
- HIPAA Safe Harbor requires the removal of all 18 identifier categories. This app targets
  most of them; targeting is not achieving. Expert Determination or a formal validation
  study is what makes a de-identification claim defensible — not this README.

---

## Download

For Windows and macOS, see [Installation Guide](docs/download-and-install.md).

## Privacy invariants

These are the properties the code is structured to make checkable, not just to claim:

| Invariant | How it is enforced |
|---|---|
| The server is never exposed on the network | `.streamlit/config.toml` binds `127.0.0.1` |
| De-identification opens no socket | `test_app.py::test_pipeline_opens_no_socket` fails the build if the load → analyse → approve path opens one |
| Generation cannot reach off-box | `ollama_client` hard-codes `127.0.0.1:11434` and never reads `OLLAMA_HOST`; `test_generation.py` asserts the source contains no `environ`/`getenv` lookup |
| The model never sees a real identifier | `carenotes.assert_deidentified()` checks the outgoing prompt against the mapping's values and raises rather than sending; the mapping is not a parameter to any backend |
| Re-identification is local and complete | Placeholder → value substitution happens in Python; an unresolved placeholder **blocks** the final document rather than filing it |
| The identity mapping never reaches disk | It lives only in `st.session_state`; `batch.write_approved()` has no parameter to pass it through |
| Everything written is de-identified | Three write paths, all in `batch.py`: the approved text, the redacted `.docx`, and the audit sidecar. The first two re-run `residual_scan()` and refuse the write if anything survives; the third records counts and types only |
| Original documents are never copied | Ingestion reads bytes into memory, and `.docx` redaction runs entirely in memory — the un-redacted original is never staged to a temp file. `test_docx_roundtrip.py::test_the_original_document_is_never_written_to_disk` spies on every write and fails if the original's bytes appear |
| The audit sidecar holds no PHI | `<name>.review.json` records checklist keys, flag counts, and a placeholder tally by type. A test asserts that no `must_redact` string from the whole stress corpus can appear in it |

`🧹 Clear session / wipe PHI` drops every document, identifier table, and identity map from
memory. It leaves approved files already on disk alone.

---

## The de-identification pipeline

CPU-only, offline, and layered. Each layer contributes character spans; the union is
resolved longest-match-wins and turned into reviewable rows.

### Layer 1 — structured regex (`structured_spans`)

Deterministic and highest precision. The formats a regex nails and a model drops:

| Category | Notes |
|---|---|
| NHS number | `943 476 5919`, `9434765919`, `943-476-5919` |
| UK phone | Matched loosely enough to catch numbers buried in prose |
| Email | Standard address form |
| UK postcode | Case-sensitive, so it does not fire on ordinary lowercase words |
| Record number | **Context-anchored** — only taken after `MRN`, `Hospital No/Number`, `Case No/Number`, `Record No/Number`, `Unit No/Number`, `Chart No/Number`, `Patient No/Number`, `Patient ID`. The label may carry a parenthetical gloss (`Hospital No (MRN): 4471982`) and the value may be grouped (`33-201-45`). A bare digit run in clinical text is far more likely to be a lab value |
| Location | A letterhead line that is **nothing but** `Town, County`, in the first or last six lines. Redacts to `[LOCATION]`. Narrow on purpose — clinical prose never takes that shape, so `travelled in from Leeds` is untouched |
| Staff initials | `A. Whitfield`, `Dr R. Patel` — one to three initials plus a surname, taken when a role word, a `Typed by`/`Dictated by` line, an attendee list, or a parenthetical job title vouches for it. `S. aureus` and `T3/T4` are excluded by shape |
| Address line | A labelled `Address:` line is taken **whole**, which is what lets layer 2 stay strict about bare place names |
| Organisation | A capitalised run ending in a known descriptor (`Hospital`, `Medical Practice`, `Clinic`, `Surgery`, `NHS Trust`, …) |
| Titled name | `Dr`/`Sister`/`Nurse`/`Prof`/`Consultant` + name. The span covers the **name only**, so it collapses onto the same person as the NER hit |

### Layer 2 — Presidio + spaCy NER (`ner_spans`)

`AnalyzerEngine` over a spaCy NLP engine. The model is chosen from
`en_core_web_lg` -> `md` -> `sm`, overridable with `CARESCRIBE_SPACY_MODEL`.
`lg` is ~750 MB and materially better on free-text names; `sm` loads far faster
and suits a modest laptop, at some cost to recall on names no label vouches for.

**The model loads once at startup, behind a spinner, cached with
`@st.cache_resource`.** Streamlit re-runs the whole script on every interaction,
so an uncached engine is rebuilt on every click — the classic "the app froze"
report on weak hardware. De-identification is also offline by force:
`HF_HUB_OFFLINE` and friends are set at import, so a missing resource fails fast
with a legible message rather than hanging on a socket behind a captive portal.
A model that cannot be found is reported and the app stops; it never falls back
to fetching one. Every load and every de-identify call is timed into
`%LOCALAPPDATA%/CareScribe/logs/carescribe.log` (timings and sizes, no PHI). Captures `PERSON`, `LOCATION`, `ORGANIZATION`, `DATE_TIME`, plus
Presidio's own pattern recognisers. **This is the layer that catches a name sitting in the
middle of a paragraph**, where no label or title vouches for it.

It is also the layer that needs guarding. Left alone, spaCy labels `ECG` and `NSTEMI` as
organisations, `ST` (as in *ST depression*) as a location, and every date-shaped number as
a date. `_span_is_plausible()` buys precision back:

- **Acronym filter** — a short all-caps token is never a name. Dotted initials (`M.E.C.`)
  are exempt.
- **Clinical-term denylist** plus a drug-suffix heuristic (`-statin`, `-olol`, `-pril`, …).
- **Dose guard** — a capitalised token followed by `75mg` is a drug, not a person.
- **Address gate** — a `LOCATION` is only an address if it contains a street word, sits on
  a labelled address line, or is followed by a postcode. `visiting family in Leeds` survives.
- **Multi-line ORG rejection** — a spanning ORG match is always a mis-span; layer 1 has the
  real name.
- **Span trimming** — honorifics come off the front (`Sister Fiona Docherty` →
  `Fiona Docherty`) and ordinary English comes off both ends, so one person ends up with
  one placeholder rather than three.

### Layer 3 — GLiNER (optional)

A small CPU NER model, run for the labels `person`, `organization`, `address`, `id`. The
import is guarded end to end: **the app runs identically without it**. Not installed by
default because it pulls in torch (~2 GB). To enable:

```bash
pip install gliner
```

### Layer 4 — variant expansion

Detected values fan out into the forms the document might actually use, all mapped to the
**same** placeholder:

- `expand_name_variants("Margaret Elizabeth Chen", known_as="Peggy")` → the full name, each
  component, `Mrs Chen` / `Dr. Chen` / every title+surname, `Margaret Chen`, and initials
  (`MEC`, `M.E.C.`, `M.C.`), plus the alias.
- `expand_org_variants("St. Aidan's General Hospital")` → the full name and `St. Aidan's`.

A leading title is stripped before deriving parts, so a value like `Dr Patel` never emits a
bare `Dr` that would redact every `Dr` in the document.

### Layer 5 — line-break-tolerant matching

Form tokens are joined with `\s+`, not a literal space:

```python
pat = r"\s+".join(re.escape(t) for t in form.split())
```

so a name split across a line break still matches:

```
stent was deployed. Margaret
Chen tolerated the procedure well
```

Overlaps resolve **longest-match-wins**, so `David Chen` beats a bare `Chen` and
`14 Leeds Road, Harrogate, LS9 4TT` is consumed as one address.

### Placeholders

Stable and per-entity. The same real value gets the same placeholder everywhere:

```
[PATIENT]  [RELATIVE_1]  [CLINICIAN_1]  [CLINIC_1]
[MRN]  [NHS_NO]  [PHONE_1]  [ADDRESS_1]  [LOCATION_1]  [DATE_1]  [EMAIL]  [DOB]
```

A type with one value gets a bare placeholder; a type with several gets numbered ones.

`[ADDRESS]` and `[LOCATION]` are deliberately separate. An address is a postal
address; a location is a bare place name from a letterhead. Keeping them apart is
what lets the address gate stay strict enough to preserve `visiting family in
Leeds` while a clinic's town and county still get redacted.

**One identity, one placeholder.** Every written form of a person collapses onto a
single canonical identity — surname plus first initial — so `Mohammed Al-Rashid`,
`Mr Al-Rashid`, `Mohammed`, `M.A.R.` and the `Known as` alias all share one
placeholder, and one row in the review table. Two people who share a surname keep
different identities: `Margaret Chen` and `David Chen` differ by first initial. A
bare surname that could belong to either is left as its own row rather than bound
to the wrong person, and the collision is reported.
Persons are typed from context: a clinical title makes a `CLINICIAN`, a kinship marker
(`David Chen (son)`, a `NEXT OF KIN` heading) makes a `RELATIVE`, a `Patient:` label makes
the `PATIENT`. Anything unclassified stays the honest generic `PERSON`, and the reviewer
can retype it.

### Dates

`REDACT_INPROSE_DATES` in `core/deidentify.py` defaults to **`False`**. In-prose dates are
the highest-false-positive category in the whole pipeline — clinical text is dense with
date-shaped numbers, and a wrong hit damages the note's meaning rather than merely leaving
an identifier behind.

With the flag off, only **identity-anchored** dates are redacted — those preceded by `DOB`,
`Date of Birth`, `Admitted`, `Discharged`, `Appointment`, `Seen on`, and similar. A
procedure date in prose (`Angiography on 06/06/2026`), a duration (`six weeks`), a dosing
frequency (`once daily`), and every lab value are left alone. Set it to `True` to redact
every date-shaped span; the dosage/lab-value guard still applies.

A **labelled date field is always redacted**, whatever the flag says — the flag governs
unlabelled prose dates only. Any line whose label ends in a colon and reads as a date field
qualifies (`Admission date:`, `Date typed:`, `Next review:`, `Date of Birth:`), which is more
robust than an anchor list: `Admission date:` matched the anchor `Admission` and then choked
on the word `date` before the colon, so the field leaked while its prose twin was redacted.

The same date value carries the same `[DATE_n]` placeholder wherever it appears, field or
prose. A date span is also clipped to its own line — an NER span running from a discharge
date into the next line's `Date typed:` label used to carry the newline into the entity
value, which both mangled the following line on replacement and stopped the value matching
the same date written in prose.

---

## The desktop app

For a clinician, CareScribe is a file you double-click. No terminal, no Python,
no setup. The packaging is the privacy model made concrete — the app runs on the
laptop rather than asking anyone to trust a server.

```bash
# Windows: icon -> PyInstaller -> Inno Setup installer
powershell -ExecutionPolicy Bypass -File packaginguild_windows.ps1
# -> dist\CareScribe\CareScribe.exe
# -> packaging\Output\CareScribeSetup.exe   (desktop + Start-menu shortcuts)

# macOS: icon -> PyInstaller -> .dmg   (must run ON macOS — no cross-compile)
bash packaging/build_macos.sh
# -> dist/CareScribe.app  and  dist/CareScribe.dmg
```

`packaging/make_icon.py` generates the placeholder icon (a teal rounded square
with "CS") with Pillow, so the build never depends on a checked-in binary asset.
It degrades to a plain square if no TrueType font is available rather than
failing the build. Compiling the installer needs Inno Setup 6 once:
`winget install -e --id JRSoftware.InnoSetup`.

The Windows build carries a PyInstaller splash, drawn by the bootloader before
Python starts — a frozen Streamlit app takes several seconds to unpack, and
without feedback a user double-clicks again and ends up with two servers. The
launcher closes it once the health check passes.

`run_app.py` is the entry point: it picks a free loopback port, starts Streamlit
headless on `127.0.0.1`, waits for it, and shows it in a native `pywebview`
window — no browser tab, no console. Closing the window stops the server.

**Signing is not optional in practice, and it applies to the installer too.**
The installer is the *first* thing a clinician runs, so an unsigned
`CareScribeSetup.exe` means the very first interaction is a SmartScreen wall.
An unsigned `.app`/`.dmg` is blocked outright by Gatekeeper. Sign the inner
binary *and* the installer/dmg — the build scripts carry the `signtool` and
`codesign`/`notarytool` commands for both. Shipping unsigned means teaching a
clinician to click through a security warning, which is a bad thing to teach.

### Generation backends

Chosen at runtime, in this order:

| | Backend | When |
|---|---|---|
| 1 | Ollama | Only if a local daemon is already answering — someone who installed it wanted a bigger model |
| 2 | **Built-in GGUF** | The default. `llama-cpp-python` on the CPU with a bundled 3B Q4 model, so the app generates with nothing installed |
| 3 | Cloud | **Off.** Requires both `CARESCRIBE_CLOUD_PROVIDER` and `CARESCRIBE_CLOUD_API_KEY`; see `docs/deployer-cloud-note.md` |

All three receive the same thing: approved de-identified text. Re-identification
stays local in Python.

**First run on a fresh machine shows a setup card, never an empty panel.**
`generation_status()` reports which backends are usable; when none are, the
panel offers a one-click download of the built-in model or a one-click Ollama
pull, then a **Test generation** action that proves it works before the
clinician relies on it. De-identification and review never block on any of this.

> **Downloading a model and running one are different things, and the code keeps
> them apart.** Fetching weights is the single outbound request this app makes,
> it lives alone in `core/model_setup.py`, and it only runs on a click — no
> module in the document pipeline imports it, which is asserted by a test.
> Running the model opens no socket, which is asserted by another. The
> "no egress during de-id → approve → generate" invariant is unchanged.

> **The built-in 3B model runs at temperature 0.0, deliberately.** At 0.2 it
> invented "anxiety and occasional insomnia" and "a history of depression" for a
> source containing neither. At 0.0 the same prompt produced `[not documented]`
> in every unsupported section. A small model has less headroom to be creative
> with, and creativity is the failure mode here. An 8B via Ollama is materially
> better and is worth the install for real clinical use.

### Where things go

Outputs are written under the user profile —
`%LOCALAPPDATA%\CareScribe` or `~/Library/Application Support/CareScribe` —
never beside the executable, which may sit in `C:\Program Files` or inside a
signed `.app`. The identity mapping is written to neither.

On first launch the app checks available RAM. Below what the bundled model
needs, it warns plainly and points at a smaller Ollama model rather than
crashing; de-identification and review are unaffected.

Practitioner guide: `docs/practitioner-guide.md`.
Deployer note on the optional cloud path: `docs/deployer-cloud-note.md`.

---

## Setup

Python 3.11+. No GPU, no Ollama, no model server.

```bash
conda activate medgpt          # or your venv

pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

The large spaCy model is ~600 MB. If the download fails, `en_core_web_sm` is used
automatically; if neither is present the pipeline falls back to layer 1 alone and the
sidebar says so.

### Run

```bash
streamlit run carescribe/app.py
```

Opens on `http://127.0.0.1:8501`, bound to loopback only.

---

## Running a batch review

1. **Load a batch** — either drop PDF/DOCX/TXT files into the uploader, or paste a local
   folder path. Folder loading is non-recursive and skips anything already ending in
   `.deid.txt`. Files are read into memory; nothing is copied.
2. **De-identify** — click the run button. Documents are processed **one at a time** with a
   `Document 3 of 10` counter. The first one also pays for loading the spaCy model
   (a few seconds); after that each document is fast.
3. **Review & approve** — pick a document from the selector and work through it:
   - The **identifier table** is editable: correct a value, fix a type, override a
     placeholder, delete a false positive, or switch **Action** to **Keep** to leave that
     string in the document without deleting the row.
   - **Add a missed identifier** — paste anything the layers missed. It is variant-expanded
     exactly like a detected value, so typing a full name also covers `Mrs Surname` and the
     initials. You are warned if the string does not appear in the document verbatim.
   - The **redacted preview** updates as you edit and is exactly what gets written.
   - **Surface forms covered** shows every string each row will actually match — one row
     usually covers many forms.
   - **Run safety sweep and approve** writes the file.
4. **Batch status** shows every document's state and where its output landed.

### Where approved output lands

```
carescribe/output/deidentified/<filename>.deid.txt
```

De-identified text only. The identity mapping is never written — it has no code path to
disk, and `write_approved()` has nowhere to accept it. The output folder is gitignored.

### The safety sweep

`residual_scan(deidentified_text)` re-runs the structured regex layer plus a PERSON-only
NER check over the **already-redacted** text and returns anything that still looks like an
identifier. It runs automatically at approve time; a non-empty result **blocks the write**
and lists the findings for you to handle.

Placeholders are not findings — anything that is, or overlaps, a `[PLACEHOLDER]` token is
excluded. Organisations are excluded too: the ORG recogniser flags ward and department
names the pipeline never redacts, and blocking approval on those would just train reviewers
to ignore the gate.

Each finding has two ways out:

- **Add it as a missed identifier** — it gets redacted, and the sweep passes.
- **Dismiss it** — for a finding that is genuinely not identifying. spaCy labels town names
  as people as readily as places, so a preserved place of care (`Leeds`, `Bolton`) will be
  flagged even though the precision rules kept it on purpose. Without dismissal the only
  route past the gate would be to over-redact, which is the failure those rules exist to
  prevent. Dismissals are per string, per document, and are never persisted.

`write_approved()` runs the sweep again itself, so the guarantee does not depend on the UI
having done so.

---

## Generating a report

Generation runs **locally, through Ollama**, on approved de-identified text only.

### Setup

```bash
# 1. Install Ollama (https://ollama.com), then start the daemon:
ollama serve            # on Windows, launching the Ollama app does this

# 2. Pull a model. An 8B-class instruct model is the sweet spot on CPU:
ollama pull llama3.1:8b
```

No Python package is needed — the client talks to the HTTP API through the
standard library, which is why `ollama` stays commented out in
`requirements.txt`. The host is **hard-pinned to `127.0.0.1:11434`** and
`OLLAMA_HOST` is deliberately ignored: it is the documented way to point a
client at another machine, which is exactly what must not be possible here.
Never reading it is a stronger guarantee than reading it and validating it.

### Using it

Section 5 of the app unlocks once a document is **approved** — generation never
runs on text a human has not signed off. Pick a model, pick a template, and the
draft streams in token by token (an 8B model on CPU is slow enough that a
progress indicator matters).

| Template | Produces |
|---|---|
| SOAP care note | S / O / A / P structured note |
| GP clinic letter | Outpatient letter to the GP |
| Discharge summary | Inpatient summary, medication reproduced verbatim |
| Custom | Your own house format, pasted in |

After the first draft you can give follow-up instructions ("make the plan more
concise", "add a risk paragraph"). Refinement re-runs on the same de-identified
source plus the current draft, so it carries exactly the same privacy
properties as the first pass.

### The two output versions

**The de-identified draft** still contains placeholders (`[PATIENT]`, `[MRN]`).
It is safe to display, share, and export. Download as `.md`, `.txt`, or `.docx`.

**The re-identified record** is opt-in and clearly labelled. It contains real
patient identifiers and is for saving into your own local record. It is produced
**entirely in Python on your machine** — placeholders are swapped back for the
values held in session memory. The model is never in that loop and never sees a
real identifier.

```
approved de-identified text  ──►  local model  ──►  draft with placeholders
                                                            │
                                    Python, on this machine ▼
                                              re-identified local record
```

That split is the point: the model's view of the document is identical whether
it runs on this laptop or, one day, somewhere else.

### What stops a bad document being filed

- **The model only ever receives de-identified text.** Before anything is sent,
  `assert_deidentified()` checks the outgoing prompt against the mapping's real
  values and raises rather than sending. The mapping is not a parameter to any
  backend.
- **Placeholder corruption is repaired in Python, not trusted to the model.** An
  8B model will occasionally write `[MATIENT_2]` for `[PATIENT_2]`.
  `check_placeholder_integrity()` finds near-misses, invented tokens, and
  placeholders that went missing.
- **Re-identification is the release gate.** If any bracketed placeholder cannot
  be resolved, the final document is **blocked** and the offending tokens are
  shown. A report filed with a literal `[PATIENT]` in it is worse than no report.
- **Every draft carries a "Draft — requires clinician review" banner**, prepended
  in Python rather than asked of the model.
- **The anti-fabrication rule is load-bearing.** `prompts/system.txt` requires
  `[not documented]` where the source is silent, rather than a plausible guess.

The mapping is never written to disk at any point, in either version.

---

## What is still not built

Generation is wired up and local by default. One thing is deliberately out of
scope:

- **No storage of the identity mapping.** There is no "resume this document
  tomorrow" feature, because that would mean persisting the mapping. Closing the
  session drops it, by design.

The optional **cloud generation** path now has a real transport
(`core/cloud_client.py` — Anthropic Messages API, or the OpenAI-compatible shape
for Azure / private / self-hosted endpoints), but it stays **off unless a
deployer sets both `CARESCRIBE_CLOUD_PROVIDER` and `CARESCRIBE_CLOUD_API_KEY`**,
it is last in the backend ladder, and it receives only approved de-identified
text. See `docs/deployer-cloud-note.md`.

Clinical-form generation can learn a clinic's **house style**: saving a
de-identified draft as an exemplar (`core/exemplars.py`) adds it to a local
BM25 index, and future drafts of that form retrieve the closest past
field-values as style examples in the prompt. Storage is placeholder text only,
guarded by `residual_scan`; retrieval is local and opens no socket. Semantic
(embedding) retrieval is a documented follow-up.

A clinic **reference library** (`core/reference_library.py`) indexes `.txt` /
`.md` formularies, care pathways, and protocols. Relevant passages are shown
**verbatim, with their source, to the clinician** in the draft review view —
they are deliberately *not* fed to the model, because a paraphrased dose or
referral criterion is a safety defect. A test enforces that `reference_library`
is not imported by the generation path.

A **retrieval planner** (`core/retrieval_planner.py`) decides, per template
field, whether exemplars and reference material are worth fetching, at what
chunk granularity (`sentence` for a dose, `section` for a formulation), and
with what query. The shipped `RuleBasedPlanner` is a keyword taxonomy over
field labels — deterministic, no model; an LLM planner would implement the same
`RetrievalPlanner` protocol. It too is kept out of generation.

`ollama` stays commented out in `requirements.txt`: the client uses the standard
library, so the package being absent is a checkable property rather than a
promise.

---

## Project structure

```
carescribe/
  app.py                    Streamlit batch review UI
  core/
    deidentify.py           the layered pipeline + residual_scan
    mapping.py              placeholders, variant expansion, matching, re-identification
    batch.py                batch loading + the one write path
    ingest.py               PDF / DOCX / TXT text extraction
    carenotes.py            handoff stub — raises NotImplementedError
    ollama_client.py        unused in this stage
  prompts/                  unused in this stage
  output/deidentified/      approved output (gitignored)
tests/
  synthetic_patient_discharge_summary.txt   the fixture — fully fabricated
  fixtures.py               recall / precision expectations
  test_deid_pipeline.py     the regression suite
  test_deid_regressions.py  the five leaks found on document #2
  test_stress_corpus.py     corpus-driven net, driven by answer_key.json
  stress_report.py          per-document pass/fail breakdown
  test_mapping.py           placeholders, variants, re-identification
  test_batch.py             loading and the write path
  test_ingest.py            document extraction
  test_app.py               UI via Streamlit AppTest
stress_corpus/
  doc0*.txt                 five synthetic documents — fully fabricated
  answer_key.json           must_redact / must_preserve per document
```

---

## Tests

```bash
pytest tests -q                 # or: python tests/run_all.py
python tests/stress_report.py   # per-document stress-corpus breakdown
```

Nothing needs a server, a GPU, or a network connection.

The fixture is a synthetic discharge summary containing every identifier form that has
leaked in testing, plus the clinical strings that must survive untouched. **Everything in
it is fabricated** — the phone number uses Ofcom's `01632 960xxx` drama range and the email
uses `example.co.uk`, both reserved for fiction.

**Recall** — none of these survive: the NHS number in any spacing, `Mrs Chen`, the
line-break-split `Margaret\nChen`, the initials `M.E.C.`, the relative `David Chen`,
`Dr O'Sullivan`, `Sister Docherty`, `Dr Patel`, the in-prose phone `01632 960 188`,
`St. Aidan's`, and `Riverside Medical Practice` — plus the hospital number, email,
postcode, street address, DOB, and the `Known as` alias.

**Precision** — these are preserved: the standalone city `Leeds` used as a place of care
rather than an address, every medication dosage, and the clinical terms (`LAD`, `NSTEMI`,
`ECG`, `ST depression`, `troponin`, `stent`, `chest pain`). The entire medication block is
asserted byte-identical.

**Safety** — `residual_scan()` returns empty on the correctly de-identified fixture, and
catches a leaked phone number or clinician name when one is spliced back in.

---

## Known limitations

- A **bare forename with no surname, no title, and no context** ("David was present") is
  only caught if NER happens to tag it. This is the category the optional GLiNER layer
  helps most with.
- When two people share a surname, the bare surname binds to whichever entity appears first
  in the table. It is still redacted, but re-identification would restore the wrong full
  name for that one form. The UI flags these collisions explicitly.
- Detection quality tracks the spaCy model. `en_core_web_lg` is materially better than
  `en_core_web_sm` on free-text names.
- Scanned PDFs with no text layer are rejected. CareScribe does not run OCR.
- The clinical denylist and drug-suffix heuristic are curated, not exhaustive. A drug or
  abbreviation they do not know may still be flagged as a name — the reviewer deletes the
  row, and the deletion sticks (`rebuild()` does not re-run detection).

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Sidebar says *Presidio + spaCy unavailable* | `python -m spacy download en_core_web_lg`. Layer 1 keeps working meanwhile. |
| Something clinical got redacted | Set the row's **Action** to `Keep`, or delete it, then **Apply table edits**. Deletions stick — detection does not re-run. |
| An identifier survived | Paste it into **Add a missed identifier**. It is variant-expanded immediately. |
| *Refusing to write / Approval blocked* | The safety sweep found something. Either add it as a missed identifier, or **Dismiss** it if it is genuinely not identifying — then approve again. |
| A preserved place name blocks approval | Expected — spaCy calls towns people. Dismiss it. |
| Listed values still appear in the preview | The table value does not match the document verbatim. Fix the spelling and **Apply table edits**. |
| Dates you want redacted are surviving | They carry no identity anchor. Add them by hand, or set `REDACT_INPROSE_DATES = True` in `core/deidentify.py`. |
| *No text could be extracted* | Scanned PDF with no text layer. OCR it first. |
| First document is slow | The spaCy model loads once, on first use. |

---

## License / disclaimer

Provided as-is, with no warranty. Not a medical device. Not a compliance control. You are
responsible for validating it before any use involving real patient data.
