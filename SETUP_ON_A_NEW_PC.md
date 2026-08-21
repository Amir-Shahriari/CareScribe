# Getting CareScribe running on a new PC

Two ways to do this. Pick the one that matches what you have.

- **[Path A — you have the built app](#path-a--you-have-the-built-app)** — copy a
  folder over, double-click. No Python, no internet. ~10 minutes.
- **[Path B — you only have the source code](#path-b--building-from-source)** —
  build it on the new machine. ~45 minutes, needs internet.

Whichever you use: **everything runs on that computer.** No patient data is
uploaded anywhere, on either path.

---

## Path A — you have the built app

This is the easy one. The `dist\CareScribe` folder is completely
self-contained — it has its own Python, the spaCy language model, and everything
else baked in.

### 1. Copy the folder

Copy the whole **`dist\CareScribe`** folder to the new PC. Put it somewhere
sensible, for example:

```
C:\Users\<name>\CareScribe
```

It is about **850 MB**. A USB stick or a network share is fine. Copy the *whole*
folder — `CareScribe.exe` on its own will not work, it needs the `_internal`
folder beside it.

### 2. Make a desktop icon

Right-click `CareScribe.exe` → **Show more options** → **Send to** →
**Desktop (create shortcut)**.

To give it the CareScribe icon rather than a generic one: right-click the new
desktop shortcut → **Properties** → **Change Icon** → **Browse** → pick
`CareScribe.ico` (copy it across from the project folder).

### 3. Double-click it

The first launch takes **30–60 seconds** — Windows is unpacking the app. You
will see a small splash, then the CareScribe window. Later launches are faster.

**You will probably see a blue "Windows protected your PC" box.** That is
SmartScreen, and it appears because the app is not code-signed — not because
anything is wrong with it. Click **More info** → **Run anyway**.

> If this app is ever going to more than a couple of machines, get it
> code-signed. Teaching clinicians to click past security warnings is a bad
> habit to build. See `packaging/build_windows.ps1` for the `signtool` commands.

### 4. Check it works

De-identification should work immediately. To confirm:

1. Click **Load a batch** and drop in a test document — use one from
   `stress_corpus\` if you have the project folder, they are all fabricated.
2. Click **De-identify**.
3. You should see identifiers found and a redacted preview.

### 5. Set up generation (in the app, one click)

De-identification and review work immediately. **Drafting notes needs an AI
model, and the app walks you through getting one** — there is no terminal step.

Open the generation panel and you will see a **Set up generation** card with two
choices:

**Option A — Download the built-in model.** One click, about 1.9 GB, downloaded
once. It goes into your user folder, not the app folder. If the connection drops
it resumes rather than starting over.

**Option B — Use Ollama.** Better drafts, free, installed separately. If Ollama
is already running the app offers a one-click download; if not, it shows the
link and the three steps.

Either way, click **Test generation** afterwards. It runs a short prompt and
shows you the result, so you get a concrete "Generation is ready ✓" rather than
having to trust a tick box.

> **What the download actually is.** It brings the AI model *onto* your
> computer — the same kind of thing as installing any other program. No patient
> data is involved and nothing about any document is sent. Once it has finished,
> the app is offline again: **running** the model opens no network connection at
> all. It is a one-time setup, and the app remembers.

---

## Path B — building from source

Do this if you have the project folder but not `dist\CareScribe`.

### 1. Install Python

Get **Python 3.11** from <https://www.python.org/downloads/> — not 3.12 or
newer, some dependencies lag behind.

**Tick "Add Python to PATH"** on the first screen of the installer. If you miss
it, nothing below works.

### 2. Copy the project and install dependencies

Copy the project folder over, then open Command Prompt in it and run:

```bat
python -m pip install -r requirements.txt
python -m spacy download en_core_web_lg
python -m pip install pywebview pyinstaller psutil pillow
python -m pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

The spaCy model is ~600 MB and the rest a few hundred more. This needs internet
and takes a while.

> **`llama-cpp-python` fails to install?** On Windows it will try to compile from
> source and hit the 260-character path limit. The `--extra-index-url` above
> avoids that by fetching a prebuilt wheel — do not drop it. If it still fails,
> skip it: everything except the *built-in* model still works, and Ollama covers
> generation.

### 3. Check it runs before building

```bat
python -m pytest tests -q
python run_app.py
```

The tests should be all green. `run_app.py` should open the CareScribe window.
Close it before continuing.

### 4. Build the app

```bat
powershell -ExecutionPolicy Bypass -File packaging\build_windows.ps1
```

Takes 5–15 minutes. Produces `dist\CareScribe\CareScribe.exe`. Then follow
**Path A step 2** onwards to make the desktop icon.

To bundle the language model into the build so generation works with nothing
else installed, first download a model into `models\`:

```bat
curl -L -o models\Qwen2.5-3B-Instruct-Q4_K_M.gguf "https://huggingface.co/bartowski/Qwen2.5-3B-Instruct-GGUF/resolve/main/Qwen2.5-3B-Instruct-Q4_K_M.gguf?download=true"
```

That is ~1.9 GB and makes the build ~2.8 GB. The build script picks it up
automatically.

### 5. Optional — a proper installer

If you want `CareScribeSetup.exe` (which creates the desktop and Start-menu
shortcuts for you), install Inno Setup 6 once from
<https://jrsoftware.org/isdl.php>, then re-run the build script. It detects
Inno Setup and compiles the installer automatically.

**Note:** I have not been able to test this step — Inno Setup would not install
on the machine this was built on. The script `packaging\carescribe.iss` is
written and should work, but you are the first person to run it.

---

## Which model should I use?

| | Speed on a laptop | Quality | Setup |
|---|---|---|---|
| **Built-in 3B** | ~1 min per note | Adequate | One click in the app |
| **Ollama + llama3.1:8b** | ~1–2 min | Noticeably better | Install Ollama, then one click in the app |

CareScribe uses Ollama automatically whenever it is running, and falls back to
the built-in model otherwise. You do not choose in the app.

**For real clinical work, use the 8B.** The small model is more prone to writing
things that were not in the source document. The built-in one is deliberately
run at temperature 0 to reduce that, but it is still a 3B model and it still
needs every draft read carefully. So does the 8B, for that matter.

---

## Requirements

| | Minimum | Comfortable |
|---|---|---|
| Windows | 10 or 11, 64-bit | — |
| RAM | 8 GB | 16 GB |
| Disk | 2 GB (Path A) | 10 GB if building |
| Internet | Only to install and to fetch the model once | Not needed to run |

CareScribe checks RAM on launch. Below about 6 GB it warns and suggests a
smaller model rather than crashing — de-identification and review still work
normally, it is only generation that needs the memory.

---

## Where your files go

Approved documents are saved to:

```
C:\Users\<name>\AppData\Local\CareScribe\output\deidentified\
```

Paste that into the File Explorer address bar to open it.

A log of what the app did — timings and file sizes, **no patient data** — is
at:

```
C:\Users\<name>\AppData\Local\CareScribe\logs\carescribe.log
```

It is safe to send to someone for help. The app also shows this path at the
bottom of its window.

**The list matching placeholders to real names is never saved anywhere.** It
exists only while the app is open. Closing the app, or clicking
**Clear session / wipe PHI**, erases it. That is deliberate — it is the most
sensitive thing in the system, so it never touches the disk at all.

---

## If something goes wrong

| What you see | What to do |
|---|---|
| "Windows protected your PC" | Expected — unsigned app. **More info** → **Run anyway**. |
| Nothing happens for a minute | Normal on first launch. Wait — do not double-click again, you will start a second copy. |
| Window opens but stays blank | Give it 30 seconds. If it stays blank, close it and reopen. |
| Sidebar says "Presidio + spaCy unavailable" | The language model is missing. Path B: `python -m spacy download en_core_web_lg`. Path A: the build is incomplete — rebuild it. |
| Generation panel shows a setup card | Expected on a new PC. Click **Download the model** — one time, then it is remembered. |
| "CareScribe could not start" | Something in the copy is missing. Re-copy the whole `dist\CareScribe` folder, `_internal` included. |
| De-identify seems to hang | It should not any more. If it does, the log above says where it stalled — send that file. |
| "The de-identification model is not installed in this build" | The build is missing its language model. It needs rebuilding, not fixing on this machine. |
| Antivirus quarantines it | Known false positive with PyInstaller apps. Add an exclusion, or code-sign the build. |

---

## What this is, and is not

CareScribe is a **drafting aid**. It is not a compliance control and it does not
make anything HIPAA- or UK GDPR-compliant on its own.

- Automated de-identification **misses things**, and it also **over-redacts** —
  removing clinical detail that mattered. The review step is not optional.
- Generated drafts can misread the source. **Read every one.**
- Before using this on real patient records, validate it on your own documents
  and get it signed off under your governance framework.

The privacy model is that everything happens on your machine. That is enforced
in the code — see the invariants table in `README.md` — but it does not remove
your responsibility for what leaves the building afterwards.
