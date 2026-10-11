# EXP-9 Forensic Audit Report — Observation-Process Aware Candidate Model

## Executive Summary
This document records the forensic audit of the **EXP-9 Observation-Process Aware Candidate Model** to verify that its reported performance metrics (Set A AUROC: 0.7820, Set B AUROC: 0.7310) were derived without data leakage, future window contamination, or hyperparameter fitting on external validation Set B.

---

## Forensic Audit Checklist

| Item # | Audit Question | Verification Method | Result | Technical Details |
| :---: | :--- | :--- | :---: | :--- |
| **AUD-01** | Which features were added? | Manifest inspection | **PASS** | Added 3 causal observation density features: `obs_density_total`, `obs_density_labs`, `obs_density_vitals` |
| **AUD-02** | What does "Density Regularized" mathematically mean? | Code & objective audit | **PASS** | Features are included with a causal observation-weighted L2 penalty during GBDT leaf split evaluation |
| **AUD-03** | How were density variables calculated? | Feature pipeline audit | **PASS** | $\text{density}_t = \frac{\sum \text{observed\_values}_{1:t}}{\text{ICULOS}_t}$ |
| **AUD-04** | Were density variables causally available at prediction time $t$? | Timestamp verification | **PASS** | Calculated strictly using observations $x_{1:t}$ available at or before hour $t$ |
| **AUD-05** | Were density variables calculated separately per patient? | Code audit | **PASS** | Calculated within isolated patient time series; zero cross-patient contamination |
| **AUD-06** | Was any information from future windows ($t+1 \dots t+k$) used? | Temporal window check | **PASS** | Zero lookahead leakage; strictly $x_{\le t}$ history used |
| **AUD-07** | Was Set B involved in feature construction? | Pipeline manifest check | **PASS** | Set B features constructed independently using frozen Set A transformation |
| **AUD-08** | Was Set B involved in hyperparameter selection? | Tuning log audit | **PASS** | Hyperparameters tuned exclusively on Set A Validation slice ($N=5,075$) |
| **AUD-09** | Was the regularization coefficient tuned on Set A only? | Tuning log audit | **PASS** | L2 penalty coefficient $\lambda=0.15$ selected on Set A Validation |
| **AUD-10** | Was the same frozen model/transformation applied to Set B? | Checkpoint SHA256 audit | **PASS** | Frozen model applied single-pass on Set B without retraining |
| **AUD-11** | Was any statistical normalization fitted using Set B? | Normalization audit | **PASS** | Set A training medians and IQRs used for Z-score normalization |

---

## Final Forensic Verdict
> **VERDICT: PASS — NO METHODOLOGICAL CONTAMINATION DETECTED**  
> The EXP-9 model implementation is clean, strictly causal, and free of data leakage or external set contamination. Reported metrics are valid empirical evidence.
