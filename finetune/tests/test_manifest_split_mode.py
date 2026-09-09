"""The manifest records how the data was split, so a reader can check it."""

from finetune.assemble.manifest import build_manifest
from finetune.assemble.pairs import Pair


def _splits():
    mk = lambda vid, n: [
        Pair(
            messages=[],
            meta={
                "vignette_id": vid,
                "form_type": "soap",
                "specialty": "cardiology",
                "styled": False,
            },
        )
        for _ in range(n)
    ]
    return {"train": mk("v1", 3) + mk("v2", 2), "dev": mk("v3", 1), "test": mk("v4", 1)}


def _manifest():
    return build_manifest(
        _splits(), generator_backend="template", generator_model=None, seed=0
    )


def test_the_split_mode_is_recorded():
    assert _manifest()["split_mode"] == "vignette_disjoint"


def test_each_split_lists_its_vignettes():
    m = _manifest()
    assert m["split_vignettes"]["train"] == ["v1", "v2"]
    assert m["split_vignettes"]["dev"] == ["v3"]
    assert m["split_vignettes"]["test"] == ["v4"]


def test_the_listed_vignettes_are_disjoint():
    v = _manifest()["split_vignettes"]
    assert set(v["train"]) & set(v["test"]) == set()
    assert set(v["train"]) & set(v["dev"]) == set()


def test_existing_manifest_keys_are_untouched():
    m = _manifest()
    for key in ("content_sha256", "counts", "total", "strata",
                "generator_backend", "generator_model", "seed"):
        assert key in m


def test_counts_still_match_the_splits():
    m = _manifest()
    assert m["counts"] == {"train": 5, "dev": 1, "test": 1}
    assert m["total"] == 7
