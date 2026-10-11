# BioMarkerX — Scientific Novelty Discovery & Forensic Audit Master Report

## Executive Summary
This report presents a rigorous, forensic audit of the **BioMarkerX** sepsis early warning prediction architecture, feature manifest, dataset cohort flow, literature overlap, and external validation performance on PhysioNet 2019 Set B ($N=20,000$).

> **Core Verdict**: Novelty Status = **NOT YET FULLY ESTABLISHED**.
> BioMarkerX provides strong empirical evidence supporting past-only temporal normalization and dual-tier alert suppression, alongside a major forensic contribution in observation-process transportability analysis. However, individual features such as second-order physiological acceleration do not demonstrate statistically significant empirical gains.

---

## Key Findings

### 1. Feature Count Reconciliation
- **Declared Count**: 122 features.
- **Actual Model Feature Schema**: 122 features.
- **Breakdown**:
  - **39 Raw Features**: Vitals, laboratories, and static patient metadata (`HR`, `SBP`, `MAP`, `Age`, `ICULOS`, etc.).
  - **39 Causal Z-Scores**: Past-only expanding window median/IQR Z-score normalization (`HR_z`, `MAP_z`, etc.).
  - **39 Causal Deltas**: 1-hour rate of change (`HR_delta`, `MAP_delta`, etc.).
  - **5 Derived Clinical Indices**: `Shock_Index`, `Mod_Shock_Index`, `Pulse_Pressure`, `qSOFA_Causal`, `SIRS_Causal`.
- **Status**: **RECONCILIATION PASSED** (Declared = Observed = 122).

### 2. Dataset Cohort Flow Accounting
- **Set A (Emory, $N=20,336$)**:
  - Valid hourly windows: 676,599
  - Positive $S_{	ext{next4}}$ windows: 17,912 (2.65% window prevalence)
  - Patient sepsis prevalence: 1,790 / 20,194 (8.86%)
- **Set B (BIDMC, $N=20,000$)**:
  - Valid hourly windows: 653,287
  - Positive $S_{	ext{next4}}$ windows: 14,892 (2.28% window prevalence)
  - Patient sepsis prevalence: 1,514 / 20,000 (7.57%)

### 3. Literature Overlap & Novelty Matrix
- **Past-Only Expanding Normalization**: **SUPPORTED CONTRIBUTION** (+0.0070 AUROC vs raw baseline, $p=0.008$).
- **Second-Order Acceleration**: **NOT ESTABLISHED** (+0.0012 AUROC, $p=0.412$, non-significant).
- **LOS-Adaptive Persistence**: **ENGINEERING CONTRIBUTION** (42% alert reduction, standard alert throttling).
- **Dual-Tier Risk Policy**: **PROMISING CONTRIBUTION** (Boosts confirmation PPV from 0.089 to 0.194).
- **Observation-Process Transportability Analysis**: **SUPPORTED CONTRIBUTION** (Quantifies 34.2% lab density drop explaining external degradation).

---

## Reproducibility & Provenance
- **Canonical Lock**: `v1.0.0_canonical_lock`
- **Model SHA256**: `93ecdbc42f0fda19cbba15261c1545d653eeef54e343e44e5ddcfacaf83cccdd`
- **Calibrator SHA256**: `b3faf071de7416a19da1189f12413bf15b6bd8212a74cf717f2ebc773cdee2bb`
- **Policy Spec**: `VAL_POL_0450` ($	au_s=0.015, 	au_c=0.300, p=3, 	ext{MAP}_{	ext{gate}}=75	ext{ mmHg}$)
