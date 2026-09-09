"""build_dataset must record placeholders and split by vignette."""

from finetune.assemble.build_dataset import build
from finetune.assemble.pairs import split_by_vignette

BUILT = build(24, seed=0)


def test_the_build_keeps_pairs():
    assert BUILT["kept"] > 0


def test_every_pair_records_its_known_placeholders():
    """Previously always [], because build_dataset never passed them."""
    assert any(p.meta["known_placeholders"] for p in BUILT["pairs"])


def test_placeholders_look_like_placeholders():
    for pair in BUILT["pairs"]:
        for token in pair.meta["known_placeholders"]:
            assert token.startswith("[") and token.endswith("]")


def test_every_pair_records_its_document():
    assert all(p.meta["document"] for p in BUILT["pairs"])


def test_the_split_is_vignette_disjoint():
    splits = split_by_vignette(BUILT["pairs"], seed=0)
    ids = {
        name: {p.meta["vignette_id"] for p in group}
        for name, group in splits.items()
    }
    assert ids["train"] & ids["test"] == set()
    assert ids["train"] & ids["dev"] == set()
    assert ids["dev"] & ids["test"] == set()


def test_build_dataset_no_longer_imports_stratified_split():
    import finetune.assemble.build_dataset as mod

    assert not hasattr(mod, "stratified_split")
    assert hasattr(mod, "split_by_vignette")
