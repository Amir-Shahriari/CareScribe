# CareScribe — a one-page guide

CareScribe de-identifies clinical documents, lets you review every change, and
drafts notes and letters. **Everything happens on your own computer.** No
patient data is uploaded anywhere.

## Install

**Windows** — run `CareScribeSetup.exe` once. It puts CareScribe on your desktop
and in the Start menu. Launch it from the desktop icon like any other app.

**Mac** — open `CareScribe.dmg` and drag CareScribe into Applications. From
there you can drag it to the Dock.

That is the whole installation. There is nothing to configure, no account, no
API key, and no Python to install. Everything runs on your computer.

To remove it later: Windows, use Add/Remove Programs; Mac, drag it from
Applications to the Bin. Your saved documents are left alone.

**You may see a security warning the first time.** Windows says "Windows
protected your PC"; macOS says the developer cannot be verified. That happens
because of how the app was distributed to you, not because of what it does — ask
whoever gave you the file to confirm before continuing.

## Using it

1. **Load** — drag in PDF, Word, or text files, or point at a folder.
2. **De-identify** — click the button. The first document takes a few seconds
   while the language model loads; the rest are fast.
3. **Review** — this is the part that matters, and the app will not let you skip
   it.
   - The **identifier table** lists everything found. Correct anything wrong,
     delete a false positive, or set **Keep** to leave something in.
   - **Highlighted spans** in the preview are things that *might* be identifiers
     the tools missed. Most will be nothing. Each needs a decision: redact it, or
     mark it not an identifier.
   - A short **checklist** appears, adapted to the document. A plain note gets
     two items; one with tables, relatives, or text boxes gets a few more.
   - **Approve** unlocks only when the checklist is complete and the safety
     sweep is clean.
4. **Generate** — pick a template (SOAP note, GP letter, discharge summary, or
   paste your own house format) and click Generate. On an ordinary laptop this
   takes about a minute. The draft streams in as it is written.
5. **Two versions come out:**
   - The **draft** still shows placeholders like `[PATIENT]`. Safe to share.
   - **Re-identify for the patient record** puts the real names back. This
     happens on your computer, and this version is for your own records.

## A stronger model (optional)

The built-in model is small enough to run on any laptop. If you want better
drafts, install [Ollama](https://ollama.com) and run:

```
ollama pull llama3.1:8b
```

CareScribe will find it and use it automatically. Nothing else changes, and it
is still entirely on your computer.

## What you must know

- **This is a drafting aid, not a compliance control.** Automated
  de-identification is not a guarantee under HIPAA or UK GDPR.
- **Every document needs your review.** The tools miss things and they also
  over-redact — removing clinical detail that mattered. You are the only check
  on both.
- **Every draft needs reading.** The model can misread the source. Smaller
  models occasionally write something that was not in the document at all.
- **Before using this on real patient records**, validate it on your own
  documents and get it signed off under your governance framework.

## Where things are saved

- Windows: `%LOCALAPPDATA%\CareScribe\output\deidentified`
- Mac: `~/Library/Application Support/CareScribe/output/deidentified`

Only de-identified documents are saved there. The list matching placeholders to
real names is never written to disk at all — it exists only while the app is
open, and `Clear session / wipe PHI` erases it immediately.
