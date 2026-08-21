"""
The approval gate.

Approval unlocks once nothing is outstanding: the blocking safety sweep
found nothing, and every clickable span the reviewer was shown has a
decision (redacted, confirmed, dismissed, or corrected). The click record
itself — the redact/confirm/dismiss decisions logged per document — is the
evidence a review happened; there is no separate itemised checklist to tick.
"""

from __future__ import annotations


def blocking_reason(residual: list[str], outstanding: int) -> str:
    """Why Approve is disabled, in one short line. Empty string means it isn't."""
    if residual:
        return f"The safety sweep found {len(residual)} finding(s) to resolve."
    if outstanding:
        return f"{outstanding} highlighted span(s) still need a decision."
    return ""


__all__ = ["blocking_reason"]
