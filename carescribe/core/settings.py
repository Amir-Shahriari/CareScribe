"""
Persisted app settings — which generation backend/model/temperature to use.

Lives at ``app_data_dir() / "settings.json"``. Deliberately excludes the
cloud API key: that stays session-only (``st.session_state`` in ``app.py``),
matching the guarantee in ``cloud_client.py`` that a key is never stored,
logged, or bundled. Everything else here is just a preference, safe to
persist in plain JSON.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path

from . import desktop

SETTINGS_FILENAME = "settings.json"


@dataclass
class Settings:
    # "" means "use the automatic ladder" — Ollama if up, else bundled GGUF,
    # else cloud if configured. A non-empty value pins one.
    backend: str = ""
    # "" means "use ollama_client.default_model()'s guess". A non-empty value
    # must be one of the currently-installed models or select_backend() falls
    # back to the guess rather than erroring.
    ollama_model: str = ""
    temperature: float = 0.0
    cloud_provider: str = ""
    cloud_base_url: str = ""
    cloud_model: str = ""


_FIELD_NAMES = {f.name for f in fields(Settings)}


def _path() -> Path:
    return desktop.app_data_dir() / SETTINGS_FILENAME


def load_settings() -> Settings:
    """Read persisted settings. A missing or unreadable file yields defaults."""
    path = _path()
    if not path.exists():
        return Settings()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return Settings()
    filtered = {k: v for k, v in data.items() if k in _FIELD_NAMES}
    return Settings(**filtered)


def save_settings(settings: Settings) -> None:
    """Persist non-secret settings, creating the app data dir if needed."""
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")


__all__ = ["Settings", "load_settings", "save_settings"]
