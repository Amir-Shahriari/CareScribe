"""
UI checks for the batch review app via Streamlit's AppTest.

No server of any kind is needed — the whole stage is local and offline, which
is precisely what makes it testable this way.
"""

import warnings
from pathlib import Path

import pytest

warnings.filterwarnings("ignore")

from streamlit.testing.v1 import AppTest  # noqa: E402

from carescribe.core import batch, carenotes, deidentify  # noqa: E402
from tests.fixtures import DISCHARGE_SUMMARY  # noqa: E402

APP = str(Path(__file__).resolve().parent.parent / "carescribe" / "app.py")


def run_app(**session) -> AppTest:
    app = AppTest.from_file(APP, default_timeout=120)
    for key, value in session.items():
        app.session_state[key] = value
    app.run()
    assert not app.exception, [e.value for e in app.exception]
    return app


def loaded_batch(count: int = 3) -> dict:
    """Session state for a batch that has been loaded but not yet analysed."""
    docs = {
        f"doc{index}.txt": batch.Document(name=f"doc{index}.txt", raw_text=DISCHARGE_SUMMARY)
        for index in range(1, count + 1)
    }
    return {"docs": docs, "order": list(docs), "selected": next(iter(docs))}


def analysed_batch(count: int = 3) -> dict:
    state = loaded_batch(count)
    for document in state["docs"].values():
        batch.analyze_document(document)
    return state


def data_editors(app: AppTest) -> list:
    """AppTest has no DataEditor accessor; st.data_editor surfaces as a Dataframe."""
    return [element for element in app.main if type(element).__name__ == "Dataframe"]


def text_of(*element_lists) -> str:
    return " ".join(item.value for items in element_lists for item in items)


# ==========================================================================
# Smoke
# ==========================================================================

def test_empty_app_renders():
    app = run_app()
    assert any("CareScribe" in heading.value for heading in app.title)


def test_sidebar_reports_the_detection_layers():
    app = run_app()
    sidebar = text_of(app.sidebar.markdown)
    assert "Structured regex" in sidebar
    assert "Presidio + spaCy" in sidebar
    assert "GLiNER" in sidebar


def test_nothing_offers_a_model_or_a_server():
    """This stage makes no network calls, so nothing should offer a provider."""
    app = run_app()
    assert "Ollama" not in text_of(app.sidebar.markdown, app.sidebar.caption)
    assert not app.sidebar.selectbox


# ==========================================================================
# Batch flow
# ==========================================================================

def test_loaded_batch_is_reported():
    app = run_app(**loaded_batch(3))
    assert any("3" in item.value for item in app.success)


def test_review_panel_appears_once_analysed():
    app = run_app(**analysed_batch(2))
    assert "Review & approve" in text_of(app.subheader)
    assert data_editors(app), "identifier table not rendered"


def test_identifier_table_has_the_review_columns():
    app = run_app(**analysed_batch(1))
    editor = data_editors(app)[0]
    assert list(editor.value.columns) == ["value", "type", "placeholder", "action"]
    assert (editor.value["action"] == "Redact").all()


def test_preview_shows_placeholders_not_identifiers():
    app = run_app(**analysed_batch(1))
    previews = [area.value for area in app.text_area if "[PATIENT]" in (area.value or "")]
    assert previews, "no redacted preview rendered"
    assert "943 476 5919" not in previews[0]


def test_batch_status_lists_every_document():
    app = run_app(**analysed_batch(3))
    assert "Batch status" in text_of(app.subheader)


def test_document_counter_is_shown():
    app = run_app(**analysed_batch(4))
    assert "of 4" in text_of(app.caption)


def test_human_review_warning_is_shown():
    app = run_app(**analysed_batch(1))
    assert "Human review required" in text_of(app.warning)


# ==========================================================================
# Approval and the handoff stub
# ==========================================================================

def test_approval_writes_only_deidentified_text(tmp_path, monkeypatch):
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "deidentified")
    state = analysed_batch(1)
    document = next(iter(state["docs"].values()))

    path = batch.write_approved(document.name, document.redacted_text)
    written = path.read_text(encoding="utf-8")

    assert "[PATIENT]" in written
    for value in document.phi_map.values():
        assert value not in written


def test_blocked_approval_is_surfaced():
    state = analysed_batch(1)
    next(iter(state["docs"].values())).residual = ["01632 960 188"]

    app = run_app(**state)
    errors = text_of(app.error)
    assert "Approval blocked" in errors
    assert "01632 960 188" in errors


def test_generate_report_is_gated_on_approval():
    """Generation must never run on text a human has not approved."""
    app = run_app(**analysed_batch(1))

    generate = [button for button in app.button if button.label == "Generate report"]
    assert generate and generate[0].disabled
    assert "approve the document first" in text_of(app.info)


def test_generation_refuses_empty_text():
    """The stub is gone; the contract it declared is still enforced."""
    with pytest.raises(carenotes.CareNoteError):
        carenotes.generate_care_note("   ", backend=_NullBackend())


class _NullBackend:
    """A backend that never runs — proves the guard fires before any call."""

    def generate(self, system, prompt, stream=True):
        raise AssertionError("the backend must not be reached")
        yield ""  # pragma: no cover


# ==========================================================================
# Privacy invariants
# ==========================================================================

def test_wipe_clears_every_document():
    app = run_app(**analysed_batch(2))
    wipe = [button for button in app.sidebar.button if "wipe PHI" in button.label][0]
    wipe.click().run()
    assert app.session_state.docs == {}
    assert app.session_state.order == []


def test_loading_and_analysing_writes_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "deidentified")
    run_app(**analysed_batch(2))
    assert not (tmp_path / "deidentified").exists()


def test_pipeline_opens_no_socket(monkeypatch, raw_text):
    """A hard assertion that this stage is offline."""
    import socket

    def refuse(*args, **kwargs):
        raise AssertionError("the de-identification stage opened a socket")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket.socket, "connect_ex", refuse)

    result = deidentify.deidentify(raw_text)
    assert "943 476 5919" not in result.redacted_text
