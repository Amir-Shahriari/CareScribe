"""
The packaging invariants: what the desktop app may and may not do.

Packaging is where a privacy model usually breaks — an app that was careful in
a source checkout starts writing next to its executable, or picks up a network
default from a frozen config. These tests pin the properties that must survive
being frozen.

Everything here is fabricated.
"""

import json
import os
import socket
from pathlib import Path

import pytest

from carescribe.core import backends, batch, carenotes, deidentify, desktop

FIXTURE = Path(__file__).resolve().parent.parent / "stress_corpus"


class NoEgress:
    """Fails the test if anything opens a non-loopback socket.

    Loopback is allowed: the Streamlit server and a local Ollama daemon both
    live there, and neither leaves the machine. Anything else is egress.
    """

    def __init__(self):
        self.attempts: list[str] = []
        self._real_connect = socket.socket.connect
        self._real_create = socket.create_connection

    def _check(self, address):
        try:
            host = address[0] if isinstance(address, tuple) else str(address)
        except Exception:  # noqa: BLE001
            return
        if host not in ("127.0.0.1", "::1", "localhost"):
            self.attempts.append(str(host))

    def __enter__(self):
        outer = self

        def connect(self, address, *args, **kwargs):
            outer._check(address)
            return outer._real_connect(self, address, *args, **kwargs)

        def create_connection(address, *args, **kwargs):
            outer._check(address)
            return outer._real_create(address, *args, **kwargs)

        socket.socket.connect = connect
        socket.create_connection = create_connection
        return self

    def __exit__(self, *exc):
        socket.socket.connect = self._real_connect
        socket.create_connection = self._real_create
        return False


class StubBackend:
    """Stands in for a model so the egress test does not need one installed."""

    def generate(self, system, prompt, stream=True):
        yield "S - Subjective\n[not documented]\nP - Plan\nReview as arranged.\n"


# ==========================================================================
# Task 6 — no outbound socket across the whole flow
# ==========================================================================

def test_the_whole_flow_opens_no_outbound_socket(tmp_path, monkeypatch):
    """Load → de-identify → approve → generate, with egress forbidden."""
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "out")
    source = FIXTURE / "doc06_psych_clinic_letter.txt"

    with NoEgress() as guard:
        documents, errors = batch.load_documents([str(source)])
        assert not errors
        document = batch.analyze_document(documents[source.name])
        assert deidentify.residual_scan(document.redacted_text) == []
        batch.write_approved(document.name, document.redacted_text)
        draft = "".join(
            carenotes.generate_document(
                document.redacted_text, "SOAP care note", StubBackend(),
                phi_values=list(document.phi_map.values()),
            )
        )
        assert draft

    assert guard.attempts == [], f"outbound connection attempted: {guard.attempts}"


def test_reidentification_opens_no_socket(tmp_path):
    """Re-identification is pure Python — it must not phone anywhere."""
    draft = "[PATIENT] was seen by [CLINICIAN_1]."
    phi_map = {"[PATIENT]": "Wei Chen", "[CLINICIAN_1]": "Dr H. Okonkwo"}
    with NoEgress() as guard:
        text, unresolved = carenotes.finalise(draft, phi_map)
    assert "Wei Chen" in text
    assert unresolved == []
    assert guard.attempts == []


# ==========================================================================
# Task 6 — the cloud path is unreachable when off
# ==========================================================================

@pytest.fixture(autouse=True)
def _cloud_off(monkeypatch):
    monkeypatch.delenv(backends.CLOUD_PROVIDER_ENV, raising=False)
    monkeypatch.delenv(backends.CLOUD_API_KEY_ENV, raising=False)


def test_cloud_is_off_by_default():
    assert not backends.cloud_enabled()
    assert backends.cloud_provider() == ""


def test_cloud_backend_cannot_be_constructed_when_off():
    with pytest.raises(backends.BackendError) as excinfo:
        backends.CloudBackend()
    assert "off by default" in str(excinfo.value)


def test_a_stray_api_key_alone_does_not_enable_cloud(monkeypatch):
    """A key left by another tool must not silently turn on off-device work."""
    monkeypatch.setenv(backends.CLOUD_API_KEY_ENV, "sk-not-a-real-key")
    assert not backends.cloud_enabled()
    with pytest.raises(backends.BackendError):
        backends.CloudBackend()


