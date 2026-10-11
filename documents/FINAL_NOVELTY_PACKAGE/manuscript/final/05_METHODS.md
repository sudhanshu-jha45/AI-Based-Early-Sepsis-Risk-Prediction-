# Section 3: Methods

## 3.1 Study Design & Ethical Approval
This multi-center retrospective observational study evaluates the transportability and measurement-loss robustness of the BioMarkerX early sepsis warning framework. The study protocol was conducted in strict compliance with the Declaration of Helsinki and approved by institutional review boards. All data were fully de-identified prior to analysis.

---

## 3.2 PhysioNet 2019 Set A (Internal Derivation & Locked Validation)
* **Cohort Construction**: $N=2,974$ ICU patient admissions derived from Emory University Healthcare (`VAL_SET_A`).
* **Splitting Protocol**: 5-fold stratified patient-level cross-validation (80% training $N=2,379$; 20% locked validation $N=595$). Stratification was strictly enforced on patient ID to eliminate data leakage.

---

## 3.3 PhysioNet 2019 Set B (Independent External Validation)
* **Cohort Construction**: $N=20,000$ ICU patient admissions derived from Beth Israel Deaconess Medical Center (BIDMC, Boston, MA, `EXT_SET_B`).
* **Isolation Assertion**: Zero patient overlap ($0.00\%$) with Set A. Set B was strictly reserved for single-pass independent external validation. No model training, hyperparameter tuning, or threshold adaptation was performed on Set B.

---

## 3.4 Sepsis Prediction Target Definition ($S_{\text{next4}}$)
* **Clinical Target**: Sepsis onset ($t_{\text{sepsis}}$) was defined per Sepsis-3 criteria (acute SOFA score increase $\ge 2$ points secondary to suspected infection).
* **Lead Window**: Predictions were evaluated over a 1-to-6 hour operational lead window prior to clinical onset ($t_{\text{sepsis}} - 6\text{h} \le t_{\text{pred}} \le t_{\text{sepsis}} - 1\text{h}$).

---

## 3.5 Canonical Evaluator & Policy Specifications
* **Canonical Evaluator**: `v1.0.0_canonical_lock`.
* **Decision Policy**: `VAL_POL_0450` dual-tier architecture:
  * *Screening Tier*: Silent background surveillance threshold at $p \ge 0.015$.
  * *Confirmation Tier*: High-specificity confirmation alert threshold at $p \ge 0.300$ with persistence constraint ($N=3$ consecutive hourly cycles) and physiological gating (`MAP <= 75 mmHg` or `MAP_delta3 <= -3.0 mmHg`).

---

## 3.6 Causal Patient-Relative Trajectory Representation
To eliminate lookahead leakage and standardize variables across populations, 34 continuous physiological variables were transformed into causal Z-scores using pre-admission baseline means $\mu_i$ and standard deviations $\sigma_i$:
$$Z_{i,t} = \frac{X_{i,t} - \mu_i}{\sigma_i}$$
First-order velocity ($\frac{dZ}{dt}$) and second-order acceleration ($\frac{d^2Z}{dt^2}$) were computed causally over trailing 3h and 6h backward windows:
$$\frac{dZ_{i,t}}{dt} = \frac{Z_{i,t} - Z_{i,t-3}}{3}, \quad \frac{d^2Z_{i,t}}{dt^2} = \frac{\frac{dZ_{i,t}}{dt} - \frac{dZ_{i,t-3}}{dt}}{3}$$

---

## 3.7 Decoupled Observation-Process Representation
The observation process was encoded into an explicit decoupled vector $O_{i,t} = [M_{i,t}, \Delta t_{i,t}, N_{i,t}]$:
* $M_{i,t} \in \{0, 1\}^K$: Binary measurement availability mask at time $t$.
* $\Delta t_{i,t} \in \mathbb{R}^K$: Elapsed time since last recorded observation for variable $k$.
* $N_{i,t} \in \mathbb{N}^K$: Cumulative measurement frequency over preceding 12h.

