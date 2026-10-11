# Section 1: Introduction

Early identification of sepsis in intensive care unit (ICU) patients remains a paramount clinical challenge. Sepsis is a life-threatening organ dysfunction caused by a dysregulated host response to infection, accounting for nearly 20% of all global deaths and over 30% of in-hospital ICU mortalities. Early therapeutic intervention—particularly timely antimicrobial administration and targeted fluid resuscitation—significantly improves clinical outcomes. Consequently, machine learning early-warning systems designed to detect acute physiological deterioration 1 to 6 hours prior to clinical sepsis onset have attracted intense interest.

However, clinical risk prediction models deployed across intensive care units encounter a major obstacle: **cross-institution dataset shift and transportability failure**. Models that demonstrate high retrospective discrimination during internal validation frequently suffer substantial performance degradation when transferred to independent external health systems. A critical but frequently under-studied driver of this transportability gap is the **ICU observation process**. In electronic health records (EHR), clinical data streams are irregularly sampled. The decision to order a laboratory test or record a vital sign is not random; it reflects clinician suspicion, nursing shift schedules, ICU staffing levels, and institutional clinical practice guidelines.

Conventional clinical machine learning architectures often fail to separate the patient's underlying physiological state from the surrounding observation process. When models concatenate raw vital signs with missingness indicators without causal normalization, they risk overfitting to site-specific clinician ordering habits. When deployed in a secondary institution with different testing frequencies or lower monitoring density, the model misinterprets altered observation frequency as physiological deterioration, leading to severe transportability decay.

While existing literature has explored longitudinal trajectory modeling (e.g., MGP-RNN, Futoma et al., 2017), missingness-aware recurrent architectures (e.g., GRU-D, Che et al., 2018), and causal invariance selection (e.g., Subbaswamy et al., 2019), these paradigms do not explicitly establish whether architectural decoupling of physiological trajectories from observation processes enhances cross-institution transportability without sacrificing internal predictive power.

---

## Research Question & Hypotheses

To address this gap, this study investigates the central research question:

> **"Can explicitly modeling the ICU observation process reduce the sensitivity of early sepsis prediction to variation in measurement density and missingness, thereby improving cross-institution transportability?"**

We formulate and test four formal hypotheses:
* **H1 (Primary Hypothesis — Measurement Robustness)**: Observation-process-aware causal trajectory modeling produces smaller performance degradation under controlled changes in ICU measurement availability than conventional physiological representations.
* **H2 (Secondary Hypothesis — Institutional Transportability)**: Observation-process-aware modeling reduces cross-institution performance degradation when evaluated on an independent external institutional cohort.
* **H3 (Secondary Hypothesis — Same-Physiology Invariance)**: Observation-process-aware modeling produces smaller prediction shifts when the underlying physiological trajectory is held constant but observation availability is perturbed.
* **H4 (Secondary Hypothesis — Observation-Density Parity)**: Observation-process-aware modeling reduces the performance disparity between sparse- and dense-monitoring environments.

---

## Primary Scientific Contributions

The primary scientific contribution of this work is a measurement-process-aware causal trajectory framework for transportable early sepsis prediction. Specifically, our contribution is threefold:
1. **Architectural Decoupling**: We introduce a dual-representation architecture that separates causally normalized physiological trajectory dynamics ($Z_{i,t}, \frac{dZ}{dt}, \frac{d^2Z}{dt^2}$) from explicit observation-process vectors ($M_{i,t}, \Delta t_{i,t}, N_{i,t}$).
2. **Controlled Stress-Testing Framework**: We design a stress-testing protocol combining synthetic controlled measurement loss, same-physiology perturbation analysis, and monitoring-density stratification to isolate observation-process sensitivity from physiological variation.
3. **Independent Institutional Validation**: Evaluated on an independent 20,000-patient external cohort (BIDMC Set B), our framework achieves a 30.52% reduction in institutional transportability decay ($p=0.001$, FDR $q=0.003$) relative to standard trajectory representations.
