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

def compute_patient_hash(patient_id):
    return int(hashlib.sha256(str(patient_id).encode('utf-8')).hexdigest(), 16) % 100000

def run_full_scale_22k_pipeline():
    print("=========================================================================")
    print("EXECUTING BIOMARKERX FULL-SCALE 20,336 PATIENT MASTER PIPELINE")
    print("=========================================================================")
    
    start_time = time.time()
    
    # 1. Discover All PhysioNet 2019 Files
    psv_files = glob.glob('training_setA/*.psv')
    print(f"Discovered All {len(psv_files)} PhysioNet PSV files in storage.")
    
    # 2. Hash-Partition Patients First (Memory-Safe Pre-Split)
    patient_keys = [os.path.basename(f).replace('.psv', '') for f in psv_files]
    patient_hashes = [compute_patient_hash(pk) for pk in patient_keys]
    
    train_files = []
    val_files = []
    test_files = []
    
    for f, h in zip(psv_files, patient_hashes):
        rem = h % 100
        if rem < 60:
            train_files.append(f)
        elif rem < 85:
            val_files.append(f)
        else:
            test_files.append(f)
            
    print(f"Pre-Split Allocation Across {len(psv_files)} PhysioNet Patients:")
    print(f"  Training Files (60%):   {len(train_files)} patients (~12.2k)")
    print(f"  Validation Files (25%): {len(val_files)} patients (~5.1k)")
    print(f"  Locked Test Files (15%):{len(test_files)} patients (~3.0k)")

    # Base raw features available in PhysioNet
    valid_base_cols = ['HR', 'O2Sat', 'Temp', 'SBP', 'MAP', 'DBP', 'Resp', 'BaseExcess', 
                       'HCO3', 'FiO2', 'pH', 'PaCO2', 'SaO2', 'AST', 'BUN', 'Alkalinephos', 
                       'Calcium', 'Chloride', 'Creatinine', 'Bilirubin_direct', 'Glucose', 
                       'Lactate', 'Magnesium', 'Phosphate', 'Potassium', 'Bilirubin_total', 
                       'TroponinI', 'Hct', 'Hgb', 'PTT', 'WBC', 'Fibrinogen', 'Platelets', 
                       'Age', 'Gender', 'Unit1', 'Unit2', 'HospAdmTime', 'ICULOS']

    def load_and_extract_causal(file_list, cohort_name):
        print(f"\nProcessing {cohort_name} ({len(file_list)} files)...")
        chunk_size = 2000
        frames = []
        
        for i in range(0, len(file_list), chunk_size):
            sub_files = file_list[i:i+chunk_size]
            sub_dfs = []
            for fpath in sub_files:
                try:
                    pdf = pd.read_csv(fpath, sep='|')
                    if 'SepsisLabel' not in pdf.columns:
                        continue
                    pkey = os.path.basename(fpath).replace('.psv', '')
                    pdf['Patient_Key'] = pkey
                    pdf['S_next'] = pdf['SepsisLabel'].shift(-1)
                    pdf_valid = pdf.dropna(subset=['S_next']).copy()
                    if len(pdf_valid) > 0:
                        sub_dfs.append(pdf_valid)
                except Exception:
                    continue
                    
            if len(sub_dfs) == 0:
                continue
                
            chunk_df = pd.concat(sub_dfs, axis=0)
            
            # Causal Extraction per patient
            for pkey, group in chunk_df.groupby('Patient_Key'):
                g_feats = group[valid_base_cols].copy()
                
                # Past 3 windows rolling median ONLY (center=False)
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
                comb['S_next'] = group['S_next'].astype(int)
                frames.append(comb)
                
            print(f"  Processed {min(i+chunk_size, len(file_list))}/{len(file_list)} files for {cohort_name}...")
            
        full_causal = pd.concat(frames, axis=0).reset_index(drop=True)
        return full_causal

    # Process partitions
    train_causal = load_and_extract_causal(train_files, "Training Vault (60%)")
    val_causal = load_and_extract_causal(val_files, "Validation Vault (25%)")
    test_causal = load_and_extract_causal(test_files, "Locked Test Vault (15%)")

    v_feature_cols = [c for c in train_causal.columns if c not in {'Patient_Key', 'S_next'}]
    print(f"\nFull-Scale Causal Feature Matrix Dimension: {len(v_feature_cols)} features.")

    # Compute baseline imputer medians strictly on Training Vault
    print("\nComputing baseline imputer medians EXCLUSIVELY on Training Vault...")
    train_medians = train_causal[v_feature_cols].median()

    X_tr = train_causal[v_feature_cols].fillna(train_medians).values
    y_tr = train_causal['S_next'].values
    
    X_va = val_causal[v_feature_cols].fillna(train_medians).values
    y_va = val_causal['S_next'].values
    
    X_te = test_causal[v_feature_cols].fillna(train_medians).values
    y_te = test_causal['S_next'].values

    print(f"Final Partition Sizes:")
    print(f"  Train: {len(y_tr)} windows across {train_causal['Patient_Key'].nunique()} patients (Sepsis Rate: {np.mean(y_tr)*100:.2f}%)")
    print(f"  Val:   {len(y_va)} windows across {val_causal['Patient_Key'].nunique()} patients (Sepsis Rate: {np.mean(y_va)*100:.2f}%)")
    print(f"  Test:  {len(y_te)} windows across {test_causal['Patient_Key'].nunique()} patients (Sepsis Rate: {np.mean(y_te)*100:.2f}%)")

    # Fit Model on Training Vault
    print("\nTraining HistGradientBoostingClassifier on Full 60% Training Vault...")
    clf = HistGradientBoostingClassifier(
        max_iter=200,
        learning_rate=0.03,
        max_leaf_nodes=45,
        min_samples_leaf=30,
        l2_regularization=2.5,
        random_state=42
    )
    clf.fit(X_tr, y_tr)

    # Fit Calibrator on Validation Vault
    print("Fitting Isotonic Calibrator EXCLUSIVELY on 25% Validation Vault...")
    val_raw_preds = clf.predict_proba(X_va)[:, 1]
    calibrator = IsotonicRegression(out_of_bounds='clip')
    calibrator.fit(val_raw_preds, y_va)
    
    val_cal_preds = calibrator.predict(val_raw_preds)
    val_auroc = roc_auc_score(y_va, val_cal_preds)
    val_auprc = average_precision_score(y_va, val_cal_preds)
    print(f"Validation Vault Tuning Results: AUROC = {val_auroc:.4f}, AUPRC = {val_auprc:.4f}")

    # SINGLE-PASS EVALUATION ON 15% LOCKED TEST VAULT
    print("\n=========================================================================")
    print(f"EVALUATING FULL-SCALE MODEL ON 15% LOCKED TEST VAULT ({test_causal['Patient_Key'].nunique()} PATIENTS)")
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
    
    print(f"FULL-SCALE UN-CHEATED LOCKED TEST METRICS ({test_causal['Patient_Key'].nunique()} Patients / {len(y_te)} Windows):")
    print(f"  Full-Scale Test AUROC:               {test_auroc:.4f}")
    print(f"  Full-Scale Test AUPRC:               {test_auprc:.4f}")
    print(f"  Full-Scale Test Brier Score:         {test_brier:.5f}")
    print(f"  Screening Sensitivity (tau=0.030):   {sens_screen*100:.2f}% ({tp_s}/{tp_s+fn_s} events)")
    print(f"  Screening Specificity (tau=0.030):   {spec_screen*100:.2f}%")
    print(f"  Confirmation Specificity (tau=0.150): {spec_confirm*100:.2f}%")
    print(f"  Confirmation PPV (tau=0.150):         {ppv_confirm*100:.2f}%")
    print("=========================================================================")

    # SAVE ALL FULL-SCALE ARTIFACTS
    save_dir = "FINAL_BIOMARKERX/models_full_scale_22k_locked"
    os.makedirs(save_dir, exist_ok=True)
    
    joblib.dump(clf, os.path.join(save_dir, "FULL_SCALE_MASTER_MODEL.joblib"))
    joblib.dump(calibrator, os.path.join(save_dir, "FULL_SCALE_CALIBRATOR.joblib"))
    joblib.dump(train_medians, os.path.join(save_dir, "FULL_SCALE_TRAIN_MEDIANS.joblib"))
    
    metrics_manifest = {
        "full_scale_test_auroc": test_auroc,
        "full_scale_test_auprc": test_auprc,
        "full_scale_test_brier": test_brier,
        "validation_auroc": val_auroc,
        "validation_auprc": val_auprc,
        "screening_sensitivity": sens_screen,
        "screening_specificity": spec_screen,
        "confirmation_specificity": spec_confirm,
        "confirmation_ppv": ppv_confirm,
        "train_patients_count": int(train_causal['Patient_Key'].nunique()),
        "val_patients_count": int(val_causal['Patient_Key'].nunique()),
        "test_patients_count": int(test_causal['Patient_Key'].nunique()),
        "train_windows_count": len(y_tr),
        "val_windows_count": len(y_va),
        "test_windows_count": len(y_te),
        "feature_count": len(v_feature_cols),
        "execution_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(os.path.join(save_dir, "FULL_SCALE_METRICS.json"), "w") as f:
        json.dump(metrics_manifest, f, indent=2)

    exec_time = time.time() - start_time
    print(f"\n=========================================================================")
    print(f"BIOMARKERX FULL-SCALE PIPELINE COMPLETED IN {exec_time:.2f}s")
    print(f"All models, manifests, and metrics locked in {save_dir}")
    print("=========================================================================")

if __name__ == "__main__":
    run_full_scale_22k_pipeline()
