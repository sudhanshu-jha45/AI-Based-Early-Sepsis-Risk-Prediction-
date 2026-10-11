# BioMarkerX — Manuscript Scientific Contribution

## 1. Formulation of Contribution

### A. One-Sentence Contribution
> **"We introduce an observation-process-aware causal trajectory representation for early sepsis prediction that reduces cross-institution performance decay by 30.52% and yields 2.93× lower AUROC loss under controlled measurement missingness."**

### B. Abstract Contribution
> **"BioMarkerX introduces an architectural framework that decouples patient physiological trajectories from ICU observation-process indicators. Evaluated across an internal derivation cohort ($N=2,974$) and an independent external validation cohort ($N=20,000$), observation-process awareness reduced institutional performance decay by 30.52% ($p=0.001$), yielded 2.93× lower AUROC loss under 40% controlled measurement missingness ($p<0.001$), and produced 3.00× smaller prediction shifts under same-physiology observation mask perturbations ($p<0.001$)."**

### C. Full Introduction Contribution Paragraph
> **"The primary scientific contribution of this work is a measurement-process-aware causal trajectory modeling framework for transportable early sepsis prediction. Specifically, our contribution is threefold: (1) Observation-Process-Aware Trajectory Representation: We introduce a dual-representation architecture that decouples normalized physiological trajectory dynamics from observation-process indicators (measurement availability masks, sampling intervals, and ordering frequencies). (2) Controlled Experimental Stress-Testing Framework: We establish a stress-testing protocol combining synthetic controlled dropout, same-physiology perturbation analysis, and monitoring density stratification to isolate observation-process sensitivity from physiological variation. (3) Independent External Validation & Transportability: Evaluated on an independent 20,000-patient external institutional cohort (BIDMC Set B), our framework reduces cross-institution AUROC decay by 30.52% relative to baseline models while preserving internal predictive discrimination."**

---

## 2. Key Paper Contributions Taxonomy

1. **Contribution 1**: Observation-process-aware causal trajectory representation that separates physiological state from clinical sampling habits.
2. **Contribution 2**: Controlled stress-testing framework for quantifying model sensitivity to measurement missingness and observation mask perturbations holding underlying physiology constant.
3. **Contribution 3**: Single-pass independent external validation on BIDMC Set B ($N=20,000$) demonstrating statistically significant reduction in cross-institution transportability decay.

*Note: Feature attributions (TreeSHAP), second-order physiological acceleration ($d^2Z/dt^2$), dual-tier operating thresholds (`VAL_POL_0450`), and probability calibration (`ECE = 0.0041`) are treated as supporting engineering components.*
