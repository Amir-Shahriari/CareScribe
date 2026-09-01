# finetune/

Local, CPU-only fine-tuning scaffolding for a clinical LLM. It generates
synthetic encounter data and trains LoRA adapters — all offline on your own
machine. It is **never imported by `carescribe/`** and is kept outside the app
package so it can never be frozen into the desktop build.

Nothing here runs in the shipping app; think of it as a separate lab bench
that consumes the app's public seams (form specs, mapping, de-id) to build
training data.

## Layout

- `datagen/` — synthetic encounter generation + the `EncounterFacts` schema
  (single source of truth for an encounter).
- `assemble/` — render encounters into form targets + SFT pairs.
- `train/` — CPU LoRA fine-tune (peft + trl).
- `eval/` — offline quality / de-id-gate evaluation.
- `integrate/` — hand the best adapter + prompts back to the app.

This directory currently ships only the skeleton and the schema.

## Isolated environment

Install the training deps on their own, keeping them out of the app env:

    python -m venv .venv-finetune
    pip install -e .

See `pyproject.toml` for the (unpinned) dependency list.
