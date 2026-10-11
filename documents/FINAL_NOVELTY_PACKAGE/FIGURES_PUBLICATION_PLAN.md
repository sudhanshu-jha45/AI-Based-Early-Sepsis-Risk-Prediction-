# BioMarkerX — Publication Figures Plan & Specifications

## FIGURE 1: BioMarkerX Conceptual Architecture & Decoupling

```
         ┌─────────────────────────────────────────────────────────┐
         │                  ICU TIME-SERIES DATA                   │
         └────────────────────────────┬────────────────────────────┘
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼                                               ▼
┌───────────────────────────┐                   ┌───────────────────────────┐
│   PHYSIOLOGICAL STATE     │                   │    OBSERVATION PROCESS    │
│  (Vital Signs & Labs X_t) │                   │  (Masks M_t, Deltas dt)   │
└─────────────┬─────────────┘                   └─────────────┬─────────────┘
              │                                               │
              ▼                                               ▼
┌───────────────────────────┐                   ┌───────────────────────────┐
│  CAUSAL TRAJECTORY Z-SCORE│                   │   DECOUPLED OBSERVATION   │
│ (Velocity & Acceleration) │                   │       VECTOR O_t          │
└─────────────┬─────────────┘                   └─────────────┬─────────────┘
              │                                               │
              └───────────────────────┬───────────────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │   OBSERVATION-AWARE GBDT  │
                        │    PREDICTION MODEL (F)   │
                        └─────────────┬─────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │    SEPSIS RISK OUTPUT     │
                        └───────────────────────────┘
```

* **Caption**: Conceptual architecture of BioMarkerX illustrating the explicit decoupling of underlying physiological trajectory dynamics ($Z_t, \frac{dZ}{dt}, \frac{d^2Z}{dt^2}$) from clinical observation process indicators ($M_t, \Delta t_t$). This separation prevents the prediction model from overfitting to site-specific clinician ordering habits.

---

## FIGURE 2: Cross-Institution Transportability Comparison

* **Format**: Bar Chart / Point Plot with 95% Confidence Intervals.
* **X-axis**: Model Representations (Model A, Model B, Model C, Model E, Model F).
* **Y-axis**: AUROC ($0.60 \rightarrow 0.80$).
* **Groupings**: Grouped bars for Emory Set A (Internal Validation) vs. BIDMC Set B (External Independent Validation).
* **Key Annotation**: Highlight the transportability gap reduction for Model F ($0.0510$ gap, $0.7310$ external AUROC) vs. Model E ($0.0734$ gap, $0.7161$ external AUROC), annotating the **30.52% relative gap reduction** ($p=0.001$).

---

## FIGURE 3: Controlled Measurement-Loss Robustness Curve

* **Format**: Line Graph with Error Bands (95% CI).
* **X-axis**: Controlled Measurement Dropout Percentage ($0\%, 10\%, 20\%, 40\%, 60\%, 80\%$).
* **Y-axis**: Test AUROC ($0.60 \rightarrow 0.80$).
* **Lines**: Model A (Raw), Model C (Causal Z), Model E (Full BioMarkerX), Model F (Observation-Aware).
* **Key Annotation**: Callout box at 40% dropout level annotating: `"2.93× lower AUROC loss at 40% controlled measurement loss (Model F loss = 0.0090 vs Model E loss = 0.0264, p < 0.001)"`. **Crucial Rule**: Do NOT label as a slope.

---

## FIGURE 4: Same-Physiology Perturbation Shift Distribution

* **Format**: Boxplot / Kernel Density Estimate (KDE) plot.
* **X-axis**: Synthetic Observation Mask Perturbation Level ($0\%, 10\%, 40\%, 60\%, 80\%$).
* **Y-axis**: Mean Absolute Prediction Shift ($\Delta p = |\hat{y}_{\text{orig}} - \hat{y}_{\text{perturbed}}|$).
* **Comparison**: Model E (Full BioMarkerX) vs Model F (Observation-Aware).
* **Key Annotation**: Annotate the primary endpoint comparison at 40% perturbation: `"3.00× smaller prediction shift for Model F (Δp = 0.0180 vs 0.0540, p < 0.001)"`.

---

## FIGURE 5: Observation-Density Stratification (Sparse vs. Dense Monitoring)

* **Format**: Grouped Bar Chart.
* **X-axis**: Monitoring Density Quartiles (Q1: Sparse, Q2: Med-Low, Q3: Med-High, Q4: Dense).
* **Y-axis**: AUROC ($0.65 \rightarrow 0.80$).
* **Bars**: Model E (BioMarkerX) vs Model F (Observation-Aware).
* **Key Annotation**: Annotate disparity gap: `"Model E Q4–Q1 gap = 7.75 percentage points"`, `"Model F Q4–Q1 gap = 3.10 percentage points"`. Use neutral terminology: `"sparse-monitoring stratum"` and `"dense-monitoring stratum"`.

---

## FIGURE 6: Proposed Transportability Mechanism Schematic

```
[Institutional Practice Differences] ──► [Altered Measurement Densities & Masks M_t]
                                                         │
                                                         ▼
                                       ┌───────────────────────────────────┐
                                       │     UNCOUPLED MODEL SENSITIVITY   │
                                       │ (Model E overfits to sampling mask)│
                                       └─────────────────┬─────────────────┘
                                                         │
                                                         ▼
                                       ┌───────────────────────────────────┐
                                       │  OBSERVATION-AWARE REPRESENTATION │
                                       │ (Model F normalizes trajectory)   │
                                       └─────────────────┬─────────────────┘
                                                         │
                                                         ▼
                                       ┌───────────────────────────────────┐
                                       │ REDUCED CROSS-SITE DECAY (30.52%) │
                                       └───────────────────────────────────┘
```
* **Caption**: Proposed mechanism of transportability preservation. Differences in clinical ordering practices across sites alter measurement masks ($M_t$). Observation-aware trajectory modeling decouples state from sampling frequency, reducing model sensitivity to institutional missingness shifts.
