"""
Generation backends, layered so the app works with nothing installed.

Selection order, decided at runtime:

1. :class:`~carescribe.core.carenotes.OllamaBackend` — only if a local Ollama
   daemon is already answering. Someone who installed it did so to run a bigger
   model, so it wins when present.
2. :class:`LocalGGUFBackend` — the default. ``llama-cpp-python`` on the CPU with
   a small bundled Q4 model. This is what makes the app generate with no
   external install at all.
3. :class:`CloudBackend` — **off unless explicitly configured**, and even then
   only if a key is present in the environment. Never bundled, never a default,
   never reached by accident. Transport lives in :mod:`carescribe.core.cloud_client`
   (Anthropic Messages API, or the OpenAI-compatible shape for Azure / private /
   self-hosted endpoints).

All three see the same thing: approved de-identified text with placeholders.
Re-identification stays in Python, after generation. That is what makes the
cloud option defensible at all — the provider receives a document that has
already passed the residual sweep, and never the mapping.
"""

from __future__ import annotations

import os
from typing import Iterator

from . import desktop, ollama_client

# The deployer opts in by setting this to a provider name. Absent or empty means
# cloud generation does not exist as far as this app is concerned.
CLOUD_PROVIDER_ENV = "CARESCRIBE_CLOUD_PROVIDER"
CLOUD_API_KEY_ENV = "CARESCRIBE_CLOUD_API_KEY"

BACKEND_OLLAMA = "ollama"
BACKEND_LOCAL_GGUF = "local"
BACKEND_CLOUD = "cloud"


class BackendError(RuntimeError):
    """Raised when a backend cannot be used, with the fix in the message."""


def _truncation_error() -> BackendError:
    """Shared message for a completion cut off by the token/context budget.

    A half-filled clinical form that looks superficially complete is worse
    than an outright crash — nothing else in the pipeline can tell a
    truncated draft apart from a genuinely short one, so this has to be
    caught here, at the one place that sees ``finish_reason``.
    """
    return BackendError(
        "Generation was cut off by the token limit before the draft was "
        "complete. This form has more fields (or the source text is longer) "
        "than the current generation budget can cover — try again with fewer "
        "source documents, a smaller form, or a backend with more headroom "
        "(Ollama with a larger model, or cloud generation if configured)."
    )


# --------------------------------------------------------------------------
# 2. The default — a small quantised model on the CPU
# --------------------------------------------------------------------------

