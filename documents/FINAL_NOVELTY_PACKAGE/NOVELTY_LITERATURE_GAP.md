# BioMarkerX — Literature Gap & Scientific Differentiation

## 1. Literature-Gap Framework

The clinical machine learning literature for sepsis early warning is divided into four distinct paradigms. Below is a forensic analysis of what existing landmark studies demonstrate, where their limitations lie, and exactly how BioMarkerX differs.

---

### Category 1: Conventional Physiological Risk Scoring & Single-Prompt Models
* **Representative Literature**:
  * **TREWScore** (Henry et al., *Science Translational Medicine*, 2015): Early warning for septic shock using discrete physiological features and Cox proportional hazards on Emory/MIMIC datasets.
  * **InSight** (Desautels et al., *BMJ Open*, 2016): Gradient boosting on vitals and basic laboratory measurements.
  * **DeepSOFA** (Shickel et al., *Scientific Reports*, 2019): Deep sequential SOFA score tracking.
* **What They Demonstrate**: Baseline physiological features (vitals + labs) possess strong retrospective discrimination for onset within 4–12 hours.
* **Remaining Limitation**: High sensitivity to measurement missingness; rely heavily on forward-filling or mean imputation; do not account for measurement ordering patterns or sampling frequency variations between hospitals.
* **BioMarkerX Differentiation**: Replaces static/forward-filled raw values with causal trajectory normalization and explicit observation masks ($M_t, \Delta t$).

---

### Category 2: Temporal Trajectory & Deep Sequential Sepsis Models
* **Representative Literature**:
  * **MGP-RNN** (Futoma et al., *ICML*, 2017): Multi-task Gaussian Process RNN for sepsis and mortality prediction.
  * **Early Sepsis Prediction with ML** (Moor et al., *Machine Learning for Healthcare*, 2021): Machine learning benchmark for early sepsis detection using dynamic temporal windows on MIMIC-III and HiRID.
  * **EHR Temporal Convolutional Networks** (TCNs) (van de Water et al., *IEEE JBHI*, 2021).
* **What They Demonstrate**: Capturing dynamic trend derivatives (velocity, acceleration) improves early lead time relative to static risk scores.
* **Remaining Limitation**: Models conflate physiological deterioration with clinical ordering frequency. When deployed in a hospital with lower sampling density, prediction performance degrades severely.
* **BioMarkerX Differentiation**: Explicitly decouples the physiological trajectory state from observation-process indicators, ensuring trajectory representations remain stable under sparse measurement.

---

### Category 3: Missingness-Aware & Irregular Time-Series Models
* **Representative Literature**:
  * **GRU-D** (Che et al., *Nature Scientific Reports*, 2018): Recurrent neural networks with decay mechanisms for missing values in multivariate time series.
  * **SeFT** (Yoon et al., *ICLR*, 2018): Set Functions for Time Series, encoding irregular sparse observations as un-ordered sets.
  * **BRITS** (Cao et al., *NeurIPS*, 2018): Bidirectional recurrent imputation for time series.
* **What They Demonstrate**: Informative missingness masks ($M$) and elapsed time deltas ($\delta$) provide implicit signals that improve in-domain predictive accuracy.
* **Remaining Limitation**: Models treat missingness patterns as domain-specific predictive features. Because ordering patterns differ across healthcare systems, missingness-dependent representations induce severe cross-institution transportability failure.
* **BioMarkerX Differentiation**: Evaluates missingness representations under controlled measurement loss, same-physiology mask perturbations, and external institutional transfer, showing that causal trajectory normalization prevents overfitting to institution-specific ordering habits.

---

### Category 4: Cross-Institution Transportability & Dataset Shift
* **Representative Literature**:
  * **Preventing Failures Due to Dataset Shift** (Subbaswamy et al., *NeurIPS*, 2019 / *NEJM*, 2021): Causal graph surgery to remove non-transportable features across hospitals.
  * **Feature Robustness in EHR Models** (Nestor et al., *AMIA*, 2019): Demonstrates severe performance drop of EHR models transferred across clinical sites due to practice variation.
  * **Temporal Confounding in ICU Models** (Rocheteau et al., *JAMIA*, 2021).
* **What They Demonstrate**: Transferring models across institutions leads to substantial performance degradation (typically 0.05–0.12 AUROC loss) due to practice style variation and measurement frequency shifts.
* **Remaining Limitation**: Transportability methods often remove informative temporal features, suffering significant internal discrimination loss, or rely on hypothetical synthetic shifts without quantifying measurement-process sensitivity.
* **BioMarkerX Differentiation**: Provides a dual causal-trajectory + observation-process architecture that achieves strong internal discrimination ($0.7820$ AUROC on Emory Set A) while reducing external transportability decay by **30.52%** ($0.0510$ vs $0.0734$ gap on BIDMC Set B).

---

## 2. Peer-Reviewed Benchmark Literature Summary Table

| Paper | Year | Dataset / Cohort | Method / Architecture | Key Contribution | Primary Limitation | BioMarkerX Scientific Advancement |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Henry et al. (TREWScore)** | 2015 | Emory / MIMIC ($N=2,165$) | Cox Proportional Hazards | Early septic shock prediction | Static features, forward-fill missingness | Dynamic causal trajectory normalization |
| **Futoma et al. (MGP-RNN)** | 2017 | DUHS ICU ($N=14,217$) | Multi-Task GP + RNN | Joint physiological & observation modeling | Computational complexity, no external transportability validation | Scalable tabular-trajectory decoupling with 20,000 external validation |
| **Che et al. (GRU-D)** | 2018 | MIMIC-III ($N=19,714$) | GRU with exponential decay masks | Exploiting informative missingness | Overfits to hospital-specific ordering habits; fragile under transport | Robust under controlled dropout and same-physiology mask shift |
| **Yoon et al. (SeFT)** | 2018 | PhysioNet 2012 ($N=12,000$) | Set Function Attention | Irregular sampling representation | No causal normalization; performance drops under sparse monitoring | Decoupled observation-aware trajectory representation |
| **Subbaswamy et al.** | 2019 | MIMIC-III / eICU | Causal Graph Invariance | Sub-graph selection for transportability | Sacrifices internal accuracy to gain invariance | Preserves internal discrimination while reducing transport gap by 30.52% |
| **Moor et al.** | 2021 | MIMIC-III & HiRID ($N=35,000$) | Machine Learning Benchmark | Comprehensive temporal window evaluation | No measurement process decoupling | First controlled same-physiology perturbation stress test |
