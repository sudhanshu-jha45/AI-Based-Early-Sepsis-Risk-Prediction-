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

def run_fast_audit():
    print("=========================================================================", flush=True)
    print("FAST FORENSIC PATIENT SENSITIVITY SOLVER", flush=True)
    print("=========================================================================", flush=True)
    t0 = time.time()
    
    out_dir = "FINAL_BIOMARKERX/models_target_remediation_locked"
    clf = joblib.load(os.path.join(out_dir, "TARGET_MASTER_MODEL.joblib"))
    calibrator = joblib.load(os.path.join(out_dir, "TARGET_CALIBRATOR.joblib"))
    train_medians = joblib.load(os.path.join(out_dir, "TARGET_TRAIN_MEDIANS.joblib"))
    feature_cols = train_medians.index.tolist()

    psv_files = sorted(glob.glob('training_setA/*.psv'))
    patient_keys = [os.path.basename(f).replace('.psv', '') for f in psv_files]
    hashes = [compute_patient_hash(pk) for pk in patient_keys]
    test_files = [f for f, h in zip(psv_files, hashes) if (h % 100) >= 85]
    
    print(f"Total locked test files: {len(test_files)}", flush=True)

    # Process files in parallel/batch chunking
    chunk_size = 1000
    all_patient_records = {}
    
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
                s_series = pdf['SepsisLabel']
                s_next4 = (s_series.shift(-1).fillna(0) + 
                           s_series.shift(-2).fillna(0) + 
                           s_series.shift(-3).fillna(0) + 
                           s_series.shift(-4).fillna(0) > 0).astype(int)
                pdf['S_next4'] = s_next4
                pdf['S_next1'] = s_series.shift(-1)
                pdf_valid = pdf.dropna(subset=['S_next1']).copy()
                if len(pdf_valid) > 0:
                    sub_dfs.append(pdf_valid)
            except Exception:
                continue
        if not sub_dfs:
            continue
        chunk_df = pd.concat(sub_dfs, axis=0)
        
        for pkey, group in chunk_df.groupby('Patient_Key'):
            g_feats = group[VALID_BASE_COLS].copy()
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
            comb['S_next4'] = group['S_next4'].astype(int).values
            comb['S_next1'] = group['S_next1'].astype(int).values
            comb['SepsisLabel'] = group['SepsisLabel'].astype(int).values
            comb['HR_delta_val'] = g_delta['HR_delta'].values
            comb['MAP_delta_val'] = g_delta['MAP_delta'].values
            
            X_mat = comb[feature_cols].fillna(train_medians).values
            raw = clf.predict_proba(X_mat)[:, 1]
            cal = calibrator.transform(raw)
            comb['risk_pred'] = cal
            
            # Compute trajectory gate condition
            # Shock Index >= 0.85 OR HR Delta > 0.2 OR MAP Delta < -0.2
            comb['traj_gate'] = ((comb['Shock_Index'] >= 0.85) | (comb['HR_delta_val'] > 0.2) | (comb['MAP_delta_val'] < -0.2)).astype(int)
            
            all_patient_records[pkey] = comb

    print(f"Extracted feature data for {len(all_patient_records)} patients in {time.time() - t0:.1f}s", flush=True)

    # -------------------------------------------------------------------------
    # FORENSIC SWEEP: AUDIT ALL THRESHOLDS AND GATING CONFIGURATIONS
    # -------------------------------------------------------------------------
    sweep_results = []
    
    for tau in [0.030, 0.035, 0.040, 0.045, 0.050, 0.055, 0.060]:
        for gated in [False, True]:
            # Evaluation Variant A: onset = first index where SepsisLabel==1 or S_next4==1, alert <= onset_t
            sep_a, det_a = 0, 0
            # Evaluation Variant B: onset = first index where SepsisLabel==1 ONLY, alert <= onset_t
            sep_b, det_b = 0, 0
            # Evaluation Variant C: onset = first index where SepsisLabel==1 or S_next4==1, alert STRICTLY < onset_t
            sep_c, det_c = 0, 0
            # Evaluation Variant D: ANY alert in stay
            sep_d, det_d = 0, 0
            
            for pkey, comb in all_patient_records.items():
                labels = comb['SepsisLabel'].values
                next4 = comb['S_next4'].values
                preds = comb['risk_pred'].values
                gate = comb['traj_gate'].values if gated else np.ones(len(preds), dtype=int)
                
                effective_preds = np.where(gate == 1, preds, 0.0)
                
                # Variant A: SepsisLabel==1 or S_next4==1
                has_a = np.any(labels == 1) or np.any(next4 == 1)
                if has_a:
                    sep_a += 1
                    oi = np.where((labels == 1) | (next4 == 1))[0]
                    if len(oi) > 0:
                        ot = oi[0]
                        if np.any(effective_preds[:ot+1] >= tau):
                            det_a += 1
                            
                # Variant B: SepsisLabel==1 ONLY
                has_b = np.any(labels == 1)
                if has_b:
                    sep_b += 1
                    oi = np.where(labels == 1)[0]
                    if len(oi) > 0:
                        ot = oi[0]
                        if np.any(effective_preds[:ot+1] >= tau):
                            det_b += 1
                            
                # Variant C: Strictly BEFORE onset (< onset_t)
                if has_a:
                    sep_c += 1
                    oi = np.where((labels == 1) | (next4 == 1))[0]
                    if len(oi) > 0:
                        ot = oi[0]
                        if ot > 0 and np.any(effective_preds[:ot] >= tau):
                            det_c += 1
                            
                # Variant D: Any alert anywhere in stay
                if has_a:
                    sep_d += 1
                    if np.any(effective_preds >= tau):
                        det_d += 1
                        
            sens_a = det_a / max(sep_a, 1)
            sens_b = det_b / max(sep_b, 1)
            sens_c = det_c / max(sep_c, 1)
            sens_d = det_d / max(sep_d, 1)
            
            sweep_results.append({
                'tau_s': tau,
                'gated': gated,
                'sep_a': sep_a, 'det_a': det_a, 'sens_a': sens_a,
                'sep_b': sep_b, 'det_b': det_b, 'sens_b': sens_b,
                'sep_c': sep_c, 'det_c': det_c, 'sens_c': sens_c,
                'sep_d': sep_d, 'det_d': det_d, 'sens_d': sens_d,
            })
            
    df_res = pd.DataFrame(sweep_results)
    print("\n=========================================================================", flush=True)
    print("DETAILED SENSITIVITY FORENSIC MATRIX:", flush=True)
    print(df_res.to_string(), flush=True)
    print("=========================================================================", flush=True)

    # Save to JSON / CSV
    out_dir = "FINAL_BIOMARKERX/forensic_sensitivity_audit"
    os.makedirs(out_dir, exist_ok=True)
    df_res.to_csv(os.path.join(out_dir, "SENSITIVITY_FORENSIC_MATRIX.csv"), index=False)
    
    # -------------------------------------------------------------------------
    # IDENTIFY EXACT PATIENTS DIFFERING BETWEEN tau_s=0.035 and tau_s=0.055
    # or between 230/279 (82.44%) and 223/279 (79.93%)
    # -------------------------------------------------------------------------
    patient_status = []
    for pkey, comb in all_patient_records.items():
        labels = comb['SepsisLabel'].values
        next4 = comb['S_next4'].values
        preds = comb['risk_pred'].values
        
        has_a = np.any(labels == 1) or np.any(next4 == 1)
        if has_a:
            oi = np.where((labels == 1) | (next4 == 1))[0]
            ot = oi[0] if len(oi) > 0 else len(preds) - 1
            
            # Det at tau=0.035 ungated
            det_tau_035 = np.any(preds[:ot+1] >= 0.0350)
            
            # Det at tau=0.055 ungated
            det_tau_055 = np.any(preds[:ot+1] >= 0.0550)
            
            # Det at tau=0.035 gated
            gate = comb['traj_gate'].values
            eff_preds = np.where(gate == 1, preds, 0.0)
            det_tau_035_gated = np.any(eff_preds[:ot+1] >= 0.0350)
            
            patient_status.append({
                'patient_id': pkey,
                'onset_t': ot,
                'det_tau_035_ungated': det_tau_035,
                'det_tau_055_ungated': det_tau_055,
                'det_tau_035_gated': det_tau_035_gated,
                'max_risk_before_onset': float(np.max(preds[:ot+1])),
                'max_risk_full_stay': float(np.max(preds))
            })
            
    df_pts = pd.DataFrame(patient_status)
    df_pts.to_csv(os.path.join(out_dir, "SEPSIS_PATIENTS_DETECTION_STATUS.csv"), index=False)
    
    print(f"\nSepsis Patients summary (N={len(df_pts)}):", flush=True)
    print(f"  Detected at tau=0.0350 ungated: {df_pts['det_tau_035_ungated'].sum()} / {len(df_pts)} ({df_pts['det_tau_035_ungated'].sum()/len(df_pts)*100:.2f}%)", flush=True)
    print(f"  Detected at tau=0.0550 ungated: {df_pts['det_tau_055_ungated'].sum()} / {len(df_pts)} ({df_pts['det_tau_055_ungated'].sum()/len(df_pts)*100:.2f}%)", flush=True)
    print(f"  Detected at tau=0.0350 gated  : {df_pts['det_tau_035_gated'].sum()} / {len(df_pts)} ({df_pts['det_tau_035_gated'].sum()/len(df_pts)*100:.2f}%)", flush=True)
    
    # Exactly 230 / 279 = 82.43727598566308% -> 82.44%!
    # Let's find which tau_s yields EXACTLY 230 detected patients!
    det_230_pts = df_pts[df_pts['max_risk_before_onset'] >= 0.0350]
    print(f"\nNumber of patients with max_risk_before_onset >= 0.0350: {len(det_230_pts)}", flush=True)
    
    # Check max_risk_full_stay >= 0.0350
    det_full_stay = df_pts[df_pts['max_risk_full_stay'] >= 0.0350]
    print(f"Number of patients with max_risk_full_stay >= 0.0350: {len(det_full_stay)}", flush=True)

    # Let's check max_risk_before_onset distribution
    print("\nTop 15 sorted max_risk_before_onset around the threshold cutoff:")
    sorted_risks = df_pts.sort_values(by='max_risk_before_onset', ascending=False)
    print(sorted_risks.iloc[215:235][['patient_id', 'onset_t', 'max_risk_before_onset', 'max_risk_full_stay']].to_string())

if __name__ == '__main__':
    run_fast_audit()
