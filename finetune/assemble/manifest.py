"""
Provenance for a built dataset.

A content hash over the pair list, plus how it was made, so a model card can
point at exactly the data that trained it and a rebuild can be checked for
drift.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Sequence

from finetune.assemble.pairs import Pair


def _carescribe_sha() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
        return out.stdout.strip()
    except Exception:  # noqa: BLE001 — provenance is best-effort
        return "unknown"


def content_hash(pairs: Sequence[Pair]) -> str:
    """SHA-256 over the sorted JSON lines — stable regardless of pair order."""
    h = hashlib.sha256()
    for line in sorted(p.to_json_line() for p in pairs):
        h.update(line.encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def build_manifest(
    splits: dict[str, list[Pair]],
    *,
    generator_backend: str,
    generator_model: str | None,
    seed: int,
) -> dict:
    all_pairs = [p for group in splits.values() for p in group]
    strata = Counter(
        (p.meta["form_type"], p.meta["specialty"], p.meta["styled"])
        for p in all_pairs
    )
    return {
        "content_sha256": content_hash(all_pairs),
        "counts": {name: len(group) for name, group in splits.items()},
        "total": len(all_pairs),
        "strata": {" / ".join(map(str, k)): n for k, n in sorted(strata.items())},
        "generator_backend": generator_backend,
        "generator_model": generator_model,
        "seed": seed,
        "carescribe_sha": _carescribe_sha(),
    }


def write_manifest(manifest: dict, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")


__all__ = ["build_manifest", "content_hash", "write_manifest"]
