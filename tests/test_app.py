"""
UI checks for the batch review app via Streamlit's AppTest.

No server of any kind is needed — the whole stage is local and offline, which
is precisely what makes it testable this way.
"""

import json
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
    # The masthead ships as an HTML component (components.hero), not st.title.
    assert "CareScribe" in text_of(app.markdown)
    assert "cs-steps" in text_of(app.markdown)  # the step tracker rendered


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
    assert list(editor.value.columns) == [
        "value", "type", "placeholder", "action", "confidence"
    ]
    assert (editor.value["action"] == "Redact").all()
    # Every row carries a confidence tier, and single-detector rows sort first.
    assert set(editor.value["confidence"]) <= {"auto", "review"}
    tiers = list(editor.value["confidence"])
    assert tiers == sorted(tiers, key=lambda tier: tier != "review")


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


def test_a_clean_auto_confidence_document_is_gated_only_by_the_attestation():
    """After the read-and-confirmed tick, a clean auto-confidence document has
    nothing else in its way: no per-span confirmations, no residual findings.

    Deliberately plain, lowercase prose — the real fixture text used
    elsewhere in this file trips the (entity-independent, by design)
    residual safety-net scanner on ordinary capitalised clinical terms
    ("Cardiology", "Leeds"), which would make this test about the residual
    mechanism instead of the one it's meant to isolate: entity confidence.
    """
    document = batch.Document(
        name="clean.txt",
        raw_text="the patient was seen today and remains well.",
        redacted_text="[PATIENT] was seen today and remains well.",
        entities=[{
            "type": "PATIENT_NAME", "value": "the patient",
            "placeholder": "[PATIENT]", "action": "Redact", "confidence": "auto",
        }],
        analyzed=True,
    )
    state = {"docs": {document.name: document}, "order": [document.name], "selected": document.name}

    app = run_app(**state)
    reasons = [c.value for c in app.caption if "Approve is disabled" in c.value]
    assert reasons == ["Approve is disabled — Tick the read-and-confirmed box above."]

    document.attested = True
    app = run_app(**state)
    reasons = [c.value for c in app.caption if "Approve is disabled" in c.value]
    assert reasons == []


def test_a_batch_of_clean_documents_needs_roughly_one_click_each(tmp_path, monkeypatch):
    """The actual goal of this redesign, made concrete and regression-tested."""
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "deidentified")
    docs = {}
    for index in range(1, 6):
        name = f"clean{index}.txt"
        docs[name] = batch.Document(
            name=name,
            raw_text="the patient was seen today and remains well.",
            redacted_text="[PATIENT] was seen today and remains well.",
            entities=[{
                "type": "PATIENT_NAME", "value": "the patient",
                "placeholder": "[PATIENT]", "action": "Redact", "confidence": "auto",
            }],
            analyzed=True,
        )
    state = {"docs": docs, "order": list(docs), "selected": next(iter(docs))}
    app = AppTest.from_file(APP, default_timeout=120)
    for key, value in state.items():
        app.session_state[key] = value
    app.run()
    assert not app.exception, [e.value for e in app.exception]

    clicks = 0
    for name in list(docs):
        app.session_state["selected"] = name
        app.run()
        clicks += 1  # selecting the document
        app.checkbox(key=f"attest_{name}").check().run()
        clicks += 1  # the read-and-confirmed tick
        app.button(key=f"approve_{name}").click()
        app.run()
        clicks += 1  # the Approve click
        assert docs[name].approved

    # 5 documents, 3 interactions each (select + attest + approve) — no per-span
    # decisions, since every entity is "auto" and the text is clean of anything
    # the residual scanner would flag. The attestation is the one tick kept by
    # design: a human says they read the redacted text.
    assert clicks == 15


def test_human_review_warning_is_shown():
    app = run_app(**analysed_batch(1))
    assert "Human review required" in text_of(app.warning)


def _clean_auto_doc(name: str = "clean.txt") -> batch.Document:
    return batch.Document(
        name=name,
        raw_text="the patient was seen today and remains well.",
        redacted_text="[PATIENT] was seen today and remains well.",
        entities=[{
            "type": "PATIENT_NAME", "value": "the patient",
            "placeholder": "[PATIENT]", "action": "Redact", "confidence": "auto",
        }],
        analyzed=True,
    )


def test_approval_is_gated_on_the_attestation(tmp_path, monkeypatch):
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "deidentified")
    document = _clean_auto_doc()
    state = {"docs": {document.name: document}, "order": [document.name], "selected": document.name}

    app = run_app(**state)
    assert any("read-and-confirmed" in c.value for c in app.caption)
    assert not document.approved

    document.attested = True
    app = run_app(**state)
    app.button(key="approve_clean.txt").click().run()
    assert document.approved
    record = json.loads(
        (tmp_path / "deidentified" / "clean.review.json").read_text(encoding="utf-8")
    )
    assert record["reviewer_attested"] is True


def test_batch_approve_leaves_an_unattested_document(tmp_path, monkeypatch):
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "deidentified")
    docs = {name: _clean_auto_doc(name) for name in ("c1.txt", "c2.txt")}
    docs["c1.txt"].attested = True  # only one reviewer has ticked the box

    app = AppTest.from_file(APP, default_timeout=120)
    for key, value in {"docs": docs, "order": list(docs), "selected": "c1.txt"}.items():
        app.session_state[key] = value
    app.run()
    app.button(key="approve_batch").click().run()

    assert docs["c1.txt"].approved
    assert not docs["c2.txt"].approved
    assert "c2.txt" in text_of(app.warning)


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
