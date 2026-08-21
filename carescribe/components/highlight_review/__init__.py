"""
Click-to-redact highlighted text.

Renders already-redacted (or already-flagged) text with clickable
``<mark data-span-id="...">`` spans, and reports which one the reviewer
clicked. Everything that crosses into or out of this component is already
placeholder text or a span id string — never raw PHI. See
``frontend/index.html`` for the (hand-rolled, no external dependency) client
side.
"""

from __future__ import annotations

import os

import streamlit.components.v1 as components

_FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
_component = components.declare_component("highlight_review", path=_FRONTEND_DIR)


def highlight_review(html: str, *, key: str | None = None) -> str | None:
    """Render ``html`` and return the ``data-span-id`` of the last click.

    Returns ``None`` until the reviewer has clicked a highlighted span at
    least once for this widget instance.
    """
    return _component(html=html, key=key, default=None)


__all__ = ["highlight_review"]
