import os
import glob
import json
import time
import hashlib
import numpy as np
import pandas as pd
import joblib
from concurrent.futures import ProcessPoolExecutor

def compute_patient_hash(patient_id):
    return int(hashlib.sha256(str(patient_id).encode('utf-8')).hexdigest(), 16) % 100000

VALID_BASE_COLS = ['HR', 'O2Sat', 'Temp', 'SBP', 'MAP', 'DBP', 'Resp', 'BaseExcess', 
                   'HCO3', 'FiO2', 'pH', 'PaCO2', 'SaO2', 'AST', 'BUN', 'Alkalinephos', 
                   'Calcium', 'Chloride', 'Creatinine', 'Bilirubin_direct', 'Glucose', 
                   'Lactate', 'Magnesium', 'Phosphate', 'Potassium', 'Bilirubin_total', 
                   'TroponinI', 'Hct', 'Hgb', 'PTT', 'WBC', 'Fibrinogen', 'Platelets', 
                   'Age', 'Gender', 'Unit1', 'Unit2', 'HospAdmTime', 'ICULOS']

def process_single_file(fpath):
    try:
        pdf = pd.read_csv(fpath, sep='|')
        if 'SepsisLabel' not in pdf.columns:
            return None
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
            return None
        
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
        comb['HR_delta_val'] = g_delta['HR_delta'].values
        comb['MAP_delta_val'] = g_delta['MAP_delta'].values
        return pkey, comb
    except Exception as e:
        return None

