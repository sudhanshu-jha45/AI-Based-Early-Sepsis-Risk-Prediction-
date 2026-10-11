# BioMarkerX — Vasopressor & Temporal Leakage Forensic Audit

## 1. Vasopressor Proxy Deconstruction
- **Formula**: `MAP_adjusted = MAP - (VasopressorProxy * 5.0)`
- **Proxy Definition**: `VasopressorProxy = (ShockIndex > 0.9).astype(float) * 1.5`
- **Source Variable**: Synthetic Shock Index (`HR / SBP`), NOT actual Medication Administration Record (MAR) dose.
- **Coefficient 5.0**: Manually selected heuristic coefficient, NOT learned from data.
- **Classification**: **UNVALIDATED HEURISTIC PROXY**. Must be labeled as a heuristic proxy rather than a physiologically validated drug dose.

## 2. Temporal Non-Leakage Confirmation
- Feature engineering employs expanding-window median/IQR (`center=False`). No lookahead leakage detected in raw predictions.
