"""
Run a model over an eval set and score it on the four metrics.

A "model" here is any ``Completer`` — ``complete(system, user) -> str``. That
keeps the harness runnable on CPU with a scripted stub; the real GGUF path is
one adapter (:class:`GgufCompleter`, lazy-imports ``llama_cpp``). Decoding is
greedy / temperature 0 everywhere, matching production.

``compare(base, tuned)`` applies the ship gate from the design: tuned ≥ base on
every target metric, and latency no worse than 1.15×.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Iterable, Protocol

from finetune.assemble.build_target import build_target
from finetune.assemble.deidentify_notes import deidentify_note, leaked_values
from finetune.assemble.validators import validate
from finetune.datagen.render_note import render
from finetune.datagen.sampler import sample_encounters
from finetune.datagen.schema import EncounterFacts, FormType
from finetune.eval.metrics import DraftScore, aggregate, score_draft
from finetune.integrate.prompt_template import build_messages

_DEFAULT_FORMS = (
    FormType.SOAP,
    FormType.PROGRESS_NOTE,
    FormType.HANDOVER,
    FormType.CARE_PLAN,
)

LATENCY_CEILING = 1.15  # tuned median seconds-to-draft / base, must be ≤ this


class Completer(Protocol):
    def complete(self, system: str, user: str) -> str: ...


@dataclass(frozen=True)
class EvalItem:
    facts: EncounterFacts
    form: FormType
    document: str                 # de-identified, placeholdered
    known_placeholders: list[str]
    target: str                   # the deterministic scaffold (reference)

    def messages(self) -> list[dict[str, str]]:
        return build_messages(self.form, self.document)


def make_eval_set(
    n: int,
    *,
    seed: int = 1000,
    forms: tuple[FormType, ...] = _DEFAULT_FORMS,
    gap_probability: float = 0.25,
) -> list[EvalItem]:
    """A held-out set built exactly like the training data (different seed)."""
    from finetune.datagen.identifiers import inject

    items: list[EvalItem] = []
    for i, facts in enumerate(
        sample_encounters(n, seed=seed, gap_probability=gap_probability)
    ):
        form = forms[i % len(forms)]
        identified, placed = inject(render(facts, seed=seed + i), seed=seed + i)
        deid = deidentify_note(identified)
        if leaked_values(deid, [p.value for p in placed]):
            continue
        target = build_target(facts, form)
        if not validate(target, facts, form, known_placeholders=deid.known_placeholders).ok:
            continue
        items.append(
            EvalItem(facts, form, deid.placeholdered_text, deid.known_placeholders, target)
        )
    return items


@dataclass
class RunResult:
    metrics: dict[str, float]
    median_seconds: float
    n: int
    scores: list[DraftScore]


def run(model: Completer, items: Iterable[EvalItem]) -> RunResult:
    items = list(items)
    scores: list[DraftScore] = []
    durations: list[float] = []
    for item in items:
        msgs = item.messages()
        started = time.monotonic()
        draft = model.complete(msgs[0]["content"], msgs[1]["content"])
        durations.append(time.monotonic() - started)
        scores.append(
            score_draft(
                draft,
                item.facts,
                item.form,
                known_placeholders=item.known_placeholders,
                style_target=item.target,
            )
        )
    durations.sort()
    median = durations[len(durations) // 2] if durations else 0.0
    return RunResult(aggregate(scores), median, len(items), scores)


def compare(base: RunResult, tuned: RunResult) -> dict:
    """Ship-gate verdict: tuned ≥ base on every target metric, latency ≤ 1.15×."""
    from finetune.eval.metrics import TARGET_METRICS

    deltas = {
        m: round(tuned.metrics.get(m, 0.0) - base.metrics.get(m, 0.0), 4)
        for m in TARGET_METRICS
    }
    regressions = [m for m, d in deltas.items() if d < 0]
    latency_ratio = (
        tuned.median_seconds / base.median_seconds if base.median_seconds else 1.0
    )
    return {
        "deltas": deltas,
        "base": base.metrics,
        "tuned": tuned.metrics,
        "latency_ratio": round(latency_ratio, 3),
        "regressions": regressions,
        "latency_ok": latency_ratio <= LATENCY_CEILING,
        "ship": not regressions and latency_ratio <= LATENCY_CEILING,
    }


class GgufCompleter:
    """Adapter over a local GGUF via llama-cpp-python. Greedy, temperature 0."""

    def __init__(self, model_path: str, *, n_ctx: int = 4096, n_threads: int | None = None):
        from llama_cpp import Llama  # lazy — not needed for the stub path

        self._llm = Llama(
            model_path=model_path, n_ctx=n_ctx, n_threads=n_threads, verbose=False
        )

    def complete(self, system: str, user: str) -> str:
        out = self._llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.0,
            max_tokens=900,
        )
        return out["choices"][0]["message"]["content"]


class CallableCompleter:
    """Wrap a plain ``(system, user) -> str`` function as a Completer."""

    def __init__(self, fn: Callable[[str, str], str]):
        self._fn = fn

    def complete(self, system: str, user: str) -> str:
        return self._fn(system, user)


class HFCompleter:
    """Greedy generation from a HF model, optionally with a LoRA adapter.

    Much faster than the GGUF path for the base-vs-tuned comparison because it
    runs on the GPU. Use :class:`GgufCompleter` to also confirm the shipped
    quantised artefact behaves.
    """

    def __init__(
        self, base_model: str, adapter_dir: str | None = None, *, max_new_tokens: int = 900
    ):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.tok = AutoTokenizer.from_pretrained(base_model)
        model = AutoModelForCausalLM.from_pretrained(
            base_model, dtype=torch.bfloat16, device_map="auto"
        )
        if adapter_dir:
            from peft import PeftModel

            model = PeftModel.from_pretrained(model, adapter_dir)
        self.model = model.eval()
        self.max_new_tokens = max_new_tokens

    def complete(self, system: str, user: str) -> str:
        import torch

        msgs = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        enc = self.tok.apply_chat_template(
            msgs,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True,
        )
        enc = {k: v.to(self.model.device) for k, v in enc.items()}
        prompt_len = enc["input_ids"].shape[1]
        with torch.no_grad():
            out = self.model.generate(
                **enc,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                pad_token_id=self.tok.pad_token_id or self.tok.eos_token_id,
            )
        return self.tok.decode(out[0][prompt_len:], skip_special_tokens=True)


def main(argv: list[str] | None = None) -> int:
    import argparse

    from finetune.eval.regression import regressed, regression_items, score_regression
    from finetune.eval.report import write_report

    ap = argparse.ArgumentParser(description="base vs tuned eval + ship gate")
    ap.add_argument("--base-gguf", required=True)
    ap.add_argument("--tuned-gguf", required=True)
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--out", default="finetune/eval/out")
    args = ap.parse_args(argv)

    items = make_eval_set(args.n, seed=args.seed)
    base = GgufCompleter(args.base_gguf)
    tuned = GgufCompleter(args.tuned_gguf)

    base_run, tuned_run = run(base, items), run(tuned, items)

    reg_items = regression_items()
    reg_base = score_regression(base, reg_items)
    reg_tuned = score_regression(tuned, reg_items)
    reg_fail = regressed(reg_base, reg_tuned)

    ship = write_report(base_run, tuned_run, args.out)
    print(f"eval items: {len(items)}   regression docs: {len(reg_items)}")
    print(f"regression failures: {reg_fail or 'none'}")
    print(f"SHIP GATE: {'PASS' if ship and not reg_fail else 'FAIL'}  -> {args.out}/")
    return 0 if (ship and not reg_fail) else 1


__all__ = [
    "CallableCompleter",
    "Completer",
    "EvalItem",
    "GgufCompleter",
    "HFCompleter",
    "LATENCY_CEILING",
    "RunResult",
    "compare",
    "main",
    "make_eval_set",
    "run",
]
