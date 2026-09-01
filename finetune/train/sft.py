"""
QLoRA supervised fine-tune.

Runnable on a single 16 GB GPU (RTX 5080 / 4090 / A10): 4-bit NF4 base, LoRA on
the attention and MLP projections, per-device batch 1 with gradient
accumulation to an effective 16, gradient checkpointing, paged 8-bit optimizer,
bf16. ~1-3 h for ~12k pairs.

    python -m finetune.train.sft \
        --train finetune/data/full/train.jsonl \
        --dev   finetune/data/full/dev.jsonl \
        --config finetune/config/train.yaml \
        --model-config finetune/config/models.yaml \
        --out finetune/runs/phi35-v1

Heavy imports (torch, peft, trl, transformers) are deferred into the functions
that need them so the module can be imported — and its config parsed — without
the training stack installed.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class LoraConfig:
    r: int = 16
    alpha: int = 32
    dropout: float = 0.05
    target_modules: list[str] = field(
        default_factory=lambda: [
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ]
    )


@dataclass
class TrainConfig:
    epochs: int = 3
    learning_rate: float = 1e-4
    lr_scheduler: str = "cosine"
    warmup_ratio: float = 0.03
    per_device_batch_size: int = 1
    grad_accum_steps: int = 16
    max_seq_length: int = 4096
    packing: bool = True
    bf16: bool = True
    gradient_checkpointing: bool = True
    optim: str = "paged_adamw_8bit"
    eval_steps: int = 100
    save_steps: int = 200
    seed: int = 0
    lora: LoraConfig = field(default_factory=LoraConfig)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "TrainConfig":
        import yaml

        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        lora_raw = raw.get("lora", {}) or {}
        lora = LoraConfig(
            r=int(lora_raw.get("rank", lora_raw.get("r", 16)) or 16),
            alpha=int(lora_raw.get("alpha", 32) or 32),
            dropout=float(lora_raw.get("dropout", 0.05) or 0.05),
            target_modules=list(lora_raw.get("target_modules") or LoraConfig().target_modules),
        )
        opt = raw.get("optim", {}) or {}
        rt = raw.get("runtime", {}) or {}
        return cls(
            epochs=int(raw.get("epochs", 3) or 3),
            learning_rate=float(opt.get("learning_rate", 1e-4) or 1e-4),
            lr_scheduler=str(opt.get("scheduler", "cosine") or "cosine"),
            warmup_ratio=float(opt.get("warmup_ratio", 0.03) or 0.03),
            per_device_batch_size=int(rt.get("batch_size", 1) or 1),
            grad_accum_steps=int(rt.get("gradient_accumulation_steps", 16) or 16),
            max_seq_length=int(rt.get("max_seq_length", 4096) or 4096),
            eval_steps=int((raw.get("eval", {}) or {}).get("steps", 100) or 100),
            seed=int(raw.get("seed", 0) or 0),
            lora=lora,
        )


def load_pairs(path: str | Path) -> list[dict]:
    """Read a chat-JSONL file into a list of ``{"messages": [...]}`` dicts."""
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def build_model_and_tokenizer(base_model: str, cfg: TrainConfig):
    import torch
    from peft import LoraConfig as PeftLoraConfig
    from peft import get_peft_model, prepare_model_for_kbit_training
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
    )

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    tok = AutoTokenizer.from_pretrained(base_model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        base_model, quantization_config=bnb, device_map="auto", torch_dtype=torch.bfloat16
    )
    model = prepare_model_for_kbit_training(
        model, use_gradient_checkpointing=cfg.gradient_checkpointing
    )
    peft_cfg = PeftLoraConfig(
        r=cfg.lora.r,
        lora_alpha=cfg.lora.alpha,
        lora_dropout=cfg.lora.dropout,
        target_modules=cfg.lora.target_modules,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, peft_cfg)
    return model, tok


def train(
    train_path: str,
    dev_path: str,
    *,
    base_model: str,
    cfg: TrainConfig,
    out_dir: str,
) -> str:
    from datasets import Dataset
    from trl import SFTConfig, SFTTrainer

    model, tok = build_model_and_tokenizer(base_model, cfg)

    def to_text(row: dict) -> dict:
        return {"text": tok.apply_chat_template(row["messages"], tokenize=False)}

    train_ds = Dataset.from_list([to_text(r) for r in load_pairs(train_path)])
    dev_ds = Dataset.from_list([to_text(r) for r in load_pairs(dev_path)])

    sft_cfg = SFTConfig(
        output_dir=out_dir,
        num_train_epochs=cfg.epochs,
        per_device_train_batch_size=cfg.per_device_batch_size,
        gradient_accumulation_steps=cfg.grad_accum_steps,
        learning_rate=cfg.learning_rate,
        lr_scheduler_type=cfg.lr_scheduler,
        warmup_ratio=cfg.warmup_ratio,
        bf16=cfg.bf16,
        gradient_checkpointing=cfg.gradient_checkpointing,
        optim=cfg.optim,
        max_seq_length=cfg.max_seq_length,
        packing=cfg.packing,
        eval_strategy="steps",
        eval_steps=cfg.eval_steps,
        save_steps=cfg.save_steps,
        logging_steps=20,
        seed=cfg.seed,
        report_to=[],
        # loss on assistant tokens only
        assistant_only_loss=True,
    )
    trainer = SFTTrainer(
        model=model,
        args=sft_cfg,
        train_dataset=train_ds,
        eval_dataset=dev_ds,
        processing_class=tok,
    )
    trainer.train()
    adapter_dir = str(Path(out_dir) / "adapter")
    trainer.save_model(adapter_dir)
    tok.save_pretrained(adapter_dir)
    return adapter_dir


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--train", required=True)
    ap.add_argument("--dev", required=True)
    ap.add_argument("--config", default="finetune/config/train.yaml")
    ap.add_argument("--model-config", default="finetune/config/models.yaml")
    ap.add_argument("--base-model", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    cfg = TrainConfig.from_yaml(args.config)
    base_model = args.base_model
    if base_model is None:
        import yaml

        mc = yaml.safe_load(Path(args.model_config).read_text(encoding="utf-8")) or {}
        base_model = (mc.get("base_model") or {}).get("name")
    if not base_model:
        ap.error("no base model: pass --base-model or set base_model.name in models.yaml")

    adapter = train(
        args.train, args.dev, base_model=base_model, cfg=cfg, out_dir=args.out
    )
    print(f"adapter saved -> {adapter}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
