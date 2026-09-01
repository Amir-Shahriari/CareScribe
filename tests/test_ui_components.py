"""The HTML-string UI helpers — pure functions, no Streamlit."""

from __future__ import annotations

from carescribe.ui import components as ui


def test_hero_carries_the_title_sub_and_privacy_pill():
    out = ui.hero("CareScribe", "de-identify locally")
    assert 'class="cs-hero__title"' in out
    assert "CareScribe" in out and "de-identify locally" in out
    assert "<svg" in out  # the lock icon
    assert 'data-tone="safe"' in out  # default offline pill

    assert 'data-tone="warn"' in ui.hero("t", "s", "cloud")
    assert 'data-tone="accent"' in ui.hero("t", "s", "downloading")
    assert 'data-tone="safe"' in ui.hero("t", "s", "nonsense")  # fallback


def test_step_tracker_states_and_count():
    n = len(ui.STEPS)
    first = ui.step_tracker(0)
    assert first.count('class="cs-step"') == n
    assert first.count('data-state="active"') == 1
    assert first.count('data-state="upcoming"') == n - 1
    assert 'data-state="done"' not in first

    mid = ui.step_tracker(2)
    assert mid.count('data-state="done"') == 2
    assert mid.count('data-state="active"') == 1
    assert mid.count('data-state="upcoming"') == n - 3
    assert mid.count("m5 12.8") == 2  # the check-icon path, one per done step

    done = ui.step_tracker(n)
    assert done.count('data-state="done"') == n
    assert 'data-state="active"' not in done


def test_chip_and_status_chip():
    c = ui.chip("Approved", "safe", "check")
    assert 'data-tone="safe"' in c and "Approved" in c and "<svg" in c
    assert 'class="cs-chip__mark"' in ui.chip("plain")  # no icon -> css mark

    s = ui.status_chip("approved")
    assert 'data-tone="safe"' in s and "Approved" in s
    assert 'data-tone="danger"' in ui.status_chip("blocked")
    unknown = ui.status_chip("???")
    assert 'data-tone="muted"' in unknown and "Not yet processed" in unknown


def test_detection_layer():
    on = ui.detection_layer("on", 1, "Structured regex", "always on")
    assert 'data-state="on"' in on and "1. Structured regex" in on
    assert "always on" in on and "<svg" in on

    off = ui.detection_layer("off", 3, "GLiNER")
    assert 'data-state="off"' in off and " — " not in off


def test_stat_strip_and_empty_state():
    strip = ui.stat_strip([("Documents", 3), ("Approved", "1 / 3")])
    assert strip.count('class="cs-stat"') == 2
    assert "Documents" in strip and "1 / 3" in strip

    empty = ui.empty_state("upload", "No documents", "Load a batch to begin.")
    assert 'class="cs-empty"' in empty and "No documents" in empty
    assert "Load a batch to begin." in empty and "<svg" in empty


def test_values_are_html_escaped():
    out = ui.hero("<script>x</script>", "a & b")
    assert "<script>" not in out
    assert "&lt;script&gt;" in out and "&amp;" in out


def test_unknown_icon_falls_back_to_dot():
    out = ui.icon("no-such-icon")
    assert out.startswith("<svg") and len(out) > 20
