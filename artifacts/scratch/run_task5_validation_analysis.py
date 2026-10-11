import os
import glob
import json
import time
import hashlib
import numpy as np
import pandas as pd
import joblib
from scipy.stats import mannwhitneyu
from concurrent.futures import ProcessPoolExecutor
from sklearn.metrics import confusion_matrix
from canonical_evaluate_policy import evaluate_policy

def compute_patient_hash(patient_id):
    return int(hashlib.sha256(str(patient_id).encode('utf-8')).hexdigest(), 16)

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
        
        g_delta_3h = (g_smooth - g_smooth.shift(3)).fillna(0.0)
        g_delta_6h = (g_smooth - g_smooth.shift(6)).fillna(0.0)
        
        hr = g_smooth['HR'].replace(0, np.nan); sbp = g_smooth['SBP'].replace(0, np.nan)
        map_v = g_smooth['MAP'].replace(0, np.nan); dbp = g_smooth['DBP'].replace(0, np.nan)
        resp = g_smooth['Resp'].replace(0, np.nan); temp = g_smooth['Temp'].replace(0, np.nan)
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
        comb['ICULOS'] = pdf_valid['ICULOS'].values
        comb['Age'] = pdf_valid['Age'].values
        comb['Gender'] = pdf_valid['Gender'].values
        comb['Unit1'] = pdf_valid['Unit1'].values
        comb['Unit2'] = pdf_valid['Unit2'].values
        
        comb['HR_delta_3h'] = g_delta_3h['HR'].values
        comb['HR_delta_6h'] = g_delta_6h['HR'].values
        comb['MAP_delta_3h'] = g_delta_3h['MAP'].values
        comb['MAP_delta_6h'] = g_delta_6h['MAP'].values
        comb['Shock_Index_delta_1h'] = shock_index.diff().fillna(0.0).values
        comb['Shock_Index_delta_3h'] = (shock_index - shock_index.shift(3)).fillna(0.0).values
        comb['PP_delta_1h'] = pulse_pressure.diff().fillna(0.0).values
        comb['PP_delta_3h'] = (pulse_pressure - pulse_pressure.shift(3)).fillna(0.0).values
        
        return comb
    except Exception:
        return None

def compute_stats(arr):
    arr_clean = arr[~np.isnan(arr)]
    if len(arr_clean) == 0:
        return {"mean": 0.0, "std": 0.0, "median": 0.0, "p25": 0.0, "p75": 0.0, "iqr": 0.0, "min": 0.0, "max": 0.0, "missingness_pct": 100.0}
    p25 = float(np.percentile(arr_clean, 25))
    p75 = float(np.percentile(arr_clean, 75))
    return {
        "mean": float(np.mean(arr_clean)),
        "std": float(np.std(arr_clean)),
        "median": float(np.median(arr_clean)),
        "p25": p25,
        "p75": p75,
        "iqr": float(p75 - p25),
        "min": float(np.min(arr_clean)),
        "max": float(np.max(arr_clean)),
        "missingness_pct": float(100.0 * (len(arr) - len(arr_clean)) / max(len(arr), 1))
    }

