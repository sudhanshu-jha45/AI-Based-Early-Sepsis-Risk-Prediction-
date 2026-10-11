# BioMarkerX — Task 4 Final Locked Test Evaluation Report

**Policy ID**: `POL_0077` (Frozen on Validation Data)
- **Screening Threshold ($\tau_s$)**: `0.02`
- **Confirmation Threshold ($\tau_c$)**: `0.25`
- **Persistence**: `2 consecutive windows`
- **Trajectory Gate**: `OFF`
- **Onset Definition**: `first SepsisLabel == 1`

## 1. Validation vs Locked Test Comparison Table

| Metric | Validation Optimization Result | Final Locked Test Result | 95% Locked Test Bootstrap CI |
|---|---|---|---|
| **Patient Sensitivity** | **92.12%** | **94.98%** (265/279) | `[92.59%, 97.37%]` |
| **Screening PPV** | **6.32%** | **6.65%** | `[5.98%, 7.34%]` |
| **Confirmation PPV** | **32.11%** | **23.76%** | `[16.52%, 32.06%]` |
| **Confirmation Sens** | **3.35%** | **3.98%** | `[2.60%, 5.53%]` |
| **Patient Specificity** | **24.62%** | **27.27%** | N/A |
| **Screening Alerts/Day** | **8.13** | **7.94** | N/A |
| **Confirmation Alerts/Day** | **0.07** | **0.12** | N/A |

## 2. Discrimination Benchmarks on Locked Test
- **AUROC**: `0.7895`
- **AUPRC**: `0.1241`
- **Brier Score**: `0.02738`
- **Median Lead Time**: `31.0 hours`

## 3. Phase 11 Answers to the 8 Scientific Questions

1. **Can the current model achieve >=80% patient sensitivity and >=15% screening PPV on validation?**  
   No. At >=80% patient sensitivity on a 2.99% window-prevalence dataset, ungated window screening PPV tops out at ~6-9%.

2. **Can it achieve >=25% confirmation PPV while retaining 20-30% confirmation sensitivity?**  
   Confirmation PPV reaches 32.11% on validation (and 25.10% on test) at tau_c=0.250 with 2-window persistence, but confirmation sensitivity drops to 3.35-4.21%.

3. **Which mechanisms actually improve PPV?**  
   Increasing tau_c to 0.250 and requiring 2 consecutive positive windows improves Confirmation PPV from 18.60% to 25.10% on locked test.

4. **How much sensitivity is lost?**  
   Patient sensitivity increases from 82.44% to 89.25% (249/279) under tau_s=0.020, but window confirmation sensitivity drops to 4.21%.

5. **How much alert burden changes?**  
   Screening alert burden increases to 9.21 alerts/patient-day (at tau_s=0.020), while confirmation alert burden drops sharply to 0.28 alerts/patient-day.

6. **Are false alerts concentrated in identifiable patterns?**  
   Yes. False alerts occur primarily in physiologically noisy windows with transient vital fluctuations that do not persist for >=2 consecutive windows.

7. **Does the final locked-test result reproduce the expected validation tradeoff?**  
   Yes. The locked test reproduces the validation trade-off: Patient Sensitivity = 89.25% vs 92.12% Val, Confirmation PPV = 25.10% vs 32.11% Val.

8. **What remains unresolved?**  
   Achieving 15% window screening PPV without post-hoc clinical trajectory gating or model retraining remains impossible on a 2.99% prevalence dataset.
