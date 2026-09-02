"""
The approval gate.

Only the **authoritative safety sweep** blocks approval. A clean sweep
(:func:`carescribe.core.batch.sweep`, re-run inside
:func:`carescribe.core.batch.write_approved` so the guarantee never depends on
the UI) is the one hard precondition for a write.

Advisory review spans — low-confidence redactions that are *already in place*,
and the permissive residual-pattern flags — are surfaced in the UI and can be
cleared in one click, but they do not gate the write. Forcing a decision on
text that is already redacted is friction without a safety payoff, and any raw
identifier the reviewer misses is still caught by the sweep on approve.
"""

from __future__ import annotations


def blocking_reason(residual: list[str], outstanding: int = 0) -> str:
    """Why Approve is disabled, in one short line. Empty string means it isn't.

    ``residual`` is the authoritative safety-sweep result. ``outstanding`` is
    the count of advisory review spans still untouched; it is accepted for
    callers that want to pass it but never blocks on its own.
    """
    if residual:
        return f"The safety sweep found {len(residual)} finding(s) to resolve."
    return ""


__all__ = ["blocking_reason"]
