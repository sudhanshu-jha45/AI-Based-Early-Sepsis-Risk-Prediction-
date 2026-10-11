# BioMarkerX Trajectory Gating Provenance Audit

## Provenance & Classification
- **Rule Investigated**: `Shock Index >= 0.85 OR HR_delta > 0.2 OR MAP_delta < -0.2`
- **First Script Lineage**: `develop_v3_high_ppv_sens_engine.py` (Legacy exploratory phase)
- **Pre-specification Status**: **EXPLORATORY / POST-HOC** (Provenance search cannot establish pre-specification prior to test data discovery).
- **Canonical Decision**: Reclassified as an exploratory candidate confirmation filter. Cannot be represented as an original locked baseline policy.

## Validation Performance Impact (tau_s=0.035, tau_c=0.180, p=2)
- **Patient Sensitivity**: Ungated = 79.87% (365/457) vs Gated = 70.02% (320/457)
- **Confirmation PPV**: Ungated = 23.96% vs Gated = 26.47%
- **Confirmation Sensitivity**: Ungated = 13.04% vs Gated = 7.43%
- **Confirmation Alert Burden**: Ungated = 0.37 alerts/pt-day vs Gated = 0.19 alerts/pt-day
