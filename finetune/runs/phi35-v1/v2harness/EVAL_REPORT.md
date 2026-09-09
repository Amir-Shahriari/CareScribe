# Evaluation report

**Ship gate: PASS**

- eval items: 50
- median seconds/draft: base 14.58s, tuned 8.94s (ratio 0.613, ceiling 1.15)
- regressions: none

| metric | base | tuned | Δ |
|---|---|---|---|
| format | 0.320 | 0.800 | ▲ +0.480 |
| faithfulness | 0.720 | 0.960 | ▲ +0.240 |
| placeholder_integrity | 1.000 | 1.000 | – +0.000 |
| residual_clean | 0.980 | 1.000 | ▲ +0.020 |

Ship gate: tuned ≥ base on every metric above, no regression on the regression set, and latency ratio ≤ 1.15.

## Confabulation (adversarial gap probes)

- base: 1.000
- tuned: 0.000

Fraction of probes where the model stated content under a heading the source leaves undocumented. Lower is better.

## Train/test overlap

- median nearest-train similarity: 0.189
- p95: 0.552
- test targets above 0.6: 0 of 50

High overlap voids the scores above: a near-copy of a training target measures recall of the corpus, not capability.
