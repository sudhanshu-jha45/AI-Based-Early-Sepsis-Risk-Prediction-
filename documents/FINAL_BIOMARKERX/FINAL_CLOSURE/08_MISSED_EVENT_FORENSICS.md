# BioMarkerX Missed-Event Forensics Report (Locked Test)

## Executive Summary
- **Missed Sepsis Patients**: 42 out of 279 sepsis episodes (15.05%).

## Evidence-Supported Missed-Event Patterns
1. **Low Model Risk Prediction (`FM-01`)**: 42 patients exhibited continuous low predicted probabilities ($P < 0.015$) prior to $SepsisLabel == 1$.
2. **Short ICU Pre-Event Stay**: 18 of the missed patients developed sepsis within <12 hours of ICU admission, providing insufficient pre-onset observation history.
3. **High Feature Missingness**: Missed patients averaged 38.4% missingness across vital sign channels vs 29.1% in detected patients.
