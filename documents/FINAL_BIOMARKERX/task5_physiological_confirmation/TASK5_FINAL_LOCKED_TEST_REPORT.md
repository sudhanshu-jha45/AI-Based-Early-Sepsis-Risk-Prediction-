# BioMarkerX Task 5 — Phase 9: Single-Pass Locked-Test Evaluation Report
**Evaluation Date**: 2026-10-03 15:05:48
**Locked Cohort**: 2,974 patients, 112,641 windows, 279 sepsis episodes

## Frozen Policy Configuration

- **Policy ID**: `VAL_POL_0450`
- **Physiological Confirmation Rule**: `Rule_E_MAP_Trend`
- **Screening Threshold ($\tau_s$)**: 0.0150
- **Confirmation Threshold ($\tau_c$)**: 0.3000
- **Persistence Windows ($p$)**: 3
- **Onset Definition**: `first SepsisLabel == 1`

## Locked Test Performance Summary (Point Estimates & 95% CIs)

| Metric | Point Estimate | 95% Confidence Interval |
|---|---|---|
| **Patient Sensitivity** | **84.95%** (237/279) | [80.68%, 88.74%] |
| **Patient PPV** | 9.69% | [8.46%, 10.90%] |
| **Window Confirmation PPV** | **32.14%** | [3.84%, 61.54%] |
| **Window Confirmation Sensitivity** | 0.27% | [0.03%, 0.69%] |
| **Window Screening PPV** | 5.17% | [4.56%, 5.79%] |
| **AUROC** | 0.7899 | [0.5786, 0.6271] |
| **AUPRC** | 0.1241 | [0.0741, 0.1046] |
| **Brier Score** | 0.02738 | N/A |

## Alert Burden & Lead Time

- **Screening Alert Burden**: 7.01 alerts/patient-day
- **Confirmation Alert Burden**: 0.01 alerts/patient-day
- **Median Lead Time**: 36.0 hours (IQR: 11.0–75.0 h)

