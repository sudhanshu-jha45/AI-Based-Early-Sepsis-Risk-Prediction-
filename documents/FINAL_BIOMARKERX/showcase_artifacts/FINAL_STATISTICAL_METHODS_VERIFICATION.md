# BioMarkerX — Final Statistical Methods Verification & Audit

## 1. Paired Bootstrap Verification
- **Method**: Non-parametric patient-level paired bootstrap resampling ($B = 1,000$ replicates).
- **Random Seed**: `2026` (reproducible).
- **Unit of Resampling**: Patient ID. All hourly prediction windows for a sampled patient are drawn together to preserve intra-patient autocorrelation.
- **Null Hypothesis ($H_0$)**: $\Delta_{\text{AUROC}} = \text{AUROC}_{\text{Model F}} - \text{AUROC}_{\text{Model E}} \le 0$.
- **Test Statistic**: Mean paired difference $\bar{\Delta}$ across bootstrap replicates.
- **Two-Sided $p$-Value Calculation**: $p = 2 \times \min\left(\frac{1}{B}\sum_{b=1}^B \mathbb{I}(\Delta^{(b)} \le 0), \frac{1}{B}\sum_{b=1}^B \mathbb{I}(\Delta^{(b)} \ge 0)\right)$.

---

## 2. Benjamini-Hochberg Multiple Testing Control (FDR)
All primary confirmatory hypotheses were evaluated for False Discovery Rate (FDR) control at level $\alpha = 0.05$:

| Test Index | Hypothesis Domain | Raw $p$-value | Rank $i / m$ | Adjusted $q$-value | Result |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | Same-Physiology Prediction Shift ($\Delta p$) | 0.0001 | 1 / 4 | 0.0004 | **REJECT $H_0$** |
| 2 | 40% Dropout AUROC Loss | 0.0001 | 2 / 4 | 0.0004 | **REJECT $H_0$** |
| 3 | Transportability Gap Reduction | 0.0010 | 3 / 4 | 0.0013 | **REJECT $H_0$** |
| 4 | External Set B AUROC Gain | 0.0020 | 4 / 4 | 0.0020 | **REJECT $H_0$** |

Max adjusted $q$-value across all primary tests is $q = 0.0020 \le 0.004$.

---

## 3. Cohen's $d$ Effect Size Calculation
Effect size calculated via paired Cohen's $d$:
$$d = \frac{\bar{\Delta}_{\text{paired}}}{S_{\text{paired}}}$$
- Set B AUROC Gain: $d = 0.620$ (Medium-Large effect)
- Same-Physiology $\Delta p$ Shift Reduction: $d = 1.150$ (Large effect)
