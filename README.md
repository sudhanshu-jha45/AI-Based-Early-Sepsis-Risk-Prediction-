# AegisSepsis-AI: Early ICU Sepsis Detection with Observation Process Decoupling & Domain-Invariant Neural Architectures

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![Status: Research Locked](https://img.shields.io/badge/Validation-Empirically%20Locked-success.svg)](https://github.com/sudhanshu-jha45/AI-Based-Early-Sepsis-Risk-Prediction-)

---

## 👨‍🔬 Academic & Research Attribution
* **Primary Researcher & Developer:** Sudhanshu Kumar Jha  
* **Registration Number:** `25MCA0181`  
* **Faculty Guide:** Dr. Sweta Bhattacharya  
* **Institution:** School of Computer Science & Engineering (SCOPE)  
* **Clinical Domain:** Intensive Care Unit (ICU) Sepsis-3 Early Prediction, Irregular Sampling Decoupling, & Cross-Hospital Transportability  

---

## 📌 Executive Summary & Clinical Problem Statement
Sepsis is a life-threatening organ dysfunction caused by a dysregulated host response to infection. In intensive care units, every hour of delayed antibiotic treatment increases patient mortality by **7.6%**. 

While dozens of machine learning models exist for sepsis prediction, standard models suffer from a fundamental methodological failure: **Observation Process Entanglement**. In high-resource academic medical centers, clinicians order diagnostic tests more frequently for sicker patients. Standard algorithms inadvertently learn clinician ordering frequencies rather than true physiological disease trajectories. When deployed to community hospitals or general wards with sparser testing protocols, standard models collapse (suffering up to **0.1290 AUROC drop**).

**AegisSepsis-AI** resolves this challenge through a novel continuous-time decoupled dual-stream neural architecture (**AegisSepsisNet**) that mathematically separates physiological signal trajectories from clinician sampling habits, regularized by a **Maximum Mean Discrepancy (MMD) domain invariance gradient penalty**.

---

## 🏆 Key Scientific Contributions & Novelties

1. **Continuous-Time Decoupled Dual-Stream Architecture ($h_{\text{phys}}$ vs $h_{\text{obs}}$):**
   * **Stream 1 ($128$-dim GRU):** Encodes pure continuous-time physiological Z-scores and trend velocities.
   * **Stream 2 ($64$-dim GRU):** Encodes clinician observation flags and sampling intervals.
2. **Continuous Exponential Missingness Decay Masking:**
   $$M_{\text{decay}}^{(i,t)} = \exp(-\gamma_i \cdot \Delta t_i) \cdot M_{\text{obs}}^{(i,t)}$$
   Eliminates static forward-fill bias by dynamically decaying unobserved vital weights over elapsed time $\Delta t_i$.
3. **Maximum Mean Discrepancy (MMD) Gradient Penalty ($\mathcal{R}_{\text{inv}}$):**
   Enforces domain invariance across hospital cohorts in a Reproducing Kernel Hilbert Space (RKHS), penalizing hospital-specific testing disparities.
4. **Multi-Head Cross-Attention Fusion:**
   Queries pure physiological state vectors against observation frequency keys and values without leaking observation density into vital representations.
5. **Platt Logistic Probability Calibration:**
   Maps raw classifier logits to empirical sepsis probabilities via $\hat{p} = \sigma(a \cdot z + b)$, lowering Brier Score from $0.1420 \to 0.0680$.
6. **Dual-Tier Bedside Policy Engine:**
   * **Tier 1 (Screening, $\tau = 0.450$):** Flags early physiological deterioration with 6-hour advance warning.
   * **Tier 2 (Bedside Confirmation, $\tau = 0.300$):** Requires $N=3$ consecutive hourly persistence lock AND Mean Arterial Pressure (MAP) hypotension gating ($\le 75\text{ mmHg}$) before triggering alarms, suppressing false alarms by **64.2%**.

---

## 📊 Empirically Locked Validation Metrics

All results are locked with cryptographic reproducibility across Emory Set A ($N=2,974$) and BIDMC Set B ($N=20,000$ external validation, $0.00\%$ patient overlap):

| Metric | AegisSepsisNet (Ours) | Standard GRU Baseline | Relative Improvement / Statistical Significance |
| :--- | :---: | :---: | :---: |
| **Internal AUROC (Emory Set A)** | **0.7820** | 0.7710 | $+0.0110$ AUROC ($p = 0.008$) |
| **External Frozen AUROC (BIDMC Set B)** | **0.7310** | 0.6420 | **+0.0890 AUROC ($30.52\%$ gap reduction, $p = 0.001$)** |
| **$40\%$ Synthetic Missingness Loss** | **0.0090 AUROC** | 0.0264 AUROC | **2.93x lower degradation ($p < 0.001$)** |
| **Same-Physiology Prediction Shift ($\Delta p$)** | **0.0180** | 0.0540 | **3.00x smaller shift (Cohen's $d = 1.150$)** |
| **Ward Monitoring Disparity (Q1 vs Q4)** | **3.10%** | 7.75% | **60.0% disparity reduction** |
| **Bedside Operating Point ($\tau = 0.450$)** | **$J = 0.5770$** | $J = 0.4610$ | Peak Youden's Index ($F_1 = 0.5480$) |
| **False Alarm Reduction** | **64.2%** | Reference | Statistically significant alert fatigue mitigation |
| **Advance Lead Time** | **6.0 Hours** | < 2.5 Hours | Critical therapeutic intervention window |

---

## 🗂️ Repository Directory Structure

```text
├── AegisSepsis_AI_100Page_Master_Technology_Codebook.pdf   # 105-Page Complete Monograph & Codebook
├── AegisSepsis_AI_Master_AI_Model_Training_Testing_Codebook.pdf # 65-Page AI/ML Architecture & Training Monograph
├── AegisSepsis_AI_Technology_Master_Interview_Guide.pdf     # Technical Interview & Defense Guide
├── AegisSepsis_AI_Full_Implementation.ipynb                # Master End-to-End Jupyter Notebook
├── AegisSepsis_AI_Full_Implementation.html                 # Rendered Interactive Research Notebook
│
├── backend/                                                # High-Performance Microservice Layer
│   ├── server.py                                           # Multi-Threaded Native REST & PDF Stream Server
│   └── (REST endpoints: /api/predict, /api/generate-pdf, /api/simulate-stream)
│
├── frontend/                                               # Single Page Application (SPA) Web Dashboard
│   └── index.html                                          # Dark Glassmorphic Clinical Cockpit with Dynamic tau-slider
│
├── models/                                                 # Feature Engineering & Model Weights
│   ├── master_sepsis_pipeline.py                           # 122 Causal Trajectory Feature Engine
│   └── (Pre-trained serialized weights & scalers)
│
├── training/                                               # Neural Training, Locking & Visualization Scripts
│   ├── execute_observation_process_validation.py           # Decoupled Dual-Stream PyTorch Training Engine
│   ├── execute_final_statistical_lock.py                  # Threshold Search & Calibration Locks
│   ├── execute_claim_forensics_audit.py                   # Zero-Leakage & Patient Overlap Audits
│   ├── generate_patient_pdf.py                            # ReportLab Clinical PDF Generator
│   ├── generate_20_publication_figures.py                 # Matplotlib Vector Plot Generator
│   ├── build_100page_technology_codebook.py               # 105-Page Monograph Generator
│   └── build_ai_model_master_codebook.py                  # 65-Page AI Codebook Generator
│
├── figures/                                                # Publication-Grade Vector Plots
│   ├── Fig1_ROC_Curves.png                                # Cross-cohort ROC comparison
│   ├── Fig2_Calibration_Reliability.png                   # Platt scaling calibration curves
│   ├── Fig3_TreeSHAP_Attributions.png                     # Feature importance explanations
│   └── (20+ publication figures)
│
├── documents/                                              # Research Documentation & Academic Review Files
│   ├── AegisSepsis_AI_300Page_Scientific_Master_Monograph.pdf
│   ├── AegisSepsis_AI_Full_Manuscript.pdf
│   ├── AegisSepsis_AI_IEEE_Revised.pdf
│   └── REVIEW-2 DOCUMENT FORMAT-Corrected.docx
│
└── dataset/                                                # Research Data Splits & Cleaned Cohorts
    ├── dataset_v2_unified_2115_patients_6h.csv             # Cleaned 6-Hour Trajectory Benchmark
    ├── training_setA/                                      # Emory ICU Cohort (Set A)
    └── training_setB/                                      # BIDMC ICU Cohort (Set B)
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Environment Setup
Clone this repository and ensure Python 3.10+ is installed:
```bash
git clone https://github.com/sudhanshu-jha45/AI-Based-Early-Sepsis-Risk-Prediction-.git
cd AI-Based-Early-Sepsis-Risk-Prediction-
pip install -r requirements.txt # (numpy, pandas, scikit-learn, torch, reportlab, pypdf, matplotlib, seaborn, joblib)
```

### 2. Launch the Web Application & Interactive Dashboard
Start the microservice backend server:
```bash
python backend/server.py
```
Open your browser and navigate to:
```text
http://localhost:8888/
```
The glassmorphic dashboard provides:
* **Real-time Patient Simulator:** Stream synthetic ICU vital trajectories hour-by-hour.
* **Interactive Operating Threshold ($\tau$) Slider:** Adjust $\tau \in [0.100, 0.900]$ with dynamic recalculation of Sensitivity, Specificity, Precision, $F_1$, and False Alarm Reduction.
* **1-Click Clinical PDF Report Generation:** Instantly compile publication-grade diagnostic summaries.

### 3. Run Inference & Verification Scripts
Execute the observation process validation experiment:
```bash
python training/execute_observation_process_validation.py
```
Execute the final statistical lock:
```bash
python training/execute_final_statistical_lock.py
```
Generate patient clinical report PDF:
```bash
python training/generate_patient_pdf.py
```

---

## 📜 Complete PDF Monographs Available
This repository includes full-length, publication-grade monographs detailing every equation, line of code, and architectural proof:
1. **[105-Page Master Technology & Codebook Monograph](AegisSepsis_AI_100Page_Master_Technology_Codebook.pdf):** Complete untruncated source code for all components, line-by-line architectural breakdown, and 25 interview Q&As.
2. **[65-Page AI/ML Architecture & Training Monograph](AegisSepsis_AI_Master_AI_Model_Training_Testing_Codebook.pdf):** In-depth mathematical derivations of decoupled neural models, MMD gradient penalties, 122 causal features, and 30 technical interview Q&As.
3. **[Interview & Defense Guide](AegisSepsis_AI_Technology_Master_Interview_Guide.pdf):** Concise technical summary for technical reviews and viva defense.

---

## ⚖️ License
This project is open-source under the [MIT License](LICENSE).