def main():
    print("=========================================================================", flush=True)
    print("BIO MARKERX — TASK 5: VALIDATION-ONLY ANALYSIS (PHASES 1 TO 8)", flush=True)
    print("=========================================================================", flush=True)
    t0 = time.time()
    
    out_dir = "FINAL_BIOMARKERX/task5_physiological_confirmation"
    os.makedirs(out_dir, exist_ok=True)
    
    model_dir = "FINAL_BIOMARKERX/models_target_remediation_locked"
    clf = joblib.load(os.path.join(model_dir, "TARGET_MASTER_MODEL.joblib"))
    calibrator = joblib.load(os.path.join(model_dir, "TARGET_CALIBRATOR.joblib"))
    train_medians = joblib.load(os.path.join(model_dir, "TARGET_TRAIN_MEDIANS.joblib"))
    feature_cols = train_medians.index.tolist()
    
    # -------------------------------------------------------------------------
    # PHASE 1 — DATA PROVENANCE & ZERO-LEAKAGE VERIFICATION
    # -------------------------------------------------------------------------
    psv_files = sorted(glob.glob('training_setA/*.psv'))
    patient_keys = [os.path.basename(f).replace('.psv', '') for f in psv_files]
    hashes = [compute_patient_hash(pk) for pk in patient_keys]
    
    val_files = [f for f, h in zip(psv_files, hashes) if 60 <= (h % 100) < 85]
    test_files = [f for f, h in zip(psv_files, hashes) if (h % 100) >= 85]
    train_files = [f for f, h in zip(psv_files, hashes) if (h % 100) < 60]
    
    val_pids = set([os.path.basename(f).replace('.psv', '') for f in val_files])
    test_pids = set([os.path.basename(f).replace('.psv', '') for f in test_files])
    train_pids = set([os.path.basename(f).replace('.psv', '') for f in train_files])
    
    overlap_val_test = val_pids.intersection(test_pids)
    overlap_train_val = train_pids.intersection(val_pids)
    overlap_train_test = train_pids.intersection(test_pids)
    
    print(f"[PHASE 1] Cohort Split:")
    print(f"  Train Set      : {len(train_files)} patients")
    print(f"  Validation Set : {len(val_files)} patients")
    print(f"  Locked Test Set: {len(test_files)} patients")
    print(f"  Val/Test Overlap   : {len(overlap_val_test)} (ASSERT ZERO)")
    print(f"  Train/Val Overlap  : {len(overlap_train_val)} (ASSERT ZERO)")
    print(f"  Train/Test Overlap : {len(overlap_train_test)} (ASSERT ZERO)")
    assert len(overlap_val_test) == 0 and len(overlap_train_val) == 0 and len(overlap_train_test) == 0
    
    provenance_meta = {
        "task": "Task 5 - Physiological Confirmation & False-Alert Forensic Analysis",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_psv_files": len(psv_files),
        "train_patients": len(train_files),
        "validation_patients": len(val_files),
        "locked_test_patients": len(test_files),
        "zero_leakage_assertion_passed": True,
        "hash_rule": {
            "train": "hash % 100 < 60",
            "validation": "60 <= hash % 100 < 85",
            "locked_test": "hash % 100 >= 85"
        }
    }
    
    with open(os.path.join(out_dir, "TASK5_PHASE1_DATA_PROVENANCE.json"), "w", encoding='utf-8') as f:
        json.dump(provenance_meta, f, indent=2)
        
    with open(os.path.join(out_dir, "TASK5_PHASE1_DATA_PROVENANCE.md"), "w", encoding='utf-8') as f:
        f.write("# BioMarkerX Task 5 — Phase 1: Data Provenance & Zero-Leakage Audit\n\n")
        f.write("## Cohort Verification\n\n")
        f.write(f"- **Total PSV Files**: {len(psv_files):,}\n")
        f.write(f"- **Development/Train Patients**: {len(train_files):,}\n")
        f.write(f"- **Validation Patients**: {len(val_files):,}\n")
        f.write(f"- **Locked Test Patients**: {len(test_files):,}\n")
        f.write("- **Validation vs. Test Patient Overlap**: 0 (PASS)\n")
        f.write("- **Train vs. Validation Patient Overlap**: 0 (PASS)\n")
        f.write("- **Train vs. Test Patient Overlap**: 0 (PASS)\n\n")
        f.write("## Strict Audit Rule\n")
        f.write("All false-alert forensics, temporal pattern analyses, candidate physiological gating sweeps, ")
        f.write("and policy lock selections are conducted strictly on **Validation Data ONLY**.\n")

    # -------------------------------------------------------------------------
    # PARALLEL EXTRACTION & MODEL INFERENCE ON VALIDATION SET
    # -------------------------------------------------------------------------
    print(f"\n[PARALLEL EXTRACTION] Extracting features & inference on {len(val_files)} validation patients...", flush=True)
    frames = []
    with ProcessPoolExecutor() as executor:
        results = executor.map(process_file_val, val_files, chunksize=50)
        for res in results:
            if res is not None:
                frames.append(res)
                
    df_val = pd.concat(frames, axis=0).reset_index(drop=True)
    print(f"Validation dataset constructed: {len(df_val):,} windows across {df_val['Patient_Key'].nunique():,} patients.", flush=True)
    
    X_val = df_val.reindex(columns=feature_cols).fillna(train_medians).values
    raw_probs = clf.predict_proba(X_val)[:, 1]
    if hasattr(calibrator, 'transform'):
        cal_probs = calibrator.transform(raw_probs)
    elif hasattr(calibrator, 'predict_proba'):
        cal_probs = calibrator.predict_proba(raw_probs.reshape(-1, 1))[:, 1]
    else:
        cal_probs = calibrator.predict(raw_probs)
    df_val['pred'] = cal_probs
    
    val_sepsis_patients = df_val.groupby('Patient_Key')['SepsisLabel'].max().sum()
    print(f"Validation Sepsis Patients: {val_sepsis_patients:,} / {df_val['Patient_Key'].nunique():,}", flush=True)
    
    # -------------------------------------------------------------------------
    # PHASE 2 — FALSE-ALERT FORENSICS ON VALIDATION DATA ONLY
    # -------------------------------------------------------------------------
    print("\n[PHASE 2] Executing False-Alert Forensics on Validation Data...", flush=True)
    tau_s_task4 = 0.020
    tau_c_task4 = 0.250
    p_task4 = 2
    
    df_val['p_s'] = (df_val['pred'] >= tau_s_task4).astype(int)
    
    from canonical_evaluate_policy import apply_persistence_filter
    p_c_raw = (df_val['pred'] >= tau_c_task4).astype(int)
    df_val['p_c'] = apply_persistence_filter(p_c_raw, df_val['Patient_Key'].values, n_windows=p_task4)
    
    w_true_trans = df_val[(df_val['S_next4'] == 1) & (df_val['p_s'] == 1)]
    w_false_screen = df_val[(df_val['S_next4'] == 0) & (df_val['p_s'] == 1)]
    w_false_confirm = df_val[(df_val['S_next4'] == 0) & (df_val['p_c'] == 1)]
    w_true_neg = df_val[(df_val['S_next4'] == 0) & (df_val['p_s'] == 0)]
    
    print(f"  True Transition Windows: {len(w_true_trans):,}")
    print(f"  False Screening Alerts: {len(w_false_screen):,}")
    print(f"  False Confirmation Alerts: {len(w_false_confirm):,}")
    print(f"  True Negative Windows: {len(w_true_neg):,}")
    
    forensic_vars = [
        'HR', 'HR_delta', 'HR_delta_3h', 'HR_delta_6h',
        'MAP', 'MAP_delta', 'MAP_delta_3h', 'MAP_delta_6h',
        'Shock_Index', 'Shock_Index_delta_1h', 'Shock_Index_delta_3h',
        'Pulse_Pressure', 'PP_delta_1h', 'PP_delta_3h',
        'qSOFA_Causal', 'SIRS_Causal'
    ]
    
    forensic_rows = []
    markdown_lines = []
    markdown_lines.append("# BioMarkerX Task 5 — Phase 2: False-Alert Forensics Report (Validation Cohort)\n")
    markdown_lines.append(f"**Cohort**: Validation Data ($N={df_val['Patient_Key'].nunique():,}$ patients, {len(df_val):,} windows)\n")
    markdown_lines.append(f"**Baseline Policy**: $\\tau_s={tau_s_task4:.3f}$, $\\tau_c={tau_c_task4:.3f}$, persistence=$2$, ungated\n\n")
    markdown_lines.append("| Variable | True Transition Median (IQR) | False Screening Median (IQR) | False Confirm Median (IQR) | Mann-Whitney p (False Screen vs True Trans) | Cohen's d |\n")
    markdown_lines.append("|---|---|---|---|---|---|\n")
    
    for var in forensic_vars:
        st_tt = compute_stats(w_true_trans[var].values)
        st_fs = compute_stats(w_false_screen[var].values)
        st_fc = compute_stats(w_false_confirm[var].values)
        st_tn = compute_stats(w_true_neg[var].values)
        
        arr_tt = w_true_trans[var].dropna().values
        arr_fs = w_false_screen[var].dropna().values
        if len(arr_tt) > 0 and len(arr_fs) > 0:
            stat_mwu, p_mwu = mannwhitneyu(arr_fs, arr_tt, alternative='two-sided')
            mean_diff = np.mean(arr_fs) - np.mean(arr_tt)
            pooled_std = np.sqrt((np.var(arr_fs) + np.var(arr_tt)) / 2.0) + 1e-8
            cohen_d = float(mean_diff / pooled_std)
        else:
            p_mwu = 1.0
            cohen_d = 0.0
            
        forensic_rows.append({
            "variable": var,
            "true_transition_median": st_tt["median"],
            "true_transition_iqr": f"{st_tt['p25']:.2f}-{st_tt['p75']:.2f}",
            "false_screening_median": st_fs["median"],
            "false_screening_iqr": f"{st_fs['p25']:.2f}-{st_fs['p75']:.2f}",
            "false_confirm_median": st_fc["median"],
            "false_confirm_iqr": f"{st_fc['p25']:.2f}-{st_fc['p75']:.2f}",
            "mwu_p_val": float(p_mwu),
            "cohens_d": cohen_d
        })
        
        markdown_lines.append(
            f"| `{var}` | {st_tt['median']:.2f} ({st_tt['p25']:.2f}–{st_tt['p75']:.2f}) | "
            f"{st_fs['median']:.2f} ({st_fs['p25']:.2f}–{st_fs['p75']:.2f}) | "
            f"{st_fc['median']:.2f} ({st_fc['p25']:.2f}–{st_fc['p75']:.2f}) | "
            f"{p_mwu:.2e} | {cohen_d:+.3f} |\n"
        )
        
    df_forensics = pd.DataFrame(forensic_rows)
    df_forensics.to_csv(os.path.join(out_dir, "TASK5_PHASE2_FALSE_ALERT_FORENSICS.csv"), index=False)
    
    with open(os.path.join(out_dir, "TASK5_PHASE2_FALSE_ALERT_FORENSICS.md"), "w", encoding='utf-8') as f:
        f.writelines(markdown_lines)
        
    # -------------------------------------------------------------------------
    # PHASE 3 — TEMPORAL PATTERN & TRAJECTORY ANALYSIS
    # -------------------------------------------------------------------------
    print("\n[PHASE 3] Computing Temporal Pattern & Trajectory Analysis...", flush=True)
    temp_rows = []
    
    for pk, grp in df_val.groupby('Patient_Key'):
        sl = grp['SepsisLabel'].values
        if np.any(sl == 1):
            onset_t = np.where(sl == 1)[0][0]
            h12_6 = grp.iloc[max(0, onset_t-12):max(0, onset_t-6)]
            h6_3 = grp.iloc[max(0, onset_t-6):max(0, onset_t-3)]
            h3_1 = grp.iloc[max(0, onset_t-3):max(0, onset_t-1)]
            h0 = grp.iloc[onset_t:onset_t+1]
            
            temp_rows.append({
                "patient_key": pk,
                "is_sepsis": 1,
                "si_12_6h": h12_6['Shock_Index'].median() if len(h12_6)>0 else np.nan,
                "si_6_3h": h6_3['Shock_Index'].median() if len(h6_3)>0 else np.nan,
                "si_3_1h": h3_1['Shock_Index'].median() if len(h3_1)>0 else np.nan,
                "si_onset": h0['Shock_Index'].values[0] if len(h0)>0 else np.nan,
                "hr_delta3h_onset": h0['HR_delta_3h'].values[0] if len(h0)>0 else np.nan,
                "map_delta3h_onset": h0['MAP_delta_3h'].values[0] if len(h0)>0 else np.nan,
                "qsofa_onset": h0['qSOFA_Causal'].values[0] if len(h0)>0 else np.nan,
                "sirs_onset": h0['SIRS_Causal'].values[0] if len(h0)>0 else np.nan
            })
            
    df_temp = pd.DataFrame(temp_rows)
    df_temp.to_csv(os.path.join(out_dir, "TASK5_PHASE3_TEMPORAL_ANALYSIS.csv"), index=False)
    
    # -------------------------------------------------------------------------
    # PHASE 4 & 5 — FAST HYPER-OPTIMIZED CANDIDATE PHYSIOLOGICAL RULE SWEEP
    # -------------------------------------------------------------------------
    print("\n[PHASE 4 & 5] Sweeping Candidate Physiological Confirmation Rules on Validation Data...", flush=True)
    
    si = df_val['Shock_Index'].values
    hr_d3 = df_val['HR_delta_3h'].values
    map_d3 = df_val['MAP_delta_3h'].values
    qsofa = df_val['qSOFA_Causal'].values
    sirs = df_val['SIRS_Causal'].values
    pp = df_val['Pulse_Pressure'].values
    pp_d3 = df_val['PP_delta_3h'].values
    
    gating_rules = {
        "Rule_A_Baseline_Ungated": np.ones(len(df_val), dtype=int),
        "Rule_B_ShockIndex_070": (si >= 0.70).astype(int),
        "Rule_C_ShockIndex_075": (si >= 0.75).astype(int),
        "Rule_D_HR_Trend": ((df_val['HR'] >= 90) | (hr_d3 >= 3)).astype(int),
        "Rule_E_MAP_Trend": ((df_val['MAP'] <= 75) | (map_d3 <= -3)).astype(int),
        "Rule_F_qSOFA_1": (qsofa >= 1).astype(int),
        "Rule_G_SIRS_2": (sirs >= 2).astype(int),
        "Rule_H_Composite_Instability": ((si >= 0.70) | (hr_d3 >= 3) | (qsofa >= 1) | (map_d3 <= -3)).astype(int),
        "Rule_I_Strict_Instability": ((si >= 0.75) & ((qsofa >= 1) | (sirs >= 2))).astype(int),
        "Rule_J_PulsePressure_Drop": ((pp <= 45) | (pp_d3 <= -5)).astype(int)
    }
    
    # Pre-structure patient slice bounds for ultra-fast persistence scanning
    pat_slice_bounds = []
    pat_has_event = []
    pat_onset_t = []
    
    idx_cursor = 0
    for _, grp in df_val.groupby('Patient_Key', sort=False):
        plen = len(grp)
        sl = grp['SepsisLabel'].values
        has_ev = np.any(sl == 1)
        oi = np.where(sl == 1)[0]
        ot = oi[0] if len(oi) > 0 else plen - 1
        
        pat_slice_bounds.append((idx_cursor, idx_cursor + plen))
        pat_has_event.append(has_ev)
        pat_onset_t.append(ot)
        idx_cursor += plen
        
    n_pats = len(pat_slice_bounds)
    pat_has_event = np.array(pat_has_event)
    pat_onset_t = np.array(pat_onset_t)
    
    y4_full = df_val['S_next4'].values
    preds_full = df_val['pred'].values
    total_days = len(df_val) / 24.0
    
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

    def eval_ultra_fast(tau_s, tau_c, p_win, g_mask):
        eff_p = np.where(g_mask == 1, preds_full, 0.0)
        
        ps = (eff_p >= tau_s).astype(int)
        tn_s, fp_s, fn_s, tp_s = confusion_matrix(y4_full, ps, labels=[0,1]).ravel()
        ws_ppv = tp_s / max(tp_s + fp_s, 1)
        ws_sens = tp_s / max(tp_s + fn_s, 1)
        
        pc_raw = (eff_p >= tau_c).astype(int)
        pc = fast_persistence(pc_raw, p_win)
        tn_c, fp_c, fn_c, tp_c = confusion_matrix(y4_full, pc, labels=[0,1]).ravel()
        wc_ppv = tp_c / max(tp_c + fp_c, 1)
        wc_sens = tp_c / max(tp_c + fn_c, 1)
        
        tp_p = fn_p = fp_p = tn_p = 0
        lead_times = []
        for i in range(n_pats):
            start_i, end_i = pat_slice_bounds[i]
            p_eff = eff_p[start_i:end_i]
            
            has_ev = pat_has_event[i]
            ot = pat_onset_t[i]
            alerted = np.any(p_eff >= tau_s)
            
            if has_ev:
                alerts_before = np.where(p_eff[:ot+1] >= tau_s)[0]
                if len(alerts_before) > 0:
                    tp_p += 1
                    lead_times.append(max(0, ot - alerts_before[0]))
                else:
                    fn_p += 1
            else:
                if alerted: fp_p += 1
                else:       tn_p += 1
                
        pat_sens = tp_p / max(tp_p + fn_p, 1)
        pat_ppv = tp_p / max(tp_p + fp_p, 1)
        pat_spec = tn_p / max(tn_p + fp_p, 1)
        med_lt = float(np.median(lead_times)) if len(lead_times) > 0 else 0.0
        
        return {
            "patient_sensitivity": pat_sens,
            "patient_ppv": pat_ppv,
            "patient_specificity": pat_spec,
            "window_screening_ppv": ws_ppv,
            "window_confirmation_ppv": wc_ppv,
            "window_confirmation_sens": wc_sens,
            "screening_alert_burden": (tp_s + fp_s) / max(total_days, 1),
            "confirmation_alert_burden": (tp_c + fp_c) / max(total_days, 1),
            "median_lead_time": med_lt,
            "tp_patients": tp_p,
            "fn_patients": fn_p,
            "fp_patients": fp_p
        }

    tau_s_grid = [0.015, 0.020, 0.025, 0.030, 0.035, 0.040]
    tau_c_grid = [0.150, 0.180, 0.200, 0.220, 0.250, 0.300]
    persistence_grid = [1, 2, 3]
    
    val_sweep_results = []
    combo_count = 0
    
    for r_name, gate_arr in gating_rules.items():
        for ts in tau_s_grid:
            for tc in tau_c_grid:
                if tc < ts:
                    continue
                for p_win in persistence_grid:
                    combo_count += 1
                    m = eval_ultra_fast(ts, tc, p_win, gate_arr)
                    val_sweep_results.append({
                        "policy_id": f"VAL_POL_{combo_count:04d}",
                        "rule_name": r_name,
                        "tau_screening": ts,
                        "tau_confirmation": tc,
                        "persistence_windows": p_win,
                        "patient_sensitivity": m['patient_sensitivity'],
                        "patient_ppv": m['patient_ppv'],
                        "patient_specificity": m['patient_specificity'],
                        "window_screening_ppv": m['window_screening_ppv'],
                        "window_confirmation_ppv": m['window_confirmation_ppv'],
                        "window_confirmation_sens": m['window_confirmation_sens'],
                        "screening_alert_burden": m['screening_alert_burden'],
                        "confirmation_alert_burden": m['confirmation_alert_burden'],
                        "median_lead_time": m['median_lead_time'],
                        "tp_patients": m['tp_patients'],
                        "fn_patients": m['fn_patients'],
                        "fp_patients": m['fp_patients'],
                        "satisfies_sens_target": bool(m['patient_sensitivity'] >= 0.80)
                    })
                    
    df_sweep = pd.DataFrame(val_sweep_results)
    df_sweep.to_csv(os.path.join(out_dir, "TASK5_PHASE4_PHYSIOLOGICAL_RULE_SWEEP.csv"), index=False)
    df_sweep.to_csv(os.path.join(out_dir, "TASK5_PHASE5_VALIDATION_RESULTS.csv"), index=False)
    
    print(f"Ultra-fast grid sweep complete! Evaluated {len(df_sweep):,} combinations.")
    df_valid_targets = df_sweep[df_sweep['satisfies_sens_target'] == True]
    print(f"Configurations satisfying Validation Patient Sensitivity >= 80.0%: {len(df_valid_targets):,} / {len(df_sweep):,}")
    
    # -------------------------------------------------------------------------
    # PHASE 7 — VALIDATION PARETO FRONTIER & SELECTION
    # -------------------------------------------------------------------------
    print("\n[PHASE 7] Constructing Validation Pareto Frontier & Locking Optimal Policy...", flush=True)
    
    pareto_rows = []
    df_valid_sorted = df_valid_targets.sort_values(by=['window_confirmation_ppv', 'patient_sensitivity'], ascending=False)
    
    best_c_ppv = -1.0
    for idx, row in df_valid_sorted.iterrows():
        if row['window_confirmation_ppv'] > best_c_ppv:
            best_c_ppv = row['window_confirmation_ppv']
            pareto_rows.append(row.to_dict())
            
    df_pareto = pd.DataFrame(pareto_rows)
    df_pareto.to_csv(os.path.join(out_dir, "TASK5_PHASE7_VALIDATION_PARETO.csv"), index=False)
    print(f"Pareto Frontier constructed: {len(df_pareto)} optimal points.")
    
    # Select optimal policy: Maximize Confirmation PPV while Patient Sensitivity >= 80.0%
    best_policy_row = df_valid_targets.sort_values(by=['window_confirmation_ppv', 'patient_sensitivity'], ascending=[False, False]).iloc[0]
    
    print(f"\nSELECTED FROZEN OPTIMAL POLICY ON VALIDATION DATA:")
    print(f"  Policy ID             : {best_policy_row['policy_id']}")
    print(f"  Physiological Rule   : {best_policy_row['rule_name']}")
    print(f"  tau_screening         : {best_policy_row['tau_screening']}")
    print(f"  tau_confirmation      : {best_policy_row['tau_confirmation']}")
    print(f"  persistence_windows   : {best_policy_row['persistence_windows']}")
    print(f"  Validation Patient Sens: {best_policy_row['patient_sensitivity']*100:.2f}% ({best_policy_row['tp_patients']}/{best_policy_row['tp_patients']+best_policy_row['fn_patients']})")
    print(f"  Validation Confirm PPV: {best_policy_row['window_confirmation_ppv']*100:.2f}%")
    print(f"  Validation Screen PPV : {best_policy_row['window_screening_ppv']*100:.2f}%")
    print(f"  Validation Median LT  : {best_policy_row['median_lead_time']:.1f} h")
    print(f"  Validation Confirm Burden: {best_policy_row['confirmation_alert_burden']:.2f} alerts/patient-day")

    # -------------------------------------------------------------------------
    # PHASE 6 — SUBGROUP & STABILITY ANALYSIS (VALIDATION DATA ONLY)
    # -------------------------------------------------------------------------
    print("\n[PHASE 6] Evaluating Subgroup & Stability Analysis on Validation Data...", flush=True)
    selected_rule_name = best_policy_row['rule_name']
    selected_gate = gating_rules[selected_rule_name]
    selected_ts = float(best_policy_row['tau_screening'])
    selected_tc = float(best_policy_row['tau_confirmation'])
    selected_p = int(best_policy_row['persistence_windows'])
    
    subgroups = {
        "Age < 65": df_val['Age'] < 65,
        "Age >= 65": df_val['Age'] >= 65,
        "Gender Female (0)": df_val['Gender'] == 0,
        "Gender Male (1)": df_val['Gender'] == 1,
        "ICULOS <= 24h": df_val['ICULOS'] <= 24,
        "ICULOS > 24h": df_val['ICULOS'] > 24
    }
    
    subgroup_rows = []
    for sg_name, sg_mask in subgroups.items():
        df_sg = df_val[sg_mask]
        if len(df_sg) == 0:
            continue
        res_sg = evaluate_policy(
            predictions=df_sg['pred'].values,
            patient_ids=df_sg['Patient_Key'].values,
            timestamps=df_sg['ICULOS'].values,
            sepsis_labels=df_sg['SepsisLabel'].values,
            s_next4=df_sg['S_next4'].values,
            tau_screening=selected_ts,
            tau_confirmation=selected_tc,
            persistence_windows=selected_p,
            trajectory_gate=selected_gate[sg_mask.values],
            onset_definition='SepsisLabel',
            run_bootstrap_cis=False
        )
        msg = res_sg['metrics']
        subgroup_rows.append({
            "subgroup": sg_name,
            "n_windows": len(df_sg),
            "n_patients": df_sg['Patient_Key'].nunique(),
            "patient_sensitivity": msg['patient_sensitivity'],
            "window_screening_ppv": msg['window_screening_ppv'],
            "window_confirmation_ppv": msg['window_confirmation_ppv'],
            "confirmation_alert_burden": msg['confirmation_alert_burden_per_day'],
            "median_lead_time": msg['lead_time_statistics'].get('median', 0.0)
        })
        
    df_subgroup = pd.DataFrame(subgroup_rows)
    df_subgroup.to_csv(os.path.join(out_dir, "TASK5_PHASE6_SUBGROUP_ANALYSIS.csv"), index=False)
    
    # -------------------------------------------------------------------------
    # PHASE 8 — PRE-SPECIFICATION & PERMANENT LOCK OF SELECTED POLICY
    # -------------------------------------------------------------------------
    print("\n[PHASE 8] Writing TASK5_VALIDATION_POLICY_LOCK.json...", flush=True)
    
    policy_lock_data = {
        "policy_id": str(best_policy_row['policy_id']),
        "rule_name": str(selected_rule_name),
        "tau_screening": selected_ts,
        "tau_confirmation": selected_tc,
        "persistence_windows": selected_p,
        "trajectory_filter_active": True,
        "onset_definition": "first SepsisLabel == 1",
        "validation_metrics": {
            "patient_sensitivity": float(best_policy_row['patient_sensitivity']),
            "patient_ppv": float(best_policy_row['patient_ppv']),
            "window_screening_ppv": float(best_policy_row['window_screening_ppv']),
            "window_confirmation_ppv": float(best_policy_row['window_confirmation_ppv']),
            "window_confirmation_sens": float(best_policy_row['window_confirmation_sens']),
            "screening_alert_burden": float(best_policy_row['screening_alert_burden']),
            "confirmation_alert_burden": float(best_policy_row['confirmation_alert_burden']),
            "median_lead_time": float(best_policy_row['median_lead_time']),
            "tp_patients": int(best_policy_row['tp_patients']),
            "fn_patients": int(best_policy_row['fn_patients']),
            "fp_patients": int(best_policy_row['fp_patients'])
        },
        "target_criteria_met": bool(best_policy_row['patient_sensitivity'] >= 0.80),
        "lock_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(os.path.join(out_dir, "TASK5_VALIDATION_POLICY_LOCK.json"), "w", encoding='utf-8') as f:
        json.dump(policy_lock_data, f, indent=2)
        
    print(f"\nValidation phases 1-8 completed in {time.time()-t0:.2f} seconds!", flush=True)

if __name__ == "__main__":
    main()
