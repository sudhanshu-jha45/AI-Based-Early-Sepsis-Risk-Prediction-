import os
import glob
import json
import time
import hashlib
import numpy as np
import pandas as pd
import joblib

def compute_patient_hash(patient_id):
    return int(hashlib.sha256(str(patient_id).encode('utf-8')).hexdigest(), 16) % 100000

VALID_BASE_COLS = ['HR', 'O2Sat', 'Temp', 'SBP', 'MAP', 'DBP', 'Resp', 'BaseExcess', 
                   'HCO3', 'FiO2', 'pH', 'PaCO2', 'SaO2', 'AST', 'BUN', 'Alkalinephos', 
                   'Calcium', 'Chloride', 'Creatinine', 'Bilirubin_direct', 'Glucose', 
                   'Lactate', 'Magnesium', 'Phosphate', 'Potassium', 'Bilirubin_total', 
                   'TroponinI', 'Hct', 'Hgb', 'PTT', 'WBC', 'Fibrinogen', 'Platelets', 
                   'Age', 'Gender', 'Unit1', 'Unit2', 'HospAdmTime', 'ICULOS']

def run_forensic_audit():
    print("=========================================================================")
    print("BIO MARKER X FORENSIC PATIENT SENSITIVITY DISCREPANCY AUDIT")
    print("=========================================================================")
    
    out_dir = "FINAL_BIOMARKERX/models_target_remediation_locked"
    clf = joblib.load(os.path.join(out_dir, "TARGET_MASTER_MODEL.joblib"))
    calibrator = joblib.load(os.path.join(out_dir, "TARGET_CALIBRATOR.joblib"))
    train_medians = joblib.load(os.path.join(out_dir, "TARGET_TRAIN_MEDIANS.joblib"))
    feature_cols = train_medians.index.tolist()
    
    # -------------------------------------------------------------------------
    # METHOD A: UNORDERED glob.glob('training_setA/*.psv') [like solve_exact_target_operating_point.py / publication_grade_engine]
    # -------------------------------------------------------------------------
    psv_files_unordered = glob.glob('training_setA/*.psv')
    patient_keys_un = [os.path.basename(f).replace('.psv', '') for f in psv_files_unordered]
    patient_hashes_un = [compute_patient_hash(pk) for pk in patient_keys_un]
    test_files_un = [f for f, h in zip(psv_files_unordered, patient_hashes_un) if (h % 100) >= 85]
    
    # -------------------------------------------------------------------------
    # METHOD B: SORTED glob.glob('training_setA/*.psv') [like canonical_evaluation_framework.py]
    # -------------------------------------------------------------------------
    psv_files_sorted = sorted(glob.glob('training_setA/*.psv'))
    patient_keys_so = [os.path.basename(f).replace('.psv', '') for f in psv_files_sorted]
    patient_hashes_so = [compute_patient_hash(pk) for pk in patient_keys_so]
    test_files_so = [f for f, h in zip(psv_files_sorted, patient_hashes_so) if (h % 100) >= 85]
    
    print(f"Files loaded Unordered count: {len(test_files_un)}, Sorted count: {len(test_files_so)}")
    
    # Verify set of files
    set_un = set([os.path.basename(f) for f in test_files_un])
    set_so = set([os.path.basename(f) for f in test_files_so])
    print(f"Set equality of test files: {set_un == set_so}")
    print(f"Unique patient count in test set: {len(set_so)}")
    
    # Extract features deterministically per patient file
    def extract_features_for_files(file_list):
        patient_frames = {}
        for fpath in file_list:
            try:
                pdf = pd.read_csv(fpath, sep='|')
                if 'SepsisLabel' not in pdf.columns:
                    continue
                pkey = os.path.basename(fpath).replace('.psv', '')
                s_series = pdf['SepsisLabel']
                s_next4 = (s_series.shift(-1).fillna(0) + 
                           s_series.shift(-2).fillna(0) + 
                           s_series.shift(-3).fillna(0) + 
                           s_series.shift(-4).fillna(0) > 0).astype(int)
                pdf['S_next4'] = s_next4
                pdf['S_next1'] = s_series.shift(-1)
                pdf_valid = pdf.dropna(subset=['S_next1']).copy()
                if len(pdf_valid) == 0:
                    continue
                
                g_feats = pdf_valid[VALID_BASE_COLS].copy()
                g_smooth = g_feats.rolling(window=3, min_periods=1, center=False).median()
                
                g_exp_med = g_smooth.expanding(min_periods=1).median()
                g_exp_q75 = g_smooth.expanding(min_periods=1).quantile(0.75)
                g_exp_q25 = g_smooth.expanding(min_periods=1).quantile(0.25)
                g_exp_iqr = (g_exp_q75 - g_exp_q25).replace(0, 1.0).fillna(1.0)
                
                g_causal_z = (g_smooth - g_exp_med) / (g_exp_iqr + 1e-5)
                g_causal_z.columns = [f"{c}_z" for c in g_causal_z.columns]
                
                g_delta = g_smooth.diff().fillna(0.0)
                g_delta.columns = [f"{c}_delta" for c in g_delta.columns]
                
                hr = g_smooth['HR'].replace(0, np.nan)
                sbp = g_smooth['SBP'].replace(0, np.nan)
                map_v = g_smooth['MAP'].replace(0, np.nan)
                dbp = g_smooth['DBP'].replace(0, np.nan)
                resp = g_smooth['Resp'].replace(0, np.nan)
                temp = g_smooth['Temp'].replace(0, np.nan)
                wbc = g_smooth['WBC'].replace(0, np.nan)
                
                shock_index = (hr / (sbp + 1e-5)).fillna(0.8)
                mod_shock_index = (hr / (map_v + 1e-5)).fillna(1.1)
                pulse_pressure = (sbp - dbp).fillna(40.0)
                qsofa = ((sbp <= 100).astype(int) + (resp >= 22).astype(int)).values
                sirs = ((hr > 90).astype(int) + ((temp > 38.0) | (temp < 36.0)).astype(int) + (resp > 20).astype(int) + (wbc > 12.0).astype(int)).values
                
                ratios = pd.DataFrame({
                    'Shock_Index': shock_index,
                    'Mod_Shock_Index': mod_shock_index,
                    'Pulse_Pressure': pulse_pressure,
                    'qSOFA_Causal': qsofa,
                    'SIRS_Causal': sirs
                }, index=g_smooth.index)
                
                comb = pd.concat([g_smooth, g_causal_z, g_delta, ratios], axis=1)
                comb['Patient_Key'] = pkey
                comb['S_next4'] = pdf_valid['S_next4'].astype(int).values
                comb['S_next1'] = pdf_valid['S_next1'].astype(int).values
                comb['SepsisLabel'] = pdf_valid['SepsisLabel'].astype(int).values
                
                # Predict
                X_mat = comb[feature_cols].fillna(train_medians).values
                raw = clf.predict_proba(X_mat)[:, 1]
                cal = calibrator.transform(raw)
                comb['risk_pred'] = cal
                
                patient_frames[pkey] = comb
            except Exception as e:
                print(f"Error processing {fpath}: {e}")
        return patient_frames

    print("\nExtracting features and predictions for all test patients...")
    patient_dict = extract_features_for_files(test_files_so)
    print(f"Successfully processed {len(patient_dict)} patients.")

    tau_s = 0.0350
    
    # -------------------------------------------------------------------------
    # PIPELINE 1: Solve Exact Target Operating Point / Publication Grade Target Engine
    # -------------------------------------------------------------------------
    # In solve_exact_target_operating_point.py / publication_grade:
    # sep_pts, det_pts = 0, 0
    # for pkey, group in df.groupby('Patient_Key'):
    #     labels = group['SepsisLabel'].values
    #     next4 = group['S_next4'].values
    #     preds = group['risk_pred'].values
    #     if np.any(labels == 1) or np.any(next4 == 1):
    #         sep_pts += 1
    #         onset_indices = np.where((labels == 1) | (next4 == 1))[0]
    #         if len(onset_indices) > 0:
    #             onset_t = onset_indices[0]
    #             if np.any(preds[:onset_t+1] >= ts):
    #                 det_pts += 1
    # -------------------------------------------------------------------------

    results_eval = []
    
    sep_count = 0
    det_count = 0
    
    for pkey, comb in patient_dict.items():
        labels = comb['SepsisLabel'].values
        next4 = comb['S_next4'].values
        preds = comb['risk_pred'].values
        
        has_sepsis = np.any(labels == 1) or np.any(next4 == 1)
        
        # Check onset definition variant 1: onset_t = first index where (SepsisLabel == 1 | S_next4 == 1)
        onset_indices_1 = np.where((labels == 1) | (next4 == 1))[0]
        onset_t_1 = onset_indices_1[0] if len(onset_indices_1) > 0 else len(preds) - 1
        det_1 = np.any(preds[:onset_t_1 + 1] >= tau_s) if has_sepsis and len(onset_indices_1) > 0 else False
        
        # Check onset definition variant 2: onset_t = first index where SepsisLabel == 1 ONLY
        onset_indices_2 = np.where(labels == 1)[0]
        onset_t_2 = onset_indices_2[0] if len(onset_indices_2) > 0 else len(preds) - 1
        det_2 = np.any(preds[:onset_t_2 + 1] >= tau_s) if np.any(labels == 1) else False
        
        # Check onset definition variant 3: onset_t = first index where S_next4 == 1 ONLY
        onset_indices_3 = np.where(next4 == 1)[0]
        onset_t_3 = onset_indices_3[0] if len(onset_indices_3) > 0 else len(preds) - 1
        det_3 = np.any(preds[:onset_t_3 + 1] >= tau_s) if np.any(next4 == 1) else False
        
        # Check onset definition variant 4: ANY alert across full stay (unconstrained lead-time)
        det_4 = np.any(preds >= tau_s) if has_sepsis else False
        
        # Check onset definition variant 5: Alert BEFORE onset ONLY (preds[:onset_t] strictly < onset_t)
        det_5 = np.any(preds[:onset_t_1] >= tau_s) if has_sepsis and len(onset_indices_1) > 0 and onset_t_1 > 0 else False

        results_eval.append({
            'patient_id': pkey,
            'has_sepsis': has_sepsis,
            'has_sepsis_label_only': np.any(labels == 1),
            'has_sepsis_next4_only': np.any(next4 == 1),
            'onset_t_1': onset_t_1,
            'det_1_any_until_onset': det_1,
            'det_2_sepsis_label_only': det_2,
            'det_3_next4_only': det_3,
            'det_4_any_stay': det_4,
            'det_5_strictly_before_onset': det_5,
            'max_risk': np.max(preds),
            'window_count': len(preds)
        })

    eval_df = pd.DataFrame(results_eval)
    
    # Calculate patient sensitivity under all variants
    tot_sepsis_1 = eval_df['has_sepsis'].sum()
    det_sepsis_1 = eval_df[eval_df['has_sepsis']]['det_1_any_until_onset'].sum()
    sens_1 = det_sepsis_1 / tot_sepsis_1
    
    tot_sepsis_2 = eval_df['has_sepsis_label_only'].sum()
    det_sepsis_2 = eval_df[eval_df['has_sepsis_label_only']]['det_2_sepsis_label_only'].sum()
    sens_2 = det_sepsis_2 / tot_sepsis_2
    
    tot_sepsis_4 = eval_df['has_sepsis'].sum()
    det_sepsis_4 = eval_df[eval_df['has_sepsis']]['det_4_any_stay'].sum()
    sens_4 = det_sepsis_4 / tot_sepsis_4
    
    tot_sepsis_5 = eval_df['has_sepsis'].sum()
    det_sepsis_5 = eval_df[eval_df['has_sepsis']]['det_5_strictly_before_onset'].sum()
    sens_5 = det_sepsis_5 / tot_sepsis_5
    
    print(f"\n=========================================================================")
    print(f"PATIENT SENSITIVITY VARIANT AUDIT (tau_s = {tau_s}):")
    print(f"Variant 1 (Onset = SepsisLabel==1 | S_next4==1, alert <= onset_t):")
    print(f"  Sepsis Patients = {tot_sepsis_1}, Detected = {det_sepsis_1}, Patient Sensitivity = {sens_1*100:.2f}% ({det_sepsis_1}/{tot_sepsis_1})")
    print(f"Variant 2 (Onset = SepsisLabel==1 ONLY, alert <= onset_t):")
    print(f"  Sepsis Patients = {tot_sepsis_2}, Detected = {det_sepsis_2}, Patient Sensitivity = {sens_2*100:.2f}% ({det_sepsis_2}/{tot_sepsis_2})")
    print(f"Variant 4 (Any alert anywhere in stay):")
    print(f"  Sepsis Patients = {tot_sepsis_4}, Detected = {det_sepsis_4}, Patient Sensitivity = {sens_4*100:.2f}% ({det_sepsis_4}/{tot_sepsis_4})")
    print(f"Variant 5 (Alert strictly BEFORE onset_t, i.e. < onset_t):")
    print(f"  Sepsis Patients = {tot_sepsis_5}, Detected = {det_sepsis_5}, Patient Sensitivity = {sens_5*100:.2f}% ({det_sepsis_5}/{tot_sepsis_5})")
    print(f"=========================================================================")

    # -------------------------------------------------------------------------
    # TEST HYPOTHESIS: THRESHOLD AUDIT (What threshold tau_s gives exactly 82.44%?)
    # -------------------------------------------------------------------------
    print("\nSweeping tau_s on locked test cohort to find threshold corresponding to 82.44%...")
    sweep_records = []
    for ts in np.linspace(0.010, 0.050, 401):
        det_c = 0
        for pkey, comb in patient_dict.items():
            labels = comb['SepsisLabel'].values
            next4 = comb['S_next4'].values
            preds = comb['risk_pred'].values
            if np.any(labels == 1) or np.any(next4 == 1):
                onset_indices = np.where((labels == 1) | (next4 == 1))[0]
                if len(onset_indices) > 0:
                    onset_t = onset_indices[0]
                    if np.any(preds[:onset_t+1] >= ts):
                        det_c += 1
        sens_c = det_c / tot_sepsis_1
        sweep_records.append({'tau_s': ts, 'det_count': det_c, 'tot_count': tot_sepsis_1, 'sens': sens_c})
    
    df_sweep = pd.DataFrame(sweep_records)
    print("\nThresholds yielding near 82.44% sensitivity:")
    match_82 = df_sweep[np.abs(df_sweep['sens'] - 0.8244) < 0.005]
    print(match_82.to_string())

    # Save patient-level comparison table
    out_dir = "FINAL_BIOMARKERX/forensic_sensitivity_audit"
    eval_df.to_csv(os.path.join(out_dir, "PATIENT_LEVEL_SENSITIVITY_FORENSIC_TABLE.csv"), index=False)
    df_sweep.to_csv(os.path.join(out_dir, "TAU_S_SENSITIVITY_SWEEP.csv"), index=False)

if __name__ == '__main__':
    run_forensic_audit()
