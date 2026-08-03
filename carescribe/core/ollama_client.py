"""
Thin wrapper around a *local* Ollama server.

Design notes
------------
* The host is hard-pinned to loopback. We deliberately do NOT honour the
  ``OLLAMA_HOST`` environment variable, because a stray value there could
  silently ship PHI to a remote machine. If you genuinely need a different
  local port, change ``OLLAMA_HOST`` below.
* Every entry point degrades gracefully: if the server is down or has no
  models installed, callers get ``False`` / ``[]`` / a clear ``OllamaError``
  instead of a traceback.
"""

from __future__ import annotations

from typing import Any, Iterator

import ollama

# Pinned to loopback on purpose — see module docstring.
OLLAMA_HOST = "http://127.0.0.1:11434"

# Short timeout for "is the server there?" probes, long one for generation.
PROBE_TIMEOUT = 3.0
CHAT_TIMEOUT = 600.0


class OllamaError(RuntimeError):
    """Raised for any recoverable problem talking to the local Ollama server."""


# The message we show the user whenever the server can't be reached.
NOT_RUNNING_HINT = (
    "Ollama does not appear to be running on 127.0.0.1:11434.\n\n"
    "Start Ollama and run:  `ollama pull llama3.1:8b`"
)


def _client(timeout: float) -> ollama.Client:
    """Build a client bound to the local server with an explicit timeout."""
    return ollama.Client(host=OLLAMA_HOST, timeout=timeout)


def is_available() -> bool:
    """Return True if the local Ollama server responds, False otherwise.

    Never raises — the UI uses this for a status indicator.
    """
    try:
        _client(PROBE_TIMEOUT).list()
        return True
    except Exception:
        return False


def _model_name(entry: Any) -> str | None:
    """Pull the model name out of one ``list()`` entry.

    The ollama client has changed shape across versions: older releases return
    plain dicts keyed ``"name"``, newer ones return pydantic objects with a
    ``.model`` attribute. Handle both rather than pinning ourselves to one.
    """
    for attr in ("model", "name"):
        value = getattr(entry, attr, None)
        if isinstance(value, str) and value:
            return value
    if isinstance(entry, dict):
        for key in ("model", "name"):
            value = entry.get(key)
            if isinstance(value, str) and value:
                return value
    return None


def list_models() -> list[str]:
    """Return the names of locally-installed models, sorted.

    Returns an empty list if the server is unreachable or nothing is pulled;
    the UI distinguishes the two cases via :func:`is_available`.
    """
    try:
        response = _client(PROBE_TIMEOUT).list()
    except Exception:
        return []

    # Same version dance as _model_name: object with .models, or dict.
    entries = getattr(response, "models", None)
    if entries is None and isinstance(response, dict):
        entries = response.get("models", [])
    entries = entries or []

    names = {name for name in (_model_name(e) for e in entries) if name}
    return sorted(names)


def _extract_content(chunk: Any) -> str:
    """Get ``message.content`` out of a chat response/chunk, dict or object."""
    message = getattr(chunk, "message", None)
    if message is None and isinstance(chunk, dict):
        message = chunk.get("message")
    if message is None:
        return ""

    content = getattr(message, "content", None)
    if content is None and isinstance(message, dict):
        content = message.get("content")
    return content or ""


def chat(
    model: str,
    system: str,
    user: str,
    stream: bool = False,
    timeout: float = CHAT_TIMEOUT,
    temperature: float = 0.1,
    num_ctx: int | None = 8192,
) -> str | Iterator[str]:
    """Send a single-turn system+user chat to a local model.

    With ``stream=False`` returns the full response text. With ``stream=True``
    returns a generator of text deltas, suitable for ``st.write_stream``.

    Raises :class:`OllamaError` with an actionable message on any failure.
    """
    if not model:
        raise OllamaError("No model selected. Pick one in the sidebar.")

    options: dict[str, Any] = {"temperature": temperature}
    if num_ctx:
        # 8k context fits comfortably alongside a Q4_K_M 7-9B model on 8GB VRAM.
        options["num_ctx"] = num_ctx

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    client = _client(timeout)

    if not stream:
        try:
            response = client.chat(model=model, messages=messages, options=options)
        except Exception as exc:  # noqa: BLE001 - surfaced verbatim to the UI
            raise OllamaError(_friendly_error(exc, model)) from exc
        return _extract_content(response)

    def _stream() -> Iterator[str]:
        try:
            for chunk in client.chat(
                model=model, messages=messages, options=options, stream=True
            ):
                text = _extract_content(chunk)
                if text:
                    yield text
        except Exception as exc:  # noqa: BLE001
            raise OllamaError(_friendly_error(exc, model)) from exc

    return _stream()


def _friendly_error(exc: Exception, model: str) -> str:
    """Turn a client/transport exception into something a user can act on."""
    text = str(exc)
    lowered = text.lower()

    if any(s in lowered for s in ("connection", "refused", "connect", "max retries")):
        return NOT_RUNNING_HINT
    if "timeout" in lowered or "timed out" in lowered:
        return (
            f"The model `{model}` timed out. Long documents on an 8GB GPU can be "
            "slow — try a shorter document or a smaller model."
        )
    if "not found" in lowered or "no such model" in lowered:
        return f"Model `{model}` is not installed locally. Run:  `ollama pull {model}`"
    if "memory" in lowered or "vram" in lowered:
        return (
            f"Not enough VRAM to load `{model}`. On 8GB, stick to a 7-9B Q4_K_M model "
            "and use the same model for both stages."
        )
    return f"Ollama call failed: {text}"
