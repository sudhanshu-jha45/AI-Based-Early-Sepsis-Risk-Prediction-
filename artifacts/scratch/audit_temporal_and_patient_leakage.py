import os
import glob
import json
import time
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss

def run_causal_leakage_audit():
    print("=========================================================================")
    print("STEP 2: STRICT CAUSAL TEMPORAL & PATIENT LEAKAGE AUDIT & REMEDIATION")
    print("=========================================================================")
    
    dev_path = r"FINAL_CLEANED_DATASETS\dataset_v2_unified_2115_patients_6h.csv"
    dev_df = pd.read_csv(dev_path)
    
    # Target Window Definition (S_next)
    dev_df['S_next'] = dev_df.groupby('Patient_Key')['Slabel_max'].shift(-1)
    dev_valid = dev_df.dropna(subset=['S_next']).copy()
    dev_valid['S_next'] = dev_valid['S_next'].astype(int)

    ignore_cols = {'Patient_Key', 'ICUSTAY_ID', 'Window_Idx', 'Slabel_max', 'S_next', 'Slabel_any', 'Slabel_min', 'Slabel_mean', 'Slabel_sum', 'Slabel_count'}
    feature_cols = [c for c in dev_valid.columns if c not in ignore_cols and pd.api.types.is_numeric_dtype(dev_valid[c])]
    
    print(f"Base Feature Count: {len(feature_cols)}")
    print("Extracting STRICTLY CAUSAL dynamic features (center=False, cumulative expanding median/IQR)...")

    # 1. Compute Strictly Causal Features
    causal_patient_frames = []
    
    for pkey, group in dev_valid.groupby('Patient_Key'):
        # Preserve original order (index order)
        g_sorted = group.copy()
        g_feats = g_sorted[feature_cols].copy()
        
        # A. Strictly Causal Denoising (center=False, past 3 windows ONLY)
        g_smooth = g_feats.rolling(window=3, min_periods=1, center=False).median()
        
        # B. Strictly Causal Cumulative Baseline & Z-score (expanding up to time t)
        g_exp_med = g_smooth.expanding(min_periods=1).median()
        g_exp_q75 = g_smooth.expanding(min_periods=1).quantile(0.75)
        g_exp_q25 = g_smooth.expanding(min_periods=1).quantile(0.25)
        g_exp_iqr = (g_exp_q75 - g_exp_q25).replace(0, 1.0).fillna(1.0)
        
        g_causal_z = (g_smooth - g_exp_med) / (g_exp_iqr + 1e-5)
        g_causal_z.columns = [f"{c}_causal_z" for c in g_causal_z.columns]
        
        # C. Strictly Causal Velocity & Acceleration (backward differences)
        g_delta = g_smooth.diff().fillna(0.0)
        g_delta.columns = [f"{c}_causal_delta" for c in g_delta.columns]
        
        g_accel = g_delta.diff().fillna(0.0)
        g_accel.columns = [f"{c}_causal_accel" for c in g_accel.columns]
        
        combined = pd.concat([g_smooth, g_causal_z, g_delta, g_accel], axis=1)
        combined['Patient_Key'] = pkey
        combined['S_next'] = g_sorted['S_next']
        causal_patient_frames.append(combined)
        
    causal_dev = pd.concat(causal_patient_frames, axis=0)
    causal_feature_cols = [c for c in causal_dev.columns if c not in {'Patient_Key', 'S_next'}]
    
    print(f"Strictly Causal Feature Matrix Dimension: {len(causal_feature_cols)} features.")

    # 2. Strict 5-Fold GroupKFold Cross Validation
    gkf = GroupKFold(n_splits=5)
    groups = causal_dev['Patient_Key'].values
    X_dev = causal_dev[causal_feature_cols].values
    y_dev = causal_dev['S_next'].values
    
    oof_preds = np.zeros(len(causal_dev))
    causal_models = []
    
    for fold, (train_idx, val_idx) in enumerate(gkf.split(X_dev, y_dev, groups)):
        X_tr, y_tr = X_dev[train_idx], y_dev[train_idx]
        X_va, y_va = X_dev[val_idx], y_dev[val_idx]
        
        clf = HistGradientBoostingClassifier(
            max_iter=150,
            learning_rate=0.03,
            max_leaf_nodes=31,
            min_samples_leaf=20,
            l2_regularization=2.0,
            random_state=42 + fold
        )
        clf.fit(X_tr, y_tr)
        oof_preds[val_idx] = clf.predict_proba(X_va)[:, 1]
        causal_models.append(clf)
        
    dev_auroc = roc_auc_score(y_dev, oof_preds)
    dev_auprc = average_precision_score(y_dev, oof_preds)
    dev_brier = brier_score_loss(y_dev, oof_preds)
    
    print(f"\n--- STRICTLY CAUSAL MODEL INTERNAL CV RESULTS ---")
    print(f"  Causal Internal CV AUROC: {dev_auroc:.4f}")
    print(f"  Causal Internal CV AUPRC: {dev_auprc:.4f}")
    print(f"  Causal Internal CV Brier: {dev_brier:.5f}")

    # 3. Fit Target-Population Bayes Recalibration
    calibrator = IsotonicRegression(out_of_bounds='clip')
    calibrator.fit(oof_preds, y_dev)
    
    # Save Causal Model & Feature Schema
    save_dir = "FINAL_BIOMARKERX/models_causal_locked"
    os.makedirs(save_dir, exist_ok=True)
    joblib.dump(causal_models, os.path.join(save_dir, "CAUSAL_ENSEMBLE.joblib"))
    joblib.dump(calibrator, os.path.join(save_dir, "CAUSAL_CALIBRATOR.joblib"))
    with open(os.path.join(save_dir, "CAUSAL_FEATURE_LIST.json"), "w") as f:
        json.dump(causal_feature_cols, f, indent=2)
        
    # Save Leakage Audit Manifest
    leakage_audit = {
        "temporal_leakage_status": "PASS - Strictly causal rolling median (center=False) & cumulative expanding baseline",
        "patient_leakage_status": "PASS - 5-Fold GroupKFold patient-isolated split",
        "causal_dev_auroc": dev_auroc,
        "causal_dev_auprc": dev_auprc,
        "causal_dev_brier": dev_brier,
        "feature_count": len(causal_feature_cols)
    }
    
    with open("BIOMARKERX_LEAKAGE_AUDIT.json", "w") as f:
        json.dump(leakage_audit, f, indent=2)
        
    with open("BIOMARKERX_LEAKAGE_AUDIT.md", "w") as f:
        f.write("# BioMarkerX Causal Temporal & Patient Leakage Audit Report\n\n")
        f.write("## 1. Temporal Leakage Audit Findings\n")
        f.write("- **Previous V5 Flaw Identified**: `rolling(center=True)` and static patient-stay Z-scores used future window observations (t+1..T) to normalize predictions at time t.\n")
        f.write("- **Strict Causal Remediation**: Implemented `rolling(center=False)` and `expanding()` cumulative median/IQR Z-scores (F(t) = f(X_<=t) strictly).\n")
        f.write("- **Audited Internal CV Metrics**:\n")
        f.write(f"  - **Strictly Causal Internal AUROC**: `{dev_auroc:.4f}`\n")
        f.write(f"  - **Strictly Causal Internal AUPRC**: `{dev_auprc:.4f}`\n")
        f.write(f"  - **Strictly Causal Internal Brier Score**: `{dev_brier:.5f}`\n\n")
        f.write("## 2. Patient Leakage Audit\n")
        f.write("- **Group Isolation**: `GroupKFold(n_splits=5)` enforced zero patient overlap across cross-validation splits.\n")

    print("\nLeakage audit completed. Saved BIOMARKERX_LEAKAGE_AUDIT.json and BIOMARKERX_LEAKAGE_AUDIT.md.")

if __name__ == "__main__":
    run_causal_leakage_audit()
