import os
import glob
import json
import time
import hashlib
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, confusion_matrix

def compute_sha256(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def compute_patient_hash(patient_id):
    return int(hashlib.sha256(str(patient_id).encode('utf-8')).hexdigest(), 16) % 100000

def run_lock_and_uncheated_pipeline():
    print("=========================================================================")
    print("1. LOCKING PREVIOUS STRICTLY CAUSAL BIOMARKERX V5 MODEL VERSION")
    print("=========================================================================")
    
    causal_dir = "FINAL_BIOMARKERX/models_causal_locked"
    if os.path.exists(causal_dir):
        manifest = {}
        for f in os.listdir(causal_dir):
            fp = os.path.join(causal_dir, f)
            if os.path.isfile(fp):
                manifest[f] = {
                    "sha256": compute_sha256(fp),
                    "size_kb": round(os.path.getsize(fp) / 1024.0, 2),
                    "last_modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(fp)))
                }
        with open(os.path.join(causal_dir, "PREVIOUS_VERSION_LOCK_MANIFEST.json"), "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"Previous causal model version cryptographically locked in {causal_dir}")
        print(f"Locked {len(manifest)} artifacts.")
    else:
        print("Causal model directory not found.")

    print("\n=========================================================================")
    print("2. EXECUTING UN-CHEATED ZERO-LEAKAGE MASTER PIPELINE (LARGE-SCALE)")
    print("=========================================================================")
    
    start_time = time.time()
    
    # Load PhysioNet 2019 Dataset (5,000 PSV files)
    psv_files = glob.glob('training_setA/*.psv')[:5000]
    print(f"Loading {len(psv_files)} PhysioNet PSV files into un-cheated pipeline...")
    
    physio_dfs = []
    for fpath in psv_files:
        pdf = pd.read_csv(fpath, sep='|')
        pkey = 'PHYS_' + os.path.basename(fpath).replace('.psv', '')
        pdf['Patient_Key'] = pkey
        pdf['S_next'] = pdf['SepsisLabel'].shift(-1)
        pdf_valid = pdf.dropna(subset=['S_next']).copy()
        if len(pdf_valid) > 0:
            physio_dfs.append(pdf_valid)
            
    physio_full = pd.concat(physio_dfs, axis=0).reset_index(drop=True)
    physio_full['S_next'] = physio_full['S_next'].astype(int)
    print(f"Loaded PhysioNet Population: {len(physio_full)} risk windows across {physio_full['Patient_Key'].nunique()} patients.")

    # Base raw features in PhysioNet
    ignore_cols = {'Patient_Key', 'SepsisLabel', 'S_next'}
    feature_cols = [c for c in physio_full.columns if c not in ignore_cols and pd.api.types.is_numeric_dtype(physio_full[c])]
    
    # Filter out columns with no variance
    valid_feature_cols = [c for c in feature_cols if physio_full[c].dropna().nunique() > 1]
    print(f"Valid Base Physiological Features: {len(valid_feature_cols)} features ({valid_feature_cols[:8]}...)")

    # 70% Train / 30% Locked Test Hash Split
    patient_keys = np.array(list(physio_full['Patient_Key'].unique()))
    patient_hashes = np.array([compute_patient_hash(pk) for pk in patient_keys])
    
    train_mask_pts = (patient_hashes % 100) < 70
    train_pts = set(patient_keys[train_mask_pts])
    test_pts = set(patient_keys[~train_mask_pts])
    
    train_df = physio_full[physio_full['Patient_Key'].isin(train_pts)].copy()
    test_df = physio_full[physio_full['Patient_Key'].isin(test_pts)].copy()
    
    print(f"  Training Vault (70%):   {len(train_df)} windows ({len(train_pts)} patients), Sepsis Rate: {train_df['S_next'].mean()*100:.2f}%")
    print(f"  Locked Test Vault (30%): {len(test_df)} windows ({len(test_pts)} patients), Sepsis Rate: {test_df['S_next'].mean()*100:.2f}%")
    
    assert len(train_pts.intersection(test_pts)) == 0, "Patient leakage detected!"
    print("  PATIENT ISOLATION VERIFIED: 0 Patient Overlap!")

    # Compute Strictly Causal Dynamic Features (center=False ONLY)
    print("\nExtracting Strictly Causal Dynamic Features (center=False, cumulative expanding median/IQR)...")
    
    def extract_causal_features(df):
        patient_frames = []
        for pkey, group in df.groupby('Patient_Key'):
            g_feats = group[valid_feature_cols].copy()
            
            # Past 3 windows rolling median ONLY
            g_smooth = g_feats.rolling(window=3, min_periods=1, center=False).median()
            
            # Cumulative expanding median & IQR
            g_exp_med = g_smooth.expanding(min_periods=1).median()
            g_exp_q75 = g_smooth.expanding(min_periods=1).quantile(0.75)
            g_exp_q25 = g_smooth.expanding(min_periods=1).quantile(0.25)
            g_exp_iqr = (g_exp_q75 - g_exp_q25).replace(0, 1.0).fillna(1.0)
            
            g_causal_z = (g_smooth - g_exp_med) / (g_exp_iqr + 1e-5)
            g_causal_z.columns = [f"{c}_z" for c in g_causal_z.columns]
            
            g_delta = g_smooth.diff().fillna(0.0)
            g_delta.columns = [f"{c}_delta" for c in g_delta.columns]
            
            comb = pd.concat([g_smooth, g_causal_z, g_delta], axis=1)
            comb['Patient_Key'] = pkey
            comb['S_next'] = group['S_next']
            patient_frames.append(comb)
            
        return pd.concat(patient_frames, axis=0)

    train_causal = extract_causal_features(train_df)
    test_causal = extract_causal_features(test_df)
    
    v_feature_cols = [c for c in train_causal.columns if c not in {'Patient_Key', 'S_next'}]
    print(f"Causal Feature Matrix Dimension: {len(v_feature_cols)} features.")

    # Fit Imputer, Model, and Calibrator EXCLUSIVELY on Training Vault
    print("\nFitting Model & Calibrator EXCLUSIVELY on Training Vault...")
    train_medians = train_causal[v_feature_cols].median()
    
    X_tr = train_causal[v_feature_cols].fillna(train_medians).values
    y_tr = train_causal['S_next'].values
    
    X_te = test_causal[v_feature_cols].fillna(train_medians).values
    y_te = test_causal['S_next'].values
    
    clf = HistGradientBoostingClassifier(
        max_iter=150,
        learning_rate=0.03,
        max_leaf_nodes=31,
        min_samples_leaf=20,
        random_state=42
    )
    clf.fit(X_tr, y_tr)
    
    tr_raw_preds = clf.predict_proba(X_tr)[:, 1]
    calibrator = IsotonicRegression(out_of_bounds='clip')
    calibrator.fit(tr_raw_preds, y_tr)
    
    # EVALUATION ON 30% LOCKED TEST VAULT
    print("\n=========================================================================")
    print("EVALUATING UN-CHEATED MODEL ON 30% LOCKED TEST VAULT")
    print("=========================================================================")
    
    te_raw_preds = clf.predict_proba(X_te)[:, 1]
    te_cal_preds = calibrator.predict(te_raw_preds)
    
    test_auroc = roc_auc_score(y_te, te_cal_preds)
    test_auprc = average_precision_score(y_te, te_cal_preds)
    test_brier = brier_score_loss(y_te, te_cal_preds)
    
    tau_screen = 0.030
    tau_confirm = 0.150
    
    y_pred_screen = (te_cal_preds >= tau_screen).astype(int)
    y_pred_confirm = (te_cal_preds >= tau_confirm).astype(int)
    
    tn_s, fp_s, fn_s, tp_s = confusion_matrix(y_te, y_pred_screen).ravel()
    tn_c, fp_c, fn_c, tp_c = confusion_matrix(y_te, y_pred_confirm).ravel()
    
    sens_screen = tp_s / (tp_s + fn_s)
    spec_screen = tn_s / (tn_s + fp_s)
    sens_confirm = tp_c / (tp_c + fn_c)
    spec_confirm = tn_c / (tn_c + fp_c)
    ppv_confirm = tp_c / max(tp_c + fp_c, 1)
    
    print(f"UN-CHEATED LOCKED TEST METRICS (30% Locked Vault - {len(test_pts)} Patients):")
    print(f"  Un-Cheated Test AUROC:               {test_auroc:.4f}")
    print(f"  Un-Cheated Test AUPRC:               {test_auprc:.4f}")
    print(f"  Un-Cheated Test Brier Score:         {test_brier:.5f}")
    print(f"  Screening Sensitivity (tau=0.030):   {sens_screen*100:.2f}% ({tp_s}/{tp_s+fn_s} events)")
    print(f"  Screening Specificity (tau=0.030):   {spec_screen*100:.2f}%")
    print(f"  Confirmation Specificity (tau=0.150): {spec_confirm*100:.2f}%")
    print(f"  Confirmation PPV (tau=0.150):         {ppv_confirm*100:.2f}%")
    print("=========================================================================")

    # SAVE ALL UN-CHEATED ARTIFACTS
    save_dir = "FINAL_BIOMARKERX/models_uncheated_master_locked"
    os.makedirs(save_dir, exist_ok=True)
    
    joblib.dump(clf, os.path.join(save_dir, "UNCHEATED_MASTER_MODEL.joblib"))
    joblib.dump(calibrator, os.path.join(save_dir, "UNCHEATED_MASTER_CALIBRATOR.joblib"))
    joblib.dump(train_medians, os.path.join(save_dir, "TRAIN_MEDIANS.joblib"))
    
    metrics_manifest = {
        "uncheated_test_auroc": test_auroc,
        "uncheated_test_auprc": test_auprc,
        "uncheated_test_brier": test_brier,
        "screening_sensitivity": sens_screen,
        "screening_specificity": spec_screen,
        "confirmation_sensitivity": sens_confirm,
        "confirmation_specificity": spec_confirm,
        "confirmation_ppv": ppv_confirm,
        "train_patients_count": len(train_pts),
        "test_patients_count": len(test_pts),
        "train_windows_count": len(train_df),
        "test_windows_count": len(test_df),
        "feature_count": len(v_feature_cols),
        "patient_overlap_count": 0,
        "temporal_leakage_status": "PASS - center=False, expanding cumulative median/IQR",
        "patient_leakage_status": "PASS - SHA-256 Patient ID hash split 70/30",
        "execution_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(os.path.join(save_dir, "UNCHEATED_MASTER_METRICS.json"), "w") as f:
        json.dump(metrics_manifest, f, indent=2)

    exec_time = time.time() - start_time
    print(f"\nBIOMARKERX UN-CHEATED MASTER PIPELINE COMPLETED IN {exec_time:.2f}s")
    print(f"Artifacts locked in {save_dir}")

if __name__ == "__main__":
    run_lock_and_uncheated_pipeline()
