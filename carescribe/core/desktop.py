"""
Desktop-app plumbing: where things live once CareScribe is a double-click app.

Running from a source checkout and running from a PyInstaller bundle differ in
two ways that matter, and both are handled here so nothing else has to care:

* **Resources** (the spaCy model, the GGUF, prompt templates, Streamlit config)
  sit next to the source tree in a checkout and inside ``sys._MEIPASS`` in a
  bundle. :func:`resource_path` resolves either.
* **Outputs** must not be written next to the executable. On Windows that is
  often ``C:\\Program Files``, which is not writable, and on macOS it is inside
  a signed ``.app`` whose contents must not change. Outputs go to a per-user
  app-data directory instead.

The identity mapping is not written to either location. It is not written
anywhere — see :mod:`carescribe.core.batch` for the enumerated write paths.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "CareScribe"

# A 3B Q4 model needs roughly this much RAM resident, plus headroom for the
# spaCy model and the Streamlit process. Below it, generation will swap or be
# killed, so the UI offers the alternatives instead of letting it crash.
MIN_RAM_GB_FOR_LOCAL_MODEL = 6.0
RECOMMENDED_RAM_GB = 8.0

DEFAULT_MODEL_FILENAME = "Qwen2.5-3B-Instruct-Q4_K_M.gguf"

# Where the bundled model is fetched from if it could not be included in the
# build. Downloaded once, then the app is offline for good.
MODEL_DOWNLOAD_URL = (
    "https://huggingface.co/bartowski/Qwen2.5-3B-Instruct-GGUF/resolve/main/"
    "Qwen2.5-3B-Instruct-Q4_K_M.gguf?download=true"
)
MODEL_APPROX_BYTES = 1_930_000_000


def is_frozen() -> bool:
    """True when running from a PyInstaller bundle rather than a checkout."""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def bundle_root() -> Path:
    """The directory bundled data files were unpacked to, or the repo root."""
    if is_frozen():
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent.parent.parent


def resource_path(*parts: str) -> Path:
    """Resolve a bundled resource, in a build or in a checkout."""
    return bundle_root().joinpath(*parts)


def app_data_dir() -> Path:
    """Per-user writable directory for this app's outputs.

    Windows: ``%LOCALAPPDATA%\\CareScribe``
    macOS:   ``~/Library/Application Support/CareScribe``
    Linux:   ``$XDG_DATA_HOME/CareScribe`` or ``~/.local/share/CareScribe``
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return base / APP_NAME


def output_dir() -> Path:
    """Where approved de-identified documents are written."""
    return app_data_dir() / "output" / "deidentified"


def models_dir() -> Path:
    """Where a fetched-once model is cached."""
    return app_data_dir() / "models"


def ensure_dirs() -> None:
    for path in (output_dir(), models_dir()):
        path.mkdir(parents=True, exist_ok=True)


def find_local_model(filename: str = DEFAULT_MODEL_FILENAME) -> Path | None:
    """Locate the GGUF: bundled first, then the per-user cache, else ``None``.

    Bundled wins so a signed build is self-contained and offline from the first
    launch. The cache is the fallback for builds shipped without the weights.
    """
    for candidate in (
        resource_path("models", filename),
        models_dir() / filename,
        Path(__file__).resolve().parent.parent.parent / "models" / filename,
    ):
        if candidate.is_file() and candidate.stat().st_size > 100_000_000:
            return candidate
    return None


def available_ram_gb() -> float:
    """Total system RAM in GB, or 0.0 if it cannot be determined."""
    try:
        import psutil

        return psutil.virtual_memory().total / 1_000_000_000
    except Exception:  # noqa: BLE001 — a missing probe must not stop the app
        return 0.0


def ram_verdict() -> dict:
    """Whether this machine can run the bundled local model.

    Returns a verdict rather than raising: a weak laptop should get a plain
    warning and the alternatives, not a crash on launch.
    """
    total = available_ram_gb()
    if total <= 0:
        return {"ok": True, "total_gb": 0.0, "message": ""}
    if total < MIN_RAM_GB_FOR_LOCAL_MODEL:
        return {
            "ok": False,
            "total_gb": total,
            "message": (
                f"This computer has about {total:.0f} GB of memory. The built-in "
                f"model needs roughly {MIN_RAM_GB_FOR_LOCAL_MODEL:.0f} GB free to "
                "run comfortably.\n\n"
                "De-identification and review work normally. For generation you "
                "can install Ollama and pull a smaller model "
                "(`ollama pull qwen2.5:1.5b`), which CareScribe will use "
                "automatically."
            ),
        }
    return {"ok": True, "total_gb": total, "message": ""}


def streamlit_config_path() -> Path:
    """The bundled Streamlit config that pins the server to loopback."""
    return resource_path(".streamlit", "config.toml")


__all__ = [
    "APP_NAME",
    "DEFAULT_MODEL_FILENAME",
    "MIN_RAM_GB_FOR_LOCAL_MODEL",
    "MODEL_APPROX_BYTES",
    "MODEL_DOWNLOAD_URL",
    "app_data_dir",
    "available_ram_gb",
    "bundle_root",
    "ensure_dirs",
    "find_local_model",
    "is_frozen",
    "models_dir",
    "output_dir",
    "ram_verdict",
    "resource_path",
    "streamlit_config_path",
]
