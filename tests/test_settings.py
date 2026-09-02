from __future__ import annotations

from carescribe.core import settings


def test_load_settings_missing_file_returns_defaults(tmp_path, monkeypatch):
    monkeypatch.setattr(settings.desktop, "app_data_dir", lambda: tmp_path)
    assert settings.load_settings() == settings.Settings()


def test_save_then_load_round_trips(tmp_path, monkeypatch):
    monkeypatch.setattr(settings.desktop, "app_data_dir", lambda: tmp_path)
    original = settings.Settings(
        backend="ollama", ollama_model="qwen2.5:32b", temperature=0.1
    )
    settings.save_settings(original)
    assert settings.load_settings() == original
    assert (tmp_path / "settings.json").exists()


def test_load_settings_ignores_unknown_fields_keeps_missing_as_default(tmp_path, monkeypatch):
    monkeypatch.setattr(settings.desktop, "app_data_dir", lambda: tmp_path)
    path = tmp_path / "settings.json"
    path.write_text('{"backend": "cloud", "unknown_field": "x"}', encoding="utf-8")
    loaded = settings.load_settings()
    assert loaded.backend == "cloud"
    assert loaded.temperature == 0.0


def test_load_settings_survives_corrupt_json(tmp_path, monkeypatch):
    monkeypatch.setattr(settings.desktop, "app_data_dir", lambda: tmp_path)
    (tmp_path / "settings.json").write_text("{not valid json", encoding="utf-8")
    assert settings.load_settings() == settings.Settings()


def test_save_settings_creates_app_data_dir_if_missing(tmp_path, monkeypatch):
    target = tmp_path / "nested" / "dir"
    monkeypatch.setattr(settings.desktop, "app_data_dir", lambda: target)
    settings.save_settings(settings.Settings(backend="local"))
    assert (target / "settings.json").exists()


def test_load_settings_survives_non_dict_json(tmp_path, monkeypatch):
    monkeypatch.setattr(settings.desktop, "app_data_dir", lambda: tmp_path)
    (tmp_path / "settings.json").write_text("[1, 2, 3]", encoding="utf-8")
    assert settings.load_settings() == settings.Settings()


def test_load_settings_coerces_stringy_temperature(tmp_path, monkeypatch):
    monkeypatch.setattr(settings.desktop, "app_data_dir", lambda: tmp_path)
    (tmp_path / "settings.json").write_text(
        '{"backend": "local", "temperature": "0.5"}', encoding="utf-8"
    )
    loaded = settings.load_settings()
    assert loaded.backend == "local"
    assert loaded.temperature == 0.5
    assert isinstance(loaded.temperature, float)


def test_load_settings_falls_back_to_default_on_bad_coercion(tmp_path, monkeypatch):
    monkeypatch.setattr(settings.desktop, "app_data_dir", lambda: tmp_path)
    (tmp_path / "settings.json").write_text(
        '{"backend": "local", "temperature": "not-a-number"}', encoding="utf-8"
    )
    loaded = settings.load_settings()
    assert loaded.backend == "local"
    assert loaded.temperature == 0.0
