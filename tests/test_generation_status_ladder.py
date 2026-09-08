"""
The generation-status ladder, tested on its own terms.

``Status`` is a plain dataclass, so every test here builds one directly and
asserts on the two derived properties and the one function that reads them.
No monkeypatching and no network: the point is to pin the pure decision logic
— the ladder order (ollama > local gguf > cloud), the agreement between
``ready`` and ``preferred``, and the branch structure of ``missing_reason``.
"""

import pytest

from carescribe.core import backends, generation_status


# ==========================================================================
# Task 1 — ready
# ==========================================================================

@pytest.mark.parametrize(
    "field",
    ["ollama", "local_gguf", "cloud"],
)
def test_ready_is_false_with_nothing_and_true_with_any_one_backend(field):
    """`ready` is simply "is any backend usable" — any single one suffices."""
    assert not generation_status.Status().ready
    assert generation_status.Status(**{field: True}).ready


# ==========================================================================
# Tasks 2-4 — preferred
# ==========================================================================

@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("ollama", backends.BACKEND_OLLAMA),
        ("local_gguf", backends.BACKEND_LOCAL_GGUF),
        ("cloud", backends.BACKEND_CLOUD),
    ],
)
def test_each_backend_alone_gives_its_own_constant(field, expected):
    status = generation_status.Status(**{field: True})
    assert status.preferred == expected


def test_the_ladder_order_is_ollama_then_local_gguf_then_cloud():
    """The preference order, not a coincidence of which field was set.

    With everything available, Ollama wins — someone who installed it chose
    a bigger model. With only local gguf and cloud, local gguf wins — cloud
    is last on purpose, off unless a deployer turns it on.
    """
    everything = generation_status.Status(
        ollama=True, local_gguf=True, cloud=True
    )
    assert everything.preferred == backends.BACKEND_OLLAMA

    no_ollama = generation_status.Status(local_gguf=True, cloud=True)
    assert no_ollama.preferred == backends.BACKEND_LOCAL_GGUF


def test_nothing_available_means_no_preference_and_not_ready():
    """`preferred` and `ready` must agree: both say "nothing" together."""
    status = generation_status.Status()
    assert status.preferred == ""
    assert not status.ready


# ==========================================================================
# Task 5 — missing_reason on a ready status
# ==========================================================================

@pytest.mark.parametrize(
    "field",
    ["ollama", "local_gguf", "cloud"],
)
def test_a_ready_status_of_any_kind_gives_no_reason(field):
    """Nothing is missing when a backend is usable, of whichever kind."""
    status = generation_status.Status(**{field: True})
    assert status.ready
    assert generation_status.missing_reason(status) == ""


# ==========================================================================
# Task 6 — missing_reason branches
# ==========================================================================

def test_every_not_ready_branch_gives_its_own_sentence():
    ollama_empty = generation_status.missing_reason(
        generation_status.Status(ollama_running=True, ollama_models=[])
    )
    assert "no model installed" in ollama_empty

    nothing_installed = generation_status.missing_reason(
        generation_status.Status(llama_runtime=False, ollama_running=False)
    )
    assert "No AI model is set up" in nothing_installed

    runtime_without_model = generation_status.missing_reason(
        generation_status.Status(llama_runtime=True, model_path="")
    )
    assert "has not been downloaded" in runtime_without_model

    # Anything else not ready — e.g. the runtime present and a model file
    # recorded, but no usable backend flag set — falls back to a sentence.
    fallback = generation_status.missing_reason(
        generation_status.Status(llama_runtime=True, model_path="C:/m.gguf")
    )
    assert fallback

    # Every branch is a sentence, never an empty string, when not ready.
    for reason in (ollama_empty, nothing_installed, runtime_without_model, fallback):
        assert reason
