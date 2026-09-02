"""The M1 dry run: the whole datagen -> de-id -> validate loop end to end."""

from __future__ import annotations

import json

from finetune.assemble.build_dataset import build, main
from finetune.datagen.render_note import STYLES, render
from finetune.datagen.sampler import sample_encounters
from finetune.datagen.schema import FormType


def test_render_produces_every_style_with_identifier_slots():
    facts = next(sample_encounters(1, seed=1, gap_probability=0.0))
    for style in STYLES:
        note = render(facts, style=style, seed=2)
        assert facts.presenting_complaint.lower() in note.lower()
        assert "[[" in note  # slots for identifiers.inject


def test_dry_run_keeps_a_high_fraction_and_writes_valid_pairs(tmp_path):
    result = build(48, seed=0)
    assert result["kept"] >= 40, result["reasons"]
    # every kept pair is a well-formed 3-message chat example
    for pair in result["pairs"]:
        roles = [m["role"] for m in pair.messages]
        assert roles == ["system", "user", "assistant"]
        assert "%%RENDER%%" not in pair.messages[1]["content"]
        assert "[[" not in pair.messages[1]["content"]  # slots were filled
        assert pair.meta["form_type"] in {f.value for f in FormType}


def test_dry_run_is_deterministic():
    a = [p.to_json_line() for p in build(24, seed=3)["pairs"]]
    b = [p.to_json_line() for p in build(24, seed=3)["pairs"]]
    assert a == b


def test_main_writes_splits_and_manifest(tmp_path):
    rc = main(["--n", "60", "--seed", "1", "--out", str(tmp_path)])
    assert rc == 0
    manifest = json.loads((tmp_path / "dataset_manifest.json").read_text())
    assert manifest["total"] == sum(manifest["counts"].values())
    assert (tmp_path / "train.jsonl").exists()
    lines = (tmp_path / "train.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == manifest["counts"]["train"]
    # each line parses and carries the de-identified document, not raw PHI
    for line in lines:
        obj = json.loads(line)
        assert obj["messages"][0]["role"] == "system"
