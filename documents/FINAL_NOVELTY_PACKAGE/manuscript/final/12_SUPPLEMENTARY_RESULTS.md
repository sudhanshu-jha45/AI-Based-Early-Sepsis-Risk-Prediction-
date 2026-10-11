# Supplementary Material: Section S2 — Supplementary Results

## S2.1 Full Controlled Dropout Curve Numerical Summary

| Dropout Level | Model A (Raw) | Model B (Deltas) | Model C (Causal Z) | Model E (BioMarkerX) | Model F (Observation-Aware) | Loss Ratio (E vs F) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **0% Baseline** | 0.7420 | 0.7680 | 0.7750 | 0.7895 | 0.7820 | 1.00x |
| **10% Dropout** | 0.7340 | 0.7612 | 0.7690 | 0.7790 | 0.7800 | 5.25x |
| **20% Dropout** | 0.7237 | 0.7523 | 0.7613 | 0.7680 | 0.7780 | 5.38x |
| **40% Dropout** | 0.7000 | 0.7320 | 0.7435 | 0.7631 | **0.7730** | **2.93x lower loss** |
| **60% Dropout** | 0.6737 | 0.7095 | 0.7238 | 0.7120 | 0.7420 | 1.94x |
| **80% Dropout** | 0.6456 | 0.6854 | 0.7027 | 0.6410 | 0.6980 | 1.77x |

---

## S2.2 Paired Bootstrap Resample Distribution Summary (1,000 Resamples)

| Endpoint Metric | Point Estimate | 95% CI Lower | 95% CI Upper | p-value | FDR q-value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Set B AUROC Improvement** | +0.0149 | +0.0062 | +0.0235 | 0.002 | 0.003 |
| **Transportability Gap Reduction** | 30.52% | 14.8% | 46.2% | 0.001 | 0.003 |
| **40% Dropout Loss Ratio** | 2.93x | 2.15x | 3.95x | 0.001 | 0.003 |
| **Same-Physiology Shift Ratio** | 3.00x | 2.45x | 3.65x | 0.001 | 0.003 |
| **Monitoring Density Gap Reduction** | 60.0% | 42.1% | 75.8% | 0.001 | 0.003 |
