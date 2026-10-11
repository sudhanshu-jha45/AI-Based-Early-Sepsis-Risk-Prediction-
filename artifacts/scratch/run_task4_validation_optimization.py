import os
import glob
import json
import time
import hashlib
import numpy as np
import pandas as pd
import joblib
from concurrent.futures import ProcessPoolExecutor
from sklearn.metrics import confusion_matrix

def compute_patient_hash(patient_id):
    return int(hashlib.sha256(str(patient_id).encode('utf-8')).hexdigest(), 16) % 100000

VALID_BASE_COLS = ['HR', 'O2Sat', 'Temp', 'SBP', 'MAP', 'DBP', 'Resp', 'BaseExcess', 
                   'HCO3', 'FiO2', 'pH', 'PaCO2', 'SaO2', 'AST', 'BUN', 'Alkalinephos', 
                   'Calcium', 'Chloride', 'Creatinine', 'Bilirubin_direct', 'Glucose', 
                   'Lactate', 'Magnesium', 'Phosphate', 'Potassium', 'Bilirubin_total', 
                   'TroponinI', 'Hct', 'Hgb', 'PTT', 'WBC', 'Fibrinogen', 'Platelets', 
                   'Age', 'Gender', 'Unit1', 'Unit2', 'HospAdmTime', 'ICULOS']

def process_file_val(fpath):
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
        
        hr = g_smooth['HR'].replace(0, np.nan); sbp = g_smooth['SBP'].replace(0, np.nan)
        map_v = g_smooth['MAP'].replace(0, np.nan); dbp = g_smooth['DBP'].replace(0, np.nan)
        resp = g_smooth['Resp'].replace(0, np.nan); temp = g_smooth['Temp'].replace(0, np.nan)
        wbc = g_smooth['WBC'].replace(0, np.nan)
        
        ratios = pd.DataFrame({
            'Shock_Index': (hr / (sbp + 1e-5)).fillna(0.8),
            'Mod_Shock_Index': (hr / (map_v + 1e-5)).fillna(1.1),
            'Pulse_Pressure': (sbp - dbp).fillna(40.0),
            'qSOFA_Causal': ((sbp <= 100).astype(int) + (resp >= 22).astype(int)).values,
            'SIRS_Causal': ((hr > 90).astype(int) + ((temp > 38.0) | (temp < 36.0)).astype(int) + (resp > 20).astype(int) + (wbc > 12.0).astype(int)).values
        }, index=g_smooth.index)
        
        comb = pd.concat([g_smooth, g_causal_z, g_delta, ratios], axis=1)
        comb['Patient_Key'] = pkey
        comb['S_next4'] = pdf_valid['S_next4'].astype(int).values
        comb['S_next1'] = pdf_valid['S_next1'].astype(int).values
        comb['SepsisLabel'] = pdf_valid['SepsisLabel'].astype(int).values
        comb['HR_delta_val'] = g_delta['HR_delta'].values
        comb['MAP_delta_val'] = g_delta['MAP_delta'].values
        return comb
    except Exception:
        return None

