# BioMarkerX Task 5 — Forensic Reconciliation & Validity Audit Report

**Audit Timestamp**: 2026-10-03 14:41:38
**Overall Status**: **ACCEPTED FOR FINAL SCIENTIFIC RECORD (YES)**

## Executive Forensic Verdict Matrix

| Audit Dimension | Verdict | Rationale / Proof |
|---|---|---|
| **1. Policy Identity** | **PASS** | Policy lock hash matches locked test evaluation hash byte-for-byte. |
| **2. Numerator/Denominator** | **PASS** | Recalculated exact numerators and denominators for all metrics across Validation and Locked Test. |
| **3. Patient vs Window Metric Consistency** | **PASS** | Proven mathematical relationship between screening patient detection and sparse confirmation window triggers. |
| **4. PPV Arithmetic** | **PASS** | Verified 18/36 = 50.00% (Val) and 9/28 = 32.14% (Test). |
| **5. Bootstrap Reproducibility** | **PASS** | Verified patient-level bootstrap (N=1,000, seed=42); wide CI explained by small N=28 confirmation count. |
| **6. Alert Burden Arithmetic** | **PASS** | Verified 28 / 4693.38 pt-days = 0.005966 alerts/pt-day (0.597 / 100 pt-days). |
| **7. Patient Detection Accounting** | **PASS** | Cataloged all 279 locked-test sepsis patients in `TASK5_PATIENT_DETECTION_STATUS.csv`. |
| **8. Lead-Time Calculation** | **PASS** | Verified median lead time = 36.0 h (N=237 detected) measured relative to first `SepsisLabel == 1`. |
| **9. Physiological Rule Leakage** | **PASS** | Verified zero future leakage, no centered rolling, no full-stay normalization in `Rule_E_MAP_Trend`. |
| **10. Locked-Test Contamination** | **PASS** | Policy lock timestamp (14:35:24) strictly preceded locked test evaluation (14:36:52). |
| **11. Internal Consistency** | **PASS** | Zero metric contradictions found across all Task 5 artifacts. |

## Detailed Phase Reconciliation Notes

### Phase 3: Mathematical Reconciliation of 0.27% Confirmation Sensitivity vs 84.95% Patient Sensitivity
- **Patient Sensitivity (84.95%, 237/279)**: Evaluates whether a patient receives at least one screening alert ($\tau_s = 0.015$) prior to sepsis onset. Because $\tau_s = 0.015$ provides continuous early surveillance, 237 out of 279 patients trigger an alert before onset.
- **Confirmation Sensitivity (0.27%, 9/3369)**: Evaluates the fraction of ALL 3,369 transition windows ($S_{next4} == 1$) across all 279 sepsis patients that simultaneously satisfy $\tau_c = 0.300$, $p=3$ consecutive persistence, AND the `Rule_E_MAP_Trend` physiological gate. Because the confirmation criteria are extremely strict, only 9 windows trigger full confirmation, yielding 0.27% window confirmation sensitivity.

### Phase 11: Objective Task 4 vs Task 5 Trade-Off
- **Task 4 Locked Test**: Patient Sens = 94.98%, Confirm PPV = 23.76%, Confirm Sensitivity = 3.95%, Confirm Burden = 0.12 alerts/pt-day.
- **Task 5 Locked Test**: Patient Sens = 84.95%, Confirm PPV = 32.14%, Confirm Sensitivity = 0.27%, Confirm Burden = 0.006 alerts/pt-day.
- **Trade-Off Summary**: Task 5 traded 10.03% patient sensitivity (84.95% vs 94.98%) to gain an 8.38% increase in Confirmation PPV (32.14% vs 23.76%) and a 20-fold reduction in interruptive alert burden (0.006 vs 0.12 alerts/pt-day). Both policies maintain Patient Sensitivity $\ge 80.0\%$.

