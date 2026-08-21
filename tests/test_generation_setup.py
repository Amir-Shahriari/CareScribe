"""
First-run generation setup: never an empty panel, and the egress line held.

The distinction these tests exist to pin:

* **Downloading a model** brings weights *in*. One outbound GET, only on a
  click, in one module that the document pipeline does not import.
* **Generating** runs that model locally and opens no socket at all.

Conflating the two would make "no egress" either false or unprovable.

Everything here is fabricated.
"""

from pathlib import Path

import pytest

from carescribe import app as carescribe_app
from carescribe.core import (
    backends, batch, carenotes, deidentify, desktop, generation_status, model_setup,
)
from tests.test_desktop_packaging import NoEgress, StubBackend

FIXTURE = Path(__file__).resolve().parent.parent / "stress_corpus"


@pytest.fixture(autouse=True)
def _cloud_off(monkeypatch):
    monkeypatch.delenv(backends.CLOUD_PROVIDER_ENV, raising=False)
    monkeypatch.delenv(backends.CLOUD_API_KEY_ENV, raising=False)


@pytest.fixture(autouse=True)
def _fresh_generation_status_cache():
    """generation_status() is now @st.cache_data(ttl=5) — a process-global

    cache keyed on nothing (the function takes no arguments). Every test in
    this file monkeypatches a different Ollama/model-file state and expects
    generation_status() to reflect it immediately; without clearing the
    cache first, whichever test happened to run first within the 5s TTL
    would poison every test after it.
    """
    generation_status.generation_status.clear()
    yield
    generation_status.generation_status.clear()


def _nothing_available(monkeypatch):
    """A fresh PC: no Ollama, no model file, no cloud."""
    monkeypatch.setattr(generation_status.ollama_client, "is_up", lambda: False)
    monkeypatch.setattr(generation_status.ollama_client, "list_models", lambda: [])
    monkeypatch.setattr(generation_status.desktop, "find_local_model", lambda *a, **k: None)


# ==========================================================================
# Task 1 — the readiness check
# ==========================================================================

def test_a_fresh_pc_is_not_ready_and_says_what_to_do(monkeypatch):
    _nothing_available(monkeypatch)
    status = generation_status.generation_status()
    assert not status.ready
    assert status.recommended_action
    assert generation_status.missing_reason(status)


def test_a_present_gguf_makes_it_ready(monkeypatch, tmp_path):
    monkeypatch.setattr(generation_status.ollama_client, "is_up", lambda: False)
    monkeypatch.setattr(generation_status.ollama_client, "list_models", lambda: [])
    fake = tmp_path / "model.gguf"
    fake.write_bytes(b"GGUF" + b"0" * 1000)
    monkeypatch.setattr(generation_status.desktop, "find_local_model", lambda *a, **k: fake)
    monkeypatch.setattr(generation_status, "_llama_runtime_available", lambda: True)

    status = generation_status.generation_status()
    assert status.ready
    assert status.local_gguf
    assert status.preferred == backends.BACKEND_LOCAL_GGUF


def test_an_ollama_model_makes_it_ready(monkeypatch):
    monkeypatch.setattr(generation_status.ollama_client, "is_up", lambda: True)
    monkeypatch.setattr(generation_status.ollama_client, "list_models", lambda: ["llama3.1:8b"])
    monkeypatch.setattr(generation_status.desktop, "find_local_model", lambda *a, **k: None)

    status = generation_status.generation_status()
    assert status.ready
    assert status.ollama
    assert status.preferred == backends.BACKEND_OLLAMA


def test_ollama_running_but_empty_recommends_pulling(monkeypatch):
    monkeypatch.setattr(generation_status.ollama_client, "is_up", lambda: True)
    monkeypatch.setattr(generation_status.ollama_client, "list_models", lambda: [])
    monkeypatch.setattr(generation_status.desktop, "find_local_model", lambda *a, **k: None)

    status = generation_status.generation_status()
    assert not status.ready
    assert status.recommended_action == generation_status.ACTION_PULL_OLLAMA
    assert "no model installed" in generation_status.missing_reason(status)


