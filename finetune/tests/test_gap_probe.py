"""A required field is absent. The model must say so, not invent."""

from finetune.eval.gap_probe import (
    confabulated,
    confabulation_rate,
    gapped_headings,
    make_gap_probes,
    sections,
)

TARGET = (
    "**Problem List**\n1. viral URTI\n\n"
    "**Interventions**\n- fluids\n\n"
    "**Follow-up**\nNot documented.\n"
)


def test_sections_splits_on_bold_headings():
    parsed = sections(TARGET)
    assert set(parsed) == {"problem list", "interventions", "follow-up"}


def test_gapped_headings_finds_the_not_documented_section():
    assert gapped_headings(TARGET) == ["follow-up"]


def test_headings_match_regardless_of_case_and_spacing():
    assert "follow-up" in sections("**  Follow-Up  **\nNot documented.\n")


def test_probes_all_admit_an_undocumented_field():
    probes = make_gap_probes(6, seed=2000)
    assert probes
    assert all(gapped_headings(p.target) for p in probes)


def test_probes_are_deterministic_for_a_seed():
    a = [p.target for p in make_gap_probes(4, seed=99)]
    b = [p.target for p in make_gap_probes(4, seed=99)]
    assert a == b


def test_reproducing_the_target_is_not_confabulation():
    probes = make_gap_probes(3, seed=2000)
    assert confabulation_rate(probes, [p.target for p in probes]) == 0.0


def test_asserting_content_under_a_gapped_heading_is_confabulation():
    probes = make_gap_probes(1, seed=2000)
    item = probes[0]
    heading = gapped_headings(item.target)[0]
    draft = f"**{heading}**\nReview in six weeks with the community team.\n"
    assert confabulated(item, draft) is True


def test_omitting_the_heading_is_a_format_fault_not_a_confabulation():
    probes = make_gap_probes(1, seed=2000)
    assert confabulated(probes[0], "**Nothing Relevant**\nx\n") is False


def test_an_empty_gapped_section_is_not_confabulation():
    probes = make_gap_probes(1, seed=2000)
    item = probes[0]
    heading = gapped_headings(item.target)[0]
    assert confabulated(item, f"**{heading}**\n   \n") is False


def test_no_probes_reports_absent_not_zero():
    assert confabulation_rate([], []) is None
