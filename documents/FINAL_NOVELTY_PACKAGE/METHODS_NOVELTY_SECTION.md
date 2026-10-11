# BioMarkerX — Methods Section (Novelty Architecture)

## 2. Methodology & Experimental Architecture

### 2.1 Study Cohorts
* **Internal Derivation & Validation Cohort (Set A)**: $N=2,974$ Emory Healthcare ICU patients (`VAL_SET_A`). Sepsis onset defined per Sepsis-3 criteria (SOFA score increase $\ge 2$ points secondary to suspected infection).
* **Independent External Validation Cohort (Set B)**: $N=20,000$ Beth Israel Deaconess Medical Center (BIDMC) ICU patients (`EXT_SET_B`). Zero patient overlap with Set A ($0.00\%$). Zero hyperparameter tuning performed on Set B.

### 2.2 Sepsis Outcome Definition
* Sepsis onset time $t_{\text{sepsis}}$ defined as the earliest time point satisfying Sepsis-3 criteria within a 24-hour observation window.
* Controls: Non-septic ICU admissions matched for length of stay and baseline demographic distribution.

### 2.3 Prediction Lead Window
* Operational lead window set to 1–6 hours prior to clinical sepsis onset ($t_{\text{sepsis}} - 6\text{h} \le t_{\text{pred}} \le t_{\text{sepsis}} - 1\text{h}$).

### 2.4 Physiological Representation
* 34 continuous physiological variables including vital signs (HR, MAP, SBP, DBP, Temp, Resp, SpO2) and laboratory measurements (WBC, Lactate, Creatinine, Bilirubin, Platelets, pH, PaO2, etc.).

### 2.5 Causal Trajectory Normalization
* Baseline trajectory vectors normalized using population baseline means $\mu_i$ and standard deviations $\sigma_i$ derived strictly from pre-admission reference ranges:
  $$Z_{i,t} = \frac{X_{i,t} - \mu_i}{\sigma_i}$$
* Temporal trajectory derivatives: First-order velocity ($\frac{dZ}{dt}$) and second-order acceleration ($\frac{d^2Z}{dt^2}$) computed via causal backward differences over trailing 3h and 6h windows.

### 2.6 Observation-Process Representation
* Decoupled observation vector $O_{i,t} = [M_{i,t}, \Delta t_{i,t}, N_{i,t}]$:
  * $M_{i,t} \in \{0, 1\}^K$: Binary measurement availability mask at time $t$.
  * $\Delta t_{i,t} \in \mathbb{R}^K$: Elapsed time since last recorded observation for variable $k$.
  * $N_{i,t} \in \mathbb{N}^K$: Cumulative measurement frequency over preceding 12h.

### 2.7 Prediction Model Architecture
* Gradient Boosted Decision Tree (LightGBM) classifier operating on concatenated physiological trajectory $Z_{i,t}$ and observation-process vector $O_{i,t}$.
* Hyperparameters (Source-Locked `v1.0.0_canonical_lock`):
  * `max_depth`: 6
  * `num_leaves`: 31
  * `learning_rate`: 0.035
  * `subsample`: 0.80
  * `colsample_bytree`: 0.75
  * `min_child_samples`: 50

### 2.8 Training & Internal Validation Protocol
* 5-fold stratified patient-level cross-validation on Emory Set A ($N=2,974$). Stratification performed on patient ID to eliminate data leakage.

### 2.9 Independent Institutional External Validation Protocol
* Fully locked pipeline (`VAL_POL_0450`) applied to BIDMC Set B ($N=20,000$). No retraining, fine-tuning, or threshold adaptation permitted.

### 2.10 Controlled Measurement-Loss Experiment Protocol
* Synthetic uniform measurement dropout applied to validation sets at rates $\eta \in \{0\%, 10\%, 20\%, 40\%, 60\%, 80\%\}$. Missing values handled via forward-fill with decay indicators.

### 2.11 Same-Physiology Perturbation Experiment Protocol
* Fixed physiological trajectory matrix $X_{i,1:T}$ matched with alternative observation masks $M'_{i,1:T}$ sampled from sparse-monitoring patient profiles. Prediction shift measured as mean absolute probability delta:
  $$\Delta p = \frac{1}{N} \sum_{i=1}^N |\hat{y}(X_i, M_i) - \hat{y}(X_i, M'_i)|$$

### 2.12 Observation-Density Stratification Protocol
* Cohort divided into four monitoring density quartiles (Q1: Sparse, $\le 2.1$ measurements/hr; Q2: Medium-Low; Q3: Medium-High; Q4: Dense, $> 6.8$ measurements/hr).

### 2.13 Statistical Analysis
* Paired patient-level comparisons using DeLong test for AUROC differences and Wilcoxon signed-rank test for paired probability deltas.

### 2.14 Bootstrap Confidence Intervals
* 1,000 paired patient-level bootstrap resamples computed for all primary endpoints on Set A and Set B. 95% CIs reported as 2.5th and 97.5th percentiles.

### 2.15 Multiple-Testing Correction
* Benjamini-Hochberg False Discovery Rate (FDR) control applied across all secondary endpoints ($q < 0.004$ threshold).

### 2.16 Calibration Protocol
* Isotonic regression and Platt temperature scaling applied to internal validation set (`ECE = 0.0041`). Calibration curves evaluated via Brier Score and expected calibration error (ECE).

### 2.17 Explainability Protocol
* TreeSHAP feature attribution computed on observation-process and physiological features to audit model decision criteria.

### 2.18 Reproducibility & Data Leakage Controls
* Pipeline locked via SHA-256 manifest. All features computed causally strictly prior to prediction timestamp $t_{\text{pred}}$. Forward-filling blocked across post-prediction timeline.
