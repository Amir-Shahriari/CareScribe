# tests/test_settings_panel_screen.py
from __future__ import annotations

import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

from streamlit.testing.v1 import AppTest  # noqa: E402

APP = str(Path(__file__).resolve().parent.parent / "carescribe" / "app.py")


def _run(**session) -> AppTest:
    app = AppTest.from_file(APP, default_timeout=120)
    for key, value in session.items():
        app.session_state[key] = value
    app.run()
    assert not app.exception, [e.value for e in app.exception]
    return app


def test_settings_expander_renders_without_error():
    app = _run()
    labels = [b.label for b in app.sidebar.button]
    assert any("Settings" in label or "settings" in label for label in labels + [
        e.label for e in app.sidebar.expander
    ])


def test_saving_settings_persists_and_survives_reload(tmp_path, monkeypatch):
    import carescribe.core.settings as settings_mod

    monkeypatch.setattr(settings_mod.desktop, "app_data_dir", lambda: tmp_path)
    app = _run()
    # Open the settings expander, pick backend "local", save.
    app.sidebar.expander[0].expanded = True
    app.run()
    selects = app.sidebar.selectbox
    backend_select = next(s for s in selects if s.key == "settings_backend")
    backend_select.set_value("local").run()
    save_button = next(b for b in app.sidebar.button if b.key == "settings_save")
    save_button.click().run()
    assert not app.exception, [e.value for e in app.exception]
    reloaded = settings_mod.load_settings()
    assert reloaded.backend == "local"
