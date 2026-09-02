# finetune/

Local fine-tuning for CareScribe's clinical drafting model: generate synthetic
encounter data, train a QLoRA adapter, evaluate it, and hand a quantised GGUF
back to the app.

**Never imported by `carescribe/`** and kept outside the app package so it can
never be frozen into the desktop build. `carescribe.core.deidentify`,
`carescribe.core.mapping` and `carescribe.prompts` are imported *from* here
(one-way) so training data and prompts cannot drift from production.

Design: `../docs/superpowers/specs/2026-09-01-local-clinical-llm-finetune-design.md`

## Layout

| dir | what |
|---|---|
| `datagen/` | `schema.py` (EncounterFacts), `sampling.py`, `vignettes/` (10 skeletons, 5 domains), `sampler.py`, `render_note.py` (4 messy styles), `identifiers.py` (fake UK IDs, valid NHS check digit), `generator_backend.py` |
| `assemble/` | `deidentify_notes.py` (real de-id), `build_target.py` (deterministic fact→form scaffold), `validators.py` (the 4 gates), `pairs.py`, `manifest.py`, `build_dataset.py` (the driver) |
| `eval/` | `metrics.py`, `run_eval.py` (Completer protocol + GgufCompleter), `regression.py`, `report.py` |
| `train/` | `sft.py` (QLoRA), `merge_and_convert.sh`, `modelcard.py`, `dpo.py` (optional) |
| `integrate/` | `prompt_template.py` (shared with carescribe), `grammar.py` (GBNF constrained decoding) |
| `config/` | `models.yaml`, `train.yaml`, `datagen.yaml` |
| `tests/` | pytest, CPU-only, run separately from the app suite |

## Environment

Datagen + eval + the whole test suite need only **pydantic + pyyaml +
carescribe** (already in the `medgpt` env). The training stack is separate:

```
python -m venv finetune/.venv && finetune/.venv/Scripts/activate
pip install -e finetune            # torch, peft, trl, transformers, datasets
```

## Milestones

**M1 — pipeline dry run** (done, no external dep):
```
python -m finetune.assemble.build_dataset --n 200 --out finetune/data/dryrun
```
200/200 validated pairs, stratified split + manifest.

**M2 — full synthetic corpus** — set `backend.name: ollama` in
`config/datagen.yaml` (needs a local Ollama with a 7–8B instruct model for prose
quality), then:
```
python -m finetune.assemble.build_dataset --config finetune/config/datagen.yaml --out finetune/data/full
```

**M3 — dry-run LoRA on CPU** — 1 epoch, tiny, just proves sft→convert→GGUF
loads.

**M4 — real run + eval** *(runs on your RTX 5080)*:
```
python -m finetune.train.sft \
    --train finetune/data/full/train.jsonl --dev finetune/data/full/dev.jsonl \
    --config finetune/config/train.yaml --model-config finetune/config/models.yaml \
    --out finetune/runs/phi35-v1
finetune/train/merge_and_convert.sh --base microsoft/Phi-3.5-mini-instruct \
    --adapter finetune/runs/phi35-v1/adapter --llama-cpp ~/src/llama.cpp \
    --out finetune/runs/phi35-v1 --name carescribe-clinical-phi35-v1 --quant Q4_K_M
python -m finetune.eval --base-gguf <stock>.gguf --tuned-gguf finetune/runs/phi35-v1/*.Q4_K_M.gguf
```
Base-model bake-off: repeat for `google/medgemma-4b-it`; keep the winner
(default Phi-3.5-mini if within noise). Ship gate is in `EVAL_REPORT.md`.

**M5 — integrate** — drop the GGUF in `models/`, wire `grammar.build_grammar`
into `LocalGGUFBackend`, render `MODEL_CARD.md` in the About box, bump the
bundled-model name in `model_setup` / docs.
