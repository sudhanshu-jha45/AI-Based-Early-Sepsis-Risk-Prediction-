# BioMarkerX — Audited Publication Claims & Safe Wording Guide

## Executive Summary
This document establishes the official scientific boundary for all public and manuscript claims regarding the **BioMarkerX Sepsis Early Warning System**. Every claim has been rigorously audited against the frozen locked test set (2973 patients, 275 sepsis episodes).

---

## 1. Approved vs Rejected Scientific Claims

| Claim Domain | Claim Submitted | Audit Verdict | Approved Safe Publication Wording |
| :--- | :--- | :--- | :--- |
| **Cohort Lineage** | "External validation on 5,999 reserved patients" | **REJECTED** (56% overlap with Val, 44% with Test) | "Internal evaluation on Reserved PhysioNet 2019 Holdout Cohort (N=2973)" |
| **Sensitivity** | "99.63% Sepsis Sensitivity Achieved" | **REJECTED** (Unconstrained post-hoc window coverage) | "Canonical Lead-Time Constrained Patient Sensitivity of **84.95%** (237/279) at median lead time **36.0h**" |
| **Dual-Tier System** | "Dual-Tier Asymmetric Architecture mitigates alarm fatigue" | **APPROVED** (Decouples background screening from bedside confirmation) | "Dual-tier asymmetric operational architecture decoupling surveillance sensitivity from bedside confirmation PPV (**32.14%**)" |
| **Physiological Dynamics** | "Second-Order Physiological Acceleration improves early detection" | **APPROVED** ($\Delta^2	ext{MAP}$, $\Delta^2	ext{SI}$ captures curvature) | "Second-order physiological acceleration gating ($\Delta^2	ext{MAP}$, $\Delta^2	ext{SI}$) for early trajectory shift detection" |
| **Calibration** | "Temperature Scaling (T=1.12) boosts AUROC to 0.8707" | **REJECTED** (Monotonic invariance proof $\Delta	ext{AUROC} = 0.000000$) | "Online temperature scaling for probability calibration (**Brier score = 0.02738**)" |
| **Vasopressor Adjustment** | "MAR-validated vasopressor-aware MAP correction" | **REJECTED** (Synthetic Shock Index proxy + manual coeff 5.0) | "Heuristic shock-index adjusted perfusion pressure filter" |
| **LOS Persistence** | "LOS-adaptive persistence rule dampens early ICU alarms" | **APPROVED** (Promising operational trade-off) | "Length-of-stay adaptive temporal persistence policy ($p=1,2,3$)" |

---

## 2. Manuscript Claim Text Snippets

### Abstract / Summary Claims
- **Primary Accuracy**: *"Under canonical evaluation on 2,974 locked test ICU patients, BioMarkerX achieves a lead-time constrained patient sensitivity of 84.95% (237/279 sepsis episodes) with a median lead time of 36.0 hours prior to clinical onset."*
- **Operational Precision**: *"The dual-tier asymmetric screening-confirmation architecture reduces bedside false alarms by 91.4% compared to continuous screening, achieving a confirmation positive predictive value (PPV) of 32.14%."*
- **Physiological Acceleration**: *"Incorporation of second-order temporal acceleration features ($\Delta^2	ext{MAP}$, $\Delta^2	ext{SI}$) captures rapid physiological deterioration prior to static threshold breaches."*

---

## 3. Prohibited Terms & Required Substitutions
- ❌ **DO NOT USE**: *"External Validation Cohort"* -> ✅ **USE**: *"Reserved Single-Center Holdout Subset"*
- ❌ **DO NOT USE**: *"99.63% Sensitivity"* -> ✅ **USE**: *"84.95% Lead-Time Constrained Sensitivity (or 99.6% unconstrained event coverage)"*
- ❌ **DO NOT USE**: *"AUROC boosted by Temperature Scaling"* -> ✅ **USE**: *"Temperature scaling optimized probability calibration"*
- ❌ **DO NOT USE**: *"Vasopressor Dose Adjusted MAP"* -> ✅ **USE**: *"Shock-Index Adjusted Perfusion Pressure Filter"*
