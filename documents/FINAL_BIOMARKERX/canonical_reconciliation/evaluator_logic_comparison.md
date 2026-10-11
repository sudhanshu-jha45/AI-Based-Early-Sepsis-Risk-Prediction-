# BioMarkerX — Evaluator Source Code Logic Comparison

## 1. Code Comparison: Target Horizon & Label Processing

```python
# =============================================================================
# A. CANONICAL EVALUATOR LOGIC (canonical_evaluate_policy.py)
# =============================================================================
s_series = pdf['SepsisLabel']
s_next4 = (s_series.shift(-1).fillna(0) + 
           s_series.shift(-2).fillna(0) + 
           s_series.shift(-3).fillna(0) + 
           s_series.shift(-4).fillna(0) > 0).astype(int)

df['S_next4'] = s_next4
df['S_next1'] = s_series.shift(-1)
pdf_valid = df.dropna(subset=['S_next1']).copy()

# Discrimination metrics evaluated against 4-hour forward lookahead horizon:
y_true4 = pdf_valid['S_next4'].values
raw_preds = pdf_valid['pred'].values
auroc = float(roc_auc_score(y_true4, raw_preds))
auprc = float(average_precision_score(y_true4, raw_preds))
brier = float(brier_score_loss(y_true4, raw_preds))

# =============================================================================
# B. PUBLICATION NOVELTY LOCK LOGIC (execute_publication_grade_novelty_lock.py)
# =============================================================================
pdf["S_next"] = pdf["SepsisLabel"].shift(-1)
valid = pdf.dropna(subset=["S_next"]).copy()

# Discrimination metrics evaluated against 1-hour forward single step:
y_true1 = valid["S_next"].values
raw_preds = valid["pred"].values
auroc = float(roc_auc_score(y_true1, raw_preds))
auprc = float(average_precision_score(y_true1, raw_preds))
brier = float(brier_score_loss(y_true1, raw_preds))
```

### **Analysis of Difference**
1. **Target Horizon**:
   - Canonical Evaluator uses `S_next4` (4-hour forward lookahead: S(k+1) or S(k+2) or S(k+3) or S(k+4)), matching the official early warning mandate of predicting deterioration within 4 hours.
   - Novelty Lock Evaluator used `S_next1` (1-hour immediate step: S(k+1)).
2. **Impact on Metrics**:
   - Model predictions on `S_next4` give **AUROC = 0.7895**, **AUPRC = 0.1241**, **Brier = 0.02738**.
   - Model predictions on `S_next1` give **AUROC = 0.8651**, **AUPRC = 0.1620**, **Brier = 0.02038**.
   - **Conclusion**: EXP-A AUROC (0.8651) is **NOT a model change**, but an evaluation target horizon shift from 4h to 1h.

---

## 2. Code Comparison: Patient Cohort & Dropna Filtering

```python
# =============================================================================
# A. CANONICAL EVALUATOR COHORT
# =============================================================================
test_files = sorted(glob.glob("training_setA/*.psv")[17362:20336]) # N = 2,974 patients
# Includes patient p117364 in total patient count (N=2,974) and event count (N=279).

# =============================================================================
# B. NOVELTY LOCK EVALUATOR COHORT
# =============================================================================
pdf["S_next"] = pdf["SepsisLabel"].shift(-1)
valid = pdf.dropna(subset=["S_next"]).copy()
if len(valid) == 0:
    continue # Patient p117364 has len(pdf)==1, so valid is empty and patient was skipped!
```

### **Analysis of Difference**
1. Patient `p117364` has only 1 row in raw dataset with `SepsisLabel == 1`.
2. Shifting by -1 produces `NaN` for row 0, leaving 0 valid rows after `dropna()`.
3. Canonical counts `p117364` as a test patient and sepsis event. Novelty lock dropped this patient, reducing patient count from 2,974 to 2,973 and event count by 1.
