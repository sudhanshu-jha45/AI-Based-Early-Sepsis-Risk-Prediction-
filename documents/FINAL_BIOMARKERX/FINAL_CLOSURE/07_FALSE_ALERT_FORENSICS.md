# BioMarkerX False-Alert Forensics Report (Locked Test)

## Executive Summary
- **Screening Alerts**: 2,208 False Positive Patients across 112,641 windows.
- **Confirmation Alerts**: 19 False Positive confirmation windows (Alert Burden: 0.006 alerts/patient-day).

## Characterized False-Alert Categories
1. **Isolated Transient Vital Abnormality**: Short 1-hour vital spikes (e.g. transient tachypnea or artifactual blood pressure dip). Suppressed by persistence $p=3$.
2. **Persistent Non-Septic Deterioration**: Chronic cardiogenic or renal ICU deterioration without active infection. Filtered down by $\tau_c=0.300$.
3. **Measurement-Density Spikes**: Bursts of vital sign recordings during procedural care triggering brief probability increases.
