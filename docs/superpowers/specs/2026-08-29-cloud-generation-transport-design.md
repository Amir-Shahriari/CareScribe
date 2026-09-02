# Cloud generation transport (`CloudBackend`) — design

Status: implemented
Date: 2026-08-29

## Problem

`core/backends.py` already has the full gate and selection logic for an
optional off-device generation backend: `cloud_provider()`, `cloud_key_present()`,
`cloud_enabled()` (two required env switches), `CloudBackend.__init__` validation,
last place in `select_backend()`'s ladder, and the `privacy_indicator()` change
when cloud is on. All of it is tested. But `CloudBackend.generate()` raised
"No transport is wired up" — the feature could be configured and could never run.

The user's production plan is API-based generation, often against a **private or
self-hosted endpoint**, so a real transport is the next increment.

## Scope

In scope: implement `CloudBackend.generate()` as a streaming transport for two
wire formats — Anthropic Messages API and the OpenAI Chat Completions shape
(which Azure OpenAI, vLLM, and most private gateways also speak). Standard
library HTTP only, matching `ollama_client`.

Out of scope: changing the gate, the selection order, or the privacy indicator;
adding a provider SDK dependency; retries/backoff beyond a single attempt;
non-streaming as anything more than a fallback branch; RAG / agent work (C/D/E).

## Architecture

### New module `core/cloud_client.py`

Mirrors `ollama_client`: `urllib.request` only, a module-level `CloudError`, a
`stream_generation(provider, system, prompt, *, stream=True) -> Iterator[str]`
entry point.

- `_config(provider)` reads `CARESCRIBE_CLOUD_API_KEY` (required),
  `CARESCRIBE_CLOUD_BASE_URL` (optional, per-provider default),
  `CARESCRIBE_CLOUD_MODEL` (optional for `anthropic` → defaults `claude-opus-5`;
  **required** for `openai` — a private endpoint has its own model names).
  The key is a local variable, never stored on an object.
- `_stream_anthropic` — `POST {base}/v1/messages`, headers `x-api-key` +
  `anthropic-version: 2023-06-01`, body `{model, max_tokens, system, messages,
  stream}`. Parses SSE `data:` lines: `content_block_delta` → `delta.text`,
  `error` → raise `CloudError`, `message_stop` → stop.
- `_stream_openai` — `POST {base}/chat/completions`, header
  `Authorization: Bearer …`, body `{model, messages:[system,user], max_tokens,
  temperature: 0.0, stream}`. Parses SSE `data:` lines: `choices[0].delta.content`,
  `[DONE]` → stop.
- `_post` translates `HTTPError`/`URLError` into `CloudError` with the status
  and a truncated body.

`temperature` is 0.0 for the same reason `LocalGGUFBackend` pins it there.

### `core/backends.py`

`CloudBackend.generate()` becomes:

```python
from . import cloud_client
try:
    yield from cloud_client.stream_generation(self.provider, system, prompt, stream=stream)
except cloud_client.CloudError as exc:
    raise BackendError(str(exc)) from exc
```

Lazy import avoids a cycle (`cloud_client` imports nothing from `backends`).
`__init__`, the gate functions, and `select_backend()` are untouched. The
module still contains no key literal and stores no key on the instance
(`test_the_key_is_read_only_from_the_environment` still passes).

### Privacy properties (unchanged, inherited)

`carenotes.generate_document()` runs `assert_deidentified()` on the source and
the built prompt **before** calling `backend.generate()`. The mapping is not a
parameter to `CloudBackend` or `cloud_client`. So the cloud path sends exactly
what every other backend sends: approved de-identified text with placeholders.

## Testing

`tests/test_cloud_client.py` (10 tests), `urlopen` stubbed, no network:

- Anthropic stream yields concatenated text deltas; request URL, `x-api-key`,
  `anthropic-version`, and body shape are asserted.
- OpenAI stream honours `CARESCRIBE_CLOUD_BASE_URL` and `CARESCRIBE_CLOUD_MODEL`;
  `Authorization: Bearer` and the system/user message shape are asserted.
- `openai` without `CARESCRIBE_CLOUD_MODEL` raises before any POST.
- A missing key raises before any POST.
- An unknown provider's error names the `openai` escape hatch.
- An `HTTPError` (401) and a mid-stream `error` event both become `CloudError`.
- `CloudBackend.generate()` streams via the transport and translates
  `CloudError` → `BackendError`.
- `core/cloud_client.py` source contains no key-shaped literal.

Full suite: 975 passed, 1 skipped.

## Follow-ups (not blocking)

- Retry/backoff on 429 and 5xx (the SDKs do this; the stdlib client does not).
- A `describe_backends()` field distinguishing "cloud configured, transport
  reachable" from "configured but unreachable", for a better setup card.
