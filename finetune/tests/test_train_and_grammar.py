"""train/ config + modelcard + dpo rejection, and integrate/grammar."""

from __future__ import annotations

from pathlib import Path

from finetune.datagen.schema import FormType
from finetune.integrate.grammar import build_grammar
from finetune.train.dpo import build_preference_rows, make_rejected
from finetune.train.modelcard import render_card
from finetune.train.sft import TrainConfig, load_pairs

_REPO = Path(__file__).resolve().parents[2]


def test_train_config_loads_from_the_committed_yaml():
    cfg = TrainConfig.from_yaml(_REPO / "finetune/config/train.yaml")
    assert cfg.lora.r == 16 and cfg.lora.alpha == 32
    # effective batch stays 16 regardless of the batch/accum split
    assert cfg.per_device_batch_size * cfg.grad_accum_steps == 16
    assert cfg.packing is False           # no flash-attn -> packing must be off
    assert cfg.gradient_checkpointing is True
    assert cfg.optim == "paged_adamw_8bit"
    assert "q_proj" in cfg.lora.target_modules


def test_train_config_yaml_overrides_every_runtime_field(tmp_path):
    y = tmp_path / "t.yaml"
    y.write_text(
        "runtime:\n  batch_size: 2\n  gradient_accumulation_steps: 8\n"
        "  packing: true\n  gradient_checkpointing: false\n  max_seq_length: 1024\n"
        "epochs: 1\n",
        encoding="utf-8",
    )
    cfg = TrainConfig.from_yaml(y)
    assert cfg.per_device_batch_size == 2 and cfg.grad_accum_steps == 8
    assert cfg.packing is True and cfg.gradient_checkpointing is False
    assert cfg.max_seq_length == 1024 and cfg.epochs == 1


def test_load_pairs_round_trips_jsonl(tmp_path):
    p = tmp_path / "t.jsonl"
    p.write_text('{"messages": [{"role": "user", "content": "hi"}]}\n\n', encoding="utf-8")
    rows = load_pairs(p)
    assert len(rows) == 1 and rows[0]["messages"][0]["content"] == "hi"


def test_grammar_pins_headings_and_constrains_brackets():
    g = build_grammar(FormType.SOAP, ["[PATIENT]", "[DATE_1]"])
    assert "**S — Subjective**" in g
    assert 'placeholder ::= "[" ( "PATIENT" | "DATE_1" ) "]"' in g
    assert "[^[<]" in g  # a bare '[' is impossible outside a placeholder


def test_grammar_with_no_placeholders_forbids_brackets_entirely():
    g = build_grammar(FormType.HANDOVER, [])
    assert "[^[<]" in g
    assert "placeholder ::=" not in g


def test_make_rejected_applies_exactly_one_corruption():
    chosen = (
        "**S — Subjective**\n- cough for [DATE_1]\n\n"
        "**O — Objective**\n- chest clear\n\n"
        "**A — Assessment**\n- viral URTI\n\n"
        "**P — Plan**\n- safety-net advice"
    )
    rej = make_rejected(chosen, seed=1)
    assert rej != chosen
    # still recognisably the same draft, just worse
    assert "Subjective" in rej or "Objective" in rej


def test_build_preference_rows_shapes_dpo_data():
    pairs = [
        {"messages": [
            {"role": "system", "content": "s"},
            {"role": "user", "content": "u"},
            {"role": "assistant", "content": "**A**\n- x\n\n**B**\n- [PATIENT] seen"},
        ]}
    ]
    rows = build_preference_rows(pairs, seed=0)
    assert rows[0]["chosen"] != rows[0]["rejected"]
    assert rows[0]["prompt"][-1]["role"] == "user"


def test_render_card_states_provenance_and_verdict():
    md = render_card(
        base_model="microsoft/Phi-3.5-mini-instruct",
        base_licence="MIT",
        lora={"r": 16, "alpha": 32, "dropout": 0.05, "target_modules": ["q_proj"]},
        manifest={
            "carescribe_sha": "abc123",
            "generator_backend": "template",
            "generator_model": None,
            "seed": 0,
            "total": 200,
            "counts": {"train": 176, "dev": 12, "test": 12},
            "content_sha256": "d" * 64,
        },
        eval_payload={
            "ship": True,
            "verdict": {"latency_ratio": 1.02, "regressions": []},
            "base": {"metrics": {"format": 0.8, "faithfulness": 0.7,
                                 "placeholder_integrity": 0.9, "residual_clean": 1.0}},
            "tuned": {"metrics": {"format": 0.98, "faithfulness": 0.95,
                                  "placeholder_integrity": 1.0, "residual_clean": 1.0}},
        },
    )
    assert "Ship gate: PASS" in md
    assert "abc123" in md
    assert "microsoft/Phi-3.5-mini-instruct" in md
    assert "clinician review" in md
