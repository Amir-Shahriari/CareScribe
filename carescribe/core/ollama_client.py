"""
Local Ollama client — pinned to the loopback interface.

Generation is the first part of CareScribe that talks to anything at all, so
the surface it can talk to is deliberately tiny: one hard-coded host,
``127.0.0.1:11434``, and nothing else.

``OLLAMA_HOST`` is **ignored on purpose**. It is the documented way to point an
Ollama client at another machine, which is precisely what must not be possible
here — a variable set for an unrelated reason would quietly turn a local-only
tool into one that ships clinical text off the box. Never reading it is a
stronger guarantee than reading it and validating it.

Even so, what reaches this module is de-identified text full of placeholders.
The loopback pin is the second line of defence, not the first.

Talks to the HTTP API through the standard library rather than the ``ollama``
package: that package is deliberately absent from ``requirements.txt``, and
leaving it uninstalled keeps "this stage has no third-party network client" a
checkable property.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Iterator

# Not configurable. See the module docstring.
OLLAMA_HOST = "127.0.0.1"
OLLAMA_PORT = 11434
BASE_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"

# A weak CPU box takes a while to produce the first token of an 8B model, so the
# connect probe is short and the generation read is generous.
CONNECT_TIMEOUT = 3
GENERATE_TIMEOUT = 900

# Preference order when auto-detecting. An 8B-class instruct model is the sweet
# spot for a clinical draft on CPU; smaller models lose the structure.
PREFERRED_MODELS = (
    "llama3.1:8b",
    "llama3.1:8b-instruct-q4_K_M",
    "llama3:8b",
    "qwen2.5:7b",
    "mistral:7b",
    "phi3:medium",
)

DAEMON_DOWN_MESSAGE = (
    "Ollama does not appear to be running on 127.0.0.1:11434.\n\n"
    "Start it and try again:\n"
    "    ollama serve\n\n"
    "On Windows, launching the Ollama app starts the daemon."
)


class OllamaError(RuntimeError):
    """Raised for any recoverable problem talking to the local Ollama server."""


def missing_model_message(model: str, available: list[str] | None = None) -> str:
    """The exact command to fix a missing model, plus what is installed."""
    lines = [
        f"The model '{model}' is not installed locally.",
        "",
        "Pull it with:",
        f"    ollama pull {model}",
    ]
    if available:
        lines += ["", "Installed models: " + ", ".join(available)]
    return "\n".join(lines)


def _request(path: str, payload: dict | None = None, timeout: int = CONNECT_TIMEOUT):
    """Open a request against the pinned loopback base URL."""
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        f"{BASE_URL}{path}", data=data, headers={"Content-Type": "application/json"}
    )
    return urllib.request.urlopen(request, timeout=timeout)  # noqa: S310 — fixed loopback URL


def is_up() -> bool:
    """True if the local Ollama daemon answers. Never raises."""
    try:
        with _request("/api/tags") as response:
            return response.status == 200
    except Exception:  # noqa: BLE001 — "is it up?" must not throw
        return False


def list_models() -> list[str]:
    """Locally-installed model names, sorted. Empty list if the daemon is down."""
    try:
        with _request("/api/tags") as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:  # noqa: BLE001
        return []
    names = [
        str(item.get("name") or item.get("model") or "").strip()
        for item in payload.get("models", [])
    ]
    return sorted(name for name in names if name)


def default_model(available: list[str] | None = None) -> str | None:
    """The best installed model to draft with, or ``None`` if none are installed.

    Never raises on a missing model — the caller surfaces the pull command.
    """
    models = available if available is not None else list_models()
    if not models:
        return None
    for preferred in PREFERRED_MODELS:
        if preferred in models:
            return preferred
    for model in models:
        lowered = model.lower()
        if "8b" in lowered or "7b" in lowered:
            return model
    return models[0]


def status() -> dict:
    """Everything the UI needs to describe the local generation backend."""
    up = is_up()
    models = list_models() if up else []
    return {
        "up": up,
        "host": f"{OLLAMA_HOST}:{OLLAMA_PORT}",
        "models": models,
        "default_model": default_model(models) if models else None,
        "message": "" if up else DAEMON_DOWN_MESSAGE,
    }


def generate(
    model: str,
    system: str,
    prompt: str,
    stream: bool = True,
    *,
    temperature: float = 0.2,
) -> Iterator[str]:
    """Stream a completion from the local model, yielding text chunks.

    Low temperature by default: this is clinical documentation, and the failure
    mode that matters is the model inventing a plausible-looking detail.
    """
    if not is_up():
        raise OllamaError(DAEMON_DOWN_MESSAGE)

    installed = list_models()
    if model not in installed:
        raise OllamaError(missing_model_message(model, installed))

    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": bool(stream),
        "options": {"temperature": float(temperature)},
    }

    try:
        response = _request("/api/generate", payload, timeout=GENERATE_TIMEOUT)
    except urllib.error.URLError as exc:
        raise OllamaError(f"Could not reach the local Ollama server: {exc}") from exc

    with response:
        if not stream:
            body = json.loads(response.read().decode("utf-8"))
            text = str(body.get("response", ""))
            if text:
                yield text
            return

        for raw_line in response:
            line = raw_line.decode("utf-8").strip()
            if not line:
                continue
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError:
                continue
            if chunk.get("error"):
                raise OllamaError(str(chunk["error"]))
            piece = chunk.get("response")
            if piece:
                yield piece
            if chunk.get("done"):
                break


__all__ = [
    "BASE_URL",
    "CONNECT_TIMEOUT",
    "DAEMON_DOWN_MESSAGE",
    "GENERATE_TIMEOUT",
    "OLLAMA_HOST",
    "OLLAMA_PORT",
    "OllamaError",
    "default_model",
    "generate",
    "is_up",
    "list_models",
    "missing_model_message",
    "status",
]
