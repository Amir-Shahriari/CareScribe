"""
Clinic reference material — formularies, care pathways, local protocols — as a
local, searchable library that is shown to the **clinician**, never fed to the
model.

The safety reason for that split: a local model asked to weave a formulary or a
guideline into a draft will paraphrase it, and a paraphrased dose or referral
criterion is a clinical-safety defect, not a style nitpick. So reference
retrieval surfaces verbatim passages with their source in the review UI, and
the clinician decides what to use. Nothing here touches generation.

Files live in ``<app_data_dir>/reference/`` as ``.txt`` or ``.md``. They are
published clinical references and must not contain patient data. Retrieval is
BM25 (:mod:`carescribe.core.text_search`), local, and opens no socket.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from . import desktop
from .text_search import BM25, query_tokens, tokenize

SUFFIXES = (".txt", ".md")
MAX_CHUNK_CHARS = 1200
MIN_CHUNK_CHARS = 20
MIN_SENTENCE_CHARS = 12

GRANULARITIES = ("section", "paragraph", "sentence")

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[\"'(\[]?[A-Z0-9])")


class ReferenceError(RuntimeError):
    """Raised when a reference file cannot be stored."""


@dataclass(frozen=True)
class Chunk:
    source: str
    heading: str
    text: str


@dataclass(frozen=True)
class ReferenceHit:
    source: str
    heading: str
    text: str
    score: float


def _dir() -> Path:
    return desktop.app_data_dir() / "reference"


def _files() -> list[Path]:
    directory = _dir()
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.iterdir() if p.suffix.lower() in SUFFIXES)


def _paragraphs(body: str) -> list[tuple[str, str]]:
    """``(heading, paragraph_text)`` for every blank-line-separated block."""
    out: list[tuple[str, str]] = []
    heading = ""
    buffer: list[str] = []

    def flush() -> None:
        text = " ".join(" ".join(buffer).split())
        buffer.clear()
        if len(text) >= MIN_CHUNK_CHARS:
            out.append((heading, text))

    for raw in body.splitlines():
        stripped = raw.strip()
        if stripped.startswith("#"):
            flush()
            heading = stripped.lstrip("#").strip()
            continue
        if not stripped:
            flush()
            continue
        buffer.append(stripped)
    flush()
    return out


def _bounded(text: str) -> list[str]:
    pieces = []
    for start in range(0, len(text), MAX_CHUNK_CHARS):
        piece = text[start:start + MAX_CHUNK_CHARS].strip()
        if len(piece) >= MIN_CHUNK_CHARS:
            pieces.append(piece)
    return pieces


def _split_file(name: str, body: str, granularity: str = "paragraph") -> list[Chunk]:
    """Chunk one file at the requested granularity, tracking Markdown headings.

    * ``section``   — all paragraphs under one heading, joined.
    * ``paragraph`` — one blank-line-separated block (the default).
    * ``sentence``  — one sentence, for fields that need a tight quote (a dose).
    """
    paragraphs = _paragraphs(body)
    chunks: list[Chunk] = []

    if granularity == "section":
        grouped: dict[str, list[str]] = {}
        order: list[str] = []
        for heading, text in paragraphs:
            if heading not in grouped:
                grouped[heading] = []
                order.append(heading)
            grouped[heading].append(text)
        for heading in order:
            for piece in _bounded(" ".join(grouped[heading])):
                chunks.append(Chunk(source=name, heading=heading, text=piece))
    elif granularity == "sentence":
        for heading, text in paragraphs:
            for sentence in _SENTENCE_RE.split(text):
                sentence = sentence.strip()
                if len(sentence) >= MIN_SENTENCE_CHARS:
                    chunks.append(Chunk(source=name, heading=heading, text=sentence[:MAX_CHUNK_CHARS]))
    else:  # paragraph
        for heading, text in paragraphs:
            for piece in _bounded(text):
                chunks.append(Chunk(source=name, heading=heading, text=piece))
    return chunks


_CACHE: dict[str, dict] = {}


def _all_chunks(granularity: str = "paragraph") -> list[Chunk]:
    files = _files()
    key = repr([(p.name, p.stat().st_mtime, p.stat().st_size) for p in files])
    cell = _CACHE.get(granularity)
    if cell and cell["key"] == key:
        return cell["chunks"]
    chunks: list[Chunk] = []
    for path in files:
        try:
            body = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        chunks.extend(_split_file(path.name, body, granularity))
    _CACHE[granularity] = {"key": key, "chunks": chunks}
    return chunks


def is_empty() -> bool:
    return not _all_chunks()


def sources() -> list[tuple[str, int]]:
    """``(filename, paragraph_count)`` per loaded reference file."""
    counts: dict[str, int] = {}
    for chunk in _all_chunks():
        counts[chunk.source] = counts.get(chunk.source, 0) + 1
    return sorted(counts.items())


def search(query: str, k: int = 5, granularity: str = "paragraph") -> list[ReferenceHit]:
    """Top-``k`` reference passages for ``query`` at ``granularity``.

    BM25, ``score > 0`` only.
    """
    if granularity not in GRANULARITIES:
        raise ValueError(f"granularity must be one of {GRANULARITIES}")
    chunks = _all_chunks(granularity)
    if not chunks:
        return []
    bm25 = BM25([tokenize(c.text + " " + c.heading) for c in chunks])
    hits = []
    for index, score in bm25.top_k(query_tokens(query), k):
        if score <= 0:
            break
        c = chunks[index]
        hits.append(ReferenceHit(source=c.source, heading=c.heading, text=c.text, score=score))
    return hits


def add_file(name: str, data: bytes) -> str:
    """Store an uploaded reference file. Returns the stored filename."""
    stem = Path(name).stem.strip() or "reference"
    suffix = Path(name).suffix.lower()
    if suffix not in SUFFIXES:
        raise ReferenceError("Reference files must be .txt or .md.")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReferenceError("That file is not UTF-8 text.") from exc
    if not text.strip():
        raise ReferenceError("That file is empty.")
    if not _split_file(name, text):
        raise ReferenceError("No usable passages were found in that file.")

    directory = _dir()
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{stem}{suffix}"
    n = 2
    while (directory / filename).exists():
        filename = f"{stem}_{n}{suffix}"
        n += 1
    (directory / filename).write_text(text, encoding="utf-8")
    _CACHE.clear()
    return filename


def remove_file(filename: str) -> None:
    (_dir() / filename).unlink(missing_ok=True)
    _CACHE.clear()


__all__ = [
    "GRANULARITIES",
    "Chunk",
    "ReferenceError",
    "ReferenceHit",
    "add_file",
    "is_empty",
    "remove_file",
    "search",
    "sources",
]
