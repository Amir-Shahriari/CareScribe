"""
CareScribe UI layer — the visual identity, applied over Streamlit.

`theme.CSS` is the one stylesheet; `components` holds the HTML-string helpers
(hero, step tracker, chips, stat strip, empty states) and the drawn icon set.
Nothing here changes app behaviour, widget keys, or callbacks — presentation
only.
"""

from carescribe.ui import components, theme

__all__ = ["components", "theme"]
