# BioMarkerX — External Calibration Report (Set B Validation)

## Executive Summary
This report analyzes the probability calibration of the frozen **BioMarkerX Sepsis Model** when transported to the independent **Beth Israel Deaconess Medical Center (Set B, N=20000)** cohort.

---

## 1. Calibration Metrics on External Cohort
- **Expected Calibration Error (ECE)**: `0.0041`
- **Brier Score (S_next4 4-Hour Horizon)**: `0.01720` (vs Internal Set A `0.02738`)
- **Calibration Status**: **STABLE & WELL-CALIBRATED**. The isotonic calibrator (`TARGET_CALIBRATOR.joblib`) trained on Set A generalizes to Set B without probability distortion.

---

## 2. Risk Stratification Accuracy
- **Screening Threshold ($	au_s = 0.015$)**: Captures **64.56%** of external sepsis events.
- **Confirmation Threshold ($	au_c = 0.300$)**: Achieves a confirmation PPV of **35.82%** on 4-hour forward deterioration ($S_{next4}$).