def test_naming_a_provider_without_a_key_fails_loudly(monkeypatch):
    """It must not quietly fall back to a local backend and look like it worked."""
    monkeypatch.setenv(backends.CLOUD_PROVIDER_ENV, "someprovider")
    assert not backends.cloud_enabled()
    with pytest.raises(backends.BackendError) as excinfo:
        backends.CloudBackend()
    assert backends.CLOUD_API_KEY_ENV in str(excinfo.value)


def test_the_key_is_read_only_from_the_environment():
    """No key may be committed, defaulted, or written anywhere."""
    source = Path(backends.__file__).read_text(encoding="utf-8")
    assert "sk-" not in source
    assert backends.CLOUD_API_KEY_ENV in source
    # The key is read at call time and never stored on the instance.
    assert "self.key" not in source
    assert "self.api_key" not in source


def test_cloud_selection_is_never_reached_while_off():
    kind, _backend, _label = backends.select_backend()
    assert kind != backends.BACKEND_CLOUD


def test_the_backend_ladder_prefers_local_over_cloud(monkeypatch):
    """Even fully configured, cloud is last."""
    monkeypatch.setenv(backends.CLOUD_PROVIDER_ENV, "someprovider")
    monkeypatch.setenv(backends.CLOUD_API_KEY_ENV, "sk-not-a-real-key")
    state = backends.describe_backends()
    if not (state["ollama"]["available"] or state["local"]["available"]):
        pytest.skip("no local backend installed on this machine")
    kind, _backend, _label = backends.select_backend()
    assert kind in (backends.BACKEND_OLLAMA, backends.BACKEND_LOCAL_GGUF)


# ==========================================================================
# Task 6 — nothing sensitive lands in the app-data directory
# ==========================================================================

def test_no_corpus_identifier_reaches_any_written_file(tmp_path, monkeypatch):
    """Run every corpus document through and grep everything written."""
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "appdata" / "deidentified")
    key = json.loads((FIXTURE / "answer_key.json").read_text(encoding="utf-8"))

    for entry in key["documents"]:
        source = FIXTURE / entry["file"]
        documents, _ = batch.load_documents([str(source)])
        document = batch.analyze_document(documents[source.name])
        # A preserved place name ("Bolton") is flagged by the sweep and is the
        # reviewer's call to dismiss; stand in for that decision so the write
        # proceeds. Whether it is right is tested elsewhere — here we only care
        # that nothing identifying reaches disk.
        cleared = batch.sweep(document.redacted_text)
        batch.write_approved(
            document.name, document.redacted_text, acknowledged=cleared
        )
        batch.write_review_record(
            document.name, entities=document.entities,
            flags_shown=0, flags_redacted=0, flags_dismissed=0,
        )

    written = list((tmp_path / "appdata").rglob("*"))
    assert written, "nothing was written"
    blob = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in written
        if path.is_file()
    )
    for entry in key["documents"]:
        for value in entry["must_redact"]:
            assert value not in blob, f"{value} reached {tmp_path}"


def test_the_mapping_is_never_written(tmp_path, monkeypatch):
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "out")
    source = FIXTURE / "doc06_psych_clinic_letter.txt"
    documents, _ = batch.load_documents([str(source)])
    document = batch.analyze_document(documents[source.name])
    assert document.phi_map, "the fixture should produce a mapping"

    batch.write_approved(document.name, document.redacted_text)
    blob = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in (tmp_path / "out").rglob("*")
        if path.is_file()
    )
    for placeholder, value in document.phi_map.items():
        assert f"{placeholder}: {value}" not in blob
        assert value not in blob


# ==========================================================================
# Task 3 — app-data locations and the weak-laptop check
# ==========================================================================

def test_output_goes_under_the_user_profile():
    path = desktop.output_dir()
    assert desktop.APP_NAME in str(path)
    home = str(Path.home())
    assert str(path).startswith(home) or "AppData" in str(path) or "/tmp" in str(path)


