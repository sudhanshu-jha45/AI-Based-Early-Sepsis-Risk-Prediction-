# BioMarkerX — Final Canonical Evaluator Specification

## Executive Summary
This document establishes the single, authoritative, frozen **BioMarkerX Canonical Evaluator Specification (v1.0.0_canonical_lock)**. All future internal, external, and manuscript evaluations MUST adhere strictly to this specification without modification.

---

## 1. Locked Scientific Parameters

| Parameter Domain | Parameter Value | Scientific Rationale |
| :--- | :--- | :--- |
| **Locked Test Cohort** | **2,974 Patients** (`training_setA[17362:20336]`) | Exact PhysioNet 2019 Set A test holdout slice |
| **Total Sepsis Episodes** | **279 Events** (`max(SepsisLabel) == 1`) | Unfiltered raw clinical sepsis onset count |
| **Primary Target Horizon** | **`S_next4`** (4-Hour Forward Lookahead) | Official clinical early warning horizon (t+1 to t+4) |
| **Secondary Target Horizon** | **`S_next1`** (1-Hour Immediate Step) | Auxiliary single-step benchmark |
| **Preprocessing** | Causal Expanding Window Median/IQR (`center=False`) | Zero lookahead data leakage guarantee |
| **Master Model** | `TARGET_MASTER_MODEL.joblib` (SHA256: `93ecdbc42f...`) | Frozen canonical LightGBM classifier |
| **Calibrator** | `TARGET_CALIBRATOR.joblib` (SHA256: `b3faf071de...`) | Frozen isotonic probability calibrator |
| **Screening Threshold (tau_s)** | **0.015** | Background surveillance threshold |
| **Confirmation Threshold (tau_c)** | **0.300** | High-precision bedside alert threshold |
| **Persistence Filter (p)** | **3 Consecutive Windows** | False alert dampening rule |
| **Gating Rule** | `Rule_E_MAP_Trend` (MAP <= 75 or MAP_d3 <= -3.0) | MAP trend confirmation gate |

---

## 2. Canonical Performance Baseline (Frozen Reference)

- **Patient Sensitivity**: **84.95%** (237 / 279 Sepsis Episodes)
- **Median Lead Time**: **36.0 Hours** prior to clinical onset
- **Confirmation PPV**: **32.14%** (9 / 28 Bedside Alarms)
- **Raw Model AUROC (S_next4)**: **0.7895**
- **Raw Model AUPRC (S_next4)**: **0.1241**
- **Raw Model Brier (S_next4)**: **0.02738**
- **Single-Step AUROC (S_next1)**: **0.8651**
- **Single-Step AUPRC (S_next1)**: **0.1620**

---

## 3. Mandatory Evaluation Rules
1. **Never alter the 2,974 patient cohort list**.
2. **Never alter the 279 sepsis event count**.
3. **Always report discrimination against `S_next4`** (4-hour forward lookahead) as the primary clinical metric.
4. **Always enforce lead-time constraint** (t_alert <= t_onset) when calculating patient sensitivity.
