# LLM Backend Flexibility + Realistic Test Corpus Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let the user pick any installed local LLM (and, secondarily, a cloud provider) from an in-app settings panel instead of env-vars + restart, fix the temperature inconsistency that was causing hallucinated clinical details, and grow the realistic-document test corpus until `pytest tests -q` is 100% green against it.

**Architecture:** Extend the existing three-tier backend ladder (`carescribe/core/backends.py`) rather than rebuild it — add a small settings-persistence module, thread explicit model/temperature overrides through `select_backend()`, add one in-app settings screen, and grow `stress_corpus/` (answer-key-driven redaction regression) and `sample_documents/` (full-pipeline generation exercise) with harder, messier, realistically-shaped fabricated documents, fixing whatever the harder documents surface.

**Tech Stack:** Python 3.11, Streamlit (+ `streamlit.testing.v1.AppTest` for headless UI tests), pytest, `python-docx` for `.docx` generation, stdlib `json`/`dataclasses`.

**Spec:** `docs/superpowers/specs/2026-09-02-llm-flexibility-and-realistic-corpus-design.md`

## Global Constraints

- Temperature default is `0.0` on every backend (Ollama, local GGUF, cloud) — a prior 0.2 default on Ollama caused the bundled model to invent unsupported clinical details; see `LocalGGUFBackend`'s docstring in `carescribe/core/backends.py` for the reasoning this generalises.
- The cloud API key is **never** persisted to disk — session-only (`st.session_state`), matching the existing guarantee in `carescribe/core/cloud_client.py`.
- No new named cloud providers beyond the existing `anthropic` / `openai`-compatible wire shapes in `cloud_client.py` (out of scope per the spec's non-goals).
- No rebuild of the backend `Protocol`/ladder architecture — this plan extends `select_backend()`'s signature, it does not replace it.
- Every new corpus document is 100% fabricated: UK-context documents (`stress_corpus/`) reuse the existing conventions — Ofcom drama-range phone numbers (`01632 960xxx`), `example.co.uk`/`example.com` emails, format-valid-but-fake NHS numbers, invented names; AU-context documents (`sample_documents/`) follow `make_sample_docs.py`'s existing Medicare/VIC-address convention. Never add a real patient document to either folder (both READMEs already state this — it stands).
- Run `pytest tests -q` after every task that touches code or corpus data; it must stay green (or, for corpus tasks, reach green through fixes, not through weakening `answer_key.json`).
- `graphify update .` after all code-touching tasks (not corpus-only text/docx additions, which graphify doesn't index).

---

### Task 1: Settings persistence module

**Files:**
- Create: `carescribe/core/settings.py`
- Test: `tests/test_settings.py`

**Interfaces:**
- Produces: `Settings` dataclass with fields `backend: str = ""`, `ollama_model: str = ""`, `temperature: float = 0.0`, `cloud_provider: str = ""`, `cloud_base_url: str = ""`, `cloud_model: str = ""`. `load_settings() -> Settings`. `save_settings(settings: Settings) -> None`. Both used by Task 3.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_settings.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_settings.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'carescribe.core.settings'`

- [ ] **Step 3: Write the implementation**

```python
# carescribe/core/settings.py
"""
Persisted app settings — which generation backend/model/temperature to use.

Lives at ``app_data_dir() / "settings.json"``. Deliberately excludes the
cloud API key: that stays session-only (``st.session_state`` in ``app.py``),
matching the guarantee in ``cloud_client.py`` that a key is never stored,
logged, or bundled. Everything else here is just a preference, safe to
persist in plain JSON.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path

from . import desktop

SETTINGS_FILENAME = "settings.json"


@dataclass
class Settings:
    # "" means "use the automatic ladder" — Ollama if up, else bundled GGUF,
    # else cloud if configured. A non-empty value pins one.
    backend: str = ""
    # "" means "use ollama_client.default_model()'s guess". A non-empty value
    # must be one of the currently-installed models or select_backend() falls
    # back to the guess rather than erroring.
    ollama_model: str = ""
    temperature: float = 0.0
    cloud_provider: str = ""
    cloud_base_url: str = ""
    cloud_model: str = ""


_FIELD_NAMES = {f.name for f in fields(Settings)}


def _path() -> Path:
    return desktop.app_data_dir() / SETTINGS_FILENAME


def load_settings() -> Settings:
    """Read persisted settings. A missing or unreadable file yields defaults."""
    path = _path()
    if not path.exists():
        return Settings()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return Settings()
    filtered = {k: v for k, v in data.items() if k in _FIELD_NAMES}
    return Settings(**filtered)


def save_settings(settings: Settings) -> None:
    """Persist non-secret settings, creating the app data dir if needed."""
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")


__all__ = ["Settings", "load_settings", "save_settings"]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_settings.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add carescribe/core/settings.py tests/test_settings.py
git commit -m "feat(settings): persisted backend/model/temperature preferences"
```

---

### Task 2: `select_backend()` explicit model/temperature overrides + Ollama temperature fix

**Files:**
- Modify: `carescribe/core/backends.py` (the `build()` closure inside `select_backend()`, and `select_backend`'s signature)
- Modify: `carescribe/core/carenotes.py:71` (`OllamaBackend.__init__` temperature default)
- Test: `tests/test_backend_overrides.py`

**Interfaces:**
- Consumes: `Settings` is NOT imported here — this task only changes `select_backend`'s signature; Task 3 is what reads `Settings` and calls it.
- Produces: `select_backend(prefer: str | None = None, model: str | None = None, temperature: float | None = None) -> tuple[str, object, str]` — same return shape as today. `OllamaBackend(model, temperature=0.0)` new default.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_backend_overrides.py
from __future__ import annotations

from carescribe.core import backends
from carescribe.core.carenotes import OllamaBackend


def test_ollama_backend_default_temperature_is_zero():
    assert OllamaBackend("llama3.1:8b").temperature == 0.0


def test_select_backend_honours_explicit_ollama_model(monkeypatch):
    monkeypatch.setattr(backends.ollama_client, "is_up", lambda: True)
    monkeypatch.setattr(
        backends.ollama_client, "list_models", lambda: ["qwen2.5:32b", "llama3.1:8b"]
    )
    kind, backend, label = backends.select_backend(prefer="ollama", model="qwen2.5:32b")
    assert kind == backends.BACKEND_OLLAMA
    assert backend.model == "qwen2.5:32b"
    assert "qwen2.5:32b" in label


def test_select_backend_falls_back_when_requested_model_not_installed(monkeypatch):
    monkeypatch.setattr(backends.ollama_client, "is_up", lambda: True)
    monkeypatch.setattr(backends.ollama_client, "list_models", lambda: ["llama3.1:8b"])
    _, backend, _ = backends.select_backend(prefer="ollama", model="not-installed:1b")
    assert backend.model == "llama3.1:8b"


def test_select_backend_threads_temperature_override_to_ollama(monkeypatch):
    monkeypatch.setattr(backends.ollama_client, "is_up", lambda: True)
    monkeypatch.setattr(backends.ollama_client, "list_models", lambda: ["llama3.1:8b"])
    _, backend, _ = backends.select_backend(prefer="ollama", temperature=0.5)
    assert backend.temperature == 0.5


def test_select_backend_threads_temperature_override_to_local_gguf(monkeypatch):
    monkeypatch.setattr(backends.ollama_client, "is_up", lambda: False)
    monkeypatch.setattr(backends.LocalGGUFBackend, "available", staticmethod(lambda: True))
    monkeypatch.setattr(
        backends.desktop, "find_local_model", lambda: __import__("pathlib").Path("model.gguf")
    )
    _, backend, _ = backends.select_backend(prefer="local", temperature=0.7)
    assert backend.temperature == 0.7


def test_select_backend_with_no_overrides_still_works(monkeypatch):
    """The default (no prefer/model/temperature) path is unchanged."""
    monkeypatch.setattr(backends.ollama_client, "is_up", lambda: True)
    monkeypatch.setattr(backends.ollama_client, "list_models", lambda: ["llama3.1:8b"])
    kind, backend, _ = backends.select_backend()
    assert kind == backends.BACKEND_OLLAMA
    assert backend.temperature == 0.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_backend_overrides.py -v`
Expected: FAIL — `test_ollama_backend_default_temperature_is_zero` fails (currently 0.2);
`select_backend() got an unexpected keyword argument 'model'` on the others.

- [ ] **Step 3: Fix the temperature default**

In `carescribe/core/carenotes.py`, change:

```python
    def __init__(self, model: str, temperature: float = 0.2) -> None:
```

to:

```python
    def __init__(self, model: str, temperature: float = 0.0) -> None:
```

- [ ] **Step 4: Thread model/temperature through `select_backend()`**

In `carescribe/core/backends.py`, replace the `build()` closure and `select_backend` signature:

```python
def select_backend(
    prefer: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
):
    """Pick a backend. Returns ``(kind, backend, label)``.

    ``prefer`` lets the UI honour an explicit backend choice; without it the
    ladder is Ollama -> bundled GGUF -> cloud-only-if-configured. ``model``
    pins an explicit installed Ollama model (falling back to the guessed
    default if it is not actually installed — a stale saved preference must
    not turn into an error). ``temperature`` overrides the backend's own
    default on Ollama and the bundled GGUF backend.
    """
    state = describe_backends()

    def build(kind: str):
        if kind == BACKEND_OLLAMA and state["ollama"]["available"]:
            from .carenotes import OllamaBackend

            chosen = model if model in state["ollama"]["models"] else None
            chosen = chosen or state["ollama"]["default_model"]
            kwargs = {} if temperature is None else {"temperature": temperature}
            return kind, OllamaBackend(chosen, **kwargs), f"Ollama · {chosen}"
        if kind == BACKEND_LOCAL_GGUF and state["local"]["available"]:
            from pathlib import Path

            name = Path(state["local"]["model_path"]).name
            kwargs = {} if temperature is None else {"temperature": temperature}
            return kind, LocalGGUFBackend(**kwargs), f"Built-in model · {name}"
        if kind == BACKEND_CLOUD and state["cloud"]["available"]:
            provider = state["cloud"]["provider"]
            return kind, CloudBackend(provider), f"Cloud · {provider}"
        return None

    if prefer:
        chosen = build(prefer)
        if chosen:
            return chosen

    for kind in (BACKEND_OLLAMA, BACKEND_LOCAL_GGUF, BACKEND_CLOUD):
        chosen = build(kind)
        if chosen:
            return chosen

    raise BackendError(
        "No generation backend is available.\n\n"
        "De-identification and review work without one. For generation, either "
        "reinstall CareScribe so the built-in model is present, or install "
        "Ollama and run: ollama pull qwen2.5:3b"
    )
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_backend_overrides.py tests/test_generation_setup.py tests/test_generation.py -v`
Expected: all pass — the last two files exercise the pre-existing `select_backend()`/`OllamaBackend` behavior and must not regress.

- [ ] **Step 6: Run the full suite**

Run: `python -m pytest tests -q`
Expected: 100% pass (this touches shared backend-selection code, so the full suite is the real gate, not just the new file)

- [ ] **Step 7: `graphify update .`**

Run: `graphify update .`

- [ ] **Step 8: Commit**

```bash
git add carescribe/core/backends.py carescribe/core/carenotes.py tests/test_backend_overrides.py
git commit -m "fix(backends): consistent 0.0 temperature default + explicit model/temperature overrides in select_backend()"
```

---

### Task 3: Settings panel UI + wiring generation call sites through it

**Files:**
- Modify: `carescribe/app.py` (import block; new `_active_backend()` helper; sidebar; 5 call sites)
- Test: `tests/test_settings_panel_screen.py`

**Interfaces:**
- Consumes: `settings.Settings` / `settings.load_settings()` / `settings.save_settings()` (Task 1); `backends.select_backend(prefer=, model=, temperature=)` (Task 2).
- Produces: `_active_backend()` — drop-in replacement for the old bare `backends.select_backend()` calls, used by later generation code unchanged.

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_settings_panel_screen.py -v`
Expected: FAIL — no settings expander/selectbox/button exists yet.

- [ ] **Step 3: Add `settings` to the core import block**

In `carescribe/app.py`, change:

```python
from carescribe.core import (  # noqa: E402
    applog, backends, batch, carenotes, deidentify, desktop, generation_status,
    ingest, mapping, model_setup, ollama_client, review_checklist, review_flags,
    review_spans,
)
```

to:

```python
from carescribe.core import (  # noqa: E402
    applog, backends, batch, carenotes, deidentify, desktop, generation_status,
    ingest, mapping, model_setup, ollama_client, review_checklist, review_flags,
    review_spans, settings,
)
```

- [ ] **Step 4: Add `_active_backend()` next to `render_test_generation`**

Insert directly above `def render_test_generation() -> None:` in `carescribe/app.py`:

```python
def _active_backend():
    """Resolve the backend to generate with, honouring saved settings.

    Centralises what used to be five separate ``backends.select_backend()``
    call sites so a saved backend/model/temperature choice (see
    ``core/settings.py`` and the sidebar Settings panel) actually takes
    effect everywhere generation happens, not just in one place.
    """
    cfg = settings.load_settings()
    return backends.select_backend(
        prefer=cfg.backend or None,
        model=cfg.ollama_model or None,
        temperature=cfg.temperature,
    )
```

- [ ] **Step 5: Replace the 5 `backends.select_backend()` call sites**

In `render_test_generation`:
```python
                _, backend, label = backends.select_backend()
```
becomes
```python
                _, backend, label = _active_backend()
```

In `_run_generation`:
```python
            _, backend, _label = backends.select_backend()
```
becomes
```python
            _, backend, _label = _active_backend()
```

In the refinement call inside `render_refinement` (the `carenotes.refine_document(...)` call):
```python
                        backends.select_backend()[1],
```
becomes
```python
                        _active_backend()[1],
```

In the clinical-form generation call:
```python
            _, backend, _label = backends.select_backend()
```
(the one immediately before `clinical_forms.generate_form_document(...)`) becomes
```python
            _, backend, _label = _active_backend()
```

In the clinical-form refinement call:
```python
                        backends.select_backend()[1], stream=True,
```
becomes
```python
                        _active_backend()[1], stream=True,
```

- [ ] **Step 6: Add the Settings panel to `render_sidebar()`**

At the end of `render_sidebar()` in `carescribe/app.py`, add:

```python
    st.sidebar.write("")
    with st.sidebar.expander("⚙ Settings"):
        cfg = settings.load_settings()
        backend_options = ["", backends.BACKEND_OLLAMA, backends.BACKEND_LOCAL_GGUF, backends.BACKEND_CLOUD]
        backend_labels = {
            "": "Automatic (recommended)",
            backends.BACKEND_OLLAMA: "Ollama",
            backends.BACKEND_LOCAL_GGUF: "Built-in model",
            backends.BACKEND_CLOUD: "Cloud",
        }
        chosen_backend = st.selectbox(
            "Generation backend", backend_options,
            index=backend_options.index(cfg.backend) if cfg.backend in backend_options else 0,
            format_func=lambda k: backend_labels[k], key="settings_backend",
        )
        installed = ollama_client.list_models() if ollama_client.is_up() else []
        chosen_model = ""
        if installed:
            model_options = [""] + installed
            chosen_model = st.selectbox(
                "Ollama model", model_options,
                index=model_options.index(cfg.ollama_model) if cfg.ollama_model in model_options else 0,
                format_func=lambda m: "Automatic" if m == "" else m, key="settings_ollama_model",
            )
        chosen_temperature = st.number_input(
            "Temperature", min_value=0.0, max_value=1.0, step=0.1,
            value=cfg.temperature, key="settings_temperature",
        )
        st.caption(
            "Cloud provider settings are configured via environment variables "
            "(see docs/deployer-cloud-note.md) — the API key is never saved here."
        )
        if st.button("Save settings", key="settings_save"):
            settings.save_settings(settings.Settings(
                backend=chosen_backend,
                ollama_model=chosen_model,
                temperature=float(chosen_temperature),
                cloud_provider=cfg.cloud_provider,
                cloud_base_url=cfg.cloud_base_url,
                cloud_model=cfg.cloud_model,
            ))
            st.success("Saved.")
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `python -m pytest tests/test_settings_panel_screen.py -v`
Expected: 2 passed. If `AppTest`'s `.expander`/`.selectbox` accessors don't expose `.key` the way assumed, inspect the actual `AppTest` element API (`app.sidebar.selectbox[0]` etc. — check with a quick `print` in a scratch run) and adjust the test's lookups to match; the behavior under test (save persists, reload reflects it) is what matters, not the exact accessor.

- [ ] **Step 8: Run the full suite**

Run: `python -m pytest tests -q`
Expected: 100% pass

- [ ] **Step 9: `graphify update .`**

Run: `graphify update .`

- [ ] **Step 10: Commit**

```bash
git add carescribe/app.py tests/test_settings_panel_screen.py
git commit -m "feat(app): in-app Settings panel for backend/model/temperature, wired into every generation call site"
```

---

### Task 4: Stress corpus expansion — batch 1 (5 documents)

**Files:**
- Create: `stress_corpus/doc11_multi_identifier_cpn_review.txt`
- Create: `stress_corpus/doc12_safeguarding_referral.txt`
- Create: `stress_corpus/doc13_ocr_style_discharge_summary.txt`
- Create: `stress_corpus/doc14_family_therapy_notes.txt`
- Create: `stress_corpus/doc15_risk_assessment_grid.txt`
- Modify: `stress_corpus/answer_key.json` (append 5 entries)

**Interfaces:**
- Consumes: nothing from earlier tasks — this is a pure data addition, exercised by the existing `tests/test_stress_corpus.py` (no test-code changes needed, per its own docstring).
- Produces: 5 new `(file, must_redact, must_preserve)` triples other tasks (Task 7) can point at for the full-pipeline run.

Each document must be fabricated (see Global Constraints), UK NHS-context like the existing 10, and deliberately harder than any single existing document along the axis named:

1. **`doc11_multi_identifier_cpn_review.txt`** — a community psychiatric nurse review letter naming FOUR different people with identifiers: the client, their named next-of-kin/carer, their GP, and their care coordinator — each with at least a name and one other identifier (phone or address). Mix three date formats in the same document (`15/03/2026`, `15-Mar-2026`, `15th March 2026`). Include a medication table rendered as plain-text pipe-separated rows (e.g. `Sertraline | 100mg | Once daily | Started 03/2026`).
2. **`doc12_safeguarding_referral.txt`** — a safeguarding referral with a letterhead block (organisation name/address/phone/fax all together, the way `doc03`/`doc05` do it but denser), abbreviated name references in the body (`J. Smith`, `Jas. Smith`, `Mr Smith`) that must all resolve to the same full name in `must_redact`, and at least one place where a bracketed placeholder-looking string already appears in the source text (e.g. `[interpreter arranged]`) — that string must land in `must_preserve` since it is not an identifier and must not be swept up as one.
3. **`doc13_ocr_style_discharge_summary.txt`** — simulates a scanned/OCR'd discharge summary: a couple of words hyphen-broken across a line break (e.g. `pati-\nent`), THREE distinct identifier numbers for the same person (hospital number, NHS number, local trust ID, each a different format), and dates mixing ISO (`2026-03-15`) with `DD/MM/YY`.
4. **`doc14_family_therapy_notes.txt`** — family therapy session notes naming the client plus mother, father, and one sibling by name, with a phone number embedded mid-sentence in prose (no `Phone:` label to anchor on), and pronoun-only references that follow a named mention (a real redaction leak risk if the de-identifier over-relies on labelled fields).
5. **`doc15_risk_assessment_grid.txt`** — a risk-assessment document that is almost entirely a grid/table (risk category, rating, identifiers repeated per row) rendered as text, plus a clinician sign-off footer with a name, professional registration number, and direct-dial phone number.

- [ ] **Step 1: Write the 5 documents**

Author each `.txt` file under `stress_corpus/`, following the exact fabrication conventions already in the other 10 files (read `stress_corpus/doc10_mha_assessment.txt` and `stress_corpus/doc05_gp_referral.txt` first for tone/format) and the specific hard-case requirement listed above for that document. Every identifier you invent (name, phone, date of birth, address, record number) must be one you can enumerate precisely — you decide the content, so the answer key is exact by construction, not guessed after the fact.

- [ ] **Step 2: Append matching `answer_key.json` entries**

For each new document, add an object to the `documents` array in `stress_corpus/answer_key.json` in the existing shape:

```json
{
  "file": "doc11_multi_identifier_cpn_review.txt",
  "covers": ["four identifiers in one document", "mixed date formats", "plain-text medication table"],
  "must_redact": ["<every name, phone, address, DOB, record number you wrote>"],
  "must_preserve": ["<every clinical term, medication name, place name you want kept>"]
}
```
(repeat for doc12–doc15, `covers` naming the hard case each one targets from the list above)

- [ ] **Step 3: Run the stress corpus test**

Run: `python -m pytest tests/test_stress_corpus.py -v`
Expected: every case for doc11–doc15 passes. If a `must_redact` string survives redaction, that is a real de-identification bug — trace it in `carescribe/core/deidentify.py` and fix the underlying pattern/rule rather than removing the assertion or softening the document. If a `must_preserve` string got redacted, same — fix the over-redaction, don't delete the assertion.

- [ ] **Step 4: Run the full suite**

Run: `python -m pytest tests -q`
Expected: 100% pass

- [ ] **Step 5: Commit**

```bash
git add stress_corpus/doc11_multi_identifier_cpn_review.txt stress_corpus/doc12_safeguarding_referral.txt stress_corpus/doc13_ocr_style_discharge_summary.txt stress_corpus/doc14_family_therapy_notes.txt stress_corpus/doc15_risk_assessment_grid.txt stress_corpus/answer_key.json
git commit -m "test(stress_corpus): 5 harder realistic documents — multi-identifier, OCR-style breaks, unlabelled phone in prose, grid-heavy layout"
```

---

### Task 5: Stress corpus expansion — batch 2 (5 documents)

**Files:**
- Create: `stress_corpus/doc16_out_of_area_transfer.txt`
- Create: `stress_corpus/doc17_email_correspondence_thread.txt`
- Create: `stress_corpus/doc18_court_report.txt`
- Create: `stress_corpus/doc19_pharmacy_medication_review.txt`
- Create: `stress_corpus/doc20_telephone_triage_log.txt`
- Modify: `stress_corpus/answer_key.json` (append 5 entries)
- Modify: `stress_corpus/README.md` (the doc table currently only lists doc01–doc05 — extend it to doc01–doc20)

**Interfaces:**
- Consumes: same as Task 4 — pure data, run against the unchanged `tests/test_stress_corpus.py`.
- Produces: 10 total new documents (with Task 4) available to Task 7's full-pipeline run.

1. **`doc16_out_of_area_transfer.txt`** — a transfer letter between two different NHS trusts, each with its own address/phone block, so the SAME client has two different local record numbers (sending trust's and receiving trust's) that must both be redacted.
2. **`doc17_email_correspondence_thread.txt`** — formatted as an email thread (`From:`/`To:`/`Subject:`/`Sent:` headers with names and email addresses, then a quoted reply chain below a `-----Original Message-----` marker) — the same identifiers repeat across the original and the quoted reply, both must be caught.
3. **`doc18_court_report.txt`** — a legal/court-style report: a solicitor's name and firm, a court case reference number, and the client's date of birth spelled out in prose (e.g. "born on the fourteenth of July, nineteen eighty-five") rather than in digits.
4. **`doc19_pharmacy_medication_review.txt`** — a dense medication review table (drug, dose, prescriber name, prescriber registration number, review date) with a different prescriber per row, so several distinct names must each be redacted independently.
5. **`doc20_telephone_triage_log.txt`** — a timestamped call log, one line per contact (`14:32 - call from Mrs J. Okafor (07700 900xxx-style Ofcom number) re: medication query`), informal shorthand instead of full clinical prose.

- [ ] **Step 1: Write the 5 documents**

Same process as Task 4 Step 1, targeting the 5 hard cases above.

- [ ] **Step 2: Append matching `answer_key.json` entries**

Same shape as Task 4 Step 2.

- [ ] **Step 3: Update `stress_corpus/README.md`'s document table**

Extend the `| Document | Exercises |` table to include rows for doc06 through doc20 (doc06–doc10 are already-existing files the current README never documented — check what each already covers by reading it, then add its row too, not just the 10 new ones).

- [ ] **Step 4: Run the stress corpus test**

Run: `python -m pytest tests/test_stress_corpus.py -v`
Expected: every case for doc16–doc20 passes, same fix-don't-weaken rule as Task 4 Step 3.

- [ ] **Step 5: Run the full suite**

Run: `python -m pytest tests -q`
Expected: 100% pass — 20 documents total in `stress_corpus/`.

- [ ] **Step 6: Commit**

```bash
git add stress_corpus/doc16_out_of_area_transfer.txt stress_corpus/doc17_email_correspondence_thread.txt stress_corpus/doc18_court_report.txt stress_corpus/doc19_pharmacy_medication_review.txt stress_corpus/doc20_telephone_triage_log.txt stress_corpus/answer_key.json stress_corpus/README.md
git commit -m "test(stress_corpus): 5 more realistic documents — dual trust IDs, email thread, prose DOB, per-row prescriber, triage log; README caught up to all 20"
```

---

### Task 6: Sample documents expansion (full-pipeline generation exercise)

**Files:**
- Modify: `sample_documents/make_sample_docs.py` (add 3 new `build_*` functions + register them in `__main__`)
- Create (generated by running the script, not hand-written): `sample_documents/05_discharge_summary.docx`, `sample_documents/06_risk_assessment.docx`, `sample_documents/07_case_conference_note.docx`
- Modify: `sample_documents/README.md` (extend the file table)

**Interfaces:**
- Consumes: the existing `_heading`, `_para`, `_two_col_table`, `_grid_table` helpers already in `make_sample_docs.py` — reuse them, don't duplicate.
- Produces: 3 new `.docx` files Task 7's full-pipeline test iterates over (it globs `sample_documents/*.docx`, so no wiring needed beyond the files existing).

Add these 3 scenarios (same fictional client, Jordan Whitfield, as the existing 4, so they can still be combined together per the README's existing convention; AU Medicare/VIC-address context like the rest of the file):

1. **`build_discharge_summary`** — a hospital discharge summary: admission/discharge dates, presenting complaint, a `_grid_table` of medications changed on discharge (drug, prior dose, new dose, reason), and a discharge diagnosis paragraph.
2. **`build_risk_assessment`** — a structured risk assessment: a `_two_col_table` of risk domains (self-harm, suicide, harm to others, self-neglect) each with a rating and a narrative paragraph per domain, plus a safety plan section.
3. **`build_case_conference_note`** — minutes from a multi-disciplinary case conference: a `_grid_table` of attendees (name, role, organisation) — deliberately more names/roles in one document than any existing sample — followed by narrative decisions/actions paragraphs.

- [ ] **Step 1: Add the 3 build functions to `make_sample_docs.py`**

Follow the exact structural pattern of `build_referral_letter` (heading, address/contact line, `_heading`+`_two_col_table` or `_grid_table` sections, narrative `_para` blocks, `doc.save(path)` at the end) for each of the 3 new functions. Use fabricated AU-context details consistent with the existing file (Medicare-style numbers, VIC addresses/phone formats, `@example.com` emails) and the same client name, Jordan Whitfield, so the four existing + three new documents remain combinable.

- [ ] **Step 2: Register the new builds in `__main__`**

```python
if __name__ == "__main__":
    build_referral_letter(os.path.join(OUT_DIR, "01_gp_referral_letter.docx"))
    build_intake_notes(os.path.join(OUT_DIR, "02_biopsychosocial_intake_notes.docx"))
    build_session_log(os.path.join(OUT_DIR, "03_session_log_progress_notes.docx"))
    build_treatment_review_source(os.path.join(OUT_DIR, "04_treatment_review_source.docx"))
    build_discharge_summary(os.path.join(OUT_DIR, "05_discharge_summary.docx"))
    build_risk_assessment(os.path.join(OUT_DIR, "06_risk_assessment.docx"))
    build_case_conference_note(os.path.join(OUT_DIR, "07_case_conference_note.docx"))
    print("done:", os.listdir(OUT_DIR))
```

- [ ] **Step 3: Generate the files**

Run: `python sample_documents/make_sample_docs.py` (from the repo root, or `cd sample_documents && python make_sample_docs.py`)
Expected: prints `done: [...]` listing all 7 `.docx` files.

- [ ] **Step 4: Update `sample_documents/README.md`**

Add rows for the 3 new files to the existing `| File | Mimics | Feeds which form best |` table.

- [ ] **Step 5: Run the full suite**

Run: `python -m pytest tests -q`
Expected: 100% pass (this task doesn't touch tested code, but confirms nothing else broke).

- [ ] **Step 6: Commit**

```bash
git add sample_documents/make_sample_docs.py sample_documents/05_discharge_summary.docx sample_documents/06_risk_assessment.docx sample_documents/07_case_conference_note.docx sample_documents/README.md
git commit -m "test(sample_documents): 3 more full-pipeline scenarios — discharge summary, risk assessment, case conference"
```

---

### Task 7: Full-pipeline validation across every sample document

**Files:**
- Create: `tests/test_full_pipeline_sample_documents.py`

**Interfaces:**
- Consumes: `carescribe.core.ingest`, `deidentify`, `batch`, `clinical_forms` (existing), `backends.LocalGGUFBackend`/`select_backend` (Task 2's extended signature, called with a deterministic no-network-required path — see below).
- Produces: nothing new for other tasks — this is the terminal validation task the spec's success criteria point at.

This test must run the pipeline **without requiring any real model to be installed** in CI/most dev environments (Ollama being up is not guaranteed), so it exercises ingest → de-identify → residual-scan → combine, and generation is exercised with a stub backend implementing the same `generate(system, prompt, stream, *, grammar=None)` interface `OllamaBackend`/`LocalGGUFBackend`/`CloudBackend` all implement — proving the pipeline plumbing end-to-end without a network or GPU dependency. (A separate manual step, Step 3 below, exercises a real backend if one happens to be available in this environment — informational, not a CI gate.)

- [ ] **Step 1: Write the test**

```python
# tests/test_full_pipeline_sample_documents.py
"""
Runs every ``sample_documents/*.docx`` through the full pipeline: ingest ->
de-identify -> approve (write de-identified text) -> combine sources ->
generate each clinical form type. A stub backend stands in for a real model
so this runs anywhere, with no GPU/network/Ollama dependency; it proves the
plumbing, not generation quality (that's a manual/informational check, see
this file's docstring in the plan).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from carescribe.core import batch, clinical_forms, deidentify, ingest

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_documents"
DOCX_FILES = sorted(SAMPLE_DIR.glob("*.docx"))


class _StubBackend:
    """Deterministic stand-in for a real generation backend."""

    def generate(self, system, prompt, stream=True, *, grammar=None):
        yield "[stub generation output]"


@pytest.mark.skipif(not DOCX_FILES, reason="no sample_documents/*.docx present")
@pytest.mark.parametrize("path", DOCX_FILES, ids=lambda p: p.name)
def test_ingest_and_deidentify_every_sample_document(path):
    text = ingest.extract_text(str(path))
    assert text.strip(), f"{path.name} extracted no text"
    result = deidentify.deidentify(text)
    assert result.redacted_text.strip()
    # The safety sweep must find no structured identifier left behind —
    # same bar tests/test_stress_corpus.py holds the stress corpus to.
    findings = deidentify.residual_scan(result.redacted_text)
    structured = [f for f in findings if any(c.isdigit() for c in f) or "@" in f]
    assert structured == [], (path.name, structured)


@pytest.mark.skipif(len(DOCX_FILES) < 2, reason="need at least 2 sample documents to combine")
def test_combined_sources_generate_every_form_type_with_a_stub_backend():
    texts = []
    for path in DOCX_FILES:
        text = ingest.extract_text(str(path))
        texts.append(deidentify.deidentify(text).redacted_text)
    combined = "\n\n".join(texts)
    backend = _StubBackend()
    for form_id, _title in clinical_forms.available_forms():
        spec = clinical_forms.get_form_spec(form_id)
        chunks = clinical_forms.generate_form_document(
            combined, spec, backend, stream=False, phi_values=[], acknowledged=set()
        )
        output = "".join(chunks)
        assert output.strip(), form_id
```

- [ ] **Step 2: Run and fix**

Run: `python -m pytest tests/test_full_pipeline_sample_documents.py -v`

`clinical_forms.available_forms() -> list[tuple[form_id, title]]`, `clinical_forms.get_form_spec(form_id) -> FormSpec`, and `generate_form_document(combined_text, form_spec, backend, stream=True, *, phi_values=None, acknowledged=(), exemplars=None)` are all confirmed against the current source (`carescribe/core/clinical_forms.py:243-258,507-523`) — no guessing needed there. `deidentify.deidentify(text).redacted_text` and `deidentify.residual_scan(text)` are likewise the exact names `tests/test_stress_corpus.py` already uses. If `ingest.extract_text` doesn't accept a plain path string, check `carescribe/core/ingest.py`'s actual signature and adjust.

Fix forward until this passes; if it surfaces a real pipeline bug (an exception on one of the 7 sample documents, or a structured identifier surviving de-identification on one of them), fix the underlying code — this is exactly the kind of bug the spec's Goal section asks this task to catch.

- [ ] **Step 3: Manual informational check — real backend, real output**

This step is not a pytest assertion (generation quality isn't a boolean pass/fail) — run it once by hand and read the output:

```bash
python -c "
from carescribe.core import backends, clinical_forms, deidentify, ingest
from pathlib import Path
kind, backend, label = backends.select_backend()
print('Using:', label)
for path in sorted(Path('sample_documents').glob('*.docx')):
    text = deidentify.deidentify(ingest.extract_text(str(path))).redacted_text
    print('---', path.name, '---')
    print(text[:300])
"
```

If a real backend (Ollama or the bundled local GGUF) is available in this environment, note in the final report to the user what backend/model was used and whether the output looked clinically sane (no invented details, given the 0.0-temperature fix from Task 2) — this is a quality observation to hand back, not something to loop on indefinitely.

- [ ] **Step 4: Run the full suite**

Run: `python -m pytest tests -q`
Expected: 100% pass.

- [ ] **Step 5: `graphify update .`**

Run: `graphify update .` (the plan touched several core modules and app.py across Tasks 1-3, 7 — keep the graph current)

- [ ] **Step 6: Commit**

```bash
git add tests/test_full_pipeline_sample_documents.py
git commit -m "test(pipeline): full ingest->deidentify->combine->generate run across every sample document"
```

---

### Task 8: Real generation pass — findings report + dedicated fix pass

> Added mid-execution at the user's explicit request: a real (non-stub) backend
> generation run across the full sample-document corpus, with one agent
> producing findings and a separate agent fixing whatever those findings
> surface. Confirmed in this environment: `backends.describe_backends()`
> reports `local.available = True` with a bundled fine-tuned model at
> `models/carescribe-clinical-phi35-v1.Q4_K_M.gguf` — Ollama is reachable but
> has zero models pulled, so `select_backend()` will pick the local GGUF
> backend by default here. This task is genuinely non-deterministic (LLM
> output), so it produces a **findings report**, not a pass/fail pytest gate
> — Task 7 already owns the deterministic plumbing gate.

**Files:**
- Create: `.superpowers/sdd/2026-09-02-llm-flexibility-and-realistic-corpus/task-8-findings.md` (the findings report; not part of the shipped codebase, workspace-scoped like the rest of this plan's SDD artifacts)
- Modify: whatever the findings report identifies as a real code bug (the fix-pass agent's job; files unknown until the findings exist)

**Interfaces:**
- Consumes: `backends.select_backend()` (Task 2), the full `sample_documents/*.docx` set (Task 6), `ingest.extract_text`, `deidentify.deidentify`, `clinical_forms.available_forms`/`get_form_spec`/`generate_form_document` — all confirmed real signatures, see Task 7.
- Produces: nothing later tasks depend on — this is the plan's terminal quality pass.

- [ ] **Step 1: Dispatch a findings agent to run the real pipeline**

For every document in `sample_documents/*.docx`, and then for the combined text of all of them together (matching the README's documented "01+02 combine for the richest Biopsychosocial test" pattern), run: ingest → de-identify → residual-scan (must be empty of structured identifiers, same bar as `tests/test_stress_corpus.py`) → for each of the 3 form types (`clinical_forms.available_forms()`), generate a full draft using a real backend obtained from `backends.select_backend()` (no `prefer` override — let it pick whatever's actually available in this environment; report which one it picked).

For each generated draft, the agent must record in its findings report:
- Whether generation completed without raising (a crash here is a Critical finding)
- Whether the output is non-empty and structurally plausible (looks like a filled-in form, not garbage/repeated tokens/truncated mid-field)
- Any content in the draft that appears to be invented/hallucinated — a specific clinical detail (a medication, a diagnosis, a date, a measure score) that does **not** appear anywhere in the combined source text. This is the exact failure mode the Task 2 temperature fix (0.2 → 0.0) targeted, so this run is also that fix's real-world verification.
- Any placeholder token (`[PATIENT]`-style bracket text) that survived into the final output unfilled where the source clearly had an answer available
- Wall-clock time per generation (informational — the bundled model is CPU-bound and this flags if something is pathologically slow)

Findings report format: one section per (document combination, form type) pair, each stating PASS or the specific problem, with the offending excerpt quoted.

- [ ] **Step 2: Controller reviews the findings report**

Read the findings report yourself (the controller, not a subagent) before deciding what happens next — this is a judgment call about what's a real bug worth a fix dispatch versus an inherent LLM quality limitation not worth chasing (e.g. a small 3B-class quantised model occasionally producing an awkward sentence is not a bug; a crash, an empty draft, or a fabricated medication name is).

- [ ] **Step 3: Dispatch a fix agent for real, code-level findings only**

If the findings report contains any Critical items (crashes, empty output, structural failures) or clear hallucination patterns traceable to a prompt/grammar issue (not just "the small model sometimes phrases things oddly"), dispatch one fix agent with the complete findings report and the specific files it implicates (likely candidates: `carescribe/core/clinical_forms.py`'s `build_prompt`/`_form_grammar`, `carescribe/core/carenotes.py`'s `generate_document`, or the grammar compiler in `carescribe/core/grammar.py`). The fix agent re-runs the specific failing case(s) from the findings report to confirm the fix, then the full test suite (`python -m pytest tests -q`), then commits.

If the findings report is clean (no Critical/Important-equivalent issues, only inherent small-model quality variance), skip this step — there is nothing to dispatch a fix for, and note that in your final report to the user.

- [ ] **Step 4: Report to the user**

Regardless of outcome, summarize for the user: which backend/model actually ran, how many (document-combo × form-type) cases were exercised, how many were clean, and — if a fix was dispatched — what was fixed and what the re-verification showed. This is the "did the app actually work end to end on real documents" answer the user asked for, and it doesn't reduce to a single pytest pass/fail line, so state it in prose.
