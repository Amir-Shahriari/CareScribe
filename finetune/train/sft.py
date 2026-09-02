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
        ev = raw.get("eval", {}) or {}
        d = cls()  # defaults for anything the yaml omits

        def _b(v, default):
            return default if v is None else bool(v)

        return cls(
            epochs=int(raw.get("epochs", d.epochs) or d.epochs),
            learning_rate=float(opt.get("learning_rate", d.learning_rate) or d.learning_rate),
            lr_scheduler=str(opt.get("scheduler", d.lr_scheduler) or d.lr_scheduler),
            warmup_ratio=float(opt.get("warmup_ratio", d.warmup_ratio) or d.warmup_ratio),
            per_device_batch_size=int(rt.get("batch_size", d.per_device_batch_size) or d.per_device_batch_size),
            grad_accum_steps=int(rt.get("gradient_accumulation_steps", d.grad_accum_steps) or d.grad_accum_steps),
            max_seq_length=int(rt.get("max_seq_length", d.max_seq_length) or d.max_seq_length),
            packing=_b(rt.get("packing"), d.packing),
            bf16=_b(rt.get("bf16"), d.bf16),
            gradient_checkpointing=_b(rt.get("gradient_checkpointing"), d.gradient_checkpointing),
            optim=str(rt.get("optim", d.optim) or d.optim),
            eval_steps=int(ev.get("steps", d.eval_steps) or d.eval_steps),
            save_steps=int(ev.get("save_steps", d.save_steps) or d.save_steps),
            seed=int(raw.get("seed", d.seed) or d.seed),
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


def _bnb_config():
    import torch
    from transformers import BitsAndBytesConfig

    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )


def _peft_config(cfg: TrainConfig):
    from peft import LoraConfig as PeftLoraConfig

    return PeftLoraConfig(
        r=cfg.lora.r,
        lora_alpha=cfg.lora.alpha,
        lora_dropout=cfg.lora.dropout,
        target_modules=cfg.lora.target_modules,
        bias="none",
        task_type="CAUSAL_LM",
    )


def train(
    train_path: str,
    dev_path: str,
    *,
    base_model: str,
    cfg: TrainConfig,
    out_dir: str,
    max_steps: int = -1,
    four_bit: bool = True,
) -> str:
    """QLoRA SFT via trl (>=1.x). Returns the saved adapter directory.

    ``max_steps`` > 0 caps the run (M3 dry run). ``four_bit=False`` trains the
    base in bf16 instead of NF4 — a fallback if bitsandbytes misbehaves.
    """
    from datasets import Dataset
    from trl import SFTConfig, SFTTrainer

    train_rows = load_pairs(train_path)
    dev_rows = load_pairs(dev_path)
    train_ds = Dataset.from_list([{"messages": r["messages"]} for r in train_rows])
    dev_ds = Dataset.from_list([{"messages": r["messages"]} for r in dev_rows])

    model_init_kwargs = {"dtype": "bfloat16", "device_map": "auto"}
    if four_bit:
        model_init_kwargs["quantization_config"] = _bnb_config()

    steps_per_epoch = max(
        1, len(train_rows) // (cfg.per_device_batch_size * cfg.grad_accum_steps)
    )
    total_steps = max_steps if max_steps > 0 else steps_per_epoch * cfg.epochs
    warmup_steps = max(2, int(cfg.warmup_ratio * total_steps))

    sft_cfg = SFTConfig(
        output_dir=out_dir,
        num_train_epochs=cfg.epochs,
        max_steps=max_steps,
        per_device_train_batch_size=cfg.per_device_batch_size,
        gradient_accumulation_steps=cfg.grad_accum_steps,
        learning_rate=cfg.learning_rate,
        lr_scheduler_type=cfg.lr_scheduler,
        warmup_steps=warmup_steps,
        bf16=cfg.bf16,
        gradient_checkpointing=cfg.gradient_checkpointing,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        optim=cfg.optim,
        max_length=cfg.max_seq_length,
        packing=cfg.packing,
        eval_strategy="steps",
        eval_steps=cfg.eval_steps,
        save_steps=cfg.save_steps,
        save_total_limit=2,
        logging_steps=20,
        seed=cfg.seed,
        report_to=[],
        model_init_kwargs=model_init_kwargs,
        assistant_only_loss=True,
    )
    trainer = SFTTrainer(
        model=base_model,
        args=sft_cfg,
        train_dataset=train_ds,
        eval_dataset=dev_ds,
        peft_config=_peft_config(cfg),
    )
    trainer.train()
    adapter_dir = str(Path(out_dir) / "adapter")
    trainer.save_model(adapter_dir)
    if trainer.processing_class is not None:
        trainer.processing_class.save_pretrained(adapter_dir)
    return adapter_dir


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--train", required=True)
    ap.add_argument("--dev", required=True)
    ap.add_argument("--config", default="finetune/config/train.yaml")
    ap.add_argument("--model-config", default="finetune/config/models.yaml")
    ap.add_argument("--base-model", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-steps", type=int, default=-1, help=">0 caps the run (M3)")
    ap.add_argument("--no-4bit", action="store_true", help="train base in bf16, not NF4")
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
        args.train,
        args.dev,
        base_model=base_model,
        cfg=cfg,
        out_dir=args.out,
        max_steps=args.max_steps,
        four_bit=not args.no_4bit,
    )
    print(f"adapter saved -> {adapter}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
