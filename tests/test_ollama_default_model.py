"""The pure-ish helpers of the Ollama client — ``default_model``, ``status``
and ``missing_model_message``. These tests never open a socket: the helpers
take their data as arguments, and the two that would reach for the daemon
(``status`` and ``available=None``) get the module's own ``is_up`` and
``list_models`` monkeypatched instead.
"""

from carescribe.core import ollama_client


def test_default_model_prefers_earliest_preferred_over_list_and_alphabet_order():
    # "zzz-first" is neither preferred nor an 8b/7b match, "phi3:medium" and
    # "qwen2.5:7b" are both preferred — qwen2.5:7b sits earlier in
    # PREFERRED_MODELS even though "phi3:medium" sorts first alphabetically.
    available = ["zzz-first", "phi3:medium", "qwen2.5:7b"]
    assert ollama_client.default_model(available) == "qwen2.5:7b"


def test_default_model_matches_8b_or_7b_case_insensitively():
    available = ["aaa-nano", "Custom-8B-Instruct", "zzz-tiny"]
    assert ollama_client.default_model(available) == "Custom-8B-Instruct"
    assert ollama_client.default_model(["Tiny-7B"]) == "Tiny-7B"


def test_default_model_falls_back_to_first_entry_and_none_when_empty():
    assert ollama_client.default_model(["zeta-mini", "alpha-mini"]) == "zeta-mini"
    assert ollama_client.default_model([]) is None


def test_default_model_with_none_asks_list_models(monkeypatch):
    monkeypatch.setattr(ollama_client, "list_models", lambda: ["probe-model"])
    assert ollama_client.default_model(None) == "probe-model"


def test_status_with_daemon_up_reports_models_and_empty_message(monkeypatch):
    monkeypatch.setattr(ollama_client, "is_up", lambda: True)
    monkeypatch.setattr(ollama_client, "list_models", lambda: ["llama3.1:8b"])
    report = ollama_client.status()
    assert report == {
        "up": True,
        "host": "127.0.0.1:11434",
        "models": ["llama3.1:8b"],
        "default_model": "llama3.1:8b",
        "message": "",
    }


def test_status_with_daemon_down_reports_no_models_and_daemon_message(monkeypatch):
    monkeypatch.setattr(ollama_client, "is_up", lambda: False)
    monkeypatch.setattr(ollama_client, "list_models", lambda: ["llama3.1:8b"])
    report = ollama_client.status()
    assert report == {
        "up": False,
        "host": "127.0.0.1:11434",
        "models": [],
        "default_model": None,
        "message": ollama_client.DAEMON_DOWN_MESSAGE,
    }


def test_missing_model_message_gives_pull_command_and_lists_installed():
    message = ollama_client.missing_model_message("llama3.1:8b", ["mistral:7b"])
    assert "    ollama pull llama3.1:8b" in message.splitlines()
    assert "Installed models: mistral:7b" in message.splitlines()
    for available in (None, []):
        message = ollama_client.missing_model_message("llama3.1:8b", available)
        assert "    ollama pull llama3.1:8b" in message.splitlines()
        assert "Installed models:" not in message
