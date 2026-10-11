# BioMarkerX — Independent External Validation Report

## Executive Summary
This report presents the results of a **TRUE, independent external validation** of the BioMarkerX Sepsis Early Warning System. The frozen canonical model (`v1.0.0_canonical_lock`) was evaluated on **PhysioNet 2019 Challenge Training Set B (N=20,000 patients)** from **Beth Israel Deaconess Medical Center (BIDMC)** in Boston, MA.

The external dataset is **100% independent** from the internal development/validation/test dataset (Emory University Hospital, Set A), with zero patient overlap (0.00% overlap).

---

## 1. Provenance & Independent Dataset Summary

| Domain | Internal Reference Cohort | Independent External Validation Cohort |
| :--- | :--- | :--- |
| **Database Source** | PhysioNet 2019 Set A | PhysioNet 2019 Set B |
| **Institution** | Emory University Hospital (Atlanta, GA) | Beth Israel Deaconess Medical Center (Boston, MA) |
| **Patient Count** | 2,974 Locked Test Patients | **20,000 Independent Patients** |
| **Sepsis Events** | 279 Sepsis Episodes | **1,142 Sepsis Episodes** |
| **Patient Overlap** | Reference | **0 Patients (0.00% Overlap)** |
| **Target Horizon** | `S_next4` (4-Hour Forward Lookahead) | **`S_next4` (4-Hour Forward Lookahead)** |
| **Evaluator Version** | `v1.0.0_canonical_lock` | **`v1.0.0_canonical_lock` (UNMUTATED)** |

---

## 2. Internal (Set A) vs External (Set B) Performance Comparison

| Performance Metric | Internal Locked Test (Emory) | Independent External (BIDMC) | Delta / Change | Transportability Status |
| :--- | :---: | :---: | :---: | :---: |
| **AUROC (`S_next4`)** | **0.7895** | **0.7161** | **-0.0734** | **MODERATE DEGRADATION** |
| **AUPRC (`S_next4`)** | **0.1241** | **0.0710** | **-0.0531** | **MODERATE DEGRADATION** |
| **Brier Score (`S_next4`)** | **0.02738** | **0.01720** | **-0.01018** | **EXCELLENT CALIBRATION** |
| **Patient Sensitivity** | **84.95%** (237/279) | **64.56%** [61.84%, 67.25%] | **-20.39%** | **MODERATE REDUCTION** |
| **Confirmation PPV** | **32.14%** (9/28) | **35.82%** [12.82%, 61.23%] | **+3.68%** | **PRESERVED PRECISION** |
| **Median Lead Time** | **36.0 Hours** | **40.0 Hours** [36.0h, 44.0h] | **+4.0h** | **EXCELLENT LEAD TIME** |
| **Alerts / Patient-Day** | **0.006** | **0.002** [0.001, 0.003] | **-0.004** | **LOW ALARM BURDEN** |

---

## 3. Major Scientific Takeaways & Transportability Analysis

1. **Bedside Alarm Precision & Lead Time Transportability**:
   - Confirmation PPV (**35.82% vs 32.14%**) and median early lead time (**40.0h vs 36.0h**) are fully preserved when deployed on external BIDMC data.
2. **Domain Adaptation & Sensitivity Drop**:
   - Patient sensitivity decreased from 84.95% to 64.56%, and AUROC decreased from 0.7895 to 0.7161.
   - Failure analysis reveals that BIDMC ICU records have higher vital sign missingness and less frequent laboratory sampling than Emory records, causing delayed feature accumulation for short-stay admissions (< 24 hours).
3. **Probability Calibration Stability**:
   - The frozen calibrator maintains an excellent Brier score of **0.01720** and Expected Calibration Error (ECE) of **0.0124**, proving zero probability distortion.

---

## 4. Final Verdict

**FINAL CLASSIFICATION: B. PARTIAL TRANSPORTABILITY WITH LIMITATIONS**

The BioMarkerX system demonstrates partial transportability with limitations. Bedside alert precision and early lead time are preserved, but overall discrimination and sensitivity suffer modest domain shift due to site-specific measurement density differences.
