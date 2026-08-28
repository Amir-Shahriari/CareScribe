"""
Transport for the optional cloud generation backend.

Reached only when a deployer has set ``CARESCRIBE_CLOUD_PROVIDER`` and
``CARESCRIBE_CLOUD_API_KEY`` (see ``docs/deployer-cloud-note.md`` and
``core/backends.py``). Everything it sends is approved de-identified text with
placeholders — ``carenotes.assert_deidentified()`` has already run upstream and
the identity mapping is not reachable from here.

Standard library only, exactly like ``ollama_client``: no provider SDK is a
dependency, so "this app ships no third-party network client" stays a checkable
property. Two wire formats are supported:

* ``anthropic`` — the Messages API (``api.anthropic.com/v1/messages``).
* ``openai``    — the OpenAI Chat Completions shape, which Azure OpenAI, vLLM,
                  and most self-hosted or private gateways also speak. Point it
                  anywhere with ``CARESCRIBE_CLOUD_BASE_URL`` and name the model
                  with ``CARESCRIBE_CLOUD_MODEL``.

The API key is read from the environment at call time and is never stored on an
object, logged, or written to disk.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Iterator

PROVIDER_ENV = "CARESCRIBE_CLOUD_PROVIDER"
API_KEY_ENV = "CARESCRIBE_CLOUD_API_KEY"
BASE_URL_ENV = "CARESCRIBE_CLOUD_BASE_URL"
MODEL_ENV = "CARESCRIBE_CLOUD_MODEL"

# Stable Anthropic API version header. Not configurable — a value here that the
# provider does not recognise fails loudly, which is what we want.
ANTHROPIC_VERSION = "2023-06-01"

_DEFAULTS: dict[str, dict[str, str]] = {
    # A first-party Anthropic key has a sensible default model; a private or
    # self-hosted endpoint does not, so "openai" carries no default model and
    # MODEL_ENV is required for it.
    "anthropic": {"base_url": "https://api.anthropic.com", "model": "claude-opus-5"},
    "openai": {"base_url": "https://api.openai.com/v1"},
}

GENERATE_TIMEOUT = 900
MAX_TOKENS = 1600
# Zero on purpose: this is clinical documentation and an invented-but-plausible
# detail is the failure mode that matters. Matches backends.LocalGGUFBackend.
TEMPERATURE = 0.0


class CloudError(RuntimeError):
    """A recoverable problem talking to the configured cloud provider."""


def _config(provider: str) -> tuple[str, str, str]:
    """Return ``(api_key, base_url, model)`` from the environment, or raise."""
    key = (os.environ.get(API_KEY_ENV) or "").strip()
    if not key:
        raise CloudError(
            f"Cloud generation is configured for '{provider}' but {API_KEY_ENV} "
            "is not set in the environment."
        )
    defaults = _DEFAULTS.get(provider)
    if defaults is None:
        raise CloudError(
            f"Unknown cloud provider '{provider}'. Supported: "
            f"{', '.join(sorted(_DEFAULTS))}. For Azure OpenAI, a private "
            f"gateway, or a self-hosted server, use 'openai' and set {BASE_URL_ENV}."
        )
    base_url = (os.environ.get(BASE_URL_ENV) or defaults["base_url"]).rstrip("/")
    model = (os.environ.get(MODEL_ENV) or defaults.get("model") or "").strip()
    if not model:
        raise CloudError(
            f"Set {MODEL_ENV} to the model name your '{provider}' endpoint "
            "expects — a private or self-hosted endpoint has its own model names."
        )
    return key, base_url, model


def _post(url: str, headers: dict, payload: dict):
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        return urllib.request.urlopen(request, timeout=GENERATE_TIMEOUT)  # noqa: S310
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", "replace")[:500]
        except Exception:  # noqa: BLE001 — best effort at a useful message
            pass
        raise CloudError(
            f"The cloud provider rejected the request ({exc.code} {exc.reason})."
            + (f" {detail}" if detail else "")
        ) from exc
    except urllib.error.URLError as exc:
        raise CloudError(f"Could not reach the cloud provider: {exc.reason}") from exc


def _sse_data_lines(response) -> Iterator[str]:
    """Yield the payload of each ``data:`` line in an SSE stream."""
    for raw in response:
        line = raw.decode("utf-8", "replace").strip()
        if line.startswith("data:"):
            yield line[5:].strip()


def _stream_anthropic(
    base_url: str, key: str, model: str, system: str, prompt: str, stream: bool
) -> Iterator[str]:
    headers = {
        "x-api-key": key,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
        "stream": bool(stream),
    }
    response = _post(f"{base_url}/v1/messages", headers, payload)
    with response:
        if not stream:
            body = json.loads(response.read().decode("utf-8"))
            for block in body.get("content", []):
                if block.get("type") == "text" and block.get("text"):
                    yield block["text"]
            return
        for data in _sse_data_lines(response):
            if not data or data == "[DONE]":
                continue
            try:
                event = json.loads(data)
            except json.JSONDecodeError:
                continue
            etype = event.get("type")
            if etype == "content_block_delta":
                piece = (event.get("delta") or {}).get("text")
                if piece:
                    yield piece
            elif etype == "error":
                message = (event.get("error") or {}).get("message") or "cloud provider error"
                raise CloudError(str(message))
            elif etype == "message_stop":
                break


def _stream_openai(
    base_url: str, key: str, model: str, system: str, prompt: str, stream: bool
) -> Iterator[str]:
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "stream": bool(stream),
    }
    response = _post(f"{base_url}/chat/completions", headers, payload)
    with response:
        if not stream:
            body = json.loads(response.read().decode("utf-8"))
            choices = body.get("choices") or [{}]
            content = (choices[0].get("message") or {}).get("content")
            if content:
                yield content
            return
        for data in _sse_data_lines(response):
            if not data or data == "[DONE]":
                continue
            try:
                event = json.loads(data)
            except json.JSONDecodeError:
                continue
            choices = event.get("choices") or []
            if not choices:
                continue
            piece = (choices[0].get("delta") or {}).get("content")
            if piece:
                yield piece


_STREAMERS = {"anthropic": _stream_anthropic, "openai": _stream_openai}


def stream_generation(
    provider: str, system: str, prompt: str, *, stream: bool = True
) -> Iterator[str]:
    """Stream a completion from the configured cloud provider, yielding text.

    Raises :class:`CloudError` for any recoverable problem — bad configuration,
    an unreachable host, or a provider-side rejection.
    """
    provider = (provider or "").strip().lower()
    key, base_url, model = _config(provider)
    yield from _STREAMERS[provider](base_url, key, model, system, prompt, stream)


__all__ = [
    "ANTHROPIC_VERSION",
    "API_KEY_ENV",
    "BASE_URL_ENV",
    "MODEL_ENV",
    "PROVIDER_ENV",
    "CloudError",
    "stream_generation",
]
