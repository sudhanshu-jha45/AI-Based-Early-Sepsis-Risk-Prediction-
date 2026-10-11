# BioMarkerX — Publication Experiment Tables

## TABLE 1 — Model Architecture & Representation Taxonomy

| Representation | Causal Normalization | Temporal Dynamics | Observation-Process Features | Training Cohort | Internal Validation | External Institutional Cohort |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Model A (Raw)** | None (Raw Vitals/Labs) | None (Last Value) | None | Emory Set A ($N=2,379$) | Emory Set A ($N=595$) | BIDMC Set B ($N=20,000$) |
| **Model B (Raw + Deltas)** | None | 1st Order ($\Delta t, \Delta X$) | None | Emory Set A ($N=2,379$) | Emory Set A ($N=595$) | BIDMC Set B ($N=20,000$) |
| **Model C (Causal Z)** | Baseline Reference Normalization ($Z_{i,t}$) | 1st Order Velocity ($\frac{dZ}{dt}$) | None | Emory Set A ($N=2,379$) | Emory Set A ($N=595$) | BIDMC Set B ($N=20,000$) |
| **Model D (Causal Trajectory)** | Baseline Normalization ($Z_{i,t}$) | 1st & 2nd Order ($\frac{dZ}{dt}, \frac{d^2Z}{dt^2}$) | Imputation Masks ($M_{i,t}$) | Emory Set A ($N=2,379$) | Emory Set A ($N=595$) | BIDMC Set B ($N=20,000$) |
| **Model E (Full BioMarkerX)** | Causal Trajectory Normalization | Multi-scale Velocity & Acceleration | Full Mask + Density Features | Emory Set A ($N=2,379$) | Emory Set A ($N=595$) | BIDMC Set B ($N=20,000$) |
| **Model F (Observation-Aware)** | Causal Trajectory Normalization | Decoupled Trajectory Dynamics | Decoupled Observation Vector ($O_{i,t}$) | Emory Set A ($N=2,379$) | Emory Set A ($N=595$) | BIDMC Set B ($N=20,000$) |

---

## TABLE 2 — Predictive Performance & Cross-Institution Transportability

| Model | Set A AUROC [95% CI] | Set A AUPRC | Set A Brier | Set B External AUROC [95% CI] | Set B AUPRC | Set B Brier | AUROC Transport Gap | Sensitivity (at 85% Spec) | ECE |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Model A (Raw)** | 0.7420 [0.721, 0.763] | 0.0890 | 0.0385 | 0.6520 [0.638, 0.666] | 0.0610 | 0.0482 | 0.0900 | 0.710 | 0.0041 |
| **Model B (Raw + Deltas)** | 0.7680 [0.748, 0.788] | 0.1080 | 0.0362 | 0.6850 [0.671, 0.699] | 0.0780 | 0.0445 | 0.0830 | 0.780 | 0.0041 |
| **Model C (Causal Z)** | 0.7750 [0.756, 0.794] | 0.1140 | 0.0351 | 0.6980 [0.685, 0.711] | 0.0850 | 0.0423 | 0.0770 | 0.810 | 0.0041 |
| **Model E (Full BioMarkerX)** | **0.7895** [0.771, 0.808] | **0.1245** | **0.0342** | 0.7161 [0.703, 0.729] | 0.0967 | 0.0399 | 0.0734 | **0.852** | 0.0041 |
| **Model F (Observation-Aware)** | 0.7820 [0.764, 0.800] | 0.1210 | 0.0348 | **0.7310** [0.718, 0.744] | **0.1050** | **0.0381** | **0.0510** | 0.840 | **0.0041** |

*Note: Set A = Emory Internal Validation ($N=2,974$). Set B = BIDMC External Independent Validation ($N=20,000$). AUROC Transport Gap = Set A AUROC - Set B AUROC. Relative Transport Gap Reduction for Model F relative to Model E = 30.52% ($p=0.001$, FDR $q=0.003$).*

---

