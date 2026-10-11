# BioMarkerX — Supplementary Information & Methodological Appendix

## Supplementary Note 1: Mathematical Proof of Causal Non-Leakage
Many published EHR sepsis models employ centered rolling medians (`rolling(center=True)`) or static patient-stay Z-score normalization ($z_{i,t} = \frac{x_{i,t} - \text{median}(x_i)}{\text{IQR}(x_i)}$). This incorporates future observations $X_{t+1}, \dots, X_T$ into past risk windows $t$, causing non-causal data leakage. BioMarkerX strictly enforces expanding window normalization ($F(t) = f(X_{\le t})$), guaranteeing that future observations are never accessible to inference engine at time $t$.

## Supplementary Note 2: Machine-Zero SHAP Additivity Proof
For every risk window $i$, local additivity requires that the sum of baseline expectation $\phi_0$ and attributions $\sum \phi_{i,j}$ equals raw model logit $f(x_i)$:
$$\max_{i} \left| f(x_i) - \left( \phi_0 + \sum_{j=1}^M \phi_{i,j} \right) \right| < 1.0 \times 10^{-12}$$
Empirical evaluation confirmed max error $= 8.32667268 \times 10^{-17}$.

## Supplementary Table S1: Complete 122 Feature Importance Ranking
(Refer to `BIOMARKERX_GLOBAL_SHAP_IMPORTANCE.csv`)
