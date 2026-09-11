"""The interface must not fetch anything at runtime.

`theme.py` pulled IBM Plex from `fonts.googleapis.com` via a CSS `@import`, on
every rerun, before the sign-in gate — while `app.py`'s own docstring said this
stage "makes no network calls of any kind" and the masthead showed an "offline —
nothing leaves this computer" lock pill. A CSS `@import` degrades silently, so
it never surfaced: the app looked right, said the right thing, and still
announced itself to a third party every time a clinician opened it.

The faces are now bundled under `carescribe/ui/fonts/` and inlined. These tests
pin that, and the wider rule it belongs to: nothing the UI renders may reference
a remote origin.
"""

from __future__ import annotations

import re

import pytest

from carescribe.ui import components, theme

# The generation backends legitimately talk to a network when the clinician
# turns them on, and the model downloader legitimately fetches a model. Neither
# renders into the stylesheet or the static HTML helpers, which is what this
# file covers.
UI_SURFACES = {
    "theme.CSS": lambda: theme.CSS,
}

# Base64 payloads contain "//" freely, so strip data: URIs before scanning and
# require a real scheme rather than a bare protocol-relative slash pair.
_DATA_URI = re.compile(r"data:[^;,)\s]*(?:;[^,)\s]*)*,[^)\s'\"]*")
REMOTE = re.compile(r"https?://(?!127\.0\.0\.1|localhost)[\w.-]+")


def _scannable(text: str) -> str:
    return _DATA_URI.sub("", text)


@pytest.mark.parametrize("name", sorted(UI_SURFACES))
def test_no_remote_origin_is_referenced(name):
    found = REMOTE.findall(_scannable(UI_SURFACES[name]()))
    assert not found, f"{name} references remote origin(s): {sorted(set(found))}"


def test_the_stylesheet_has_no_css_import():
    """An @import is the specific shape that failed silently before."""
    assert "@import" not in theme.CSS


def test_the_faces_are_bundled_and_inlined():
    assert theme.FONTS_DIR.is_dir(), theme.FONTS_DIR
    faces = sorted(p.name for p in theme.FONTS_DIR.glob("*.woff2"))
    assert faces, "no bundled font files"
    assert theme.CSS.count("@font-face") == len(faces)
    assert "data:font/woff2;base64," in theme.CSS


def test_the_bundled_faces_carry_their_licence():
    """IBM Plex is OFL; redistributing it means shipping the licence."""
    licence = theme.FONTS_DIR / "LICENSE.txt"
    assert licence.is_file()
    assert "SIL Open Font License" in licence.read_text(encoding="utf-8")


def test_the_stylesheet_still_names_the_intended_families():
    """Closing the hole must not have cost the type identity."""
    assert "IBM Plex Sans" in theme.CSS
    assert "IBM Plex Mono" in theme.CSS


def test_static_html_helpers_reference_nothing_remote():
    """The drawn icon set and the HTML-string helpers stay local too."""
    blobs = ["".join(components.ICON.values())]
    for value in vars(components).values():
        if isinstance(value, str) and "<" in value:
            blobs.append(value)
    found = REMOTE.findall(_scannable("".join(blobs)))
    assert not found, f"components reference remote origin(s): {sorted(set(found))}"
