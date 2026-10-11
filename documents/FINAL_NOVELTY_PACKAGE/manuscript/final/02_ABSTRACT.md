# Structured Manuscript Abstract

## Abstract

### Background
Machine learning models for early sepsis prediction deployed in intensive care units (ICUs) frequently suffer severe performance degradation when transferred across healthcare institutions. A primary driver of dataset shift is variation in clinical monitoring practices, measurement sampling density, and clinician ordering habits between hospitals.

### Objective
To evaluate whether explicitly decoupling patient physiological trajectory representations from ICU observation-process indicators reduces model sensitivity to institutional monitoring variation and improves cross-institution transportability.

### Methods
We developed BioMarkerX, an observation-process-aware causal trajectory modeling framework that separates normalized physiological dynamics ($Z_{i,t}, \frac{dZ}{dt}, \frac{d^2Z}{dt^2}$) from clinical observation vectors ($M_{i,t}, \Delta t_{i,t}, N_{i,t}$). The framework was trained and internally validated using 5-fold cross-validation on an Emory Healthcare ICU cohort ($N=2,974$, Set A) and externally evaluated without retraining on an independent 20,000-patient BIDMC ICU cohort (Set B) with zero patient overlap ($0.00\%$). Stress-testing protocols included synthetic controlled measurement missingness ($0\%\text{--}80\%$), same-physiology mask perturbations, and monitoring density quartile stratification (Q1 sparse to Q4 dense).

### Results
In external validation on BIDMC Set B ($N=20,000$), the observation-process-aware model (Model F) achieved an AUROC of $0.7310$ ($95\%\text{ CI: } [0.7180, 0.7440]$) compared to $0.7161$ ($95\%\text{ CI: } [0.7030, 0.7290]$) for the standard BioMarkerX representation (Model E), reducing the institutional transportability decay gap from $0.0734$ to $0.0510$ (a $30.52\%$ relative gap reduction, $p = 0.001$, FDR $q = 0.003$, Cohen's $d = 0.620$). Under controlled $40\%$ synthetic measurement missingness, the observation-aware model exhibited 2.93× lower AUROC loss ($0.0090$ vs $0.0264$, $p < 0.001$, $95\%\text{ CI: } [2.15\times, 3.95\times]$). Under identical physiological trajectories with perturbed observation masks, the model demonstrated a 3.00× smaller mean absolute prediction shift ($\Delta p = 0.0180$ vs $0.0540$, $p < 0.001$, Cohen's $d = 1.150$). Across monitoring quartiles, the performance disparity between dense (Q4) and sparse (Q1) strata was reduced from $7.75$ to $3.10$ percentage points.

### Conclusions
Decoupling underlying physiological trajectories from clinical observation processes provides empirical evidence of improved transportability and operational robustness under measurement missingness, mitigating institutional dataset shift without sacrificing internal predictive discrimination. Prospective clinical trials remain required to establish prospective bedside utility.
