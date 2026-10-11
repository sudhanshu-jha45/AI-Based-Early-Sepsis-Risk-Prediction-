# BioMarkerX — Strictly Prohibited Scientific Claims

To maintain scientific auditability and avoid peer-review rejection, the following **10 prohibited claim types** MUST NOT appear in any manuscript, abstract, presentation, or webpage:

1. **PROHIBITED**: Claiming a "2.93× flatter degradation slope".
   * **CORRECTION**: Must strictly state *"2.93× lower AUROC loss at 40% controlled measurement loss"* because no linear regression slope was fitted across all 6 dropout levels.
2. **PROHIBITED**: Claiming "first-ever AI sepsis model" or "unprecedented performance".
   * **CORRECTION**: Use evidence-based relative statements comparing BioMarkerX to standard baseline models.
3. **PROHIBITED**: Claiming "solves distribution shift" or "eliminates measurement bias".
   * **CORRECTION**: Use *"reduces cross-institution performance degradation"* (Set B AUROC gap remains $0.0510$).
4. **PROHIBITED**: Claiming "universally transportable across all health systems".
   * **CORRECTION**: Limit claims strictly to the evaluated Emory Set A ($N=2,974$) and BIDMC Set B ($N=20,000$) cohorts.
5. **PROHIBITED**: Calling Set B validation "multicenter prospective clinical validation".
   * **CORRECTION**: Must strictly label Set B as *"independent external retrospective validation ($N=20,000$)"*.
6. **PROHIBITED**: Claiming "clinically proven to reduce sepsis mortality".
   * **CORRECTION**: Must state that no prospective silent trial or randomized clinical trial has been conducted.
7. **PROHIBITED**: Claiming "equitable performance across all patient demographics".
   * **CORRECTION**: Use neutral technical phrasing such as *"reduced performance disparity between sparse- and dense-monitoring strata"*.
8. **PROHIBITED**: Claiming "proved causal mediation of missingness".
   * **CORRECTION**: Label mechanisms as *"proposed mechanisms evaluated via controlled perturbation stress tests"*.
9. **PROHIBITED**: Claiming "zero performance loss under missing data".
   * **CORRECTION**: Report exact non-zero loss values ($0.0090$ AUROC loss at 40% dropout).
10. **PROHIBITED**: Framing supporting engineering features (SHAP, dual thresholds, LOS persistence) as central novelties.
    * **CORRECTION**: Treat supporting components strictly as operational helpers secondary to measurement-process-aware causal trajectory modeling.
