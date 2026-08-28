"""Okapi BM25 over a small in-memory document set — standard library only.

Shared by the house-style exemplar store (:mod:`carescribe.core.exemplars`) and
the reference library (:mod:`carescribe.core.reference_library`). Both index a
handful to a few hundred short passages, so a plain in-memory scorer with no
persistence beats pulling in a search engine or an embedding model.
"""

from __future__ import annotations

import math
import re
from collections import Counter

_TOKEN_RE = re.compile(r"[a-z0-9]+")

# A short function-word list. Dropped from *queries* only — a tiny corpus of
# short passages otherwise lets a stray "the" outweigh a rare content word.
STOPWORDS = frozenset(
    """
    a an and are as at be but by for from had has have in into is it its of on
    or that the their them then there these this to was were what when where
    which who whom why will with would you your
    """.split()
)


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall((text or "").lower())


def query_tokens(text: str) -> list[str]:
    """Tokens for the *query* side — content words only."""
    return [token for token in tokenize(text) if token not in STOPWORDS]


class BM25:
    """Okapi BM25. ``documents`` is a list of token lists."""

    def __init__(self, documents: list[list[str]], k1: float = 1.5, b: float = 0.75) -> None:
        self.docs = documents
        self.k1 = k1
        self.b = b
        self.doc_len = [len(d) for d in documents]
        self.avg_len = (sum(self.doc_len) / len(documents)) if documents else 0.0
        self.freqs = [Counter(d) for d in documents]
        df: Counter = Counter()
        for doc in documents:
            df.update(set(doc))
        n = len(documents)
        # +1 inside the log keeps idf non-negative for terms in every document.
        self.idf = {
            term: math.log(1 + (n - count + 0.5) / (count + 0.5))
            for term, count in df.items()
        }

    def scores(self, query_tokens: list[str]) -> list[float]:
        out = [0.0] * len(self.docs)
        for term in query_tokens:
            idf = self.idf.get(term)
            if idf is None:
                continue
            for i, freq in enumerate(self.freqs):
                tf = freq.get(term, 0)
                if not tf:
                    continue
                denom = tf + self.k1 * (
                    1 - self.b + self.b * (self.doc_len[i] / (self.avg_len or 1))
                )
                out[i] += idf * (tf * (self.k1 + 1)) / denom
        return out

    def top_k(self, query_tokens: list[str], k: int) -> list[tuple[int, float]]:
        """``(index, score)`` for the ``k`` best-scoring documents, best first."""
        scored = list(enumerate(self.scores(query_tokens)))
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:k]


__all__ = ["BM25", "STOPWORDS", "query_tokens", "tokenize"]
