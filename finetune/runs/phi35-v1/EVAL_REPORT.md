> **SUPERSEDED 2026-09-09.** The numbers below were produced by a harness with
> four defects (D1-D4 in `docs/superpowers/specs/2026-09-09-clinical-finetune-v2-design.md`):
> the test split shared vignette skeletons with training; the evaluator never
> read that split at all, re-sampling the same skeletons instead; faithfulness
> was scored against the same `EncounterFacts` the target was rendered from;
> and `style_match` scored a dimension no pair in the corpus varied -- in fact
> it compared every draft against the deterministic scaffold.
>
> Honest re-scoring on a vignette-disjoint holdout: **`v2harness/EVAL_REPORT.md`**.
> Summary of the difference:
>
> | metric | this report | honest |
> |---|---|---|
> | format | 1.000 | 0.800 |
> | faithfulness | 1.000 | 0.960 |
> | placeholder_integrity | 1.000 | 1.000 |
> | residual_clean | 1.000 | 1.000 |
> | style_match | 0.998 | withdrawn -- measured nothing |
>
> The model is still genuinely better than its base on every axis, and the new
> harness adds the metric that matters most clinically: on adversarial gap
> probes the base model invents content **every time** (1.000) and the tuned
> model **never** does (0.000). Train/test overlap on the new holdout is low
> (median 0.189, 0 of 50 above 0.6), so those numbers are measuring capability
> rather than recall of the corpus.

# Evaluation report

**Ship gate: PASS**

- eval items: 50
- median seconds/draft: phi35-base 5.42s, phi35-tuned 4.41s (ratio 0.813, ceiling 1.15)
- regressions: none

| metric | phi35-base | phi35-tuned | Δ |
|---|---|---|---|
| format | 0.520 | 1.000 | ▲ +0.480 |
| faithfulness | 0.740 | 1.000 | ▲ +0.260 |
| placeholder_integrity | 1.000 | 1.000 | – +0.000 |
| residual_clean | 0.940 | 1.000 | ▲ +0.060 |
| style_match | 0.551 | 0.998 | ▲ +0.448 |

Ship gate: tuned ≥ base on every metric above the style row, no regression on the regression set, and latency ratio ≤ 1.15.

## Regression set (real de-identified corpus docs)

10 documents from stress_corpus/, scored on the fact-free gates.

| metric | base | tuned |
|---|---|---|
| format | 1.00 | 1.00 |
| placeholder_integrity | 1.00 | 1.00 |
| residual_clean | 0.70 | 0.90 |

regressions: none
