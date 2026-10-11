import os
import glob
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss

def run_large_physionet_experiment():
    print("=========================================================================")
    print("STRATEGY DISCOVERY: LARGE-SCALE PHYSIONET (20,336 PATIENTS) EXPERIMENT")
    print("=========================================================================")
    
    psv_files = glob.glob('training_setA/*.psv')
    print(f"Total PhysioNet 2019 PSV Files Found: {len(psv_files)}")
    
    sample_files = psv_files[:5000]
    patient_dfs = []
    
    for fpath in sample_files:
        pdf = pd.read_csv(fpath, sep='|')
        pdf['Patient_Key'] = os.path.basename(fpath).replace('.psv', '')
        pdf['S_next'] = pdf['SepsisLabel'].shift(-1)
        pdf_valid = pdf.dropna(subset=['S_next']).copy()
        if len(pdf_valid) > 0:
            patient_dfs.append(pdf_valid)
            
    full_df = pd.concat(patient_dfs, axis=0)
    print(f"Loaded {len(full_df)} risk windows across {full_df['Patient_Key'].nunique()} patients.")
    
    ignore_cols = {'Patient_Key', 'SepsisLabel', 'S_next'}
    feature_cols = [c for c in full_df.columns if c not in ignore_cols and pd.api.types.is_numeric_dtype(full_df[c])]
    
    # Drop all-NaN columns
    valid_feats = []
    for c in feature_cols:
        if full_df[c].dropna().nunique() > 1:
            valid_feats.append(c)
            
    print(f"Valid Non-Constant Features Count: {len(valid_feats)}")
    
    # 50/50 Train/Test Split
    pts = list(full_df['Patient_Key'].unique())
    np.random.seed(42)
    np.random.shuffle(pts)
    
    train_pts = set(pts[:2500])
    test_pts = set(pts[2500:])
    
    train_df = full_df[full_df['Patient_Key'].isin(train_pts)]
    test_df = full_df[full_df['Patient_Key'].isin(test_pts)]
    
    X_tr = train_df[valid_feats].fillna(train_df[valid_feats].median()).values
    y_tr = train_df['S_next'].astype(int).values
    
    X_te = test_df[valid_feats].fillna(train_df[valid_feats].median()).values
    y_te = test_df['S_next'].astype(int).values
    
    clf = HistGradientBoostingClassifier(max_iter=100, learning_rate=0.05, random_state=42)
    clf.fit(X_tr, y_tr)
    
    preds_te = clf.predict_proba(X_te)[:, 1]
    
    auc_te = roc_auc_score(y_te, preds_te)
    auprc_te = average_precision_score(y_te, preds_te)
    brier_te = brier_score_loss(y_te, preds_te)
    
    print(f"\n=========================================================================")
    print(f"PHYSIONET 50/50 SPLIT RESULTS (Train 2,500 pts, Test 2,500 pts):")
    print(f"  PhysioNet Internal Test AUROC: {auc_te:.4f}")
    print(f"  PhysioNet Internal Test AUPRC: {auprc_te:.4f}")
    print(f"  PhysioNet Internal Test Brier: {brier_te:.5f}")
    print(f"=========================================================================")

if __name__ == "__main__":
    run_large_physionet_experiment()
