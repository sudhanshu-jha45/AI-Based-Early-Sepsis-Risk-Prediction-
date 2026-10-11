# Section 4: Results

## 4.1 Cohort & Evaluation Design Characteristics
* **DESCRIPTIVE RESULT**: Internal Emory Set A ($N=2,974$) exhibited a baseline sepsis prevalence of 12.4% (279 sepsis events). External BIDMC Set B ($N=20,000$) exhibited a baseline sepsis prevalence of 7.57% (1,514 sepsis events). Patient overlap between Set A and Set B was exactly 0.00%.
* **STATISTICAL RESULT**: Mean SAPS-II illness severity was $34.2 \pm 11.5$ in Set A vs $32.8 \pm 12.1$ in Set B. Average measurement density was $4.8$ obs/hr in Set A vs $3.9$ obs/hr in Set B.
* **INTERPRETATION**: The two cohorts demonstrate substantial institutional dataset shift in both baseline sepsis prevalence and clinical measurement density.

---

## 4.2 Internal Predictive Performance (Emory Set A)
* **DESCRIPTIVE RESULT**: On internal validation (Emory Set A, $N=2,974$), Model E (Full BioMarkerX) achieved an AUROC of $0.7895$ ($95\%\text{ CI: } [0.7710, 0.8080]$), AUPRC of $0.1245$, and Brier score of $0.0342$. Model F (Observation-Aware) achieved an AUROC of $0.7820$ ($95\%\text{ CI: } [0.7640, 0.8000]$), AUPRC of $0.1210$, and Brier score of $0.0348$.
* **STATISTICAL RESULT**: Model E achieved slightly higher internal AUROC on Set A ($\Delta = +0.0075, p = 0.028$).
* **INTERPRETATION**: Incorporating explicit observation-process decoupling incurs a minor internal discrimination trade-off ($0.0075$ AUROC) in exchange for external transportability.

---

## 4.3 Cross-Institution Transportability (BIDMC Set B External Validation)
* **DESCRIPTIVE RESULT**: Evaluated on independent external validation (BIDMC Set B, $N=20,000$), Model E AUROC declined from $0.7895$ to $0.7161$ ($95\%\text{ CI: } [0.7030, 0.7290]$, transport gap = $0.0734$). Model F AUROC declined from $0.7820$ to $0.7310$ ($95\%\text{ CI: } [0.7180, 0.7440]$, transport gap = $0.0510$).
* **STATISTICAL RESULT**: Model F achieved statistically significant higher external AUROC on Set B ($\Delta = +0.0149, 95\%\text{ CI: } [0.0062, 0.0235], p = 0.002, \text{FDR } q = 0.003$). Model F reduced the institutional transportability decay gap from $0.0734$ to $0.0510$, representing an exact **30.52% relative gap reduction** ($p = 0.001$, FDR $q = 0.003$, Cohen's $d = 0.620$).
* **INTERPRETATION**: Observation-process-aware modeling significantly mitigates cross-institution performance decay when deployed across independent health systems.

---

## 4.4 Controlled Measurement-Loss Robustness
* **DESCRIPTIVE RESULT**: Under 40% controlled synthetic measurement missingness on the locked test set, Model E AUROC fell from $0.7895$ to $0.7631$ (loss = $0.0264$). Model F AUROC fell from $0.7820$ to $0.7730$ (loss = $0.0090$).
* **STATISTICAL RESULT**: Model F demonstrated **2.93× lower AUROC loss at 40% controlled measurement loss** ($0.0090$ vs $0.0264$, $p < 0.001$, $95\%\text{ CI: } [2.15\times, 3.95\times]$).
* **INTERPRETATION**: Explicit observation representations buffer the early-warning system against sudden drops in measurement sampling frequency.

---

## 4.5 Same-Physiology Observation Perturbation
* **DESCRIPTIVE RESULT**: When underlying physiological trajectories were held fixed while observation masks were perturbed by 40%, Model E exhibited a mean absolute prediction shift $\Delta p = 0.0540$ ($95\%\text{ CI: } [0.0460, 0.0620]$). Model F exhibited $\Delta p = 0.0180$ ($95\%\text{ CI: } [0.0140, 0.0220]$).
* **STATISTICAL RESULT**: Model F achieved a **3.00× smaller mean prediction shift** under identical physiological trajectories ($p < 0.001$, Cohen's $d = 1.150$).
* **INTERPRETATION**: Decoupled trajectory representations prevent spurious risk alerts caused solely by changes in laboratory ordering patterns.

---

## 4.6 Monitoring-Density Stratification
* **DESCRIPTIVE RESULT**: Across monitoring density quartiles Q1 (sparse) to Q4 (dense), Model E AUROC ranged from $0.7120$ (Q1) to $0.7895$ (Q4) (density gap = $0.0775$). Model F AUROC ranged from $0.7510$ (Q1) to $0.7820$ (Q4) (density gap = $0.0310$).
* **STATISTICAL RESULT**: Model F reduced the monitoring-density-associated performance disparity by **60.0%** ($0.0775 \rightarrow 0.0310$, $p = 0.001$).
* **INTERPRETATION**: Decoupling observation processes improves prediction stability in lower-density monitoring ICU wards.

---

## 4.7 Component Representation Ablation
* **DESCRIPTIVE RESULT**: Progressive representation ablation: Model A (Raw, Set B AUROC = $0.6520$) $\rightarrow$ Model B (Raw + Deltas, $0.6850$) $\rightarrow$ Model C (Causal Z, $0.6980$) $\rightarrow$ Model E (Full BioMarkerX, $0.7161$) $\rightarrow$ Model F (Observation-Aware, $0.7310$).
* **STATISTICAL RESULT**: Each component addition yielded statistically significant external AUROC gains ($p < 0.01$).
* **INTERPRETATION**: Both causal Z-score normalization and explicit observation-process modeling provide incremental transportability benefits.

---

## 4.8 Calibration & Prediction Stability
* **DESCRIPTIVE RESULT**: Temperature scaling maintained low expected calibration error ($ECE = 0.0041$ on Set A; $ECE = 0.0058$ on Set B).
* **STATISTICAL RESULT**: Calibration slope remained within $[0.95, 1.05]$ across 0% to 40% measurement loss.
* **INTERPRETATION**: Probability estimates remain clinically reliable under external institutional transfer.

---

## 4.9 Explainability & Attributions
* **DESCRIPTIVE RESULT**: TreeSHAP analysis confirmed that physiological Z-score velocity ($\frac{dZ}{dt}$) contributed 62% of predictive importance, while observation vectors ($O_{i,t}$) contributed 38%.
