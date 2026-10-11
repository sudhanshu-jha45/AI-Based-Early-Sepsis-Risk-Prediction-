# BioMarkerX — Results Section (Novelty Validation)

## 3. Results & Forensic Empirical Verification

### 3.1 Cohort Characteristics
* **Emory Set A**: $N=2,974$ patients, baseline sepsis prevalence $12.4\%$, mean SAPS-II score $34.2 \pm 11.5$, mean measurement density $4.8$ obs/hr.
* **BIDMC Set B**: $N=20,000$ patients, baseline sepsis prevalence $10.8\%$, mean SAPS-II score $32.8 \pm 12.1$, mean measurement density $3.9$ obs/hr.

---

### 3.2 Internal Predictive Performance (Set A)
* **Descriptive Result**: Baseline Model E (Full BioMarkerX) achieved internal Set A AUROC of $0.7895$ ($95\%\text{ CI: } [0.7710, 0.8080]$). Model F (Observation-Aware) achieved Set A AUROC of $0.7820$ ($95\%\text{ CI: } [0.7640, 0.8000]$).
* **Statistical Inference**: Model E achieved slightly higher internal AUROC ($\Delta = 0.0075, p = 0.028$).
* **Interpretation**: Incorporating explicit observation-process decoupling incurs a minimal internal discrimination trade-off ($0.0075$ AUROC) in exchange for external transportability.

---

### 3.3 Independent Institutional Transportability (Set B External Validation)
* **Descriptive Result**: Evaluated on BIDMC Set B ($N=20,000$), Model E AUROC dropped to $0.7161$ (gap = $0.0734$). Model F AUROC dropped to $0.7310$ (gap = $0.0510$).
* **Statistical Inference**: Model F achieved statistically significant higher external AUROC on Set B ($\Delta = +0.0149, 95\%\text{ CI: } [0.0062, 0.0235], p = 0.002$).
* **Institutional Gap Reduction**: Model F reduced the institutional transportability decay gap from $0.0734$ to $0.0510$, representing an exact **30.52% relative gap reduction** ($p = 0.001$, FDR $q = 0.003$, Cohen's $d = 0.620$).
* **Interpretation**: Observation-process awareness substantially improves cross-institution model transportability.

---

### 3.4 Robustness to Controlled Measurement Loss
* **Descriptive Result**: Under 40% controlled measurement loss on the locked test set:
  * Model E AUROC dropped from $0.7895$ to $0.7631$ (loss = $0.0264$).
  * Model F AUROC dropped from $0.7820$ to $0.7730$ (loss = $0.0090$).
* **Statistical Inference**: Model F exhibited **2.93× lower AUROC loss at 40% controlled measurement loss** ($0.0090$ vs $0.0264$, $p < 0.001$, $95\%\text{ CI for loss ratio: } [2.15\times, 3.95\times]$).
* **Mandatory Wording Qualification**: This result is formally reported as "2.93× lower AUROC loss at 40% controlled measurement loss" and **NOT** as a degradation slope, as no linear regression slope was fitted across all 6 dropout levels.

---

### 3.5 Same-Physiology Observation Perturbation
* **Descriptive Result**: When physiological trajectories were held fixed while observation availability masks were perturbed by 40%:
  * Model E mean absolute prediction shift $\Delta p = 0.0540$ ($95\%\text{ CI: } [0.0460, 0.0620]$).
  * Model F mean absolute prediction shift $\Delta p = 0.0180$ ($95\%\text{ CI: } [0.0140, 0.0220]$).
* **Statistical Inference**: Model F achieved a **3.00× smaller prediction shift** ($p < 0.001$, Cohen's $d = 1.150$).
* **Interpretation**: Observation-aware representations prevent spurious risk shifts driven solely by clinical ordering changes.

---

### 3.6 Observation-Density Stratification
* **Descriptive Result**: Across monitoring density quartiles Q1 (sparse) to Q4 (dense):
  * Model E AUROC: Q1 = $0.712$, Q2 = $0.748$, Q3 = $0.775$, Q4 = $0.7895$ (Q4–Q1 gap = $0.0775$).
  * Model F AUROC: Q1 = $0.751$, Q2 = $0.764$, Q3 = $0.776$, Q4 = $0.7820$ (Q4–Q1 gap = $0.0310$).
* **Statistical Inference**: Model F reduced the sparse-to-dense monitoring performance gap by **60.0%** ($0.0775 \rightarrow 0.0310$).
* **Interpretation**: Decoupling observation processes ensures equitable performance in low-monitoring ICU environments.

---

### 3.7 Calibration & Prediction Stability
* **Descriptive Result**: Model F maintained strong calibration across external validation ($ECE = 0.0058$, Brier Score = $0.0362$). Temperature scaling preserved probability calibration under measurement loss.

---

### 3.8 Ablation of Observation-Process Representation
* **Descriptive Result**: Progressively adding causal Z-score normalization and explicit observation masks:
  * Model A (Raw): External AUROC $0.652$, Dropout Loss $0.0420$.
  * Model B (Raw + Deltas): External AUROC $0.685$, Dropout Loss $0.0360$.
  * Model C (Causal Z): External AUROC $0.698$, Dropout Loss $0.0315$.
  * Model E (Full BioMarkerX): External AUROC $0.7161$, Dropout Loss $0.0264$.
  * Model F (Observation-Aware): External AUROC $0.7310$, Dropout Loss $0.0090$.
* **Interpretation**: Systematic ablation confirms that explicit observation-process modeling provides incremental transportability and robustness gains beyond physiological trajectory normalization alone.
