# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the CareScribe desktop app.

One spec for both platforms; the per-OS differences are the icon, the console
flag, and whether a ``BUNDLE`` (macOS ``.app``) is produced.

Streamlit is awkward to freeze: it discovers pages, static assets and its own
version at runtime through package metadata, so it needs ``copy_metadata`` and
its full data tree rather than just its Python modules. spaCy and Presidio are
the same — the model is data, not code.

Build with:
    pyinstaller packaging/carescribe.spec --noconfirm

Set CARESCRIBE_BUNDLE_MODEL=0 to build without the ~2 GB GGUF, in which case
the app fetches it once on first launch.
"""

import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_data_files, copy_metadata

ROOT = Path(SPECPATH).resolve().parent
BUNDLE_MODEL = os.environ.get("CARESCRIBE_BUNDLE_MODEL", "1") != "0"

# Written by packaging/make_icon.py, which every build script runs first.
ICON_PNG = ROOT / "packaging" / "carescribe.png"
ICON_ICO = ROOT / "packaging" / "carescribe.ico"
ICON_ICNS = ROOT / "packaging" / "carescribe.icns"

# PyInstaller raises on a missing icon path, so pass None when one is absent
# rather than failing a build over cosmetics.
def _icon(path):
    return str(path) if path.is_file() else None

datas = []
binaries = []
hiddenimports = []

# Packages that need their data files and metadata, not just their modules.
for package in (
    "streamlit",
    "spacy",
    "thinc",
    "presidio_analyzer",
    "llama_cpp",
    "webview",
    "docx",
    "pdfplumber",
    "pypdf",
    "pandas",
    "altair",
):
    try:
        pkg_datas, pkg_binaries, pkg_hidden = collect_all(package)
        datas += pkg_datas
        binaries += pkg_binaries
        hiddenimports += pkg_hidden
    except Exception as exc:  # noqa: BLE001 — an absent optional package is fine
        print(f"[carescribe.spec] skipping {package}: {exc}")

# Streamlit reads its own version, and its dependencies', from metadata.
for dist in (
    "streamlit", "spacy", "presidio-analyzer", "presidio-anonymizer",
    "python-docx", "pdfplumber", "pypdf", "pandas", "altair", "numpy",
    "llama-cpp-python", "pywebview", "psutil",
):
    try:
        datas += copy_metadata(dist)
    except Exception as exc:  # noqa: BLE001
        print(f"[carescribe.spec] no metadata for {dist}: {exc}")

# The spaCy model is a package of its own, and collect_data_files alone is not
# enough: spaCy validates a model against its distribution metadata before
# loading it, and a model that fails to validate is one spaCy tries to DOWNLOAD.
# On a clinic network behind a captive portal that does not fail, it hangs.
# collect_all pulls the module, its data and its binaries; copy_metadata is what
# stops the download path being reached at all.
for model in ("en_core_web_sm", "en_core_web_md", "en_core_web_lg"):
    try:
        import importlib.util as _util

        if _util.find_spec(model) is None:
            print(f"[carescribe.spec] spaCy model {model} not installed - skipping")
            continue
        model_datas, model_binaries, model_hidden = collect_all(model)
        datas += model_datas
        binaries += model_binaries
        hiddenimports += model_hidden
        hiddenimports.append(model)
        try:
            datas += copy_metadata(model)
        except Exception as meta_exc:  # noqa: BLE001
            print(f"[carescribe.spec] no metadata for {model}: {meta_exc}")
        print(f"[carescribe.spec] bundled spaCy model: {model}")
    except Exception as exc:  # noqa: BLE001
        print(f"[carescribe.spec] spaCy model {model} not bundled: {exc}")

# The app itself: source, prompts, protected terms, Streamlit config.
datas += [
    (str(ROOT / "carescribe"), "carescribe"),
    (str(ROOT / ".streamlit"), ".streamlit"),
]

# The icon travels as data too, so runtime code (window, about box) can find it.
for icon_file in (ICON_PNG, ICON_ICO, ICON_ICNS):
    if icon_file.is_file():
        datas.append((str(icon_file), "packaging"))

# The generation model. Large; optional at build time.
model_dir = ROOT / "models"
if BUNDLE_MODEL and model_dir.is_dir():
    for gguf in model_dir.glob("*.gguf"):
        datas.append((str(gguf), "models"))
        print(f"[carescribe.spec] bundling model: {gguf.name}")
elif BUNDLE_MODEL:
    print("[carescribe.spec] no models/*.gguf found — app will fetch on first run")

hiddenimports += [
    "carescribe", "carescribe.app", "carescribe.core",
    "streamlit.web.cli", "streamlit.runtime.scriptrunner.magic_funcs",
    "presidio_analyzer.predefined_recognizers",
    "sklearn.utils._typedefs", "srsly.msgpack.util", "blis",
]

block_cipher = None

a = Analysis(
    [str(ROOT / "run_app.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[str(ROOT / "packaging" / "hooks")],
    runtime_hooks=[str(ROOT / "packaging" / "hooks" / "rthook_carescribe.py")],
    excludes=["tkinter", "matplotlib", "pytest", "torch", "gliner"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# An instant splash. Unpacking a frozen Streamlit app takes a few seconds before
# Python is even ready, and without feedback a user double-clicks again and ends
# up with two servers. This is drawn by the bootloader, so it appears at once.
# Not supported on macOS by PyInstaller.
splash = None
if sys.platform != "darwin" and ICON_PNG.is_file():
    splash = Splash(
        str(ICON_PNG),
        binaries=a.binaries,
        datas=a.datas,
        text_pos=(10, 260),
        text_size=11,
        text_color="white",
        text_default="Starting CareScribe...",
        minify_script=True,
        always_on_top=False,
    )

exe = EXE(
    pyz,
    a.scripts,
    *( [splash] if splash else [] ),
    [],
    exclude_binaries=True,
    name="CareScribe",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    # No console window: a clinician double-clicks an icon and gets an app.
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=(sys.platform == "darwin"),
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_icon(ICON_ICO),
)

coll = COLLECT(
    exe,
    *( [splash.binaries] if splash else [] ),
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="CareScribe",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="CareScribe.app",
        icon=_icon(ICON_ICNS),
        bundle_identifier="uk.carescribe.desktop",
        info_plist={
            "CFBundleName": "CareScribe",
            "CFBundleDisplayName": "CareScribe",
            "NSHighResolutionCapable": True,
            # No camera, mic, or location. Declared so the OS prompt never
            # appears and a reviewer can see the app asks for nothing.
            "LSApplicationCategoryType": "public.app-category.medical",
        },
    )
