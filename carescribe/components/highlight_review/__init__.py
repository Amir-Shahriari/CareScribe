"""
Click-to-redact highlighted text.

Renders already-redacted (or already-flagged) text with clickable
``<mark data-span-id="...">`` spans, and reports which one the reviewer
clicked. Everything that crosses into or out of this component is already
placeholder text or a span id string — never raw PHI. See
``frontend/index.html`` for the (hand-rolled, no external dependency) client
side.

The component is an iframe, so the app's stylesheet does not reach it and it
cannot inherit the interface typeface. The faces are handed across explicitly
instead: ``theme`` bundles them (SIL OFL) and inlines them as data URIs, and the
same rules are passed in here, so the toolbar reads as part of the app rather
than falling back to whatever sans the host happens to have.
"""

from __future__ import annotations

import os

import streamlit.components.v1 as components

_FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
_component = components.declare_component("highlight_review", path=_FRONTEND_DIR)


def _font_css() -> str:
    """The bundled `@font-face` rules, or "" if the faces are unavailable."""
    try:
        from carescribe.ui.theme import FONT_IMPORT

        return FONT_IMPORT
    except Exception:  # noqa: BLE001 — the pane must render without its font
        return ""


def highlight_review(html: str, *, key: str | None = None) -> str | None:
    """Render ``html`` and return the ``data-span-id`` of the last click.

    Returns ``None`` until the reviewer has clicked a highlighted span at
    least once for this widget instance.
    """
    return _component(html=html, font_css=_font_css(), key=key, default=None)


__all__ = ["highlight_review"]
