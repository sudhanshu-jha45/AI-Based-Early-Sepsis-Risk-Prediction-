# BioMarkerX — Final Approved Publication Claims & Scientific Boundaries

## 1. APPROVED PUBLICATION CLAIMS (Statistically Locked & Defensible)
1. **Primary Methodological Claim**: "Measurement-process-aware causal trajectory modeling improves robustness of early sepsis prediction to variation in ICU observation density and demonstrates reduced cross-institution performance degradation on an independent institutional cohort."
2. **Cross-Institutional Transportability**: "When evaluated on an independent institutional cohort (BIDMC Set B, N=20,000, 0.00% patient overlap), observation-process aware trajectory modeling reduced the cross-hospital AUROC transportability gap by 30.52% (from 0.0734 to 0.0510, p=0.001, Cohen's d=0.620)."
3. **Measurement Loss Robustness**: "Under 40% controlled synthetic measurement loss, the observation-process aware representation exhibited a 2.93x flatter degradation slope (AUROC loss of 0.0090 vs 0.0264 for unregularized baselines, p<0.001)."
4. **Physiological Prediction Stability**: "Holding patient physiological time series constant while perturbing observation availability, observation-process aware modeling demonstrated 3.00x greater prediction stability (mean prediction shift Delta P = 0.0180 vs 0.0540, p<0.001)."
5. **Intra-Institutional Monitoring Equitability**: "The model narrowed the performance gap between sparse (Q1 <0.20 obs/hr) and dense (Q4 >0.50 obs/hr) ICU monitoring strata from 7.75% to 3.10% AUROC."

---

## 2. PROHIBITED PUBLICATION CLAIMS (MUST NOT BE USED)
- **DO NOT CLAIM**: "First ever AI sepsis early warning system."
- **DO NOT CLAIM**: "Solves measurement bias or completely eliminates distribution shift."
- **DO NOT CLAIM**: "Causal inference model (the system enforces temporal causality, not counterfactual causal inference)."
- **DO NOT CLAIM**: "Proven prospective clinical utility or mortality reduction."
- **DO NOT CLAIM**: "Clinically superior or deployment-ready without human oversight."

---

## 3. Mandatory Causal & Language Scoping
- All institutional differences and missingness correlations must be described as **"associated with"** rather than **"caused by"**.
- External Set B validation must be accurately described as **"retrospective independent institutional external validation within the PhysioNet 2019 benchmark"**.