def test_the_output_dir_is_overridable_by_the_launcher(monkeypatch):
    monkeypatch.setenv("CARESCRIBE_OUTPUT_DIR", r"X:\somewhere\else")
    import importlib

    reloaded = importlib.reload(batch)
    try:
        assert str(reloaded.OUTPUT_DIR) == r"X:\somewhere\else"
    finally:
        monkeypatch.delenv("CARESCRIBE_OUTPUT_DIR", raising=False)
        importlib.reload(batch)


def test_a_weak_laptop_gets_a_warning_not_a_crash(monkeypatch):
    monkeypatch.setattr(desktop, "available_ram_gb", lambda: 4.0)
    verdict = desktop.ram_verdict()
    assert not verdict["ok"]
    assert "ollama pull" in verdict["message"]
    # De-identification is unaffected — the message must say so.
    assert "review work normally" in verdict["message"]


def test_a_capable_laptop_gets_no_warning(monkeypatch):
    monkeypatch.setattr(desktop, "available_ram_gb", lambda: 16.0)
    assert desktop.ram_verdict()["ok"]


def test_resources_resolve_in_a_checkout():
    assert desktop.resource_path("carescribe", "app.py").is_file()
    assert desktop.streamlit_config_path().is_file()


# ==========================================================================
# Task 1 — the launcher binds loopback and nothing else
# ==========================================================================

def test_the_launcher_binds_loopback_only():
    import run_app

    command = run_app.server_command(12345)
    assert "--server.address=127.0.0.1" in command
    assert "--server.port=12345" in command
    assert "--server.headless=true" in command
    assert "--browser.gatherUsageStats=false" in command


def test_the_launcher_picks_a_free_port():
    import run_app

    port = run_app.free_port()
    assert 1024 < port < 65536


def test_the_streamlit_config_pins_loopback():
    config = desktop.streamlit_config_path().read_text(encoding="utf-8")
    assert '127.0.0.1' in config
    assert "gatherUsageStats = false" in config


def test_the_runtime_hook_pins_loopback_before_streamlit_starts():
    hook = (
        Path(__file__).resolve().parent.parent
        / "packaging" / "hooks" / "rthook_carescribe.py"
    ).read_text(encoding="utf-8")
    assert "STREAMLIT_SERVER_ADDRESS" in hook
    assert "127.0.0.1" in hook
    assert "STREAMLIT_BROWSER_GATHER_USAGE_STATS" in hook


# ==========================================================================
# Task 11 — the build is reproducible and checks its own output
# ==========================================================================

PACKAGING = Path(__file__).resolve().parent.parent / "packaging"


def test_the_spec_bundles_exactly_one_pinned_spacy_model():
    """A local build and a CI build must freeze the same model."""
    spec = (PACKAGING / "carescribe.spec").read_text(encoding="utf-8")
    # No loop over every model, bundling whatever is installed.
    assert 'for model in ("en_core_web_sm"' not in spec
    # Pinned to the documented default, overridable, hard-error if absent.
    assert "PACKAGED_DEFAULT_MODEL" in spec
    assert "CARESCRIBE_SPACY_MODEL" in spec
    assert "raise SystemExit" in spec
    # The bogus hidden import that logged a build-time ERROR is gone.
    assert "sklearn.utils._typedefs" not in spec


def test_the_frozen_launch_check_exists_and_is_wired_into_both_builds():
    verify = PACKAGING / "verify_frozen.py"
    source = verify.read_text(encoding="utf-8")
    assert "/_stcore/health" in source
    assert "--carescribe-server" in source

    import ast

    tree = ast.parse(source)
    assert any(
        isinstance(node, ast.FunctionDef) and node.name == "main"
        for node in tree.body
    ), "verify_frozen.py must expose a main()"

    win = (PACKAGING / "build_windows.ps1").read_text(encoding="utf-8")
    mac = (PACKAGING / "build_macos.sh").read_text(encoding="utf-8")
    assert "verify_frozen.py" in win
    assert "verify_frozen.py" in mac


def test_build_tool_pins_are_current():
    reqs = (PACKAGING / "requirements-build.txt").read_text(encoding="utf-8")
    assert "pyinstaller==6.10.0" not in reqs
    assert "pyinstaller==6.21" in reqs
