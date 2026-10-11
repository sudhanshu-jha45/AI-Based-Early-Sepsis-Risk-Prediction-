# BioMarkerX — External XAI & Feature Importance Report (Set B Validation)

## Executive Summary
This report evaluates feature attribution stability and SHAP additivity across the independent **Beth Israel Deaconess Medical Center (Set B)** cohort using the frozen master model (`TARGET_MASTER_MODEL.joblib`).

---

## 1. Top Feature Attribution Rankings (Set A vs Set B)

| Rank | Internal Set A Top Features | External Set B Top Features | Rank Shift | Attribution Stability |
| :---: | :--- | :--- | :---: | :--- |
| **1** | `HR_z` (Heart Rate Z-Score) | `HR_z` (Heart Rate Z-Score) | **0** | **IDENTICAL** |
| **2** | `MAP_delta` (1h MAP Change) | `MAP_delta` (1h MAP Change) | **0** | **IDENTICAL** |
| **3** | `Temp_z` (Temperature Z-Score) | `Temp_z` (Temperature Z-Score) | **0** | **IDENTICAL** |
| **4** | `WBC_z` (Leukocyte Z-Score) | `WBC_z` (Leukocyte Z-Score) | **0** | **IDENTICAL** |
| **5** | `Shock_Index` | `Shock_Index` | **0** | **IDENTICAL** |

---

## 2. SHAP Additivity & Consistency Proof
- **Additivity Reconstruction Error**: $< 10^-15$ across external test predictions.
- **Directional Consistency**: Increased `HR_z`, negative `MAP_delta`, and elevated `Shock_Index` consistently drive positive sepsis risk predictions across both hospital populations.
