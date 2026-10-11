# BioMarkerX — Temperature Scaling Calibration Audit

## Mathematical Invariance Verification
- **Temperature Parameter (T)**: `1.12`
- **AUROC Before Calibration**: `0.86512495`
- **AUROC After Calibration**: `0.86512495`
- **Absolute AUROC Difference**: `0.00000000e+00`

### **Scientific Verdict**
Temperature scaling is a strictly monotonic transformation ($p_{\text{cal}} = \sigma(z / T)$). Because rank-ordering is preserved, **Temperature Scaling CANNOT change ROC AUC by even $10^{-12}$**. Attributing AUROC improvements (0.8658 -> 0.8707) to temperature scaling is **MATHEMATICALLY INCORRECT**.