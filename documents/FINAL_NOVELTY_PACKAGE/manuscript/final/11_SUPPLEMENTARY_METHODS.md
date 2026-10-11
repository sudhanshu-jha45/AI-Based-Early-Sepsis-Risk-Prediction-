# Supplementary Material: Section S1 — Supplementary Methods

## S1.1 Mathematical Formulation of Causal Trajectory Derivatives
For a patient time series $X_{i,t}$, causal Z-score normalization is computed using baseline population reference statistics $\mu_i, \sigma_i$:
$$Z_{i,t} = \frac{X_{i,t} - \mu_i}{\sigma_i}$$
Backward multi-scale temporal derivatives are formulated without lookahead as:
$$\text{Vel}_{3\text{h}}(Z_{i,t}) = \frac{Z_{i,t} - Z_{i,t-3}}{3}$$
$$\text{Acc}_{6\text{h}}(Z_{i,t}) = \frac{\text{Vel}_{3\text{h}}(Z_{i,t}) - \text{Vel}_{3\text{h}}(Z_{i,t-3})}{3}$$

---

## S1.2 LightGBM Master Hyperparameter Specification (`v1.0.0_canonical_lock`)

| Hyperparameter | Value | Description |
| :--- | :--- | :--- |
| `boosting_type` | `gbdt` | Traditional Gradient Boosted Decision Tree |
| `max_depth` | 6 | Maximum tree depth constraint |
| `num_leaves` | 31 | Maximum leaves per tree |
| `learning_rate` | 0.035 | Shrinkage learning rate |
| `subsample` | 0.80 | Row subsampling fraction per tree |
| `colsample_bytree` | 0.75 | Feature subsampling fraction per tree |
| `min_child_samples` | 50 | Minimum data instances in a leaf |
| `objective` | `binary` | Binary log-loss classification |
| `metric` | `auc` | Area under ROC curve optimization |

---

## S1.3 Dual-Tier Policy Threshold Specification (`VAL_POL_0450`)
* **Screening Tier**: Operating threshold $\tau_{\text{screen}} = 0.015$ ($1.5\%$ probability threshold for background risk monitoring).
* **Confirmation Tier**: Operating threshold $\tau_{\text{confirm}} = 0.300$ ($30.0\%$ probability threshold) requiring:
  1. *Persistence Gate*: Risk score $\ge 0.300$ across $N=3$ consecutive hourly cycles.
  2. *Physiological Gate*: `MAP <= 75 mmHg` OR `MAP_delta3 <= -3.0 mmHg`.
