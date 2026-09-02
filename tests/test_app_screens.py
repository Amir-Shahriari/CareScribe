"""
Every screen renders without error through the pipeline, after the UI refresh.

A visual walk lives in the browser; this is the headless guarantee that the
redesigned components (masthead, step tracker, chip table, empty states,
sidebar) render and that no state on the load -> de-identify -> review ->
approve -> generate path raises.
"""

from __future__ import annotations

import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

from streamlit.testing.v1 import AppTest  # noqa: E402

from carescribe.core import batch  # noqa: E402
from tests.fixtures import DISCHARGE_SUMMARY  # noqa: E402

APP = str(Path(__file__).resolve().parent.parent / "carescribe" / "app.py")


def _run(**session) -> AppTest:
    app = AppTest.from_file(APP, default_timeout=120)
    for key, value in session.items():
        app.session_state[key] = value
    app.run()
    assert not app.exception, [e.value for e in app.exception]
    return app


def _md(app: AppTest) -> str:
    return " ".join(m.value for m in app.markdown)


def _loaded(n: int = 3) -> dict:
    docs = {
        f"doc{i}.txt": batch.Document(name=f"doc{i}.txt", raw_text=DISCHARGE_SUMMARY)
        for i in range(1, n + 1)
    }
    return {"docs": docs, "order": list(docs), "selected": next(iter(docs))}


def _analysed(n: int = 3) -> dict:
    state = _loaded(n)
    for doc in state["docs"].values():
        batch.analyze_document(doc)
    return state


def _approved(n: int = 3, approve: int = 3) -> dict:
    state = _analysed(n)
    for i, doc in enumerate(state["docs"].values()):
        if i < approve:
            doc.approved = True
            doc.approved_path = f"/out/{doc.name}.deid.txt"
    return state


# ---------------------------------------------------------------------------

def test_empty_screen_has_masthead_and_step_tracker():
    md = _md(_run())
    assert "CareScribe" in md
    assert 'class="cs-steps"' in md
    assert 'data-state="active"' in md  # step 1 active
    assert 'class="cs-privacy"' in md   # compact offline line, not the old alert


def test_loaded_screen_shows_the_deidentify_step_and_chip_table():
    md = _md(_run(**_loaded()))
    assert "2. De-identify" in md or "De-identify" in md
    assert 'class="cs-table"' in md          # batch status is the chip table
    assert "Not yet processed" in md          # a pending status chip


def test_analysed_screen_shows_review_and_awaiting_review_chips():
    app = _run(**_analysed())
    md = _md(app)
    assert 'data-tone="accent"' in md and "Awaiting review" in md
    assert "Redacted preview" in md


def test_partly_approved_screen_advances_the_tracker():
    md = _md(_run(**_approved(approve=1)))
    # one approved, two not -> tracker on the Approve step (index 3)
    assert md.count('data-state="done"') >= 2
    assert "Approved" in md  # a safe-tone chip in the table


def test_fully_approved_screen_offers_generation_modes():
    app = _run(**_approved(approve=3))
    radios = [r for r in app.radio]
    labels = [o for r in radios for o in r.options]
    assert "Free-form note" in labels and "Clinical form" in labels


def test_clinical_form_panel_renders_for_an_approved_batch():
    app = _run(**_approved(approve=3), generation_mode="Clinical form")
    assert not app.exception
    sel = [s for s in app.selectbox]
    assert any("Form" in (s.label or "") for s in sel)


def test_generation_panel_empty_state_before_approval():
    # analysed but nothing approved -> the free-form panel shows the empty state
    md = _md(_run(**_analysed(), generation_mode="Free-form note"))
    assert 'class="cs-empty"' in md
