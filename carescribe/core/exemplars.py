"""
House-style exemplar retrieval for clinical-form generation.

A clinic accumulates its own **de-identified** form drafts (placeholder text
only, never real identifiers) and CareScribe retrieves the closest past
field-values to steer the model's tone, length, and structure — the "clinic's
own paperwork" part of the pitch, without a vector database or an embedding
model.

* **Chunk** — one stored field value.
* **Retrieve** — Okapi BM25 (hand-rolled, standard library only) over the
  stored values for the field being generated, queried with the de-identified
  source text.
* **Augment** — :func:`carescribe.core.clinical_forms.build_prompt` injects the
  top matches as "house-style example" lines for that field.

Storage is ``<app_data_dir>/exemplars/<form_id>.jsonl``, one JSON object per
line, appended. Retrieval is pure local Python and opens no socket. Nothing
here calls a model.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from . import desktop
from .text_search import BM25, query_tokens, tokenize

NOT_DOCUMENTED = "Not documented"


class ExemplarError(RuntimeError):
    """Raised when an exemplar cannot be stored — e.g. it still holds an identifier."""


def _dir() -> Path:
    return desktop.app_data_dir() / "exemplars"


def _path(form_id: str) -> Path:
    return _dir() / f"{form_id}.jsonl"


# --- store ----------------------------------------------------------------

_CACHE: dict[str, tuple[float, list[dict]]] = {}


def _load(form_id: str) -> list[dict]:
    path = _path(form_id)
    try:
        mtime = path.stat().st_mtime
    except OSError:
        _CACHE.pop(form_id, None)
        return []
    cached = _CACHE.get(form_id)
    if cached and cached[0] == mtime:
        return cached[1]
    records: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if isinstance(obj.get("fields"), dict):
            records.append(obj)
    _CACHE[form_id] = (mtime, records)
    return records


def add_exemplar(form_id: str, field_values: dict[str, str]) -> None:
    """Append one de-identified draft as a house-style exemplar.

    Refuses (``ExemplarError``, writes nothing) if the residual sweep finds
    anything identifier-shaped in the values — exemplars must be as clean as
    an approved output.
    """
    cleaned = {
        key: value.strip()
        for key, value in (field_values or {}).items()
        if value and value.strip() and value.strip() != NOT_DOCUMENTED
    }
    if not cleaned:
        raise ExemplarError("Nothing to save — every field is blank or 'Not documented'.")

    from . import deidentify  # lazy: keep the retrieval path free of the NLP stack

    findings = deidentify.residual_scan("\n".join(cleaned.values()))
    if findings:
        raise ExemplarError(
            "This draft still contains something identifier-shaped "
            f"({', '.join(sorted(set(findings))[:5])}) and was not saved."
        )

    directory = _dir()
    directory.mkdir(parents=True, exist_ok=True)
    record = {"fields": cleaned, "saved_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    with _path(form_id).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    _CACHE.pop(form_id, None)


def count(form_id: str) -> int:
    return len(_load(form_id))


def retrieve(form_id: str, field_key: str, query: str, k: int = 3) -> list[str]:
    """Top-``k`` stored values for ``field_key``, ranked by BM25 against ``query``."""
    values: list[str] = []
    seen: set[str] = set()
    for record in _load(form_id):
        value = str(record["fields"].get(field_key) or "").strip()
        if value and value != NOT_DOCUMENTED and value not in seen:
            seen.add(value)
            values.append(value)
    if not values:
        return []
    if len(values) <= k:
        return values
    bm25 = BM25([tokenize(v) for v in values])
    return [values[i] for i, _score in bm25.top_k(query_tokens(query), k)]


def retrieve_all(
    form_id: str, field_keys: list[str], query: str, k: int = 3
) -> dict[str, list[str]]:
    """``{field_key: [examples]}`` for every key that has at least one exemplar."""
    if not _load(form_id):
        return {}
    out: dict[str, list[str]] = {}
    for key in field_keys:
        hits = retrieve(form_id, key, query, k)
        if hits:
            out[key] = hits
    return out


__all__ = [
    "ExemplarError",
    "add_exemplar",
    "count",
    "retrieve",
    "retrieve_all",
]