def test_cloud_alone_counts_as_ready(monkeypatch):
    _nothing_available(monkeypatch)
    monkeypatch.setenv(backends.CLOUD_PROVIDER_ENV, "someprovider")
    monkeypatch.setenv(backends.CLOUD_API_KEY_ENV, "sk-not-real")
    status = generation_status.generation_status()
    assert status.ready and status.cloud


def test_generation_status_is_cached(monkeypatch):
    """A second call within the TTL must not re-probe Ollama."""
    calls = {"n": 0}

    def fake_is_up():
        calls["n"] += 1
        return False

    monkeypatch.setattr(generation_status.ollama_client, "is_up", fake_is_up)
    generation_status.generation_status()
    generation_status.generation_status()
    assert calls["n"] == 1


# ==========================================================================
# Task 2 — the panel is never empty
# ==========================================================================

def test_the_setup_card_exists_and_names_the_options():
    import inspect

    source = inspect.getsource(carescribe_app.render_setup_card)
    assert "Option A" in source and "Option B" in source
    assert "one-time" in source
    # The copy must make the direction of travel explicit.
    assert "onto this computer" in source
    assert "No patient data is involved" in source


def test_the_panel_falls_back_to_the_setup_card_when_not_ready():
    import inspect

    source = inspect.getsource(carescribe_app.render_generation_panel)
    assert "generation_status" in source
    assert "render_setup_card" in source
    # The early return is what guarantees the panel is never rendered empty.
    assert "return" in source


def test_the_setup_card_is_reachable_from_the_unapproved_gate():
    import inspect

    source = inspect.getsource(carescribe_app.section_handoff)
    assert "render_setup_card" in source


def test_a_test_generation_action_exists():
    import inspect

    source = inspect.getsource(carescribe_app.render_test_generation)
    assert "Generation is ready" in source


# ==========================================================================
# Task 3 / 7 — the download is explicit, and separate from the pipeline
# ==========================================================================

def test_nothing_downloads_on_import_or_launch():
    """No module may fetch a model as a side effect of being imported."""
    import inspect

    for module in (generation_status, backends, desktop, carenotes, batch):
        source = inspect.getsource(module)
        assert "urlopen" not in source, f"{module.__name__} can reach the network"


def test_the_document_pipeline_never_imports_the_downloader():
    """The one outbound path must not be reachable from the de-id flow."""
    import inspect

    for module in (deidentify, batch, carenotes, mapping_module()):
        assert "model_setup" not in inspect.getsource(module)


def mapping_module():
    from carescribe.core import mapping

    return mapping


def test_the_downloader_is_the_only_module_with_an_outbound_get():
    import inspect

    source = inspect.getsource(model_setup)
    assert "urlopen" in source
    # And it is never called at import time.
    assert "download_model(" not in source.split("def download_model")[0]


def test_model_presence_is_the_persisted_marker(monkeypatch, tmp_path):
    """Setup is one-time because the file itself is the state."""
    monkeypatch.setattr(desktop, "find_local_model", lambda *a, **k: None)
    assert not model_setup.is_model_present()
    fake = tmp_path / "m.gguf"
    fake.write_bytes(b"GGUF")
    monkeypatch.setattr(desktop, "find_local_model", lambda *a, **k: fake)
    assert model_setup.is_model_present()


def test_a_truncated_download_is_rejected(tmp_path):
    partial = tmp_path / "m.gguf"
    partial.write_bytes(b"GGUF" + b"0" * 100)
    with pytest.raises(model_setup.ModelSetupError) as excinfo:
        model_setup._verify(partial, 2_000_000_000)
    assert "stopped early" in str(excinfo.value)


def test_an_html_error_page_is_rejected(tmp_path):
    """A captive portal returns HTML with a plausible size."""
    decoy = tmp_path / "m.gguf"
    decoy.write_bytes(b"<!DOCTYPE html>" + b"0" * 200_000_000)
    with pytest.raises(model_setup.ModelSetupError) as excinfo:
        model_setup._verify(decoy, 200_000_000)
    assert "not a valid model" in str(excinfo.value)


