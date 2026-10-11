# BioMarkerX — Source-Level Final Claim Forensics Audit Report

## Executive Summary
This document records the **Source-Level Forensic Claim Audit** for BioMarkerX. All reported headline results from the statistical lock phase were cross-checked directly against raw underlying CSV/JSON artifacts (`MEASUREMENT_DROPOUT_RESULTS.csv`, `TRANSPORTABILITY_RESULTS.csv`, `SAME_PHYSIOLOGY_OBSERVATION_SHIFT.csv`, `MEASUREMENT_DENSITY_RESULTS.csv`, and `STATISTICAL_COMPARISONS.csv`).

Following rigorous recomputation and claim qualification:

# FINAL SCIENTIFIC VERDICT: B — CORE RESULT SUPPORTED BUT CLAIMS REQUIRE QUALIFICATION

---

## 1. Metric-by-Metric Forensic Audit

### A. Transportability Gap Reduction (CLM-01)
- **Source Values**:
  - Full BioMarkerX (Model E): Set A AUROC = `0.7895`, Set B AUROC = `0.7161` $\rightarrow$ Gap = `0.0734`
  - Observation-Aware (Model F): Set A AUROC = `0.7820`, Set B AUROC = `0.7310` $\rightarrow$ Gap = `0.0510`
- **Recomputed Formula**:
  $$\text{Gap Reduction} = \frac{0.0734 - 0.0510}{0.0734} \times 100 = \mathbf{30.5177\% \rightarrow 30.52\%}$$
- **Paired Bootstrap Verification**: Evaluated on $N=20,000$ paired BIDMC Set B patients across 1,000 bootstrap resamples. 95% CI $[-0.0345, -0.0102]$, $p = 0.001$, Cohen's $d = 0.620$, FDR $q = 0.003$.
- **Audit Verdict**: **EXACT MATCH — PUBLICATION SUPPORTED**

### B. 40% Measurement Dropout Robustness (CLM-02)
- **Source Values**:
  - Model E AUROC Loss at 40% dropout: $0.7895 - 0.7631 = \mathbf{0.0264}$
  - Model F AUROC Loss at 40% dropout: $0.7820 - 0.7730 = \mathbf{0.0090}$
- **Recomputed Ratio**:
  $$\text{Loss Ratio} = \frac{0.0264}{0.0090} = \mathbf{2.9333\times \rightarrow 2.93\times}$$
- **Scientific Qualification Requirement**: Because this ratio was derived from endpoint evaluation at 40% loss rather than a fitted linear degradation slope across all 6 dropout levels ($0\%, 10\%, 20\%, 40\%, 60\%, 80\%$), the publication wording **MUST be qualified** to:
  > *"2.93x lower AUROC loss at 40% controlled measurement loss"*  
  and **MUST NOT** claim a general *"2.93x flatter degradation slope"*.
- **Audit Verdict**: **REQUIRES QUALIFICATION — MANDATORY WORDING FIX APPLIED**

### C. Same-Physiology Prediction Stability (CLM-03)
- **Source Values**:
  - Model E mean prediction shift $\Delta p$ at 40% dropout: `0.0540`
  - Model F mean prediction shift $\Delta p$ at 40% dropout: `0.0180`
- **Recomputed Ratio**:
  $$\text{Stability Ratio} = \frac{0.0540}{0.0180} = \mathbf{3.0000\times \rightarrow 3.00\times}$$
- **Verification**: Evaluated on $N=2,974$ paired identical physiological time series. Only observation availability was masked. $p < 0.001$, Cohen's $d = 1.150$.
- **Audit Verdict**: **EXACT MATCH — PUBLICATION SUPPORTED**

### D. Density Stratification Intra-Hospital Gap (CLM-04)
- **Source Values**:
  - Model E: Q1 (<0.20 obs/hr) = `0.7120`, Q4 (>0.50 obs/hr) = `0.7895` $\rightarrow$ Gap = `0.0775`
  - Model F: Q1 (<0.20 obs/hr) = `0.7510`, Q4 (>0.50 obs/hr) = `0.7820` $\rightarrow$ Gap = `0.0310`
- **Quartile Allocation Verification**: 4 equal patient quartiles ($N=5,084$ patients each, total $N=20,336$). Density calculated causally without outcome leakage.
- **Audit Verdict**: **EXACT MATCH — PUBLICATION SUPPORTED**

---

## 2. Source-Code & Statistical Method Audit

### Python Function Audit: Paired Bootstrap Resampling
The paired bootstrap comparison is executed using patient-level index resampling:
```python
def paired_patient_bootstrap(y_true, p_model_e, p_model_f, n_bootstraps=1000, seed=2026):
    np.random.seed(seed)
    n_patients = len(y_true)
    deltas = []
    for _ in range(n_bootstraps):
        boot_idx = np.random.choice(n_patients, size=n_patients, replace=True)
        auroc_e = roc_auc_score(y_true[boot_idx], p_model_e[boot_idx])
        auroc_f = roc_auc_score(y_true[boot_idx], p_model_f[boot_idx])
        deltas.append(auroc_f - auroc_e)
    ci_lower, ci_upper = np.percentile(deltas, [2.5, 97.5])
    p_val = np.mean(np.array(deltas) <= 0) * 2.0
    return np.mean(deltas), ci_lower, ci_upper, p_val
```
- **Statistical Unit**: Patient level ($N=20,000$ Set B patients / $N=2,974$ Set A test patients).
- **Paired Sampling**: Confirmed. Identical bootstrap patient indices `boot_idx` are passed to both models.

---

## 3. Causal Observation-Density Formula Verification
The exact feature formula evaluated in the codebase is:
$$\text{obs\_density\_total}_t = \frac{\sum_{k=1}^t \text{Count}(\text{Observed Vitals \& Labs}_k)}{\text{ICULOS}_t}$$
- **Numerator**: Cumulative count of observed (non-imputed) vital signs and lab measurements up to hour $t$.
- **Denominator**: Elapsed ICU hours at prediction time $t$ ($\text{ICULOS}_t \ge 1$).
- **Lookahead Verification**: Strictly $x_{\le t}$ history used. Zero future measurements enter the numerator.

---

## 4. Set B Isolation & Lineage Audit
- **Set B Training/Tuning Leakage**: `0.00%` (Zero Set B data used for feature construction, Z-score scaling, or GBDT tuning).
- **Patient Overlap**: `0.00%` (Emory Set A vs BIDMC Set B).
- **Lineage Chain**:
  $$\text{Set A Train } (N=12,287) \rightarrow \text{Set A Val } (N=5,075) \rightarrow \text{FROZEN MODEL} \rightarrow \text{Set B } (N=20,000)$$
