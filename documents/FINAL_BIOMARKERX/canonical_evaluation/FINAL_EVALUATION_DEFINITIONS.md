# BioMarkerX — Canonical Evaluation Definitions v1

## Sepsis Event Definition

| Symbol | Definition |
|--------|-----------|
| `S(t)` | PhysioNet SepsisLabel at window t ∈ {0,1}. Dataset-defined. **NOT** independently adjudicated clinical onset. |
| `Y(t)` | 4h lookahead: Y(t)=1 iff any of S(t+1)…S(t+4)=1 |
| positive_window | Y(t)=1 |
| negative_window | Y(t)=0 |
| transition_window | first t* where S(t*)=1 per patient |
| sepsis_episode | first contiguous S=1 block per patient (max 1 per patient) |
| patient_with_event | patient where any(S)=1 or any(Y)=1 |

## Evaluation Units and Formulas

### A. Window-Level (unit = 1-hour time window)
| Metric | Formula |
|--------|---------|
| window_ppv | TP_w / (TP_w + FP_w) |
| window_sensitivity | TP_w / (TP_w + FN_w) |
| window_specificity | TN_w / (TN_w + FP_w) |
| window_npv | TN_w / (TN_w + FN_w) |
| window_f1 | 2·TP_w / (2·TP_w + FP_w + FN_w) |

TP_w = window with Y(t)=1 AND pred ≥ τ

### B. Alert-Level (unit = contiguous run of above-threshold windows)
| Metric | Formula |
|--------|---------|
| alert_ppv | TP_alerts / total_alerts |
| alerts_per_day | total_alerts / (total_windows / 24) |

TP_alert = alert run overlapping ≥1 positive window

### C. Episode-Level (unit = sepsis episode per patient)
| Metric | Formula |
|--------|---------|
| episode_sensitivity | detected_episodes / total_sepsis_episodes |
| episode_ppv | detected / (detected + false_alert_patients) |

detected = ≥1 pred ≥ τ_s in [0, onset_t]

### D. Patient-Level (unit = patient)
| Metric | Formula |
|--------|---------|
| patient_sensitivity | TP_p / (TP_p + FN_p) |
| patient_ppv | TP_p / (TP_p + FP_p) |
| patient_specificity | TN_p / (TN_p + FP_p) |

### E. Lead-Time (hours before PhysioNet label transition)
first_alert_t = earliest window in [0..onset_t] where pred ≥ τ_s  
lead_time = onset_t − first_alert_t

**All lead-time claims use**: "hours prior to PhysioNet Sepsis-3 label transition"  
**NOT**: "hours before clinical sepsis onset"

## Persistence Rule
- Screening: no persistence. Single window ≥ τ_s = alert.
- Confirmation: 2 consecutive windows ≥ τ_c within patient = confirmed alert.

## Trajectory Gating
**NOT applied** in canonical framework.  
Old pipeline applied: Shock_Index ≥ 0.85 OR HR_delta > 0.2 OR MAP_delta < −0.2  
This was NOT pre-specified in the target definition.
