from pathlib import Path

from carescribe.components.highlight_review import highlight_review


def _frontend_path() -> Path:
    return (
        Path(__file__).resolve().parent.parent
        / "carescribe" / "components" / "highlight_review" / "frontend" / "index.html"
    )


def test_frontend_file_exists():
    assert _frontend_path().exists()


def test_frontend_has_no_external_script_or_link_tags():
    """Offline-first: nothing in this file may fetch from a CDN."""
    text = _frontend_path().read_text(encoding="utf-8")
    assert "http://" not in text
    assert "https://" not in text


def test_wrapper_is_callable_and_importable():
    assert callable(highlight_review)
