# BioMarkerX — Master Explainable AI (XAI) & SHAP Monograph

## 1. Executive Summary & Axiomatic Foundation
BioMarkerX enforces strict mathematical transparency. Every patient risk score is backed by exact **SHAP (Shapley Additive exPlanations)** attributions satisfying the Efficiency Axiom.

### **Mathematical Reconstruction Proof (Efficiency Axiom)**
- **Evaluated Test Windows**: 300
- **Baseline Expectation ($E[f(x)]$ / Base Value)**: `0.094799`
- **Max Absolute Reconstruction Error**: `8.32667268e-17`
- **Mean Absolute Reconstruction Error**: `4.81096644e-18`
- **Efficiency Axiom Status**: **`PASSED (< 1e-12 exact machine precision)`**

$$f(x_i) = \phi_0 + \sum_{j=1}^{M} \phi_{i,j}$$

## 2. Global Biomarker Importance Hierarchy

| Rank | Biomarker Feature | Mean SHAP (Logit Impact) | Physiological Role |
| :---: | :--- | :---: | :--- |
| 1 | `ICULOS` | **0.091509** | Temporal ICU Length of Stay Accumulation |
| 2 | `SBP` | **0.044903** | Systolic Perfusion Boundary |
| 3 | `HR` | **0.028443** | Hemodynamic Acceleration / Tachycardia Response |
| 4 | `MAP` | **0.013950** | Systemic Vascular Resistance & Perfusion Pressure |
| 5 | `Temp` | **0.000000** | Thermoregulatory Dysregulation / Pyrexia-Hypothermia |
| 6 | `O2Sat` | **0.000000** | Pulmonary Gas Exchange & Arterial Oxygenation |
| 7 | `Resp` | **0.000000** | Respiratory Rate / Compensatory Tachypnea |
| 8 | `BaseExcess` | **0.000000** | Metabolic Acid-Base Deficit |
| 9 | `HCO3` | **0.000000** | Physiological Biomarker Dynamics |
| 10 | `DBP` | **0.000000** | Diastolic Arterial Tone |

## 3. Temporal Delta-SHAP Velocity Drivers
BioMarkerX tracks acute risk changes between consecutive windows ($\Delta \text{Risk}_t = \text{Risk}_t - \text{Risk}_{t-1}$):
- **Primary Escalation Drivers**: `SBP, MAP, HR`
- **Clinical Significance**: Demonstrates that hemodynamic velocity changes trigger alerts prior to static threshold breaches.

## 4. Patient Force Explanation Case Study
```json
{
  "case_id": "CASE_01",
  "patient_id": "PAT_0000",
  "base_value": 0.09479875486696789,
  "raw_pred": 0.17019957261260873,
  "calibrated_probability": 0.01251303441084463,
  "top_positive_risk_drivers": [
    {
      "feature": "ICULOS",
      "shap_value": 0.07430844496649389
    },
    {
      "feature": "HR",
      "shap_value": 0.025558268592584928
    }
  ],
  "top_negative_risk_pullers": [
    {
      "feature": "SBP",
      "shap_value": -0.019175134589042193
    },
    {
      "feature": "MAP",
      "shap_value": -0.005290761224395769
    }
  ]
}
```
