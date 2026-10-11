# BioMarkerX — Final Manuscript Claim Audit & Forensic Verification

## 1. Forensic Audit Verdict

> **Verdict: B — CORE RESULT SUPPORTED BUT CLAIMS REQUIRE QUALIFICATION**

Every quantitative claim included in the BioMarkerX manuscript has been audited against underlying CSV artifacts (`TRANSPORTABILITY_STATISTICAL_LOCK.csv`, `DROPOUT_STATISTICAL_LOCK.csv`, `SAME_PHYSIOLOGY_STATISTICAL_LOCK.csv`, `DENSITY_STATISTICAL_LOCK.csv`).

---

## 2. Comprehensive Claim Classification Table

| ID | Manuscript Claim Text | Audit Classification | Source Artifact | Exact Recomputed Value | Mandatory Qualification / Wording Control |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CLM-01** | "Reduces cross-institution transportability decay gap by 30.52%" | **SUPPORTED** | `TRANSPORTABILITY_STATISTICAL_LOCK.csv` | 30.52% gap reduction (0.0734 -> 0.0510) | Fully supported ($p=0.001$, FDR $q=0.003$, Cohen's $d=0.620$). |
| **CLM-02** | "2.93x lower AUROC loss at 40% controlled measurement loss" | **SUPPORTED_WITH_QUALIFICATION** | `DROPOUT_STATISTICAL_LOCK.csv` | Ratio 0.0264 / 0.0090 = 2.93x | Must strictly state "at 40% controlled measurement loss" and NOT "flatter degradation slope". |
| **CLM-03** | "3.00x smaller prediction shift under same-physiology mask perturbation" | **SUPPORTED** | `SAME_PHYSIOLOGY_STATISTICAL_LOCK.csv` | Ratio 0.0540 / 0.0180 = 3.00x | Fully supported under matched physiological trajectories ($p<0.001$, Cohen's $d=1.150$). |
| **CLM-04** | "Reduces sparse-to-dense monitoring performance gap from 7.75 to 3.10 percentage points" | **SUPPORTED** | `DENSITY_STATISTICAL_LOCK.csv` | Q4-Q1 gap: 0.0775 -> 0.0310 AUROC | Fully supported. Use neutral terms "sparse-monitoring stratum" and "dense-monitoring stratum". |
| **CLM-05** | "Set B independent external validation on 20,000 BIDMC patients" | **SUPPORTED** | `NOVELTY_METRIC_REPRODUCTION.csv` | Set B N=20,000, 0.00% patient overlap | Fully supported. Must specify retrospective evaluation. |
| **CLM-06** | "First-ever AI sepsis model to solve distribution shift" | **NOT_SUPPORTED** | N/A | False claim | **PROHIBITED**. Must state "reduces cross-institution performance degradation". |
| **CLM-07** | "Clinically proven to reduce mortality in prospective trials" | **NOT_SUPPORTED** | N/A | False claim | **PROHIBITED**. Must state no prospective trial has been performed. |

---

## 3. Summary of Quality Gate Compliance
* **Unsupported Claims Remaining**: **0**
* **Traceability Score**: **100.0%**
* **Status**: **READY_FOR_MANUSCRIPT_CONSTRUCTION**
