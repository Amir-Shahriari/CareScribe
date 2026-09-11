"""Contract of the click-to-redact review component.

This is the reviewer's primary reading surface: the one screen where missing an
identifier means it reaches disk. It is a hand-rolled iframe, so nothing else in
the suite covers it, and its own document does not inherit the app stylesheet.

These tests read the shipped HTML. They cannot prove the JavaScript behaves —
only a browser does that — but they pin the properties that were actually wrong
(mouse-only marks, a fixed 360px viewport, no way to search) and the ones that
must never regress (no remote asset, no raw PHI crossing the boundary).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from carescribe.components.highlight_review import highlight_review  # noqa: F401

FRONTEND = (
    Path(__file__).resolve().parent.parent
    / "carescribe" / "components" / "highlight_review" / "frontend" / "index.html"
)


@pytest.fixture(scope="module")
def html() -> str:
    return FRONTEND.read_text(encoding="utf-8")


def test_the_component_ships(html):
    assert html.strip().startswith("<!doctype html>")


def test_it_loads_nothing_remote(html):
    """A CDN here would breach the offline guarantee as surely as in the theme."""
    remote = re.findall(r"https?://(?!127\.0\.0\.1|localhost)[\w.-]+", html)
    assert not remote, f"component references {sorted(set(remote))}"
    assert "@import" not in html


def test_highlights_are_keyboard_operable(html):
    """They were click-only: no tabindex, no role, no key handler."""
    assert 'setAttribute("tabindex", "0")' in html
    assert 'setAttribute("role", "button")' in html
    assert 'addEventListener("keydown"' in html
    assert '"Enter"' in html and '" "' in html


def test_the_reading_pane_is_taller_than_it_was(html):
    """360px hid most of a real letter behind a scroll with no way to search."""
    assert "max-height: 360px" not in html
    match = re.search(r"#doc\s*\{[^}]*?height:\s*(\d+)px", html, re.DOTALL)
    assert match, "expected an explicit pixel height on #doc"
    assert int(match.group(1)) >= 480, match.group(1)


def test_the_pane_height_does_not_depend_on_the_frame_it_sets(html):
    """A vh unit here feeds back into the height the host derives from it.

    The host sizes this iframe from our own scrollHeight, so a viewport-relative
    height resolves against the value it just produced and settles on its own
    floor — smaller than the fixed height it replaced.
    """
    without_comments = re.sub(r"/\*.*?\*/", "", html, flags=re.DOTALL)
    doc_rule = re.search(r"#doc\s*\{(.*?)\}", without_comments, re.DOTALL)
    assert doc_rule, "no #doc rule"
    assert "vh" not in doc_rule.group(1), doc_rule.group(1)


def test_there_is_a_find_in_page(html):
    assert 'id="find"' in html
    assert "Find in this document" in html
    # Next/previous match, and a live count.
    assert 'id="next"' in html and 'id="prev"' in html
    assert 'aria-live="polite"' in html


def test_the_find_term_is_escaped_before_it_becomes_a_regex(html):
    """A reviewer searching for "(" must not crash the pane."""
    assert "escapeRegExp" in html
    assert r"replace(/[.*+?^${}()|[\]\\]/g" in html


def test_find_restores_the_untouched_render_each_time(html):
    """Otherwise find highlighting compounds and can eat the redaction marks."""
    assert "doc.innerHTML = baseHtml" in html


def test_only_a_span_id_crosses_back_to_python(html):
    """The boundary carries placeholder text in and an id out — never PHI."""
    sent = re.findall(r"sendValue\(([^)]*)\)", html)
    assert sent, "no sendValue call found"
    for argument in sent:
        assert "data-span-id" in argument or argument.strip() == "value", argument


def test_every_streamlit_message_is_marked_as_one(html):
    """The host silently drops postMessages without this flag."""
    # Count call sites, not mentions -- the rule is also stated in a comment.
    calls = re.findall(
        r"window\.parent\.postMessage\(\s*\{(.*?)\}", html, re.DOTALL
    )
    assert len(calls) >= 3, f"expected at least 3 postMessage calls, got {len(calls)}"
    for body in calls:
        assert "isStreamlitMessage: true" in body, body[:80]
