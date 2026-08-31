# Installing CareScribe

This guide covers installing and running CareScribe on Windows or macOS. The app
runs entirely on your own computer. It needs the internet once — a one-time model
download the first time you open it — and never again after that.

## Before you start

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Operating system | Windows 10/11 (64-bit) or macOS 12 or newer | — |
| Memory (RAM) | 6 GB | 8 GB |
| Free disk space | 3 GB | — |
| Internet | Once, for the first-run model download | — |

If your computer has less than 6 GB of RAM, CareScribe still installs and runs.
De-identification and document review work normally; only the draft-generation
step needs the smaller model described under **First launch**.

## Windows

1. Download `CareScribeSetup.exe` from the link you were sent.
2. Double-click it. Windows shows a blue box: **"Windows protected your PC."**
   This is expected — the app is not code-signed yet. Click **More info**, then
   **Run anyway**.
3. Follow the installer. It installs for your user account only, so it does not
   ask for an administrator password.
4. When it finishes you have a **CareScribe** desktop icon and a Start-menu
   entry. Open either one.

## macOS

1. Download `CareScribe.dmg` from the link you were sent.
2. Double-click the `.dmg` to open it, then drag the **CareScribe** icon onto
   the **Applications** folder shown in the same window.
3. Open **Applications**, **right-click** (or Control-click) CareScribe, and
   choose **Open**. macOS says it "cannot verify the developer" and offers an
   **Open** button — click it. You only need to do this the first time; after
   that a normal double-click works.
   - A plain double-click on the first run only offers a **Cancel** button, with
     no way through. Use right-click → **Open**.

## First launch

CareScribe opens in its own window — not a browser tab. It may take a few
seconds the first time while it unpacks.

If the installer did not include the language model, CareScribe offers to
download it once — about **1.9 GB**. Let it finish. After that the app works
with no network connection at all.

**On a computer with less than 6 GB of RAM**, CareScribe shows a message like:

> This computer has about *N* GB of memory. The built-in model needs roughly
> 6 GB free to run comfortably. De-identification and review work normally. For
> generation you can install Ollama and pull a smaller model
> (`ollama pull qwen2.5:1.5b`), which CareScribe will use automatically.

To do that on Windows:

1. Open **ollama.com/download** and install Ollama for Windows.
2. Launch it once — it runs quietly in the background.
3. Come back to CareScribe and click **Refresh**.

CareScribe then uses that smaller model for generation automatically.

## Where your files go

Approved, de-identified documents are written to a per-user folder:

| Platform | Location |
|----------|----------|
| Windows | `%LOCALAPPDATA%\CareScribe\output\deidentified` |
| macOS | `~/Library/Application Support/CareScribe/output/deidentified` |

The downloaded model is cached alongside it, under `CareScribe\models`. Nothing
is ever written next to the app itself, and the uninstaller leaves this folder
untouched so your output survives a reinstall.

## Updating

Download the newer installer and run it over the top of the existing
installation. Your output folder and the downloaded model are kept.

## If it will not start

- Run the installer again over the top — this repairs a damaged installation.
- Check your computer's RAM and free disk space against the table above.
- Make sure the first-run model download was allowed to finish.

Building CareScribe from source is a separate path for developers and is covered
in `SETUP_ON_A_NEW_PC.md`, not here.