def test_the_download_goes_to_app_data_not_beside_the_exe():
    destination = model_setup.model_destination()
    assert desktop.APP_NAME in str(destination)
    assert "models" in str(destination)


# ==========================================================================
# Task 6 / 7 — de-identification needs no model, and opens no socket
# ==========================================================================

def test_the_whole_deid_path_works_with_no_model_at_all(tmp_path, monkeypatch):
    """A fresh PC must still de-identify, review and approve."""
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "out")
    _nothing_available(monkeypatch)
    assert not generation_status.generation_status().ready

    source = FIXTURE / "doc06_psych_clinic_letter.txt"
    with NoEgress() as guard:
        documents, errors = batch.load_documents([str(source)])
        assert not errors
        document = batch.analyze_document(documents[source.name])
        assert document.entities
        assert deidentify.residual_scan(document.redacted_text) == []
        written = batch.write_approved(document.name, document.redacted_text)

    assert written.exists()
    assert guard.attempts == [], guard.attempts


def test_inference_opens_no_socket_even_after_setup(tmp_path, monkeypatch):
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "out")
    source = FIXTURE / "doc06_psych_clinic_letter.txt"
    documents, _ = batch.load_documents([str(source)])
    document = batch.analyze_document(documents[source.name])

    with NoEgress() as guard:
        draft = "".join(
            carenotes.generate_document(
                document.redacted_text, "SOAP care note", StubBackend(),
                phi_values=list(document.phi_map.values()),
            )
        )
    assert draft
    assert guard.attempts == []


def test_the_local_model_stays_pinned_at_temperature_zero():
    """It fabricates otherwise — measured, not assumed."""
    assert backends.LocalGGUFBackend().temperature == 0.0


def test_generated_output_keeps_the_review_banner():
    assert carenotes.with_banner("Body").startswith("> **DRAFT")


def test_the_privacy_indicator_has_a_downloading_state():
    import inspect

    source = inspect.getsource(carescribe_app.privacy_indicator)
    assert "downloading_model" in source
    assert "no patient data is going out" in source
    assert "Running fully offline" in source


# ==========================================================================
# Task 4 / 7 — de-identification is provably offline, and fails loud
# ==========================================================================

def test_deidentification_opens_no_socket_at_all():
    """The load that used to hang on a captive portal must not exist."""
    from carescribe.core import applog  # noqa: F401

    text = (FIXTURE / "doc06_psych_clinic_letter.txt").read_text(encoding="utf-8")
    deidentify.get_analyzer()  # warm, so the guard covers the model load too
    with NoEgress() as guard:
        result = deidentify.deidentify(text)
    assert result.entities
    assert guard.attempts == [], guard.attempts


def test_the_cold_model_load_opens_no_socket(monkeypatch):
    """Reset the cache so the guard covers a genuine first load."""
    monkeypatch.setattr(deidentify, "_ANALYZER_TRIED", False)
    monkeypatch.setattr(deidentify, "_ANALYZER", None)
    with NoEgress() as guard:
        deidentify.get_analyzer()
    assert guard.attempts == [], guard.attempts


def test_offline_flags_are_set_at_import():
    import os

    assert os.environ.get("HF_HUB_OFFLINE") == "1"
    assert os.environ.get("TRANSFORMERS_OFFLINE") == "1"


def test_a_missing_model_fails_loudly_instead_of_fetching(monkeypatch):
    """The reported hang: no model, so something tries to download it."""
    monkeypatch.setattr(deidentify, "SPACY_MODELS", ("en_core_web_nonexistent",))
    with NoEgress() as guard:
        engine, model, error = deidentify._build_analyzer()
    assert engine is None
    assert error and "not installed" in error
    # The point of the fix: it reports, it does not reach for the network.
    assert guard.attempts == []


