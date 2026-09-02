#!/usr/bin/env bash
# Merge a LoRA adapter into its base, export fp16 HF weights, convert to GGUF,
# and quantize. Run on the training box (needs llama.cpp checked out).
#
#   finetune/train/merge_and_convert.sh \
#       --base   microsoft/Phi-3.5-mini-instruct \
#       --adapter finetune/runs/phi35-v1/adapter \
#       --llama-cpp ~/src/llama.cpp \
#       --out    finetune/runs/phi35-v1 \
#       --name   carescribe-clinical-phi35-v1 \
#       --quant  Q4_K_M
set -euo pipefail

BASE="" ADAPTER="" LLAMA_CPP="" OUT="" NAME="carescribe-clinical" QUANT="Q4_K_M"
while [ $# -gt 0 ]; do
  case "$1" in
    --base) BASE="$2"; shift 2;;
    --adapter) ADAPTER="$2"; shift 2;;
    --llama-cpp) LLAMA_CPP="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    --name) NAME="$2"; shift 2;;
    --quant) QUANT="$2"; shift 2;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done
: "${BASE:?--base required}" "${ADAPTER:?--adapter required}" \
  "${LLAMA_CPP:?--llama-cpp required}" "${OUT:?--out required}"

MERGED="$OUT/merged-fp16"
mkdir -p "$MERGED"

echo "[1/3] merging adapter into base -> $MERGED"
python - "$BASE" "$ADAPTER" "$MERGED" <<'PY'
import sys
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

base, adapter, out = sys.argv[1:4]
model = AutoModelForCausalLM.from_pretrained(base, torch_dtype=torch.float16)
model = PeftModel.from_pretrained(model, adapter)
model = model.merge_and_unload()
model.save_pretrained(out, safe_serialization=True)
AutoTokenizer.from_pretrained(base).save_pretrained(out)
print("merged")
PY

echo "[2/3] HF -> GGUF (f16)"
GGUF_F16="$OUT/$NAME.f16.gguf"
python "$LLAMA_CPP/convert_hf_to_gguf.py" "$MERGED" --outfile "$GGUF_F16" --outtype f16

echo "[3/3] quantize -> $QUANT"
GGUF_Q="$OUT/$NAME.$QUANT.gguf"
"$LLAMA_CPP/llama-quantize" "$GGUF_F16" "$GGUF_Q" "$QUANT"

echo "done: $GGUF_Q"