class LocalGGUFBackend:
    """CPU-only generation from a bundled GGUF via ``llama-cpp-python``.

    The model is loaded once per process and cached: a 3B Q4 takes a few
    seconds to map into memory, and paying that on every draft would make the
    app feel broken on the laptops it is aimed at.
    """

    _cache: dict = {}

    def __init__(
        self,
        model_path=None,
        *,
        context_tokens: int = 8192,
        # 4096, not the 1600 this started as. Measured against the bundled
        # 62-field biopsychosocial form (the largest shipped clinical form):
        # the model's own observed field-content density (~50 tokens/field
        # including the <<FIELD:key>> marker, from a real truncated run) puts
        # a full 62-field draft at roughly 3700-4000 completion tokens, so
        # 4096 is sized to that, not picked round. It is safe to set this
        # higher than what a given prompt leaves in the context window:
        # llama-cpp-python clamps ``max_tokens`` to whatever room remains
        # under ``n_ctx`` rather than erroring, so a large combined source
        # that leaves little headroom just generates less and reports
        # ``finish_reason == "length"`` — which ``generate()`` below turns
        # into a ``BackendError`` instead of a silent partial draft.
        max_tokens: int = 4096,
        # Zero, not the 0.2 the Ollama backend uses. Measured on the bundled 3B:
        # at 0.2 it invented "anxiety and occasional insomnia" and "a history of
        # depression" for a source that contained neither; at 0.0 the same
        # prompt produced [not documented] in every unsupported section. A small
        # model has less headroom to be creative with, and in clinical
        # documentation creativity is the failure mode.
        temperature: float = 0.0,
        threads: int | None = None,
    ) -> None:
        self.model_path = str(model_path or "") or None
        self.context_tokens = context_tokens
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.threads = threads

    @staticmethod
    def available() -> bool:
        """True if the runtime and a model file are both present."""
        try:
            import llama_cpp  # noqa: F401
        except Exception:  # noqa: BLE001
            return False
        return desktop.find_local_model() is not None

    def _resolve_path(self) -> str:
        if self.model_path:
            return self.model_path
        found = desktop.find_local_model()
        if found is None:
            raise BackendError(
                "The built-in model file is missing. Reinstall CareScribe, or "
                "install Ollama and pull a model to use that instead."
            )
        return str(found)

    def _llama(self):
        path = self._resolve_path()
        cached = LocalGGUFBackend._cache.get(path)
        if cached is not None:
            return cached
        try:
            from llama_cpp import Llama
        except Exception as exc:  # noqa: BLE001
            raise BackendError(
                "The local generation runtime (llama-cpp-python) is not "
                f"available: {exc}"
            ) from exc

        try:
            model = Llama(
                model_path=path,
                n_ctx=self.context_tokens,
                n_threads=self.threads or max(1, (os.cpu_count() or 4) // 2),
                verbose=False,
            )
        except Exception as exc:  # noqa: BLE001
            raise BackendError(f"The local model could not be loaded: {exc}") from exc
        LocalGGUFBackend._cache[path] = model
        return model

    def generate(
        self, system: str, prompt: str, stream: bool = True, *, grammar: str | None = None
    ) -> Iterator[str]:
        model = self._llama()
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]
        kwargs: dict = dict(
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=bool(stream),
        )
        # A GBNF grammar constrains decoding structurally (see
        # carescribe.core.grammar). Best-effort: a compile failure or a missing
        # runtime feature just means unconstrained generation.
        if grammar:
            from carescribe.core.grammar import compile_grammar

            compiled = compile_grammar(grammar)
            if compiled is not None:
                kwargs["grammar"] = compiled
        try:
            completion = model.create_chat_completion(**kwargs)
        except Exception as exc:  # noqa: BLE001
            raise BackendError(f"Local generation failed: {exc}") from exc

        if not stream:
            choice = completion["choices"][0]
            if choice.get("finish_reason") == "length":
                raise _truncation_error()
            yield choice["message"]["content"]
            return

        # llama-cpp-python's chat-completion stream carries "finish_reason":
        # None on every chunk except the last, where it is "stop" (natural
        # completion) or "length" (cut off by the token budget / remaining
        # context). That final chunk's delta is empty, so it never yields
        # text — only the reason is read from it.
        finish_reason = None
        for chunk in completion:
            choice = chunk.get("choices", [{}])[0]
            piece = choice.get("delta", {}).get("content")
            if piece:
                yield piece
            reason = choice.get("finish_reason")
            if reason is not None:
                finish_reason = reason

        if finish_reason == "length":
            raise _truncation_error()


# --------------------------------------------------------------------------
# 3. The optional one — off unless a deployer turns it on
# --------------------------------------------------------------------------

def cloud_provider() -> str:
    """The configured provider name, or "" when cloud generation is off."""
    return (os.environ.get(CLOUD_PROVIDER_ENV) or "").strip()


def cloud_key_present() -> bool:
    return bool((os.environ.get(CLOUD_API_KEY_ENV) or "").strip())


def cloud_enabled() -> bool:
    """Cloud generation exists only with BOTH an explicit provider and a key.

    Two separate switches on purpose. A key left in the environment by another
    tool must not silently enable off-device generation, and naming a provider
    without a key must fail loudly rather than fall back to it.
    """
    return bool(cloud_provider()) and cloud_key_present()