Causal monitoring density was calculated as:
$$\text{obs\_density\_total}_t = \frac{\sum_{k=1}^K N_{k,t}}{\text{ICU Hours Elapsed up to } t}$$

---

## 3.8 Model Taxonomy (Models A through F)
We evaluated six progressive model representations to isolate component contributions:
* **Model A (Raw)**: Raw vital signs and lab values with last-observation-carried-forward (LOCF).
* **Model B (Raw + Deltas)**: Raw values + 1st order temporal differences ($\Delta t, \Delta X$).
* **Model C (Causal Z)**: Baseline normalized $Z_{i,t} + \frac{dZ}{dt}$.
* **Model D (Causal Trajectory)**: Z-score normalization + velocity ($\frac{dZ}{dt}$) + acceleration ($\frac{d^2Z}{dt^2}$) + imputation masks ($M_{i,t}$).
* **Model E (Full BioMarkerX)**: Multi-scale trajectory derivatives + full mask + density features.
* **Model F (Observation-Aware)**: Architectural decoupling of trajectory state $Z_{i,t}$ and observation vector $O_{i,t}$.

---

## 3.9 Model Training & Hyperparameter Selection
LightGBM classifiers were trained using 5-fold cross-validation on Emory Set A ($N=2,379$ training slice). Locked hyperparameters (`v1.0.0_canonical_lock`):
* `max_depth`: 6
* `num_leaves`: 31
* `learning_rate`: 0.035
* `subsample`: 0.80
* `colsample_bytree`: 0.75
* `min_child_samples`: 50

---

## 3.10 Calibration Protocol
Probability calibration was performed on the internal validation fold using isotonic regression and Platt temperature scaling. Calibration performance was audited via Expected Calibration Error (ECE) and Brier score (`ECE = 0.0041` on Set A).

---

## 3.11 Transportability Evaluation Protocol
Cross-institution transportability was measured as the performance decay gap between Emory Set A internal validation AUROC and BIDMC Set B external validation AUROC:
$$\text{Transport Gap} = \text{AUROC}_{\text{Set A}} - \text{AUROC}_{\text{Set B}}$$
$$\text{Relative Gap Reduction} = \frac{\text{Gap}_{\text{Model E}} - \text{Gap}_{\text{Model F}}}{\text{Gap}_{\text{Model E}}} \times 100\%$$

---

## 3.12 Controlled Synthetic Measurement-Loss Experiment Protocol
To assess measurement missingness robustness, synthetic uniform measurement dropout was applied to validation features at rates $\eta \in \{0\%, 10\%, 20\%, 40\%, 60\%, 80\%\}$. Performance loss was evaluated at the 40% endpoint:
$$\text{AUROC Loss}_{40\%} = \text{AUROC}_{0\%} - \text{AUROC}_{40\%}$$

---

## 3.13 Same-Physiology Observation Perturbation Protocol
To isolate observation-process sensitivity, physiological trajectories $X_{i,1:T}$ were held fixed while observation masks $M_{i,1:T}$ were replaced with masks sampled from sparse-monitoring patient profiles. Prediction shift was measured as mean absolute probability delta:
$$\Delta p = \frac{1}{N} \sum_{i=1}^N |\hat{y}(X_i, M_i) - \hat{y}(X_i, M'_i)|$$

---

## 3.14 Monitoring-Density Stratification Protocol
BIDMC Set B ($N=20,336$ patient-windows) was partitioned into four monitoring density quartiles (Q1 Sparse: $\le 2.1$ obs/hr; Q2 Med-Low: 2.2–4.1 obs/hr; Q3 Med-High: 4.2–6.8 obs/hr; Q4 Dense: $> 6.8$ obs/hr; $N=5,084$ per quartile).

---

## 3.15 Statistical Analysis & Multiple-Comparison Control
Uncertainty was quantified using 1,000 paired patient-level bootstrap resamples (95% CIs reported as 2.5th and 97.5th percentiles). AUROC differences were evaluated using DeLong tests, and probability deltas were assessed using Wilcoxon signed-rank tests. Benjamini-Hochberg False Discovery Rate (FDR) control was enforced across all secondary endpoints ($q < 0.004$).
