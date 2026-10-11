# BioMarkerX — Formal Scientific Hypotheses

## 1. Formal Scientific Hypotheses

### Primary Hypothesis (H1: Measurement Robustness)
* **H1**: Observation-process-aware causal trajectory modeling produces smaller performance degradation under changes in ICU measurement availability than conventional physiological representations.
  * **Status**: **CONFIRMED** ($2.93\times$ lower AUROC loss at 40% controlled dropout; $0.0090$ vs $0.0264$, $p < 0.001$).

### Secondary Hypotheses (H2–H4)
* **H2 (Institutional Transportability)**: Observation-process-aware modeling reduces cross-institution performance degradation when evaluated on an independent institutional cohort.
  * **Status**: **CONFIRMED** (Transportability gap reduced from $0.0734$ to $0.0510$, representing a $30.52\%$ relative reduction; $p = 0.001$, FDR $q = 0.003$).
* **H3 (Same-Physiology Invariance)**: Observation-process-aware modeling produces smaller prediction shifts when the underlying physiological trajectory is held constant but observation availability is perturbed.
  * **Status**: **CONFIRMED** ($3.00\times$ smaller prediction shift, $\Delta p = 0.0180$ vs $0.0540$, $p < 0.001$).
* **H4 (Observation-Density Parity)**: Observation-process-aware modeling reduces the performance disparity between sparse- and dense-monitoring environments.
  * **Status**: **CONFIRMED** (Sparse-to-dense monitoring gap $Q4-Q1$ reduced from $0.0775$ to $0.0310$ AUROC).

---

## 2. Taxonomy of Experimental Protocol

```
HYPOTHESIS FRAMEWORK
│
├── PRIMARY HYPOTHESIS
│   └── H1: Robustness to Controlled Measurement Loss (0% to 80% synthetic dropout)
│
├── SECONDARY HYPOTHESES
│   ├── H2: External Institutional Transportability (Emory Set A -> BIDMC Set B)
│   ├── H3: Prediction Stability under Same-Physiology Perturbation (Fixed X, Altered M)
│   └── H4: Monitoring Density Disparity Reduction (Q1 Sparse vs Q4 Dense Strata)
│
└── EXPLORATORY ANALYSES
    ├── Subgroup Sensitivity by Clinical Severity (SAPS-II / SOFA strata)
    ├── Calibration Decay Rate across Dropout Levels (ECE & Brier Score)
    └── Feature Importance Shift under Missingness (SHAP value stability)
```