class CloudBackend:
    """A remote provider, reachable only when explicitly configured.

    Receives approved de-identified text and nothing else — the same input the
    local backends get. The key is read from the environment at call time (in
    :mod:`carescribe.core.cloud_client`) and is never written, logged, or
    bundled.

    Enabling this is still a deployment decision that needs an
    information-governance sign-off and a paid no-training tier — see
    ``docs/deployer-cloud-note.md``. The two-switch gate and the last-place
    position in the selection ladder are what stop it being tripped into.
    """

    def __init__(self, provider: str | None = None) -> None:
        self.provider = provider or cloud_provider()
        if not self.provider:
            raise BackendError(
                "Cloud generation is not configured. It is off by default and "
                f"requires {CLOUD_PROVIDER_ENV} to be set."
            )
        if not cloud_key_present():
            raise BackendError(
                f"Cloud generation is configured for '{self.provider}' but no "
                f"API key is present. Set {CLOUD_API_KEY_ENV} in the "
                "environment. CareScribe never bundles or stores a key."
            )

    def generate(
        self, system: str, prompt: str, stream: bool = True, *, grammar: str | None = None
    ) -> Iterator[str]:
        # A remote API cannot be handed a GBNF grammar generically; the
        # placeholder/format guarantees still hold via assert_deidentified and
        # parse_fields' "Not documented" default.
        from . import cloud_client

        try:
            yield from cloud_client.stream_generation(
                self.provider, system, prompt, stream=stream
            )
        except cloud_client.CloudError as exc:
            raise BackendError(str(exc)) from exc


# --------------------------------------------------------------------------
# Selection
# --------------------------------------------------------------------------

def describe_backends() -> dict:
    """What is available right now, for the UI's status line."""
    ollama_up = ollama_client.is_up()
    ollama_models = ollama_client.list_models() if ollama_up else []
    return {
        "ollama": {
            "available": bool(ollama_up and ollama_models),
            "models": ollama_models,
            "default_model": ollama_client.default_model(ollama_models)
            if ollama_models
            else None,
        },
        "local": {
            "available": LocalGGUFBackend.available(),
            "model_path": str(desktop.find_local_model() or ""),
        },
        "cloud": {
            "available": cloud_enabled(),
            "provider": cloud_provider(),
            "key_present": cloud_key_present(),
        },
    }


def select_backend(
    prefer: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
):
    """Pick a backend. Returns ``(kind, backend, label)``.

    ``prefer`` lets the UI honour an explicit backend choice; without it the
    ladder is Ollama -> bundled GGUF -> cloud-only-if-configured. ``model``
    pins an explicit installed Ollama model (falling back to the guessed
    default if it is not actually installed — a stale saved preference must
    not turn into an error). ``temperature`` overrides the backend's own
    default on Ollama and the bundled GGUF backend.
    """
    state = describe_backends()

    def build(kind: str):
        if kind == BACKEND_OLLAMA and state["ollama"]["available"]:
            from .carenotes import OllamaBackend

            chosen = model if model in state["ollama"]["models"] else None
            chosen = chosen or state["ollama"]["default_model"]
            kwargs = {} if temperature is None else {"temperature": temperature}
            return kind, OllamaBackend(chosen, **kwargs), f"Ollama · {chosen}"
        if kind == BACKEND_LOCAL_GGUF and state["local"]["available"]:
            from pathlib import Path

            name = Path(state["local"]["model_path"]).name
            kwargs = {} if temperature is None else {"temperature": temperature}
            return kind, LocalGGUFBackend(**kwargs), f"Built-in model · {name}"
        if kind == BACKEND_CLOUD and state["cloud"]["available"]:
            provider = state["cloud"]["provider"]
            return kind, CloudBackend(provider), f"Cloud · {provider}"
        return None

    if prefer:
        chosen = build(prefer)
        if chosen:
            return chosen

    for kind in (BACKEND_OLLAMA, BACKEND_LOCAL_GGUF, BACKEND_CLOUD):
        chosen = build(kind)
        if chosen:
            return chosen

    raise BackendError(
        "No generation backend is available.\n\n"
        "De-identification and review work without one. For generation, either "
        "reinstall CareScribe so the built-in model is present, or install "
        "Ollama and run: ollama pull qwen2.5:3b"
    )


__all__ = [
    "BACKEND_CLOUD",
    "BACKEND_LOCAL_GGUF",
    "BACKEND_OLLAMA",
    "CLOUD_API_KEY_ENV",
    "CLOUD_PROVIDER_ENV",
    "BackendError",
    "CloudBackend",
    "LocalGGUFBackend",
    "cloud_enabled",
    "cloud_key_present",
    "cloud_provider",
    "describe_backends",
    "select_backend",
]
