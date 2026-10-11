# BioMarkerX — Scientific Publication & Validation Roadmap

| Phase | Milestone | Objective | Status | Key Deliverable |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1** | Data Forensic Accounting | Reconstruct exact CONSORT cohort flow for Set A & Set B | **COMPLETED** | `COHORT_FLOW.csv` |
| **Phase 2** | Feature Reconciliation | Resolve 122 feature manifest schema inconsistency | **COMPLETED** | `FEATURE_RECONCILIATION.csv` |
| **Phase 3** | Literature Audit Matrix | Audit 10+ key sepsis ML papers for exact novelty overlap | **COMPLETED** | `LITERATURE_MATRIX.csv` |
| **Phase 4** | Controlled Feature Ablation | Run EXP-0 to EXP-9 feature & policy component ablations | **COMPLETED** | `ABLATION_RESULTS.csv` |
| **Phase 5** | Statistical Uncertainty | Compute paired bootstrap 95% CIs for all metric deltas | **COMPLETED** | `ABLATION_STATISTICAL_COMPARISON.csv` |
| **Phase 6** | Observation Density Analysis | Quantify sampling frequency shift & PSI between Set A and Set B | **COMPLETED** | `OBSERVATION_DENSITY_AUDIT.csv` |
| **Phase 7** | Density-Robust Modeling | Train observation-process regularized baseline model | **PLANNED** | Candidate Model EXP-9 |
| **Phase 8** | Locked Internal Validation | Freeze model parameters and evaluate on Set A test split | **COMPLETED** | AUROC 0.7895, AUPRC 0.1245 |
| **Phase 9** | Independent External Validation | Evaluate frozen pipeline on uncalibrated Set B | **COMPLETED** | AUROC 0.7161, Sensitivity 71.2% |
| **Phase 10** | Subgroup & Calibration Audit | Evaluate performance across LOS and missingness strata | **COMPLETED** | `MISSINGNESS_AUDIT.csv` |
| **Phase 11** | Final Novelty Freeze | Classify each component as Supported, Promising, or Engineering | **COMPLETED** | `NOVELTY_CLAIM_MATRIX.csv` |
| **Phase 12** | Manuscript Drafting | Prepare defensible scientific manuscript for journal review | **READY** | `PUBLICATION_CLAIMS.md` |
