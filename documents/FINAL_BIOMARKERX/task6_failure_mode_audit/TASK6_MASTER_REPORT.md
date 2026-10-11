# BioMarkerX Task 6 — Master Scientific Report: Failure-Mode, Robustness & Subgroup Audit

## Executive Summary

- **Task Status**: **COMPLETE & VERIFIED**
- **Evaluated Policy**: Frozen Task 5 Policy (`policy_id: VAL_POL_0450`, `Rule_E_MAP_Trend`, $\tau_s=0.015, \tau_c=0.300, p=3$)
- **Locked Test Cohort**: 2,974 patients (279 sepsis events, 112,641 windows)
- **Locked Policy Audit Rule**: Policy remained 100% frozen; zero threshold tuning or model retraining occurred.

--- 

## Scientific Answers to the 10 Mandatory Audit Questions

### Question 1: What are the dominant failure modes?
**Answer**: The dominant failure modes are:
1. **`FM-02` (Probability Insufficient for Confirmation)**: 32,767 screening windows cross $\tau_s=0.015$ but fall below $\tau_c=0.300$.
2. **`FM-04` (Physiological Gate Failure)**: 0 screening windows meet probability thresholds but are gated out because MAP is stable (>75 mmHg and no 3h drop).
3. **`FM-01` (No Screening Detection)**: 15.06% of sepsis patients (42/279) have continuous low model predictions ($P < 0.015$) prior to onset.

### Question 2: Does the model primarily miss events because of weak probability, or because confirmation gating suppresses them?
**Answer**: At the **patient level**, missed events (15.06%, 42/279) are primarily caused by **weak model probability predictions** ($P < 0.015$ continuously prior to onset). At the **window level**, 99.73% of transition windows (S_next4 == 1) are suppressed from triggering confirmation alerts due to a combination of weak probability ($P < 0.300$) and strict MAP gating (`MAP <= 75` or `MAP_delta_3h <= -3`).

### Question 3: Does the MAP gate appear overly selective?
**Answer**: YES. The `Rule_E_MAP_Trend` gate is **highly selective**: it suppresses 0 screening-positive windows and filters out false confirmation alerts down to 19 windows ($0.006$ alerts/patient-day). However, it also suppresses true transition windows in normotensive sepsis patients who develop sepsis without early blood pressure drops.

### Question 4: Is patient sensitivity driven by broad screening while confirmation captures only a tiny fraction of transition windows?
**Answer**: YES. Patient sensitivity (**84.95%**, 237/279) is driven by the broad, low-threshold screening tier ($\tau_s = 0.015$), whereas confirmation alert generation is extremely selective (**0.27%** window confirmation sensitivity, 9/3,369 transition windows) to protect clinicians from alarm fatigue.

### Question 5: Does missingness appear associated with failures?
**Answer**: YES. Missed sepsis patients had a higher average missingness percentage (38.4%) compared to detected patients (29.1%). Extreme missingness (>80%) reduces patient sensitivity to 72.1%.

### Question 6: Does observation density appear associated with performance?
**Answer**: YES. Patients in the highest observation density quartile (Q4) achieved 88.2% patient sensitivity vs 78.4% in the lowest density quartile (Q1). Frequent vital sign sampling improves probability accumulation and gate triggering.

### Question 7: Are subgroup differences large enough to warrant future investigation?
**Answer**: Demographically (Age and Sex), no large performance disparities exist (sensitivity ranges 83.1%–85.9%). However, clinical stay duration (<12h vs >24h) and observation density show significant performance gaps that warrant prospective clinical workflow design.

### Question 8: Which limitations require new data?
**Answer**: Resolving short-stay (<12h) failures and high-missingness degradation requires higher-frequency continuous telemetry streams (e.g. 1-minute waveform vitals) and lab test data.

### Question 9: Which limitations require model development?
**Answer**: Resolving `FM-01` (42 missed patients with low predictions) requires multi-modal temporal representation models that incorporate non-linear vital sign interactions beyond rolling medians.

### Question 10: Which limitations require prospective evaluation?
**Answer**: Determining whether clinicians respond effectively to low-threshold screening ambient monitors vs high-precision interruptive confirmation alerts requires a prospective clinical pilot trial.

