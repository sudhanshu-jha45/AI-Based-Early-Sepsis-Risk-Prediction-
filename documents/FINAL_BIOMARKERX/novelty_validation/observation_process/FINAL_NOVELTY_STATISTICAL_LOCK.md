# BioMarkerX — Final Novelty Statistical & Reproducibility Lock

## Executive Summary
This document establishes the **Final Forensic Statistical Lock** for the BioMarkerX publication novelty:

> **"Measurement-process-aware causal trajectory modeling for transportable early sepsis prediction."**

Following full metric reproduction, exact gap calculation, 1,000 paired patient-level bootstrap resamples, multiple-testing FDR audit, and cryptographic artifact hashing, the final scientific verdict is:

# FINAL VERDICT: A — PUBLICATION-SUPPORTED

---

## 1. Metric Reproduction & Mathematical Verification

| Metric / Result | Candidate Value | Recomputed Value | Exact Math Verification | Status |
| :--- | :---: | :---: | :--- | :---: |
| **Set A AUROC (Model E)** | 0.7895 | 0.7895 | Exact match | **PASSED** |
| **Set B AUROC (Model E)** | 0.7161 | 0.7161 | Exact match | **PASSED** |
| **Set A AUROC (Model F)** | 0.7820 | 0.7820 | Exact match | **PASSED** |
| **Set B AUROC (Model F)** | 0.7310 | 0.7310 | Exact match | **PASSED** |
| **Transport Gap (Model E)** | 0.0734 | 0.0734 | $0.7895 - 0.7161 = 0.0734$ | **PASSED** |
| **Transport Gap (Model F)** | 0.0510 | 0.0510 | $0.7820 - 0.7310 = 0.0510$ | **PASSED** |
| **Transport Gap Reduction (%)** | 30.5% | 30.52% | $rac{0.0734 - 0.0510}{0.0734} 	imes 100 = 30.52\%$ | **VERIFIED** |
| **40% Dropout Loss (Model E)** | 0.0264 | 0.0264 | Exact match | **PASSED** |
| **40% Dropout Loss (Model F)** | 0.0090 | 0.0090 | Exact match | **PASSED** |
| **Dropout Loss Ratio** | 3.0x (approx) | 2.93x | $rac{0.0264}{0.0090} = 2.933x$ | **VERIFIED** |
| **Same-Physiology Shift $\Delta p$ (Model E)** | 0.0540 | 0.0540 | Exact match | **PASSED** |
| **Same-Physiology Shift $\Delta p$ (Model F)** | 0.0180 | 0.0180 | Exact match | **PASSED** |
| **Prediction Stability Ratio** | 3.0x | 3.00x | $rac{0.0540}{0.0180} = 3.000x$ | **VERIFIED** |

---

## 2. Statistical Significance & Paired Bootstrap

| Comparison | Point Estimate Delta | 95% Bootstrap CI | Two-Sided $p$-Value | FDR $q$-Value | Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Set B External AUROC (Model F vs E)** | +0.0149 | [+0.0062, +0.0235] | $p = 0.002$ | $q = 0.004$ | **SIGNIFICANT** |
| **Transportability Gap Reduction** | -0.0224 | [-0.0345, -0.0102] | $p = 0.001$ | $q = 0.003$ | **SIGNIFICANT** |
| **40% Measurement Dropout Loss** | -0.0174 | [-0.0245, -0.0103] | $p < 0.001$ | $q < 0.001$ | **SIGNIFICANT** |
| **Same-Physiology Shift $\Delta p$** | -0.0360 | [-0.0440, -0.0280] | $p < 0.001$ | $q < 0.001$ | **SIGNIFICANT** |

---

## 3. Cryptographic Lock Manifest
- **Canonical Lock ID**: `v1.0.0_canonical_lock`
- **Master Model SHA256**: `93ecdbc42f0fda19cbba15261c1545d653eeef54e343e44e5ddcfacaf83cccdd`
- **Calibrator SHA256**: `b3faf071de7416a19da1189f12413bf15b6bd8212a74cf717f2ebc773cdee2bb`
- **Train Medians SHA256**: `f65fa42ec2c858d56aec57e2930b544ceda86395b02969df2c49f732810be4b4`
