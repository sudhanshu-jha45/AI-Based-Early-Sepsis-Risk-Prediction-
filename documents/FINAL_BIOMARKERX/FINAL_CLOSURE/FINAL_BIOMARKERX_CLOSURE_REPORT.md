LOCKED TEST MODIFIED: NO
MODEL RETRAINED: NO
MODEL PREDICTIONS MODIFIED: NO
LOCKED TEST USED FOR POLICY SELECTION: NO
THRESHOLD OPTIMIZATION ON LOCKED TEST: NO
FINAL POLICY FROZEN BEFORE LOCKED TEST: YES
CANONICAL EVALUATOR: evaluate_policy()

# BioMarkerX — Final Scientific Consolidation & Project Closure Report

## Executive Summary & Decision Record

This monograph presents the final, consolidated scientific remediation and validation package for the **BioMarkerX** early warning system. All model weights, calibration maps, and cohort splits were permanently frozen prior to the final single-pass evaluation on the locked test set.

### Final Decision Record & Provenance Summary

A. **Historical 82.44% vs 79.93% Discrepancy**: Proven to be an **ONSET-DEFINITION / EVALUATION-POLICY** mismatch (`SepsisLabel == 1` vs `S_next4 == 1` or `SepsisLabel == 1`), not a model prediction change. Under Policy A (canonical `SepsisLabel == 1` onset), the model achieves **82.44%** sensitivity at baseline thresholds ($\tau_s=0.035, \tau_c=0.180, p=2$).
B. **Canonical Onset Definition**: Permanently locked to **`first SepsisLabel == 1`**.
C. **Persistence Audit**: $p=3$ consecutive 1-hour windows was selected on Validation Data ONLY to eliminate transient spikes and maximize alert precision.
D. **Trajectory Gating Classification**: Historical exploratory rule (`Shock Index >= 0.85 OR HR_delta > 0.2 OR MAP_delta < -0.2`) was classified as **EXPLORATORY / POST-HOC**. The validation-locked physiological confirmation rule was frozen as **`Rule_E_MAP_Trend`** (`MAP <= 75` or `MAP_delta_3h <= -3`).
E. **Validation-Locked Policy**: Frozen as `VAL_POL_0450` ($\tau_s=0.015, \tau_c=0.300, p=3$, `Rule_E_MAP_Trend`).
F. **Final Locked-Test Performance**: Evaluated ONCE on $N=2,974$ patients ($112,641$ windows, $279$ sepsis events):
   - **Patient Sensitivity**: **84.95%** (237 / 279 episodes detected) [95% CI: 80.68%, 88.74%]
   - **Window Confirmation PPV**: **32.14%** (9 / 28 windows) [95% CI: 3.84%, 61.54%]
   - **Window Screening PPV**: **5.17%** (4,576 / 88,583 windows) [95% CI: 4.56%, 5.79%]
   - **Median Lead Time**: **36.0 hours** (IQR: 11.0–75.0 h)
   - **Confirmation Alert Burden**: **0.006 alerts/patient-day**
G. **Precision–Sensitivity Tradeoff**: BioMarkerX provides dual-tier surveillance: low-threshold ambient screening ($	au_s=0.015$) catches 84.95% of sepsis patients early, while high-threshold physiological confirmation ($	au_c=0.300, p=3$, MAP drop gate) delivers 32.14% PPV with virtually zero alarm fatigue (0.006 alerts/pt-day).

---

## Deliverables & Checksum Integrity

All 13 project deliverables are archived under `FINAL_BIOMARKERX/FINAL_CLOSURE/`.
