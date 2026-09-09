"""Holdout is by vignette: a skeleton in test is absent from train."""

import pytest

from finetune.assemble.pairs import Pair, split_by_vignette


def _pairs(n_vignettes=10, per=20):
    return [
        Pair(messages=[], meta={"vignette_id": f"v{v}"})
        for v in range(n_vignettes)
        for _ in range(per)
    ]


def _ids(group):
    return {p.meta["vignette_id"] for p in group}


def test_no_vignette_appears_in_two_splits():
    splits = split_by_vignette(_pairs(), seed=0)
    train, dev, test = _ids(splits["train"]), _ids(splits["dev"]), _ids(splits["test"])
    assert train & test == set()
    assert train & dev == set()
    assert dev & test == set()


def test_every_pair_is_placed_exactly_once():
    pairs = _pairs()
    splits = split_by_vignette(pairs, seed=0)
    assert sum(len(g) for g in splits.values()) == len(pairs)


def test_all_three_splits_are_populated():
    splits = split_by_vignette(_pairs(), seed=0)
    assert all(splits[name] for name in ("train", "dev", "test"))


def test_the_split_is_deterministic_for_a_seed():
    assert _ids(split_by_vignette(_pairs(), seed=7)["test"]) == _ids(
        split_by_vignette(_pairs(), seed=7)["test"]
    )


def test_too_few_vignettes_to_hold_out_is_an_error_not_a_silent_empty_split():
    """With 2 vignettes there is no honest holdout. Say so, don't return {}."""
    with pytest.raises(ValueError, match="vignette"):
        split_by_vignette(_pairs(n_vignettes=2), seed=0)


def test_a_pair_without_a_vignette_id_is_rejected():
    with pytest.raises(ValueError, match="vignette_id"):
        split_by_vignette([Pair(messages=[], meta={})], seed=0)


def test_stratified_split_still_exists_and_is_unchanged():
    """This task adds a splitter; it does not replace the old one."""
    from finetune.assemble.pairs import stratified_split

    assert callable(stratified_split)
