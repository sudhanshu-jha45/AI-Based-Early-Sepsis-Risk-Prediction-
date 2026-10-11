# BioMarkerX — Publication Claim Guidelines & Scientific Boundaries

## 1. Approved Publication Claims (Defensible)
1. **Past-Only Normalization**: "We present a strictly temporal-causal, expanding-window normalization method that eliminates future data leakage in retrospective ICU benchmark evaluation."
2. **Dual-Tier Alert Policy**: "An asymmetric two-stage risk policy coupling a high-sensitivity silent screening gate (tau_s = 0.015) with a high-specificity audible confirmation gate (tau_c = 0.300, MAP gate <= 75 mmHg, p=3) significantly reduces false alarm rates while retaining high patient recall."
3. **Observation-Process Transportability Analysis**: "External validation on PhysioNet Set B (BIDMC, N=20,000) demonstrates that external performance degradation (AUROC 0.7895 -> 0.7161) is strongly associated with institutional shifts in measurement density and laboratory sampling frequency (PSI = 0.285)."

## 2. Conservative Claims
1. "Expanding Z-scores offer a practical mechanism for streaming normalization without future lookahead."
2. "Second-order acceleration features yielded minor (+0.0012 AUROC) non-significant empirical gains."
3. "Model transportability is partially preserved but limited by inter-hospital practice variation."

## 3. PROHIBITED CLAIMS (MUST NOT BE MADE)
- **DO NOT CLAIM**: "First-ever AI sepsis early warning system."
- **DO NOT CLAIM**: "Clinically superior or production-ready."
- **DO NOT CLAIM**: "100% transportable or immune to dataset shift."
- **DO NOT CLAIM**: "Proven mortality reduction or prospective clinical utility."
- **DO NOT CLAIM**: "Causal inference model (the model enforces temporal causality, not counterfactual causal inference)."
