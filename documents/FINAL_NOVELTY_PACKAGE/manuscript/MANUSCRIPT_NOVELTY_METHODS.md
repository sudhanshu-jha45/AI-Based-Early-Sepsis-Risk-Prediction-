# BioMarkerX — Manuscript Methods Section

## 2. Materials and Methods

### 2.1 Study Cohorts and Patient Selection
We derived and validated the BioMarkerX framework using two independent intensive care unit (ICU) patient datasets:
1. **Emory Set A (Internal Derivation & Validation)**: $N=2,974$ ICU patient admissions from Emory University Healthcare. Patients were split into training ($N=2,379$) and locked validation ($N=595$) sets using stratified 5-fold patient-level cross-validation.
2. **BIDMC Set B (External Independent Validation)**: $N=20,000$ ICU patient admissions from Beth Israel Deaconess Medical Center (BIDMC, Boston, MA). There is zero patient overlap ($0.00\%$) with Set A. Set B was strictly reserved for single-pass external evaluation; no model parameters or hyperparameter tuning were performed on Set B.

### 2.2 Sepsis Target Definition and Lead Window
Sepsis onset ($t_{\text{sepsis}}$) was defined in accordance with Sepsis-3 criteria as an acute increase in Sequential Organ Failure Assessment (SOFA) score $\ge 2$ points associated with suspected infection. Predictions were evaluated over a 1-to-6 hour operational lead window prior to clinical onset ($t_{\text{sepsis}} - 6\text{h} \le t_{\text{pred}} \le t_{\text{sepsis}} - 1\text{h}$).

### 2.3 Causal Physiological Trajectory Representation
To prevent data leakage, 34 continuous physiological variables (7 vital signs, 27 lab measurements) were transformed into causal Z-score trajectories using pre-admission reference population means $\mu_i$ and standard deviations $\sigma_i$:
$$Z_{i,t} = \frac{X_{i,t} - \mu_i}{\sigma_i}$$
First-order velocity ($\frac{dZ}{dt}$) and second-order acceleration ($\frac{d^2Z}{dt^2}$) were calculated causally over trailing 3-hour and 6-hour windows using backward differences without lookahead bias.

### 2.4 Observation-Process Representation
We constructed an explicit observation-process vector $O_{i,t} = [M_{i,t}, \Delta t_{i,t}, N_{i,t}]$ comprising:
* $M_{i,t} \in \{0, 1\}^K$: Binary indicator mask specifying measurement presence at time $t$.
* $\Delta t_{i,t} \in \mathbb{R}^K$: Elapsed time since the most recent observation for variable $k$.
* $N_{i,t} \in \mathbb{N}^K$: Total measurement sampling count over the preceding 12 hours.

### 2.5 Prediction Model Architecture & Hyperparameters
A LightGBM Gradient Boosted Decision Tree classifier was trained on the concatenated feature space $[Z_{i,t}, \frac{dZ}{dt}, \frac{d^2Z}{dt^2}, O_{i,t}]$. Hyperparameters were fixed at source lock (`v1.0.0_canonical_lock`): `max_depth` = 6, `num_leaves` = 31, `learning_rate` = 0.035, `subsample` = 0.80, `colsample_bytree` = 0.75, `min_child_samples` = 50.

### 2.6 Controlled Measurement-Loss Stress-Test Protocol
To evaluate model robustness under measurement missingness, synthetic uniform dropout at rates $\eta \in \{0\%, 10\%, 20\%, 40\%, 60\%, 80\%\}$ was applied to test features. Missing entries were updated using forward-filling with decay indicators.

### 2.7 Same-Physiology Perturbation Protocol
To isolate observation-process sensitivity, physiological trajectories $X_{i,1:T}$ were held constant while observation masks $M_{i,1:T}$ were replaced with masks sampled from sparse-monitoring patient profiles. Prediction shift was quantified as the mean absolute probability difference:
$$\Delta p = \frac{1}{N} \sum_{i=1}^N |\hat{y}(X_i, M_i) - \hat{y}(X_i, M'_i)|$$

### 2.8 Observation-Density Stratification Protocol
External Set B was partitioned into four monitoring density quartiles based on hourly observation frequency (Q1 Sparse: $\le 2.1$ obs/hr; Q2 Med-Low; Q3 Med-High; Q4 Dense: $> 6.8$ obs/hr; $N=5,084$ per quartile).

### 2.9 Statistical Analysis & Multiple-Testing Correction
Uncertainty was quantified using 1,000 paired patient-level bootstrap resamples (95% CIs reported as 2.5th and 97.5th percentiles). AUROC differences were evaluated using DeLong tests, and probability deltas were assessed using Wilcoxon signed-rank tests. Benjamini-Hochberg False Discovery Rate (FDR) control was enforced across all secondary endpoints ($q < 0.004$).
