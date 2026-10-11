# BioMarkerX — Central Scientific Contribution

## 1. Core Scientific Contribution

> **"Measurement-process-aware causal trajectory modeling for transportable early sepsis prediction."**

The central contribution of BioMarkerX is an architectural and representation framework that decouples the underlying physiological trajectory from the ICU observation process (measurement density, sampling intervals, missingness masks, and clinician ordering patterns). By incorporating explicit observation-process representation alongside causal physiological trajectory normalization, BioMarkerX reduces model sensitivity to institutional variation in monitoring practices and controlled measurement loss.

---

## 2. Central Research Question

> **"Can explicitly modeling the ICU observation process reduce the sensitivity of early sepsis prediction to variation in measurement density and missingness, thereby improving cross-institution transportability?"**

---

## 3. Disambiguation of Supporting Components

To maintain scientific integrity and auditability, the primary novelty is strictly framed around **measurement-process-aware causal trajectory modeling**. The following features are categorized as **supporting engineering components** and are **NOT** claimed as central scientific novelties:

* **SHAP Explainability Alone**: Standard post-hoc tree explainability; useful for clinical interpretation but not novel in ML architecture.
* **Second-Order Physiological Acceleration Alone**: Feature-engineering derivative ($d^2/dt^2$); provides local trend signals but does not solve distribution shift.
* **Dual-Tier Thresholding Alone**: Decision-policy operating curve optimization (`VAL_POL_0450`); operational calibration, not representation novelty.
* **Length-of-Stay (LOS) Persistence Alone**: Accumulation feature; supports risk contextualization but does not capture observation process dynamics.
* **Temperature Scaling**: Post-hoc probability calibration method (`ECE = 0.0041`); established technique.
* **Synthetic Vasopressor Proxies**: Data processing helper for missing medication logs; domain heuristic.

---

## 4. Empirical Summary of Validated Contribution

Across four distinct stress-testing regimes on internal Emory Set A ($N=2,974$) and independent external BIDMC Set B ($N=20,000$):

1. **Cross-Institution Transportability**: Reduces institutional AUROC decay gap from **0.0734** (Full BioMarkerX) to **0.0510** (Observation-Aware Model F), representing a **30.52% relative gap reduction** ($p = 0.001$, FDR $q = 0.003$).
2. **Controlled Measurement Loss**: Achieves **2.93× lower AUROC loss at 40% controlled measurement loss** ($0.0090$ vs $0.0264$, $p < 0.001$).
3. **Same-Physiology Stability**: Demonstrates **3.00× smaller prediction shift ($\Delta p = 0.0180$ vs $0.0540$)** under altered measurement masks holding physiological trajectory constant ($p < 0.001$).
4. **Observation-Density Stratification**: Reduces performance disparity between dense (Q4) and sparse (Q1) monitoring strata from **0.0775** to **0.0310** AUROC percentage-points.
