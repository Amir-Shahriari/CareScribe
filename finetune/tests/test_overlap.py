"""Character 5-gram overlap between test targets and their nearest train target."""

from finetune.eval.overlap import max_similarity, overlap_report, similarity


def test_identical_text_is_one():
    assert similarity("the patient was seen today", "the patient was seen today") == 1.0


def test_unrelated_text_is_low():
    assert max_similarity("chest pain on exertion", ["dispense fluoride varnish"]) < 0.2


def test_max_similarity_picks_the_nearest_neighbour():
    corpus = ["totally unrelated words here", "the patient was seen today"]
    assert max_similarity("the patient was seen today", corpus) == 1.0


def test_report_counts_the_high_overlap_tail():
    """One near-copy among unrelated targets: flagged in the tail, not the median."""
    train = ["alpha bravo charlie delta echo"]
    test = [
        "alpha bravo charlie delta echo",
        "zulu yankee xray whisky victor",
        "papa quebec romeo sierra tango",
    ]
    r = overlap_report(train, test)
    assert r["n"] == 3
    assert r["n_above_0_6"] == 1
    assert r["median"] < 0.5
    assert r["p95"] == 1.0


def test_empty_train_reports_absent_not_zero():
    """No training text means the metric is uncomputable, not 0.0."""
    r = overlap_report([], ["anything"])
    assert r["median"] is None
    assert r["p95"] is None


def test_empty_test_reports_absent_and_counts_zero():
    r = overlap_report(["anything"], [])
    assert r["median"] is None
    assert r["n"] == 0


def test_max_similarity_of_an_empty_corpus_is_zero():
    assert max_similarity("anything", []) == 0.0
