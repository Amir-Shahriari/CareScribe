"""
Is generation usable right now, and if not, what should the user do?

Kept separate from :mod:`carescribe.core.model_setup` on purpose. Everything in
*this* module only inspects: the filesystem, an importable package, environment
variables, and a loopback probe of an already-running Ollama daemon. Nothing
here reaches off the machine. The single outbound request the app can make lives
in ``model_setup.py`` and only runs when a user clicks to start it.

That split is the point. "Is a model present?" and "fetch a model" are different
questions with different privacy properties, and putting them in one module
would make the distinction impossible to state cleanly or test.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import streamlit as st

from . import backends, desktop, ollama_client

# What the UI should offer when nothing is usable yet.
ACTION_DOWNLOAD_MODEL = "download_model"
ACTION_PULL_OLLAMA = "pull_ollama_model"
ACTION_INSTALL_OLLAMA = "install_ollama"


@dataclass
class Status:
    """Which generation backends are usable at this moment."""

    ollama: bool = False
    local_gguf: bool = False
    cloud: bool = False
    ollama_running: bool = False
    ollama_models: list[str] = field(default_factory=list)
    model_path: str = ""
    llama_runtime: bool = False
    cloud_provider: str = ""
    recommended_action: str = ""

    @property
    def ready(self) -> bool:
        return bool(self.ollama or self.local_gguf or self.cloud)

    @property
    def preferred(self) -> str:
        """Which backend would actually be used, matching the backend ladder."""
        if self.ollama:
            return backends.BACKEND_OLLAMA
        if self.local_gguf:
            return backends.BACKEND_LOCAL_GGUF
        if self.cloud:
            return backends.BACKEND_CLOUD
        return ""


def _llama_runtime_available() -> bool:
    try:
        import llama_cpp  # noqa: F401
    except Exception:  # noqa: BLE001
        return False
    return True


@st.cache_data(ttl=5)
def generation_status() -> Status:
    """Inspect what is available, cached for 5 seconds.

    Called unconditionally on every rerun regardless of which step the
    practitioner is on, so this is cached rather than merely "cheap" — an
    uncached call here was a confirmed source of avoidable per-rerun cost
    during a large review batch. The Ollama probe is a loopback HTTP call to
    a daemon already running on this machine — it never leaves the box, and
    it fails closed to "not running".
    """
    running = ollama_client.is_up()
    models = ollama_client.list_models() if running else []

    model_file = desktop.find_local_model()
    runtime = _llama_runtime_available()

    status = Status(
        ollama=bool(running and models),
        local_gguf=bool(model_file is not None and runtime),
        cloud=backends.cloud_enabled(),
        ollama_running=running,
        ollama_models=models,
        model_path=str(model_file or ""),
        llama_runtime=runtime,
        cloud_provider=backends.cloud_provider(),
    )

    if not status.ready:
        if running and not models:
            # Ollama is installed and running but empty — pulling a model there
            # is fewer steps than anything else, and gives better output.
            status.recommended_action = ACTION_PULL_OLLAMA
        elif runtime:
            # The runtime is present, so the built-in model just needs fetching.
            status.recommended_action = ACTION_DOWNLOAD_MODEL
        else:
            status.recommended_action = ACTION_INSTALL_OLLAMA
    return status


def missing_reason(status: Status) -> str:
    """One plain sentence on why generation is not available yet."""
    if status.ready:
        return ""
    if status.ollama_running and not status.ollama_models:
        return "Ollama is running on this computer but has no model installed yet."
    if not status.llama_runtime and not status.ollama_running:
        return "No AI model is set up on this computer yet."
    if status.llama_runtime and not status.model_path:
        return "The AI model file has not been downloaded to this computer yet."
    return "No AI model is set up on this computer yet."


__all__ = [
    "ACTION_DOWNLOAD_MODEL",
    "ACTION_INSTALL_OLLAMA",
    "ACTION_PULL_OLLAMA",
    "Status",
    "generation_status",
    "missing_reason",
]