def main():
    print("=========================================================================", flush=True)
    print("TASK 4: HYPER-FAST VALIDATION-ONLY OPTIMIZATION (PHASES 1 TO 9)", flush=True)
    print("=========================================================================", flush=True)
    t0 = time.time()
    
    out_dir = "FINAL_BIOMARKERX/models_target_remediation_locked"
    val_out_dir = "FINAL_BIOMARKERX/validation_optimization"
    os.makedirs(val_out_dir, exist_ok=True)
    
    clf_path = os.path.join(out_dir, "TARGET_MASTER_MODEL.joblib")
    cal_path = os.path.join(out_dir, "TARGET_CALIBRATOR.joblib")
    med_path = os.path.join(out_dir, "TARGET_TRAIN_MEDIANS.joblib")
    
    clf = joblib.load(clf_path)
    calibrator = joblib.load(cal_path)
    train_medians = joblib.load(med_path)
    feature_cols = train_medians.index.tolist()

    # PHASE 1 — IDENTIFY VALIDATION COHORT
    psv_files = sorted(glob.glob('training_setA/*.psv'))
    patient_keys = [os.path.basename(f).replace('.psv', '') for f in psv_files]
    hashes = [compute_patient_hash(pk) for pk in patient_keys]
    
    val_files = [f for f, h in zip(psv_files, hashes) if 60 <= (h % 100) < 85]
    test_files = [f for f, h in zip(psv_files, hashes) if (h % 100) >= 85]
    
    val_pids = set([os.path.basename(f).replace('.psv', '') for f in val_files])
    test_pids = set([os.path.basename(f).replace('.psv', '') for f in test_files])
    overlap = val_pids.intersection(test_pids)
    
    print(f"[PHASE 1] Validation Set: {len(val_files)} files | Locked Test: {len(test_files)} files", flush=True)
    print(f"  Patient Overlap: {len(overlap)} overlapping patients (ZERO OVERLAP ASSERTION PASSED!)", flush=True)
    assert len(overlap) == 0
    
    print(f"  Parallel loading {len(val_files)} validation files...", flush=True)
    frames = []
    with ProcessPoolExecutor() as executor:
        results = executor.map(process_file_val, val_files, chunksize=50)
        for res in results:
            if res is not None:
                frames.append(res)
                
    df_val = pd.concat(frames, axis=0).reset_index(drop=True)
    X_val = df_val[feature_cols].fillna(train_medians).values
    raw_val = clf.predict_proba(X_val)[:, 1]
    cal_val = calibrator.transform(raw_val)
    
    df_val['pred'] = cal_val
    val_patients_count = df_val['Patient_Key'].nunique()
    val_windows_count = len(df_val)
    val_sepsis_events = df_val.groupby('Patient_Key')['SepsisLabel'].max().sum()
    
    print(f"  Loaded Validation Cohort: {val_windows_count} windows | {val_patients_count} patients | {val_sepsis_events} sepsis events in {time.time()-t0:.1f}s.", flush=True)

    # PRE-STRUCTURE PATIENT BOUNDARIES AND ARRAYS FOR 100X FAST PERSISTENCE
    pat_slice_bounds = []
    pat_preds = []
    pat_y4 = []
    pat_has_event = []
    pat_onset_t = []
    
    idx_cursor = 0
    for _, grp in df_val.groupby('Patient_Key', sort=False):
        plen = len(grp)
        pr = grp['pred'].values
        y4 = grp['S_next4'].values
        sl = grp['SepsisLabel'].values
        has_ev = np.any(sl == 1)
        oi = np.where(sl == 1)[0]
        ot = oi[0] if len(oi) > 0 else plen - 1
        
        pat_slice_bounds.append((idx_cursor, idx_cursor + plen))
        pat_preds.append(pr)
        pat_y4.append(y4)
        pat_has_event.append(has_ev)
        pat_onset_t.append(ot)
        idx_cursor += plen
        
    n_pats = len(pat_slice_bounds)
    pat_has_event = np.array(pat_has_event)
    pat_onset_t = np.array(pat_onset_t)
    
    y4_full = df_val['S_next4'].values
    preds_full = df_val['pred'].values
    total_days = len(df_val) / 24.0

    # Hyper-fast persistence scanner operating on contiguous numpy slices
    def fast_persistence(pc_raw, n_win):
        if n_win <= 1:
            return pc_raw
        pc_out = np.zeros(len(pc_raw), dtype=int)
        for start_i, end_i in pat_slice_bounds:
            vals = pc_raw[start_i:end_i]
            consec = 0
            for t in range(len(vals)):
                consec = consec + 1 if vals[t] == 1 else 0
                if consec >= n_win:
                    pc_out[start_i + t] = 1
        return pc_out

    # Fast evaluation function
    def eval_ultra_fast(tau_s, tau_c, p_win, g_mask=None):
        eff_p = np.where(g_mask == 1, preds_full, 0.0) if g_mask is not None else preds_full
        
        # Window screening
        ps = (eff_p >= tau_s).astype(int)
        tn_s, fp_s, fn_s, tp_s = confusion_matrix(y4_full, ps, labels=[0,1]).ravel()
        ws_ppv = tp_s / max(tp_s + fp_s, 1)
        ws_sens = tp_s / max(tp_s + fn_s, 1)
        
        # Window confirmation persistence
        pc_raw = (eff_p >= tau_c).astype(int)
        pc = fast_persistence(pc_raw, p_win)
        tn_c, fp_c, fn_c, tp_c = confusion_matrix(y4_full, pc, labels=[0,1]).ravel()
        wc_ppv = tp_c / max(tp_c + fp_c, 1)
        wc_sens = tp_c / max(tp_c + fn_c, 1)
        
        # Patient-level detection
        tp_p = fn_p = fp_p = tn_p = 0
        for i in range(n_pats):
            start_i, end_i = pat_slice_bounds[i]
            p_eff = eff_p[start_i:end_i]
            
            has_ev = pat_has_event[i]
            ot = pat_onset_t[i]
            alerted = np.any(p_eff >= tau_s)
            
            if has_ev:
                if np.any(p_eff[:ot+1] >= tau_s):
                    tp_p += 1
                else:
                    fn_p += 1
            else:
                if alerted: fp_p += 1
                else:       tn_p += 1
                
        pat_sens = tp_p / max(tp_p + fn_p, 1)
        pat_ppv = tp_p / max(tp_p + fp_p, 1)
        pat_spec = tn_p / max(tn_p + fp_p, 1)
        
        return {
            "patient_sensitivity": pat_sens,
            "patient_ppv": pat_ppv,
            "patient_specificity": pat_spec,
            "window_screening_sens": ws_sens,
            "window_screening_ppv": ws_ppv,
            "window_confirmation_ppv": wc_ppv,
            "window_confirmation_sens": wc_sens,
            "screening_alerts_per_day": (tp_s + fp_s) / max(total_days, 1),
            "confirmation_alerts_per_day": (tp_c + fp_c) / max(total_days, 1),
            "tp_patients": tp_p,
            "fn_patients": fn_p,
            "fp_patients": fp_p
        }

    # PHASE 2 — BASELINE VALIDATION POLICY
    print("\n[PHASE 2] Evaluating Baseline Policy on Validation Data...", flush=True)
    val_base_m = eval_ultra_fast(tau_s=0.0350, tau_c=0.1800, p_win=2, g_mask=None)
    print(f"  Validation Baseline Metrics:")
    print(f"    Patient Sensitivity : {val_base_m['patient_sensitivity']*100:.2f}% ({val_base_m['tp_patients']}/{val_base_m['tp_patients']+val_base_m['fn_patients']})")
    print(f"    Screening PPV       : {val_base_m['window_screening_ppv']*100:.2f}%")
    print(f"    Confirmation PPV    : {val_base_m['window_confirmation_ppv']*100:.2f}%")
    print(f"    Confirmation Sens   : {val_base_m['window_confirmation_sens']*100:.2f}%")
    print(f"    Screening Alerts/day: {val_base_m['screening_alerts_per_day']:.2f}")

    with open(os.path.join(val_out_dir, "PHASE2_VALIDATION_BASELINE_METRICS.json"), "w", encoding='utf-8') as f:
        json.dump(val_base_m, f, indent=2)

    # PHASES 3-6 — GRID SEARCH ON VALIDATION
    print("\n[PHASES 3-6] Running Ultra-Fast Grid Search on Validation Data...", flush=True)
    tau_s_grid = [0.020, 0.025, 0.030, 0.035, 0.040, 0.050]
    tau_c_grid = [0.100, 0.125, 0.150, 0.180, 0.200, 0.225, 0.250]
    persist_grid = [1, 2, 3]
    
    gate_dict = {
        "OFF": None,
        "ShockIndex_085_or_HR_MAP_delta": ((df_val['Shock_Index'] >= 0.85) | (df_val['HR_delta_val'] > 0.2) | (df_val['MAP_delta_val'] < -0.2)).astype(int).values,
        "ShockIndex_085_only": (df_val['Shock_Index'] >= 0.85).astype(int).values,
        "Delta_HR_MAP_03": ((df_val['HR_delta_val'] > 0.3) | (df_val['MAP_delta_val'] < -0.3)).astype(int).values,
    }
    
    grid_rows = []
    pid_counter = 1
    t_grid_start = time.time()
    
    for ts in tau_s_grid:
        for tc in tau_c_grid:
            if tc < ts: continue
            for p_win in persist_grid:
                for g_name, g_val in gate_dict.items():
                    m = eval_ultra_fast(ts, tc, p_win, g_mask=g_val)
                    row = {
                        "policy_id": f"POL_{pid_counter:04d}",
                        "tau_screening": ts,
                        "tau_confirmation": tc,
                        "persistence_windows": p_win,
                        "trajectory_filter": g_name,
                        "patient_sensitivity": m['patient_sensitivity'],
                        "window_screening_sens": m['window_screening_sens'],
                        "window_screening_ppv": m['window_screening_ppv'],
                        "window_confirmation_ppv": m['window_confirmation_ppv'],
                        "window_confirmation_sens": m['window_confirmation_sens'],
                        "patient_specificity": m['patient_specificity'],
                        "screening_alerts_per_day": m['screening_alerts_per_day'],
                        "confirmation_alerts_per_day": m['confirmation_alerts_per_day'],
                        "tp_patients": m['tp_patients'],
                        "fn_patients": m['fn_patients'],
                        "fp_patients": m['fp_patients']
                    }
                    grid_rows.append(row)
                    pid_counter += 1

    print(f"  Completed Grid Search: {len(grid_rows)} candidate policies evaluated in {time.time() - t_grid_start:.2f} seconds!", flush=True)

    df_grid = pd.DataFrame(grid_rows)

    # PHASE 8 — PARETO FRONTIER ON VALIDATION
    print("\n[PHASE 8] Validation Candidate Table (Sorted by Confirmation PPV at Patient Sensitivity >= 80%):", flush=True)
    df_80 = df_grid[df_grid['patient_sensitivity'] >= 0.80].copy()
    top_candidates = df_80.sort_values(by='window_confirmation_ppv', ascending=False).head(15)
    print(top_candidates[['policy_id', 'tau_screening', 'tau_confirmation', 'persistence_windows', 'trajectory_filter', 'patient_sensitivity', 'window_screening_ppv', 'window_confirmation_ppv', 'window_confirmation_sens']].to_string())

    df_grid.to_csv(os.path.join(val_out_dir, "PHASE8_VALIDATION_GRID_SWEEP.csv"), index=False)

    # PHASE 9 — PRE-SPECIFY AND LOCK FINAL POLICY BASED ON VALIDATION ONLY
    print("\n[PHASE 9] Pre-Specifying and Locking Final Policy Based ONLY on Validation Data...", flush=True)
    
    selected_policy_row = top_candidates.iloc[0].to_dict()
    
    policy_lock = {
        "policy_id": selected_policy_row['policy_id'],
        "policy_hash": hashlib.sha256(json.dumps(selected_policy_row, sort_keys=True, default=str).encode('utf-8')).hexdigest(),
        "tau_screening": float(selected_policy_row['tau_screening']),
        "tau_confirmation": float(selected_policy_row['tau_confirmation']),
        "persistence_windows": int(selected_policy_row['persistence_windows']),
        "trajectory_filter": selected_policy_row['trajectory_filter'],
        "onset_definition": "SepsisLabel",
        "episode_grouping_rule": "first_episode_per_patient",
        "validation_performance_metrics": selected_policy_row,
        "selection_dataset": f"Validation Cohort (N={val_patients_count} patients, N={val_windows_count} windows)",
        "selection_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "lock_status": "FROZEN_VALIDATION_POLICY_LOCK"
    }
    
    lock_path = os.path.join(val_out_dir, "TASK4_VALIDATION_POLICY_LOCK.json")
    with open(lock_path, "w", encoding='utf-8') as f:
        json.dump(policy_lock, f, indent=2)
        
    print(f"  FROZEN POLICY LOCK WRITTEN TO: {lock_path}")
    print(f"  Selected Policy: {policy_lock['policy_id']}")
    print(f"    tau_screening        : {policy_lock['tau_screening']}")
    print(f"    tau_confirmation     : {policy_lock['tau_confirmation']}")
    print(f"    persistence_windows  : {policy_lock['persistence_windows']}")
    print(f"    trajectory_filter    : {policy_lock['trajectory_filter']}")
    print(f"    Val Patient Sens     : {selected_policy_row['patient_sensitivity']*100:.2f}%")
    print(f"    Val Screening PPV    : {selected_policy_row['window_screening_ppv']*100:.2f}%")
    print(f"    Val Confirmation PPV : {selected_policy_row['window_confirmation_ppv']*100:.2f}%")
    print(f"    Val Confirmation Sens: {selected_policy_row['window_confirmation_sens']*100:.2f}%")

    print(f"\nTask 4 Validation Optimization complete in {time.time() - t0:.1f}s!", flush=True)

if __name__ == '__main__':
    main()
