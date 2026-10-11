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
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, roc_curve, precision_recall_curve

def run_v4_master_remediation():
    print("=========================================================================")
    print("EXECUTING BIOMARKERX V4 MASTER SCIENTIFIC REMEDIATION PIPELINE")
    print("=========================================================================")
    
    start_time = time.time()
    
    # Paths
    dev_path = r"FINAL_CLEANED_DATASETS\dataset_v2_unified_2115_patients_6h.csv"
    ext_path = r"external_test_A\predictions\external_test_predictions.csv" # fallback if needed
    
    if not os.path.exists(dev_path):
        print(f"Error: Dev dataset {dev_path} not found.")
        return
        
    dev_df = pd.read_csv(dev_path)
    print(f"Loaded Development Cohort: {dev_df.shape[0]} rows, {dev_df.shape[1]} columns across {dev_df['Patient_Key'].nunique()} patients.")

    # 1. Target Window Definition
    dev_df['S_next'] = dev_df.groupby('Patient_Key')['Slabel_max'].shift(-1)
    dev_valid = dev_df.dropna(subset=['S_next']).copy()
    dev_valid['S_next'] = dev_valid['S_next'].astype(int)
    
    ignore_cols = {'Patient_Key', 'ICUSTAY_ID', 'Window_Idx', 'Slabel_max', 'S_next', 'Slabel_any', 'Slabel_min', 'Slabel_mean', 'Slabel_sum', 'Slabel_count'}
    feature_cols = [c for c in dev_valid.columns if c not in ignore_cols and pd.api.types.is_numeric_dtype(dev_valid[c])]
    
    print(f"Base physiological feature count: {len(feature_cols)}")

    # 2. Compute Intra-Patient Relative Dynamic Trajectories (Z-Score & Delta)
    print("Computing Intra-Patient Z-Score Standardization & Relative Dynamics...")
    dev_z_list = []
    
    # Group by patient for intra-patient standardization
    for pkey, group in dev_valid.groupby('Patient_Key'):
        g_feats = group[feature_cols].copy()
        
        # Median and IQR per patient
        p_med = g_feats.median()
        p_iqr = g_feats.quantile(0.75) - g_feats.quantile(0.25)
        p_iqr = p_iqr.replace(0, 1.0).fillna(1.0)
        
        # Z-score relative to patient baseline
        g_z = (g_feats - p_med) / (p_iqr + 1e-5)
        
        # Delta features
        g_delta = g_feats.diff().fillna(0.0)
        g_delta.columns = [f"{c}_delta" for c in g_delta.columns]
        
        combined = pd.concat([g_feats, g_z, g_delta], axis=1)
        combined['Patient_Key'] = pkey
        combined['S_next'] = group['S_next']
        dev_z_list.append(combined)
        
    dev_v4 = pd.concat(dev_z_list, axis=0)
    v4_feature_cols = [c for c in dev_v4.columns if c not in {'Patient_Key', 'S_next'}]
    print(f"V4 Feature Matrix Dimension: {len(v4_feature_cols)} features.")

    # 3. 5-Fold GroupKFold Cross-Validation Model Training
    gkf = GroupKFold(n_splits=5)
    groups = dev_v4['Patient_Key'].values
    X_dev = dev_v4[v4_feature_cols].values
    y_dev = dev_v4['S_next'].values
    
    oof_preds = np.zeros(len(dev_v4))
    models = []
    
    for fold, (train_idx, val_idx) in enumerate(gkf.split(X_dev, y_dev, groups)):
        X_tr, y_tr = X_dev[train_idx], y_dev[train_idx]
        X_va, y_va = X_dev[val_idx], y_dev[val_idx]
        
        clf = HistGradientBoostingClassifier(
            max_iter=150,
            learning_rate=0.05,
            max_leaf_nodes=31,
            min_samples_leaf=20,
            l2_regularization=1.0,
            random_state=42 + fold
        )
        clf.fit(X_tr, y_tr)
        oof_preds[val_idx] = clf.predict_proba(X_va)[:, 1]
        models.append(clf)
        
    dev_auroc = roc_auc_score(y_dev, oof_preds)
    dev_auprc = average_precision_score(y_dev, oof_preds)
    dev_brier = brier_score_loss(y_dev, oof_preds)
    
    print(f"\nBioMarkerX V4 Internal Cross-Validation Results:")
    print(f"  Internal AUROC: {dev_auroc:.4f}")
    print(f"  Internal AUPRC: {dev_auprc:.4f}")
    print(f"  Internal Brier: {dev_brier:.5f}")

    # 4. Target-Population Bayes Logit Recalibration
    pi_dev = np.mean(y_dev)
    print(f"Development Cohort Prevalence: {pi_dev:.4f}")
    
    # Fit Isotonic Calibrator on OOF predictions
    calibrator = IsotonicRegression(out_of_bounds='clip')
    calibrator.fit(oof_preds, y_dev)
    
    # 5. Save V4 Locked Models & Artifacts
    v4_model_dir = "FINAL_BIOMARKERX/models_v4"
    os.makedirs(v4_model_dir, exist_ok=True)
    
    joblib.dump(models, os.path.join(v4_model_dir, "BIOMARKERX_V4_ENSEMBLE.joblib"))
    joblib.dump(calibrator, os.path.join(v4_model_dir, "BIOMARKERX_V4_CALIBRATOR.joblib"))
    
    # Save Feature Mapping
    with open(os.path.join(v4_model_dir, "V4_FEATURE_LIST.json"), "w") as f:
        json.dump(v4_feature_cols, f, indent=2)
        
    exec_time = time.time() - start_time
    print(f"\n=========================================================================")
    print(f"BIOMARKERX V4 MASTER REMEDIATION PIPELINE COMPLETED IN {exec_time:.2f}s")
    print(f"Artifacts locked in {v4_model_dir}")
    print("=========================================================================")

if __name__ == "__main__":
    run_v4_master_remediation()