def test_a_missing_model_in_a_frozen_build_says_so(monkeypatch):
    monkeypatch.setattr(deidentify, "SPACY_MODELS", ("en_core_web_nonexistent",))
    monkeypatch.setattr(deidentify, "is_frozen_build", lambda: True)
    _engine, _model, error = deidentify._build_analyzer()
    assert "not installed in this build" in error
    assert "rebuilding" in error


def test_model_paths_resolve_explicitly():
    assert deidentify.resolve_model_path("en_core_web_nonexistent") is None
    assert deidentify.available_models()


def test_the_log_records_timings_without_phi(tmp_path, monkeypatch):
    from carescribe.core import applog

    text = (FIXTURE / "doc06_psych_clinic_letter.txt").read_text(encoding="utf-8")
    result = deidentify.deidentify(text)
    written = applog.log_path().read_text(encoding="utf-8", errors="ignore")
    assert "de-identify: done" in written
    # Lengths and counts, never content.
    for value in result.phi_map.values():
        assert value not in written


def test_the_engine_loader_is_cached_per_session():
    import inspect

    from carescribe import app as carescribe_app

    source = inspect.getsource(carescribe_app)
    assert "@st.cache_resource" in source
    assert "ensure_engine_ready" in source
    # Loaded up front, not on the first click.
    assert "ensure_engine_ready()" in inspect.getsource(carescribe_app.main)


# ==========================================================================
# The KeyError regression: two dictionaries, one variable name
# ==========================================================================

def test_the_draft_state_and_backend_state_are_not_confused():
    """`state` held the draft dict, then the backend dict overwrote it.

    The draft dict has "deidentified"; the backend dict has "ollama"/"local"/
    "cloud". Reading the first key off the second is the reported KeyError.
    """
    import inspect

    source = inspect.getsource(carescribe_app.render_generation_panel)
    # The two must never share a name again.
    assert "backends_available = render_generation_status()" in source
    assert "draft = _draft_state(" in source
    assert "state = render_generation_status()" not in source


def test_the_draft_state_carries_the_expected_keys():
    """The canonical shape of a document's generated-draft state."""
    import inspect

    source = inspect.getsource(carescribe_app._draft_state)
    for key in ("deidentified", "reidentified", "history", "unresolved"):
        assert f'"{key}"' in source


def test_the_panel_reads_the_draft_defensively():
    import inspect

    source = inspect.getsource(carescribe_app.render_generation_panel)
    # .get(), so a state dict from an older session cannot crash the panel.
    assert 'draft.get("deidentified")' in source


def test_an_unapproved_document_gets_a_message_not_a_traceback():
    import inspect

    source = inspect.getsource(carescribe_app.render_generation_panel)
    assert "hasn't been approved for generation yet" in source
    # The guard must come before anything that indexes into state.
    guard = source.index("hasn't been approved")
    first_state_read = source.index("_draft_state(")
    assert guard < first_state_read


def test_the_helpers_name_the_draft_dict_explicitly():
    """Renamed from `state` so the collision cannot recur."""
    import inspect

    for function in (
        carescribe_app.render_draft,
        carescribe_app.render_refinement,
        carescribe_app.render_reidentification,
    ):
        signature = inspect.signature(function)
        assert "draft_state" in signature.parameters


def test_an_approved_document_exposes_its_deidentified_text(tmp_path, monkeypatch):
    """The canonical source of truth for approved text is the document itself."""
    monkeypatch.setattr(batch, "OUTPUT_DIR", tmp_path / "out")
    source = FIXTURE / "doc06_psych_clinic_letter.txt"
    documents, _ = batch.load_documents([str(source)])
    document = batch.analyze_document(documents[source.name])
    batch.write_approved(document.name, document.redacted_text)
    document.approved = True

    assert document.redacted_text.strip()
    assert "[PATIENT]" in document.redacted_text
    # Generation reads this, never a parallel copy in session state.
    assert not any(v in document.redacted_text for v in document.phi_map.values())