def main():
    print("=========================================================================", flush=True)
    print("PARALLEL FORENSIC PATIENT SENSITIVITY SOLVER", flush=True)
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
    
    print(f"Parallel processing {len(test_files)} locked test files...", flush=True)
    
    patient_dict = {}
    with ProcessPoolExecutor() as executor:
        results = executor.map(process_single_file, test_files, chunksize=50)
        for res in results:
            if res is not None:
                pkey, comb = res
                patient_dict[pkey] = comb
                
    print(f"Loaded {len(patient_dict)} patients in {time.time() - t0:.2f} seconds!", flush=True)

    # Batch prediction
    all_dfs = []
    for pkey, comb in patient_dict.items():
        all_dfs.append(comb)
    full_df = pd.concat(all_dfs, axis=0).reset_index(drop=True)
    
    X_mat = full_df[feature_cols].fillna(train_medians).values
    raw_preds = clf.predict_proba(X_mat)[:, 1]
    cal_preds = calibrator.transform(raw_preds)
    full_df['risk_pred'] = cal_preds
    full_df['traj_gate'] = ((full_df['Shock_Index'] >= 0.85) | (full_df['HR_delta_val'] > 0.2) | (full_df['MAP_delta_val'] < -0.2)).astype(int)
    
    # Re-group by patient key
    patient_groups = {pkey: grp for pkey, grp in full_df.groupby('Patient_Key')}

    print("\n-------------------------------------------------------------------------", flush=True)
    print("FORENSIC THRESHOLD & POLICY SWEEP", flush=True)
    print("-------------------------------------------------------------------------", flush=True)
    
    sweep_results = []
    for tau in np.linspace(0.01, 0.08, 71):
        for gated in [False, True]:
            sep_a, det_a = 0, 0 # Onset = SepsisLabel==1 or S_next4==1
            sep_b, det_b = 0, 0 # Onset = SepsisLabel==1 ONLY
            sep_d, det_d = 0, 0 # Any alert anywhere in stay
            
            for pkey, grp in patient_groups.items():
                labels = grp['SepsisLabel'].values
                next4 = grp['S_next4'].values
                preds = grp['risk_pred'].values
                gate = grp['traj_gate'].values if gated else np.ones(len(preds), dtype=int)
                eff_preds = np.where(gate == 1, preds, 0.0)
                
                # Variant A: SepsisLabel==1 or S_next4==1
                has_a = np.any(labels == 1) or np.any(next4 == 1)
                if has_a:
                    sep_a += 1
                    oi = np.where((labels == 1) | (next4 == 1))[0]
                    if len(oi) > 0:
                        ot = oi[0]
                        if np.any(eff_preds[:ot+1] >= tau):
                            det_a += 1
                            
                # Variant B: SepsisLabel==1 ONLY
                has_b = np.any(labels == 1)
                if has_b:
                    sep_b += 1
                    oi = np.where(labels == 1)[0]
                    if len(oi) > 0:
                        ot = oi[0]
                        if np.any(eff_preds[:ot+1] >= tau):
                            det_b += 1
                            
                # Variant D: Any stay
                if has_a:
                    sep_d += 1
                    if np.any(eff_preds >= tau):
                        det_d += 1
                        
            sens_a = det_a / max(sep_a, 1)
            sens_b = det_b / max(sep_b, 1)
            sens_d = det_d / max(sep_d, 1)
            
            sweep_results.append({
                'tau': tau, 'gated': gated,
                'det_a': det_a, 'sep_a': sep_a, 'sens_a': sens_a,
                'det_b': det_b, 'sep_b': sep_b, 'sens_b': sens_b,
                'det_d': det_d, 'sep_d': sep_d, 'sens_d': sens_d
            })
            
    df_sw = pd.DataFrame(sweep_results)
    
    # Print results near 82.44% (det=230) and near 79.93% (det=223)
    print("\nExact Threshold Matches for det_a (Variant A, SepsisLabel | S_next4 onset):", flush=True)
    matches_230 = df_sw[df_sw['det_a'] == 230]
    print("Matches for 230 detected patients (82.44%):")
    print(matches_230.to_string())
    
    matches_223 = df_sw[df_sw['det_a'] == 223]
    print("\nMatches for 223 detected patients (79.93%):")
    print(matches_223.to_string())

    # Patient-level comparison table between tau_s=0.035 (223 det) and tau_s_old (230 det)
    # Find exact threshold tau that gives 230 detected patients
    tau_230 = matches_230.iloc[0]['tau'] if len(matches_230) > 0 else 0.0310
    gated_230 = matches_230.iloc[0]['gated'] if len(matches_230) > 0 else False
    
    patient_status = []
    for pkey, grp in patient_groups.items():
        labels = grp['SepsisLabel'].values
        next4 = grp['S_next4'].values
        preds = grp['risk_pred'].values
        gate = grp['traj_gate'].values
        
        has_a = np.any(labels == 1) or np.any(next4 == 1)
        if has_a:
            oi = np.where((labels == 1) | (next4 == 1))[0]
            ot = oi[0] if len(oi) > 0 else len(preds) - 1
            
            # Current canonical: tau=0.0350, ungated
            det_current = np.any(preds[:ot+1] >= 0.0350)
            
            # Old 82.44% run: tau=tau_230, gated/ungated
            eff_old = np.where(gate == 1, preds, 0.0) if gated_230 else preds
            det_old = np.any(eff_old[:ot+1] >= tau_230)
            
            # lock_final_target_operating_point.py: tau=0.0550, ungated
            det_055 = np.any(preds[:ot+1] >= 0.0550)
            
            patient_status.append({
                'patient_id': pkey,
                'onset_t': ot,
                'det_old_8244': det_old,
                'det_current_7993': det_current,
                'det_tau_055': det_055,
                'max_risk_before_onset': float(np.max(preds[:ot+1])),
                'max_risk_full_stay': float(np.max(preds))
            })
            
    df_pts = pd.DataFrame(patient_status)
    
    # Identify the 7 patients where OLD=1, CURRENT=0 or differing
    diff_pts = df_pts[df_pts['det_old_8244'] != df_pts['det_current_7993']]
    print(f"\n=========================================================================", flush=True)
    print(f"PATIENTS DIFFERING BETWEEN OLD 82.44% (det=230) AND CURRENT 79.93% (det=223):", flush=True)
    print(f"Total differing patients: {len(diff_pts)}")
    print(diff_pts.to_string(), flush=True)
    print("=========================================================================", flush=True)

    out_dir = "FINAL_BIOMARKERX/forensic_sensitivity_audit"
    os.makedirs(out_dir, exist_ok=True)
    df_sw.to_csv(os.path.join(out_dir, "FULL_FORENSIC_POLICY_SWEEP_MATRIX.csv"), index=False)
    df_pts.to_csv(os.path.join(out_dir, "EXACT_279_SEPSIS_PATIENTS_DETECTION_STATUS.csv"), index=False)
    diff_pts.to_csv(os.path.join(out_dir, "DIFFERING_PATIENTS_FORENSIC_LIST.csv"), index=False)

if __name__ == '__main__':
    main()
