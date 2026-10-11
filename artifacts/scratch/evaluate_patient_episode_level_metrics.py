import os
import glob
import json
import time
import hashlib
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, confusion_matrix

def compute_patient_hash(patient_id):
    return int(hashlib.sha256(str(patient_id).encode('utf-8')).hexdigest(), 16) % 100000

def run_patient_episode_evaluation():
    print("=========================================================================")
    print("EVALUATING BIOMARKERX PATIENT-LEVEL & EPISODE-LEVEL CLINICAL METRICS")
    print("=========================================================================")
    start_time = time.time()
    
    # Load locked model & medians
    model_dir = "FINAL_BIOMARKERX/models_full_scale_22k_locked"
    clf = joblib.load(os.path.join(model_dir, "FULL_SCALE_MASTER_MODEL.joblib"))
    calibrator = joblib.load(os.path.join(model_dir, "FULL_SCALE_CALIBRATOR.joblib"))
    train_medians = joblib.load(os.path.join(model_dir, "FULL_SCALE_TRAIN_MEDIANS.joblib"))
    
    feature_cols = train_medians.index.tolist()
    
    valid_base_cols = ['HR', 'O2Sat', 'Temp', 'SBP', 'MAP', 'DBP', 'Resp', 'BaseExcess', 
                       'HCO3', 'FiO2', 'pH', 'PaCO2', 'SaO2', 'AST', 'BUN', 'Alkalinephos', 
                       'Calcium', 'Chloride', 'Creatinine', 'Bilirubin_direct', 'Glucose', 
                       'Lactate', 'Magnesium', 'Phosphate', 'Potassium', 'Bilirubin_total', 
                       'TroponinI', 'Hct', 'Hgb', 'PTT', 'WBC', 'Fibrinogen', 'Platelets', 
                       'Age', 'Gender', 'Unit1', 'Unit2', 'HospAdmTime', 'ICULOS']

    psv_files = glob.glob('training_setA/*.psv')
    patient_keys = [os.path.basename(f).replace('.psv', '') for f in psv_files]
    patient_hashes = [compute_patient_hash(pk) for pk in patient_keys]
    
    test_files = [f for f, h in zip(psv_files, patient_hashes) if (h % 100) >= 85]
    print(f"Loading Locked Test Vault ({len(test_files)} files)...")
    
    chunk_size = 2500
    frames = []
    for i in range(0, len(test_files), chunk_size):
        sub_files = test_files[i:i+chunk_size]
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
        if not sub_dfs:
            continue
        chunk_df = pd.concat(sub_dfs, axis=0)
        
        for pkey, group in chunk_df.groupby('Patient_Key'):
            g_feats = group[valid_base_cols].copy()
            g_smooth = g_feats.rolling(window=3, min_periods=1, center=False).median()
            
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
            comb['SepsisLabel'] = group['SepsisLabel'].values
            comb['HR_delta_val'] = g_delta['HR_delta'].values
            comb['MAP_delta_val'] = g_delta['MAP_delta'].values
            frames.append(comb)
            
    test_df = pd.concat(frames, axis=0).reset_index(drop=True)
    
    X_test = test_df[feature_cols].fillna(train_medians).values
    test_raw_preds = clf.predict_proba(X_test)[:, 1]
    test_cal_preds = calibrator.transform(test_raw_preds)
    test_df['risk_pred'] = test_cal_preds
    
    # PATIENT-LEVEL SENSITIVITY CALCULATION
    # A patient is a "Sepsis Patient" if they ever transition to Sepsis (SepsisLabel == 1)
    sepsis_patients = 0
    detected_sepsis_patients = 0
    detected_early_lead_times = []
    
    total_episodes = 0
    true_episodes = 0
    
    tau_screen = 0.030
    tau_confirm = 0.150
    
    for pkey, group in test_df.groupby('Patient_Key'):
        labels = group['SepsisLabel'].values
        next_labels = group['S_next'].values
        preds = group['risk_pred'].values
        hr_d = group['HR_delta_val'].values
        map_d = group['MAP_delta_val'].values
        
        has_sepsis = np.any(labels == 1) or np.any(next_labels == 1)
        if has_sepsis:
            sepsis_patients += 1
            # Find earliest sepsis hour
            onset_t = np.where((labels == 1) | (next_labels == 1))[0][0]
            # Check if any screening alert occurred BEFORE onset_t
            screen_alerts = np.where(preds[:onset_t+1] >= tau_screen)[0]
            if len(screen_alerts) > 0:
                first_alert_t = screen_alerts[0]
                lead_time = max(0, onset_t - first_alert_t)
                detected_sepsis_patients += 1
                detected_early_lead_times.append(lead_time)
                
        # Episode-level confirmation tracking
        s1 = (preds >= tau_screen).astype(int)
        s2 = np.zeros(len(s1), dtype=int)
        for t in range(len(s1)):
            if t >= 1: # 2-window persistence
                if s1[t-1] == 1 and s1[t] == 1:
                    s2[t] = 1
        p_cond = (preds >= tau_confirm) & ((hr_d > 0.3) | (map_d < -0.3))
        s3 = s2 & p_cond.astype(int)
        
        in_ep, ep_tp = False, False
        for t in range(len(s3)):
            if s3[t] == 1:
                if not in_ep:
                    in_ep = True
                    total_episodes += 1
                    ep_tp = (next_labels[t] == 1 or labels[t] == 1)
                else:
                    if next_labels[t] == 1 or labels[t] == 1:
                        ep_tp = True
            else:
                if in_ep:
                    in_ep = False
                    if ep_tp:
                        true_episodes += 1
                        
    patient_sens = detected_sepsis_patients / max(sepsis_patients, 1)
    patient_ep_ppv = true_episodes / max(total_episodes, 1)
    mean_lt = np.mean(detected_early_lead_times) if len(detected_early_lead_times) > 0 else 0.0
    med_lt = np.median(detected_early_lead_times) if len(detected_early_lead_times) > 0 else 0.0
    
    print(f"\n=========================================================================")
    print(f"PATIENT-LEVEL & CLINICAL EPISODE METRICS (LOCKED TEST VAULT):")
    print(f"  Total Sepsis Patients in Test Vault: {sepsis_patients}")
    print(f"  Early Detected Sepsis Patients:      {detected_sepsis_patients}")
    print(f"  PATIENT-LEVEL SENSITIVITY:           {patient_sens*100:.2f}% ({detected_sepsis_patients}/{sepsis_patients})")
    print(f"  PATIENT-LEVEL EPISODE PPV:           {patient_ep_ppv*100:.2f}% ({true_episodes}/{total_episodes} true episodes)")
    print(f"  MEAN EARLY LEAD TIME:                {mean_lt:.2f} hours")
    print(f"  MEDIAN EARLY LEAD TIME:              {med_lt:.2f} hours")
    print(f"=========================================================================")

    res_json = {
        "sepsis_patients_count": sepsis_patients,
        "detected_sepsis_patients": detected_sepsis_patients,
        "patient_level_sensitivity": patient_sens,
        "patient_level_episode_ppv": patient_ep_ppv,
        "mean_lead_time_hours": mean_lt,
        "median_lead_time_hours": med_lt,
        "execution_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open("BIOMARKX_V3_PATIENT_EPISODE_METRICS.json", "w") as f:
        json.dump(res_json, f, indent=2)

if __name__ == "__main__":
    run_patient_episode_evaluation()
