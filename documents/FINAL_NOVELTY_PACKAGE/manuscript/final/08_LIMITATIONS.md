# Section 6: Explicit Study Limitations

The following **13 explicit scientific limitations** must be acknowledged when interpreting the findings of this study:

1. **Retrospective Evaluation of Set B**: Independent external validation on BIDMC Set B ($N=20,000$) is retrospective; real-time deployment dynamics were not prospectively measured.
2. **PhysioNet 2019 Ecosystem Restriction**: Both Emory Set A and BIDMC Set B originate from the PhysioNet Challenge 2019 benchmark ecosystem; evaluation across geographically diverse non-challenge health systems remains required.
3. **Single External Institution**: External validation is restricted to a single secondary academic medical center (BIDMC); validation across community hospitals and regional health networks is needed.
4. **Dataset Sepsis Label Proxy**: Dataset-defined Sepsis-3 labels depend on EHR chart records and billing codes, which are not perfectly equivalent to adjudicated real-time bedside clinical onset.
5. **Synthetic Controlled Measurement Loss**: Controlled measurement-loss stress tests ($0\%\text{--}80\%$) utilize synthetic uniform dropout, which may not fully capture non-random clinical missingness mechanics.
6. **Observation Density as Proxy**: Clinical measurement density is an indirect proxy for the underlying clinical decision-making process.
7. **Absence of Prospective Silent Trial**: No prospective silent clinical trial has been conducted to measure real-world alert volume or clinician acceptance.
8. **Absence of Randomized Clinical Trial**: No randomized controlled trial (RCT) has been performed to evaluate patient outcomes or survival benefit.
9. **External Performance Decay**: External performance on Set B ($0.7310$ AUROC) remains lower than internal performance on Set A ($0.7820$ AUROC), proving that dataset shift is reduced but not eliminated.
10. **Non-Zero Transportability Decay**: Observation-process-aware modeling does not completely eliminate institutional transportability degradation.
11. **Measurement Density Severity Confounding**: Clinical measurement density is intrinsically correlated with patient illness severity; associations between missingness representations and transportability require cautious interpretation.
12. **Internal Discrimination Trade-off**: Observation-aware Model F trades a minor amount of internal Set A AUROC ($0.7820$ vs $0.7895$) in exchange for improved external Set B AUROC ($0.7310$ vs $0.7161$).
13. **Prohibition of Universal Transportability Claims**: The empirical evidence does not support claims of "universal transportability," "guaranteed cross-site invariance," or "complete elimination of bias."
