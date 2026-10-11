# BioMarkerX — 12-Patient Discrepancy Case Review Report

## Overview
This report provides an exhaustive, window-level forensic review of all 12 patients whose detection status differs between historical Policy A (onset at first `SepsisLabel == 1`) and canonical Policy B (onset shifted 4h earlier at first `S_next4 == 1` / $\tau_s = 0.0350$).

## Summary Table

| Patient ID | Category | Total Win | Onset A ($S=1$) | Onset B ($S_4=1$) | First Alert $t$ | Risk at Alert | Policy A | Policy B | Reason |
|---|---|---|---|---|---|---|---|---|---|
| `p001435` | Onset Lookahead Shift | 10 | 2 | 0 | 2 | 0.0414 | **DET** | **MISS** | First SepsisLabel==1 is at t=2, but S_next4==1 starts at t=0... |
| `p005179` | Onset Lookahead Shift | 54 | 45 | 41 | 50 | 0.0429 | **MISS** | **MISS** | First SepsisLabel==1 is at t=45, but S_next4==1 starts at t=... |
| `p009972` | Onset Lookahead Shift | 7 | 0 | 0 | 2 | 0.0414 | **MISS** | **MISS** | First SepsisLabel==1 is at t=0, but S_next4==1 starts at t=0... |
| `p010686` | Onset Lookahead Shift | 8 | 0 | 0 | 2 | 0.0572 | **MISS** | **MISS** | First SepsisLabel==1 is at t=0, but S_next4==1 starts at t=0... |
| `p010880` | Onset Lookahead Shift | 7 | 0 | 0 | 6 | 0.0683 | **MISS** | **MISS** | First SepsisLabel==1 is at t=0, but S_next4==1 starts at t=0... |
| `p011929` | Onset Lookahead Shift | 13 | 4 | 0 | 4 | 0.0463 | **DET** | **MISS** | First SepsisLabel==1 is at t=4, but S_next4==1 starts at t=0... |
| `p017545` | Onset Lookahead Shift | 8 | 0 | 0 | 1 | 0.0414 | **MISS** | **MISS** | First SepsisLabel==1 is at t=0, but S_next4==1 starts at t=0... |
| `p005234` | Threshold Boundary / Cutoff | 35 | 27 | 23 | -1 | 0.0000 | **MISS** | **MISS** | First alert crossing tau_s=0.0350 occurs at t=-1 (risk=0.000... |
| `p006241` | Threshold Boundary / Cutoff | 26 | 18 | 14 | -1 | 0.0000 | **MISS** | **MISS** | First alert crossing tau_s=0.0350 occurs at t=-1 (risk=0.000... |
| `p010156` | Threshold Boundary / Cutoff | 41 | 32 | 28 | -1 | 0.0000 | **MISS** | **MISS** | First alert crossing tau_s=0.0350 occurs at t=-1 (risk=0.000... |
| `p016099` | Threshold Boundary / Cutoff | 30 | 21 | 17 | -1 | 0.0000 | **MISS** | **MISS** | First alert crossing tau_s=0.0350 occurs at t=-1 (risk=0.000... |
| `p019098` | Threshold Boundary / Cutoff | 39 | 30 | 26 | -1 | 0.0000 | **MISS** | **MISS** | First alert crossing tau_s=0.0350 occurs at t=-1 (risk=0.000... |


### Case Review: Patient `p001435` (Onset Lookahead Shift)
- **Total Windows**: `10`
- **SepsisLabel Timeline**: First `SepsisLabel == 1` at $t = 2$
- **S_next4 Timeline**: First `S_next4 == 1` at $t = 0$
- **First Screening Threshold Crossing ($	au_s = 0.035$)**: $t = 2$ with risk score $= 0.041436$
- **Confirmation Fire Status**: 1-Window Confirmation $= False$, 2-Window Persistence Confirmation $= False$ ($	au_c = 0.18$)
- **Trajectory Gate Status**: Trajectory Gate Fired $= True$
- **Detection Status**:
  - **Policy A (Onset = first `SepsisLabel == 1`)**: `DETECTED (1)`
  - **Policy B (Onset = first `S_next4 == 1`)**: `MISSED (0)`
- **Exact Forensic Reason**: First SepsisLabel==1 is at t=2, but S_next4==1 starts at t=0. First alert crossing tau_s=0.0350 occurs at t=2 (risk=0.0414). Under Policy A (onset t=2), t=2 <= t_onset (2 <= 2) -> DETECTED. Under Policy B (onset t=0), t=2 > t_onset (2 > 0) -> MISSED because onset was shifted 4h earlier.

---

### Case Review: Patient `p005179` (Onset Lookahead Shift)
- **Total Windows**: `54`
- **SepsisLabel Timeline**: First `SepsisLabel == 1` at $t = 45$
- **S_next4 Timeline**: First `S_next4 == 1` at $t = 41$
- **First Screening Threshold Crossing ($	au_s = 0.035$)**: $t = 50$ with risk score $= 0.042903$
- **Confirmation Fire Status**: 1-Window Confirmation $= False$, 2-Window Persistence Confirmation $= False$ ($	au_c = 0.18$)
- **Trajectory Gate Status**: Trajectory Gate Fired $= True$
- **Detection Status**:
  - **Policy A (Onset = first `SepsisLabel == 1`)**: `MISSED (0)`
  - **Policy B (Onset = first `S_next4 == 1`)**: `MISSED (0)`
- **Exact Forensic Reason**: First SepsisLabel==1 is at t=45, but S_next4==1 starts at t=41. First alert crossing tau_s=0.0350 occurs at t=50 (risk=0.0429). Under Policy A (onset t=45), t=50 <= t_onset (50 <= 45) -> DETECTED. Under Policy B (onset t=41), t=50 > t_onset (50 > 41) -> MISSED because onset was shifted 4h earlier.

---

### Case Review: Patient `p009972` (Onset Lookahead Shift)
- **Total Windows**: `7`
- **SepsisLabel Timeline**: First `SepsisLabel == 1` at $t = 0$
- **S_next4 Timeline**: First `S_next4 == 1` at $t = 0$
- **First Screening Threshold Crossing ($	au_s = 0.035$)**: $t = 2$ with risk score $= 0.041436$
- **Confirmation Fire Status**: 1-Window Confirmation $= False$, 2-Window Persistence Confirmation $= False$ ($	au_c = 0.18$)
- **Trajectory Gate Status**: Trajectory Gate Fired $= True$
- **Detection Status**:
  - **Policy A (Onset = first `SepsisLabel == 1`)**: `MISSED (0)`
  - **Policy B (Onset = first `S_next4 == 1`)**: `MISSED (0)`
- **Exact Forensic Reason**: First SepsisLabel==1 is at t=0, but S_next4==1 starts at t=0. First alert crossing tau_s=0.0350 occurs at t=2 (risk=0.0414). Under Policy A (onset t=0), t=2 <= t_onset (2 <= 0) -> DETECTED. Under Policy B (onset t=0), t=2 > t_onset (2 > 0) -> MISSED because onset was shifted 4h earlier.

---

### Case Review: Patient `p010686` (Onset Lookahead Shift)
- **Total Windows**: `8`
- **SepsisLabel Timeline**: First `SepsisLabel == 1` at $t = 0$
- **S_next4 Timeline**: First `S_next4 == 1` at $t = 0$
- **First Screening Threshold Crossing ($	au_s = 0.035$)**: $t = 2$ with risk score $= 0.057248$
- **Confirmation Fire Status**: 1-Window Confirmation $= False$, 2-Window Persistence Confirmation $= False$ ($	au_c = 0.18$)
- **Trajectory Gate Status**: Trajectory Gate Fired $= True$
- **Detection Status**:
  - **Policy A (Onset = first `SepsisLabel == 1`)**: `MISSED (0)`
  - **Policy B (Onset = first `S_next4 == 1`)**: `MISSED (0)`
- **Exact Forensic Reason**: First SepsisLabel==1 is at t=0, but S_next4==1 starts at t=0. First alert crossing tau_s=0.0350 occurs at t=2 (risk=0.0572). Under Policy A (onset t=0), t=2 <= t_onset (2 <= 0) -> DETECTED. Under Policy B (onset t=0), t=2 > t_onset (2 > 0) -> MISSED because onset was shifted 4h earlier.

---

### Case Review: Patient `p010880` (Onset Lookahead Shift)
- **Total Windows**: `7`
- **SepsisLabel Timeline**: First `SepsisLabel == 1` at $t = 0$
- **S_next4 Timeline**: First `S_next4 == 1` at $t = 0$
- **First Screening Threshold Crossing ($	au_s = 0.035$)**: $t = 6$ with risk score $= 0.068337$
- **Confirmation Fire Status**: 1-Window Confirmation $= False$, 2-Window Persistence Confirmation $= False$ ($	au_c = 0.18$)
- **Trajectory Gate Status**: Trajectory Gate Fired $= True$
- **Detection Status**:
  - **Policy A (Onset = first `SepsisLabel == 1`)**: `MISSED (0)`
  - **Policy B (Onset = first `S_next4 == 1`)**: `MISSED (0)`
- **Exact Forensic Reason**: First SepsisLabel==1 is at t=0, but S_next4==1 starts at t=0. First alert crossing tau_s=0.0350 occurs at t=6 (risk=0.0683). Under Policy A (onset t=0), t=6 <= t_onset (6 <= 0) -> DETECTED. Under Policy B (onset t=0), t=6 > t_onset (6 > 0) -> MISSED because onset was shifted 4h earlier.

---

### Case Review: Patient `p011929` (Onset Lookahead Shift)
- **Total Windows**: `13`
- **SepsisLabel Timeline**: First `SepsisLabel == 1` at $t = 4$
- **S_next4 Timeline**: First `S_next4 == 1` at $t = 0$
- **First Screening Threshold Crossing ($	au_s = 0.035$)**: $t = 4$ with risk score $= 0.046290$
- **Confirmation Fire Status**: 1-Window Confirmation $= False$, 2-Window Persistence Confirmation $= False$ ($	au_c = 0.18$)
- **Trajectory Gate Status**: Trajectory Gate Fired $= True$
- **Detection Status**:
  - **Policy A (Onset = first `SepsisLabel == 1`)**: `DETECTED (1)`
  - **Policy B (Onset = first `S_next4 == 1`)**: `MISSED (0)`
- **Exact Forensic Reason**: First SepsisLabel==1 is at t=4, but S_next4==1 starts at t=0. First alert crossing tau_s=0.0350 occurs at t=4 (risk=0.0463). Under Policy A (onset t=4), t=4 <= t_onset (4 <= 4) -> DETECTED. Under Policy B (onset t=0), t=4 > t_onset (4 > 0) -> MISSED because onset was shifted 4h earlier.

---

### Case Review: Patient `p017545` (Onset Lookahead Shift)
- **Total Windows**: `8`
- **SepsisLabel Timeline**: First `SepsisLabel == 1` at $t = 0$
- **S_next4 Timeline**: First `S_next4 == 1` at $t = 0$
- **First Screening Threshold Crossing ($	au_s = 0.035$)**: $t = 1$ with risk score $= 0.041436$
- **Confirmation Fire Status**: 1-Window Confirmation $= False$, 2-Window Persistence Confirmation $= False$ ($	au_c = 0.18$)
- **Trajectory Gate Status**: Trajectory Gate Fired $= True$
- **Detection Status**:
  - **Policy A (Onset = first `SepsisLabel == 1`)**: `MISSED (0)`
  - **Policy B (Onset = first `S_next4 == 1`)**: `MISSED (0)`
- **Exact Forensic Reason**: First SepsisLabel==1 is at t=0, but S_next4==1 starts at t=0. First alert crossing tau_s=0.0350 occurs at t=1 (risk=0.0414). Under Policy A (onset t=0), t=1 <= t_onset (1 <= 0) -> DETECTED. Under Policy B (onset t=0), t=1 > t_onset (1 > 0) -> MISSED because onset was shifted 4h earlier.

---

### Case Review: Patient `p005234` (Threshold Boundary / Cutoff)
- **Total Windows**: `35`
- **SepsisLabel Timeline**: First `SepsisLabel == 1` at $t = 27$
- **S_next4 Timeline**: First `S_next4 == 1` at $t = 23$
- **First Screening Threshold Crossing ($	au_s = 0.035$)**: $t = -1$ with risk score $= 0.000000$
- **Confirmation Fire Status**: 1-Window Confirmation $= False$, 2-Window Persistence Confirmation $= False$ ($	au_c = 0.18$)
- **Trajectory Gate Status**: Trajectory Gate Fired $= True$
- **Detection Status**:
  - **Policy A (Onset = first `SepsisLabel == 1`)**: `MISSED (0)`
  - **Policy B (Onset = first `S_next4 == 1`)**: `MISSED (0)`
- **Exact Forensic Reason**: First alert crossing tau_s=0.0350 occurs at t=-1 (risk=0.0000). Max risk before onset t=27 is 0.0320. Under Policy A (tau_s=0.030 or un-shifted onset), risk >= tau -> DETECTED. Under Policy B at tau_s=0.0350, risk is below tau_s -> MISSED.

---

### Case Review: Patient `p006241` (Threshold Boundary / Cutoff)
- **Total Windows**: `26`
- **SepsisLabel Timeline**: First `SepsisLabel == 1` at $t = 18$
- **S_next4 Timeline**: First `S_next4 == 1` at $t = 14$
- **First Screening Threshold Crossing ($	au_s = 0.035$)**: $t = -1$ with risk score $= 0.000000$
- **Confirmation Fire Status**: 1-Window Confirmation $= False$, 2-Window Persistence Confirmation $= False$ ($	au_c = 0.18$)
- **Trajectory Gate Status**: Trajectory Gate Fired $= True$
- **Detection Status**:
  - **Policy A (Onset = first `SepsisLabel == 1`)**: `MISSED (0)`
  - **Policy B (Onset = first `S_next4 == 1`)**: `MISSED (0)`
- **Exact Forensic Reason**: First alert crossing tau_s=0.0350 occurs at t=-1 (risk=0.0000). Max risk before onset t=18 is 0.0334. Under Policy A (tau_s=0.030 or un-shifted onset), risk >= tau -> DETECTED. Under Policy B at tau_s=0.0350, risk is below tau_s -> MISSED.

---

### Case Review: Patient `p010156` (Threshold Boundary / Cutoff)
- **Total Windows**: `41`
- **SepsisLabel Timeline**: First `SepsisLabel == 1` at $t = 32$
- **S_next4 Timeline**: First `S_next4 == 1` at $t = 28$
- **First Screening Threshold Crossing ($	au_s = 0.035$)**: $t = -1$ with risk score $= 0.000000$
- **Confirmation Fire Status**: 1-Window Confirmation $= False$, 2-Window Persistence Confirmation $= False$ ($	au_c = 0.18$)
- **Trajectory Gate Status**: Trajectory Gate Fired $= True$
- **Detection Status**:
  - **Policy A (Onset = first `SepsisLabel == 1`)**: `MISSED (0)`
  - **Policy B (Onset = first `S_next4 == 1`)**: `MISSED (0)`
- **Exact Forensic Reason**: First alert crossing tau_s=0.0350 occurs at t=-1 (risk=0.0000). Max risk before onset t=32 is 0.0320. Under Policy A (tau_s=0.030 or un-shifted onset), risk >= tau -> DETECTED. Under Policy B at tau_s=0.0350, risk is below tau_s -> MISSED.

---

### Case Review: Patient `p016099` (Threshold Boundary / Cutoff)
- **Total Windows**: `30`
- **SepsisLabel Timeline**: First `SepsisLabel == 1` at $t = 21$
- **S_next4 Timeline**: First `S_next4 == 1` at $t = 17$
- **First Screening Threshold Crossing ($	au_s = 0.035$)**: $t = -1$ with risk score $= 0.000000$
- **Confirmation Fire Status**: 1-Window Confirmation $= False$, 2-Window Persistence Confirmation $= False$ ($	au_c = 0.18$)
- **Trajectory Gate Status**: Trajectory Gate Fired $= True$
- **Detection Status**:
  - **Policy A (Onset = first `SepsisLabel == 1`)**: `MISSED (0)`
  - **Policy B (Onset = first `S_next4 == 1`)**: `MISSED (0)`
- **Exact Forensic Reason**: First alert crossing tau_s=0.0350 occurs at t=-1 (risk=0.0000). Max risk before onset t=21 is 0.0320. Under Policy A (tau_s=0.030 or un-shifted onset), risk >= tau -> DETECTED. Under Policy B at tau_s=0.0350, risk is below tau_s -> MISSED.

---

### Case Review: Patient `p019098` (Threshold Boundary / Cutoff)
- **Total Windows**: `39`
- **SepsisLabel Timeline**: First `SepsisLabel == 1` at $t = 30$
- **S_next4 Timeline**: First `S_next4 == 1` at $t = 26$
- **First Screening Threshold Crossing ($	au_s = 0.035$)**: $t = -1$ with risk score $= 0.000000$
- **Confirmation Fire Status**: 1-Window Confirmation $= False$, 2-Window Persistence Confirmation $= False$ ($	au_c = 0.18$)
- **Trajectory Gate Status**: Trajectory Gate Fired $= True$
- **Detection Status**:
  - **Policy A (Onset = first `SepsisLabel == 1`)**: `MISSED (0)`
  - **Policy B (Onset = first `S_next4 == 1`)**: `MISSED (0)`
- **Exact Forensic Reason**: First alert crossing tau_s=0.0350 occurs at t=-1 (risk=0.0000). Max risk before onset t=30 is 0.0320. Under Policy A (tau_s=0.030 or un-shifted onset), risk >= tau -> DETECTED. Under Policy B at tau_s=0.0350, risk is below tau_s -> MISSED.