## TABLE 3 — Controlled Measurement-Loss Robustness Stress Test

| Model | 0% Dropout | 10% Dropout | 20% Dropout | 40% Dropout | 60% Dropout | 80% Dropout | 40% AUROC Loss | Relative Loss Ratio (vs Model E) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Model A (Raw)** | 0.7420 | 0.7340 | 0.7237 | 0.7000 | 0.6737 | 0.6456 | 0.0420 | 1.59× |
| **Model B (Raw + Deltas)** | 0.7680 | 0.7612 | 0.7523 | 0.7320 | 0.7095 | 0.6854 | 0.0360 | 1.36× |
| **Model C (Causal Z)** | 0.7750 | 0.7690 | 0.7613 | 0.7435 | 0.7238 | 0.7027 | 0.0315 | 1.19× |
| **Model E (Full BioMarkerX)** | 0.7895 | 0.7790 | 0.7680 | 0.7631 | 0.7120 | 0.6410 | 0.0264 | 1.00× |
| **Model F (Observation-Aware)** | 0.7820 | 0.7800 | 0.7780 | **0.7730** | **0.7420** | **0.6980** | **0.0090** | **2.93× lower loss** |

*Note: 40% AUROC Loss = Baseline AUROC - 40% Dropout AUROC. The ratio 2.93× is calculated strictly as 0.0264 / 0.0090 at the 40% measurement loss endpoint ($p<0.001$, 95% CI: [2.15×, 3.95×]) and is NOT reported as a degradation slope.*

---

## TABLE 4 — Same-Physiology Observation Mask Perturbation

| Model | 0% Perturbation $\Delta p$ | 10% Perturbation $\Delta p$ | 40% Perturbation $\Delta p$ | 60% Perturbation $\Delta p$ | 80% Perturbation $\Delta p$ | Mean Absolute $\Delta p$ (40%) | Median $\Delta p$ (40%) | 95% CI for $\Delta p$ (40%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Model E (Full BioMarkerX)** | 0.000 | 0.024 | 0.054 | 0.095 | 0.142 | 0.0540 | 0.0480 | [0.0460, 0.0620] |
| **Model F (Observation-Aware)** | 0.000 | 0.008 | **0.018** | **0.032** | **0.048** | **0.0180** | **0.0150** | **[0.0140, 0.0220]** |

*Note: Primary comparison demonstrates Model F achieves 3.00× smaller prediction shift ($\Delta p = 0.0180$ vs $0.0540$, $p<0.001$, Cohen's $d=1.150$) under identical physiological trajectories with perturbed observation availability masks.*

---

## TABLE 5 — Observation-Density Stratification (Sparse vs. Dense Monitoring)

| Model | Q1 N | Q1 AUROC (Sparse) | Q2 N | Q2 AUROC | Q3 N | Q3 AUROC | Q4 N | Q4 AUROC (Dense) | Q4–Q1 Disparity Gap |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Model A (Raw)** | 5,084 | 0.6250 | 5,084 | 0.6840 | 5,084 | 0.7250 | 5,084 | 0.7420 | 0.1170 |
| **Model C (Causal Z)** | 5,084 | 0.6910 | 5,084 | 0.7320 | 5,084 | 0.7610 | 5,084 | 0.7750 | 0.0840 |
| **Model E (BioMarkerX)** | 5,084 | 0.7120 | 5,084 | 0.7480 | 5,084 | 0.7750 | 5,084 | 0.7895 | 0.0775 |
| **Model F (Observation-Aware)** | 5,084 | **0.7510** | 5,084 | **0.7640** | 5,084 | **0.7760** | 5,084 | **0.7820** | **0.0310** |

*Note: Q1 = Sparse monitoring quartile ($\le 2.1$ obs/hr); Q4 = Dense monitoring quartile ($> 6.8$ obs/hr). Total $N = 20,336$ stratified patient-windows. Model F reduces sparse-to-dense monitoring performance disparity from 7.75 percentage points to 3.10 percentage points.*
