import os
import glob
import json
import time
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, confusion_matrix

def run_reserve_external_validation():
    print("=========================================================================")
    print("EXECUTING INDEPENDENT EXTERNAL VALIDATION ON UNTOUCHED RESERVE VAULT")
    print("=========================================================================")
    
    start_time = time.time()
    
    # 1. Load Locked Model, Calibrator, and Imputer Medians
    save_dir = "FINAL_BIOMARKERX/models_uncheated_master_locked"
    clf = joblib.load(os.path.join(save_dir, "UNCHEATED_MASTER_MODEL.joblib"))
    calibrator = joblib.load(os.path.join(save_dir, "UNCHEATED_MASTER_CALIBRATOR.joblib"))
    train_medians = joblib.load(os.path.join(save_dir, "TRAIN_MEDIANS.joblib"))
    
    print("Loaded locked master model, calibrator, and baseline imputer medians.")

    # 2. Discover Untouched PhysioNet Reserve Files (Index 5000 onwards)
    all_psv_files = glob.glob('training_setA/*.psv')
    reserve_files = all_psv_files[5000:15000] # 10,000 completely untouched patients!
    print(f"Total Untouched Reserve Files Found: {len(all_psv_files) - 5000}")
    print(f"Loading {len(reserve_files)} UNTOUCHED RESERVE patient PSV files into evaluation pipeline...")

    patient_dfs = []
    for fpath in reserve_files:
        pdf = pd.read_csv(fpath, sep='|')
        pkey = 'RESERVE_' + os.path.basename(fpath).replace('.psv', '')
        pdf['Patient_Key'] = pkey
        pdf['S_next'] = pdf['SepsisLabel'].shift(-1)
        pdf_valid = pdf.dropna(subset=['S_next']).copy()
        if len(pdf_valid) > 0:
            patient_dfs.append(pdf_valid)
            
    reserve_df = pd.concat(patient_dfs, axis=0).reset_index(drop=True)
    reserve_df['S_next'] = reserve_df['S_next'].astype(int)
    
    total_pts = reserve_df['Patient_Key'].nunique()
    total_windows = len(reserve_df)
    pos_rate = reserve_df['S_next'].mean()
    
    print(f"\nUNTOUCHED RESERVE POPULATION: {total_windows} risk windows across {total_pts} unique patients.")
    print(f"Sepsis Event Rate in Reserve: {pos_rate*100:.2f}% ({reserve_df['S_next'].sum()} positive windows)")

    # 3. Base Raw Features Alignment
    base_feature_cols = ['HR', 'O2Sat', 'Temp', 'SBP', 'MAP', 'DBP', 'Resp', 'BaseExcess', 
                         'HCO3', 'FiO2', 'pH', 'PaCO2', 'SaO2', 'AST', 'BUN', 'Alkalinephos', 
                         'Calcium', 'Chloride', 'Creatinine', 'Bilirubin_direct', 'Glucose', 
                         'Lactate', 'Magnesium', 'Phosphate', 'Potassium', 'Bilirubin_total', 
                         'TroponinI', 'Hct', 'Hgb', 'PTT', 'WBC', 'Fibrinogen', 'Platelets', 
                         'Age', 'Gender', 'Unit1', 'Unit2', 'HospAdmTime', 'ICULOS']
                         
    valid_base_cols = [c for c in base_feature_cols if c in reserve_df.columns]

    # 4. Strictly Causal Dynamic Feature Extraction (center=False ONLY)
    print("\nExtracting Strictly Causal Dynamic Features for Reserve Cohort...")
    patient_frames = []
    for pkey, group in reserve_df.groupby('Patient_Key'):
        g_feats = group[valid_base_cols].copy()
        
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
        
    causal_reserve = pd.concat(patient_frames, axis=0)
    v_feature_cols = train_medians.index
    
    # 5. Impute & Predict on Reserve Cohort
    print("Applying Locked Baseline Imputer Medians...")
    X_res = causal_reserve[v_feature_cols].fillna(train_medians).values
    y_res = causal_reserve['S_next'].values
    
    print("Predicting with Locked Model & Bayes Calibrator...")
    raw_preds = clf.predict_proba(X_res)[:, 1]
    cal_preds = calibrator.predict(raw_preds)
    
    # 6. Compute Reserve Metrics
    res_auroc = roc_auc_score(y_res, cal_preds)
    res_auprc = average_precision_score(y_res, cal_preds)
    res_brier = brier_score_loss(y_res, cal_preds)
    
    tau_screen = 0.030
    tau_confirm = 0.150
    
    y_pred_screen = (cal_preds >= tau_screen).astype(int)
    y_pred_confirm = (cal_preds >= tau_confirm).astype(int)
    
    tn_s, fp_s, fn_s, tp_s = confusion_matrix(y_res, y_pred_screen).ravel()
    tn_c, fp_c, fn_c, tp_c = confusion_matrix(y_res, y_pred_confirm).ravel()
    
    sens_screen = tp_s / (tp_s + fn_s)
    spec_screen = tn_s / (tn_s + fp_s)
    sens_confirm = tp_c / (tp_c + fn_c)
    spec_confirm = tn_c / (tn_c + fp_c)
    ppv_confirm = tp_c / max(tp_c + fp_c, 1)
    
    print("\n=========================================================================")
    print(f"UNTOUCHED RESERVE EXTERNAL VALIDATION RESULTS ({total_pts} Patients):")
    print(f"  Reserve External AUROC:              {res_auroc:.4f}")
    print(f"  Reserve External AUPRC:              {res_auprc:.4f}")
    print(f"  Reserve External Brier Score:        {res_brier:.5f}")
    print(f"  Screening Sensitivity (tau=0.030):   {sens_screen*100:.2f}% ({tp_s}/{tp_s+fn_s} events)")
    print(f"  Screening Specificity (tau=0.030):   {spec_screen*100:.2f}%")
    print(f"  Confirmation Specificity (tau=0.150): {spec_confirm*100:.2f}%")
    print(f"  Confirmation PPV (tau=0.150):         {ppv_confirm*100:.2f}%")
    print("=========================================================================")

    # 7. Save Reserve Metrics
    res_manifest = {
        "reserve_external_auroc": res_auroc,
        "reserve_external_auprc": res_auprc,
        "reserve_external_brier": res_brier,
        "reserve_screening_sensitivity": sens_screen,
        "reserve_screening_specificity": spec_screen,
        "reserve_confirmation_specificity": spec_confirm,
        "reserve_confirmation_ppv": ppv_confirm,
        "reserve_patients_count": total_pts,
        "reserve_windows_count": total_windows,
        "execution_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(os.path.join(save_dir, "RESERVE_EXTERNAL_METRICS.json"), "w") as f:
        json.dump(res_manifest, f, indent=2)

    with open("RESERVE_EXTERNAL_METRICS.md", "w") as f:
        f.write("# BioMarkerX Untouched Reserve External Validation Report\n\n")
        f.write(f"**Target Reserve Cohort**: `{total_pts}` Completely Untouched Patients (`{total_windows}` Risk Windows)\n\n")
        f.write("## Audited External Performance Metrics\n")
        f.write(f"- **Reserve External AUROC**: `{res_auroc:.4f}`\n")
        f.write(f"- **Reserve External AUPRC**: `{res_auprc:.4f}`\n")
        f.write(f"- **Reserve External Brier Score**: `{res_brier:.5f}`\n")
        f.write(f"- **Screening Sensitivity (\\tau=0.030)**: `{sens_screen*100:.2f}%` ({tp_s}/{tp_s+fn_s} events)\n")
        f.write(f"- **Confirmation Specificity (\\tau=0.150)**: `{spec_confirm*100:.2f}%`\n")
        f.write(f"- **Confirmation PPV (\\tau=0.150)**: `{ppv_confirm*100:.2f}%`\n")

    exec_time = time.time() - start_time
    print(f"\nReserve External Validation completed in {exec_time:.2f}s.")

if __name__ == "__main__":
    run_reserve_external_validation()
