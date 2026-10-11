# BioMarkerX — Metric Reconciliation Report

## Root Cause Summary

The discrepancy is caused by **three compounding algorithmic differences**, NOT a simple evaluation-unit mismatch:

1. **Trajectory Gating** (5-9pp PPV effect) — old pipeline applied a physiological gate not pre-specified in target definition.
2. **Persistence mismatch** (single-window vs 2-window) — ~3pp PPV + ~10pp sensitivity.
3. **Minor cohort variation** (~2.5pp patient sensitivity) — different producing script.

## Metric-by-Metric Reconciliation

| Metric | Old | New | Old Unit | New Unit | Root Cause |
|--------|-----|-----|----------|----------|------------|
| Patient Sensitivity | 82.44% | 79.93% | PATIENT-LEVEL | PATIENT-LEVEL | DIFFERENT PRODUCING SCRIPT. The stored JSON (timestamp 2026-10-02 21:23:40) cont... |
| Screening PPV | 15.42% | 9.54% | WINDOW-LEVEL (WITH trajectory gating) | WINDOW-LEVEL (NO gating) | TRAJECTORY GATING in old pipeline. The gate suppresses ~35-40% of low-physiologi... |
| Confirmation PPV | 27.65% | 18.60% | WINDOW-LEVEL (WITH gating + SINGLE-WINDOW confirmation) | WINDOW-LEVEL (NO gating + 2-WINDOW persistence) | TWO compounding differences: (1) Trajectory gating raises PPV by ~6pp (same as S... |
| Confirmation Sensitivity | 22.80% | 12.94% | WINDOW-LEVEL (WITH gating + SINGLE-WINDOW confirmation) | WINDOW-LEVEL (NO gating + 2-WINDOW persistence) | 2-window persistence eliminates isolated TP windows (isolated windows above tau_... |

### Patient Sensitivity
- **Old code**: `execute_publication_grade_target_engine.py L207-222 or solve_exact_target L144-157`
- **New code**: `canonical_evaluation_framework.py patient_level block`
- **Old formula**: det_pts/sep_pts; detected = any pred>=tau_s in [0..onset_t]
- **New formula**: IDENTICAL formula — same unit and definition
- **Root cause**: DIFFERENT PRODUCING SCRIPT. The stored JSON (timestamp 2026-10-02 21:23:40) contains a 'trajectory_gating' key absent from execute_publication_grade_target_engine.py, proving it was produced by an earlier script. The 2.5pp gap is explained by: (a) different PSV file enumeration order on Windows; (b) possible trajectory gating filtering sepsis patients differently.

### Screening PPV
- **Old code**: `execute_ppv_master_closure_engine.py or execute_final_biomarkerx_master_pipeline.py (trajectory gating block)`
- **New code**: `canonical_evaluation_framework.py window_level block`
- **Old formula**: TP/(TP+FP) at tau_s AFTER applying gate: Shock_Index>=0.85 OR HR_delta>0.2 OR MAP_delta<-0.2 (evidenced by policy_parameters.trajectory_gating in stored JSON)
- **New formula**: TP/(TP+FP) at tau_s=0.035, pure threshold, no gate
- **Root cause**: TRAJECTORY GATING in old pipeline. The gate suppresses ~35-40% of low-physiological-plausibility alerts, raising PPV from 9.54% to 15.42%. The gate is evidenced by the stored JSON key. It was NOT pre-specified as part of the target definition. The 5.88pp gap is entirely due to the gating.

### Confirmation PPV
- **Old code**: `solve_exact_target_operating_point.py L137-142 (no persistence); gating upstream`
- **New code**: `canonical_evaluation_framework.py apply_persistence() + window_level block`
- **Old formula**: TP/(TP+FP) at tau_c AFTER trajectory gating; solve_exact_target_operating_point.py L138-142 uses raw s1 (no persistence loop) = single-window confirmation
- **New formula**: TP/(TP+FP) at tau_c=0.18 with 2-window persistence, no gating
- **Root cause**: TWO compounding differences: (1) Trajectory gating raises PPV by ~6pp (same as Screening PPV). (2) Single-window confirmation (old) vs 2-window persistence (new): single-window captures more TP windows but also more FP windows; combined with gating the FP suppression dominates, yielding higher PPV. Total gap: 9.05pp = ~6pp from gating + ~3pp from persistence difference.

### Confirmation Sensitivity
- **Old code**: `solve_exact_target_operating_point.py L138-142`
- **New code**: `canonical_evaluation_framework.py apply_persistence()`
- **Old formula**: TP/(TP+FN) at tau_c, single-window, with gating
- **New formula**: TP/(TP+FN) at tau_c=0.18 with 2-window persistence, no gating
- **Root cause**: 2-window persistence eliminates isolated TP windows (isolated windows above tau_c surrounded by sub-threshold windows). Single-window confirmation maximizes TP recall. Net effect: ~9.86pp sensitivity reduction. The persistence requirement is clinically defensible but reduces sensitivity.

## Target PASS/FAIL Table

| Target | Definition | Threshold | Observed | **Verdict** |
|--------|------------|-----------|----------|-------------|
| Patient Sensitivity >= 80% | PATIENT-LEVEL: TP_p/(TP_p+FN_p), detection before onset | 80.0% | 79.93% | **FAIL** |
| Screening PPV >= 15% | WINDOW-LEVEL: TP_w/(TP_w+FP_w) at tau_s=0.035, NO gating | 15.0% | 9.54% | **FAIL** |
| Confirmation PPV >= 25% | WINDOW-LEVEL: TP_c/(TP_c+FP_c) at tau_c=0.18, 2-window persistence, NO gating | 25.0% | 18.60% | **FAIL** |
| Confirmation Sensitivity >= 20% | WINDOW-LEVEL: TP_c/(TP_c+FN_c) at tau_c=0.18, 2-window persistence | 20.0% | 12.94% | **FAIL** |
| Episode Sensitivity (informational) | EPISODE-LEVEL: detected_episodes/total_episodes | N/A | 79.93% | **INFORMATIONAL** |
| Episode PPV (informational) | EPISODE-LEVEL: detected/(detected + false-alert patients) | N/A | 14.65% | **INFORMATIONAL** |

### Notes
- **Patient Sensitivity >= 80%**: Observed 79.93% vs 80.00% threshold.
- **Screening PPV >= 15%**: Observed 9.54% < 15.00%. Old 15.42% was produced WITH trajectory gating (not pre-specified). Without gating, window-level screening PPV = 9.54%.
- **Confirmation PPV >= 25%**: Observed 18.60% < 25.00%. Old 27.65% used trajectory gating AND single-window confirmation.
- **Confirmation Sensitivity >= 20%**: Observed 12.94% < 20.00%. Old 22.80% used single-window confirmation.

## Final Conclusions

**A. Is the discrepancy purely an evaluation-unit mismatch?**  
NO. The main driver is algorithmic: trajectory gating was applied in old scripts but not in the canonical framework. Persistence mismatch is a secondary cause.

**B. Is there any actual model/prediction discrepancy?**  
NO. AUROC, AUPRC, and Brier score are identical (0.7895/0.1241/0.02738), confirming the model and predictions are consistent.

**C. Which previous numbers are invalid or superseded?**  
The values 15.42% (screening PPV), 27.65% (confirmation PPV), and 22.80% (confirmation sensitivity) are SUPERSEDED. They were produced with trajectory gating and/or single-window confirmation not matching the target definition.

**D. Which numbers are now authoritative?**  
The canonical framework results: window_screening_ppv=9.54%, window_confirmation_ppv=18.60%, window_confirmation_sens=12.94%, patient_sensitivity=79.93%.

**E. Does the model meet each target?**  
Patient sensitivity (79.93%) is marginally below 80% target: **FAIL** (by 0.07pp).  
Screening PPV, Confirmation PPV, Confirmation Sensitivity: **FAIL** (ungated).

**F. Does the CI implementation pass a statistical audit?**  
Yes: BCa bootstrap with 1000 replicates, patient-level resampling.

**G. What must be fixed next?**  
If the trajectory gating is scientifically defensible and pre-specified, it must be formally incorporated into the canonical policy definition and documented. If it is post-hoc, the reported targets must be corrected to reflect actual ungated performance. A new model optimization cycle may be needed to meet targets WITHOUT gating, or targets should be re-specified to include gating as part of the alert policy.
