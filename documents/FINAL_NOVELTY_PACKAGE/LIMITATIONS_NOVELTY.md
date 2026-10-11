# BioMarkerX — Mandatory Scientific Limitations

To ensure absolute publication integrity, the following **12 mandatory scientific limitations** must be explicitly detailed in all manuscript submissions and project reporting:

1. **Retrospective Evaluation of Set B**: Independent external validation on BIDMC Set B ($N=20,000$) is retrospective; real-time deployment dynamics were not prospectively measured.
2. **Cohort Origin Restriction**: External Set B is derived from the PhysioNet 2019 Challenge benchmark cohort; validation across geographically diverse non-challenge health systems remains required.
3. **Absence of Prospective Silent Trial**: No prospective silent clinical trial has been conducted to measure real-world alert volume, clinician burnout, or alert fatigue.
4. **Absence of Randomized Clinical Evaluation**: No randomized controlled trial (RCT) has been performed to evaluate whether BioMarkerX alerts alter clinical decision-making or improve patient survival.
5. **Synthetic Controlled Dropout**: Controlled measurement-loss experiments ($0\%\text{--}80\%$) utilize synthetic uniform dropout, which may not capture complex non-random clinical missingness mechanics.
6. **Incomplete Causal Missingness Mechanics**: Observation-density and missingness experiments do not capture all unobserved confounding factors influencing clinician ordering habits (e.g., staffing ratios, nursing shifts).
7. **Dataset Sepsis Label Proxy**: Dataset-defined Sepsis-3 labels depend on EHR chart records and billing codes, which are not perfectly equivalent to adjudicated real-time bedside clinical onset.
8. **External Performance Decay**: External performance on Set B ($0.7310$ AUROC) remains lower than internal performance on Set A ($0.7820$ AUROC), proving that dataset shift is reduced but not eliminated.
9. **Non-Zero Transportability Degradation**: Observation-process-aware modeling does not completely eliminate institutional transportability degradation.
10. **Contemporary Workflow Re-validation Required**: Performance results reflect historical EHR records and require re-validation under contemporary clinical ICU protocols and modern EHR systems.
11. **Measurement Density Severity Confounding**: Clinical measurement density is intrinsically correlated with patient illness severity; associations between missingness representations and transportability require cautious interpretation.
12. **Prohibition of Universal Transportability Claims**: The empirical evidence does not support claims of "universal transportability," "guaranteed cross-site invariance," or "complete elimination of bias."
