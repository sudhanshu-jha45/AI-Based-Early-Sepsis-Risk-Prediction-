# Section 2: Related Work

The clinical machine learning literature for sepsis early warning and time-series risk scoring spans six major thematic areas. Below is a systematic synthesis of existing literature, highlighting landmark contributions, remaining limitations, and the specific advancements evaluated in this work.

---

### 2.1 Early Sepsis Prediction & Static Risk Scores
Landmark early-warning scores—such as the Modified Early Warning Score (MEWS), Systemic Inflammatory Response Syndrome (SIRS) criteria, and Sequential Organ Failure Assessment (SOFA)—rely on rule-based combinations of vital signs and laboratory values. Machine learning scores such as TREWScore (Henry et al., *Science Translational Medicine*, 2015) and InSight (Desautels et al., *BMJ Open*, 2016) demonstrated that gradient-boosted trees and Cox proportional hazard models significantly outperform static clinical rules for predicting septic shock 4 to 12 hours prior to onset. DeepSOFA (Shickel et al., *Scientific Reports*, 2019) extended this by tracking dynamic SOFA score transitions.
* **Limitation**: These models rely heavily on forward-filling or mean imputation and treat observations as static snapshots, rendering them vulnerable to missingness and practice variation across hospitals.

---

### 2.2 Longitudinal & Trajectory Modeling in the ICU
To capture dynamic trend information, researchers introduced temporal trajectory models. Futoma et al. (*ICML*, 2017) developed the Multi-Task Gaussian Process RNN (MGP-RNN) to model continuous physiological trajectories and clinical event times jointly. Moor et al. (*Machine Learning for Healthcare*, 2021) established comprehensive machine learning benchmarks for early sepsis detection using dynamic temporal windows on MIMIC-III and HiRID datasets. Van de Water et al. (*IEEE JBHI*, 2021) applied Temporal Convolutional Networks (TCNs) to capture multi-scale physiological trends.
* **Limitation**: Dynamic trend derivatives (velocity, acceleration) are often conflated with clinical measurement frequency. When sampling rates drop, trajectory representations degrade rapidly.

---

### 2.3 Missingness-Aware & Irregular Time-Series Architectures
Because clinical data are irregularly sampled, specialized deep learning architectures were developed to exploit informative missingness. Che et al. (*Nature Scientific Reports*, 2018) proposed GRU-D, introducing exponential decay mechanisms on hidden states based on elapsed time deltas ($\Delta t$) and binary masks ($M$). Yoon et al. (*ICLR*, 2018) introduced Set Functions for Time Series (SeFT), encoding irregular observations as un-ordered sets using attention. Cao et al. (*NeurIPS*, 2018) developed BRITS, performing bidirectional recurrent imputation.
* **Limitation**: These models treat missingness patterns as domain-specific predictive features. Because clinician ordering habits differ between health systems, missingness-dependent representations induce severe cross-institution transportability failure.

---

### 2.4 Cross-Institution Transportability & Dataset Shift
Dataset shift in clinical machine learning has been rigorously documented. Subbaswamy et al. (*NeurIPS*, 2019; *NEJM*, 2021) formalized causal graph invariance surgery to select shift-stable feature subsets across institutions. Nestor et al. (*AMIA*, 2019) demonstrated that EHR models experience severe performance drops (0.05–0.12 AUROC decay) when transferred across clinical sites due to practice variation. Rocheteau et al. (*JAMIA*, 2021) highlighted temporal confounding in ICU predictive models.
* **Limitation**: Invariance methods often discard informative temporal features, suffering internal accuracy loss, or rely on hypothetical synthetic shifts without evaluating observation-process sensitivity directly.

---

### 2.5 Dynamic Explainability in Clinical Decision Support
Feature attribution methods such as TreeSHAP (Lundberg et al., *Nature Machine Intelligence*, 2020) and integrated gradients have been widely adopted to render complex clinical models interpretable to bedside providers.
* **Limitation**: Post-hoc explainability provides transparency but does not alter underlying representation stability or prevent model overfitting to missingness patterns.

---

### 2.6 Alarm Management & Operating Policy Optimization
High false-alarm rates drive severe clinical alert fatigue. Standard risk thresholding frameworks optimize single static operating points. BioMarkerX incorporates a dual-tier screening and confirmation policy (`VAL_POL_0450`) to contextualize alerts; however, policy optimization operates secondary to underlying representation transportability.

---

## Summary of Novelty & Differentiation Matrix

| Paradigm | Key Benchmark Literature | Main Demonstrated Capability | Remaining Limitation | BioMarkerX Scientific Advancement |
| :--- | :--- | :--- | :--- | :--- |
| **Static Risk Scoring** | Henry et al. (2015), Desautels et al. (2016) | High retrospective discrimination | Sensitive to missingness & forward-fill bias | Causal trajectory normalization ($Z_{i,t}, \frac{dZ}{dt}$) |
| **Trajectory Modeling** | Futoma et al. (2017), Moor et al. (2021) | Captures physiological trend velocity | Conflates trend velocity with sampling rate | Decouples physiological state from observation process |
| **Missingness Architectures** | Che et al. (2018), Yoon et al. (2018) | Exploits informative missingness signals | Overfits to site-specific ordering habits | Robust under controlled dropout and same-physiology mask shifts |
| **Causal Transportability** | Subbaswamy et al. (2019), Nestor et al. (2019) | Identifies shift-stable feature sub-graphs | Sacrifices internal predictive accuracy | Preserves internal accuracy while reducing transport gap by 30.52% |
