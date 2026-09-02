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
