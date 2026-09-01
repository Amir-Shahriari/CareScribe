# CareScribe clinical drafting model — model card

- **Base model:** microsoft/Phi-3.5-mini-instruct
- **Licence:** MIT
- **Method:** QLoRA SFT (r=16, alpha=32, dropout=0.05, targets=q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj)
- **Built:** 2026-09-01
- **carescribe commit:** 99314e5586552963249ab3a478ab25256a2b7974

## Training data

- 100% synthetic. Generator: template
- Seed: 0
- Pairs: 2500 ({"dev": 243, "test": 243, "train": 2014})
- Dataset SHA-256: `90cafbfab905cf78d473f8834de43c12f84b4d67b2fb50a2e68345e54266e02f`

## Evaluation

**Ship gate: PASS**  (latency ratio 0.813, regressions: none)

| metric | base | tuned |
|---|---|---|
| format | 0.520 | 1.000 |
| faithfulness | 0.740 | 1.000 |
| placeholder_integrity | 1.000 | 1.000 |
| residual_clean | 0.940 | 1.000 |

## Known limitations

- Trained only on synthetic encounters — real-note performance is unverified.
- Specialty coverage limited to the vignette set (GP, mental health, cardiology, respiratory, elderly care).
- Not a clinical decision tool; every draft requires clinician review.
