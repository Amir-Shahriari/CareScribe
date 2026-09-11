"""Every key in datagen.yaml must actually change the corpus.

Nine of the twelve keys in this file were read by nothing. `specialty_weights`
was the worst of them: `sample_encounters` has always accepted the parameter,
`build_dataset` simply never passed it, so a carefully rebalanced corpus came
out exactly as before with no error and no warning. `styled_fraction: 0.30`
promised that three pairs in ten were style-conditioned when
`datagen/vignettes/styles/` had never been created and the value was hardcoded
`False` — that one reached an EVAL_REPORT as a `style_match` of 0.998, a metric
scoring a dimension that never varied.

A config value that is read by nothing is worse than a missing one: it reads as
a knob, it survives review, and it makes the report of a run describe settings
that never applied. So this file pins the whole surface, both ways.
"""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

from finetune.assemble import build_dataset
from finetune.datagen.schema import FormType

CONFIG = Path("finetune/config/datagen.yaml")

# Keys build_dataset reads and acts on. Adding a key to datagen.yaml without
# adding it here fails `test_no_key_is_decorative` below.
LIVE_KEYS = {
    "rng": {"seed"},
    "counts": {"total"},
    "quality": {"gap_probability"},
    "specialty_weights": None,   # whole block is passed to the sampler
    "form_types": None,          # whole block selects the output forms
}


def _config() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}


def test_no_key_is_decorative():
    """Fail on a key that no longer corresponds to behaviour.

    If you are here because you added a setting: wire it into
    `build_dataset.main` and add it to LIVE_KEYS. If you are here because you
    removed a feature, delete the key from datagen.yaml too — leaving it behind
    is how `styled_fraction` outlived the thing it configured.
    """
    cfg = _config()
    unknown = set(cfg) - set(LIVE_KEYS)
    assert not unknown, (
        f"datagen.yaml declares {sorted(unknown)}, which build_dataset never "
        f"reads. Wire it up or delete it."
    )
    for block, allowed in LIVE_KEYS.items():
        if allowed is None or block not in cfg:
            continue
        extra = set(cfg[block] or {}) - allowed
        assert not extra, (
            f"datagen.yaml declares {block}.{sorted(extra)}, which "
            f"build_dataset never reads. Wire it up or delete it."
        )


def test_form_types_are_real_form_names():
    for name in _config().get("form_types") or []:
        FormType(name)  # raises ValueError on a typo


def test_specialty_weights_name_real_specialties():
    from finetune.datagen.vignettes import SPECIALTIES

    for name in _config().get("specialty_weights") or {}:
        assert name in SPECIALTIES, f"{name!r} is not a vignette specialty"


def test_specialty_weights_actually_reach_the_sampler():
    """The bug that motivated this file: accepted upstream, never passed."""
    seen = {}
    real = build_dataset.sample_encounters

    def spy(n, **kwargs):
        seen.update(kwargs)
        return real(n, **kwargs)

    weights = {"general practice": 5.0}
    original = build_dataset.sample_encounters
    build_dataset.sample_encounters = spy
    try:
        build_dataset.build(2, seed=0, specialty_weights=weights)
    finally:
        build_dataset.sample_encounters = original

    assert seen.get("specialty_weights") == weights


def test_weighting_a_specialty_changes_what_is_sampled():
    """End to end: the knob must move the corpus, not just be forwarded."""
    from finetune.datagen.sampler import sample_encounters

    def specialties(weights):
        return [
            f.specialty for f in
            sample_encounters(60, seed=11, specialty_weights=weights)
        ]

    skewed = specialties({"general practice": 100.0})
    even = specialties(None)
    assert skewed.count("general practice") > even.count("general practice")
