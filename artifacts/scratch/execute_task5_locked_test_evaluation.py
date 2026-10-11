import os
import glob
import json
import time
import hashlib
import numpy as np
import pandas as pd
import joblib
from concurrent.futures import ProcessPoolExecutor
from canonical_evaluate_policy import evaluate_policy

def compute_patient_hash(patient_id):
    return int(hashlib.sha256(str(patient_id).encode('utf-8')).hexdigest(), 16)

VALID_BASE_COLS = ['HR', 'O2Sat', 'Temp', 'SBP', 'MAP', 'DBP', 'Resp', 'BaseExcess', 
                   'HCO3', 'FiO2', 'pH', 'PaCO2', 'SaO2', 'AST', 'BUN', 'Alkalinephos', 
                   'Calcium', 'Chloride', 'Creatinine', 'Bilirubin_direct', 'Glucose', 
                   'Lactate', 'Magnesium', 'Phosphate', 'Potassium', 'Bilirubin_total', 
                   'TroponinI', 'Hct', 'Hgb', 'PTT', 'WBC', 'Fibrinogen', 'Platelets', 
                   'Age', 'Gender', 'Unit1', 'Unit2', 'HospAdmTime', 'ICULOS']

def process_file_test(fpath):
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

def main():
    print("=========================================================================", flush=True)
    print("TASK 5: PHASE 9 — SINGLE-PASS LOCKED-TEST EVALUATION", flush=True)
    print("=========================================================================", flush=True)
    t0 = time.time()
    
    out_dir = "FINAL_BIOMARKERX/task5_physiological_confirmation"
    lock_path = os.path.join(out_dir, "TASK5_VALIDATION_POLICY_LOCK.json")
    
    if not os.path.exists(lock_path):
        raise FileNotFoundError(f"Validation policy lock file not found: {lock_path}")
        
    with open(lock_path, "r", encoding='utf-8') as f:
        policy_lock = json.load(f)
        
    print(f"Loaded Validation Policy Lock:")
    print(f"  Policy ID             : {policy_lock['policy_id']}")
    print(f"  Rule Name             : {policy_lock['rule_name']}")
    print(f"  tau_screening         : {policy_lock['tau_screening']}")
    print(f"  tau_confirmation      : {policy_lock['tau_confirmation']}")
    print(f"  persistence_windows   : {policy_lock['persistence_windows']}")
    
    model_dir = "FINAL_BIOMARKERX/models_target_remediation_locked"
    clf = joblib.load(os.path.join(model_dir, "TARGET_MASTER_MODEL.joblib"))
    calibrator = joblib.load(os.path.join(model_dir, "TARGET_CALIBRATOR.joblib"))
    train_medians = joblib.load(os.path.join(model_dir, "TARGET_TRAIN_MEDIANS.joblib"))
    feature_cols = train_medians.index.tolist()
    
    psv_files = sorted(glob.glob('training_setA/*.psv'))
    patient_keys = [os.path.basename(f).replace('.psv', '') for f in psv_files]
    hashes = [compute_patient_hash(pk) for pk in patient_keys]
    
    test_files = [f for f, h in zip(psv_files, hashes) if (h % 100) >= 85]
    print(f"Locked Test Cohort: {len(test_files)} files", flush=True)
    
    print(f"Parallel loading {len(test_files)} test files...", flush=True)
    frames = []
    with ProcessPoolExecutor() as executor:
        results = executor.map(process_file_test, test_files, chunksize=50)
        for res in results:
            if res is not None:
                frames.append(res)
                
    df_test = pd.concat(frames, axis=0).reset_index(drop=True)
    print(f"Locked test dataset constructed: {len(df_test):,} windows across {df_test['Patient_Key'].nunique():,} patients.", flush=True)
    
    X_test = df_test.reindex(columns=feature_cols).fillna(train_medians).values
    raw_probs = clf.predict_proba(X_test)[:, 1]
    if hasattr(calibrator, 'transform'):
        cal_probs = calibrator.transform(raw_probs)
    elif hasattr(calibrator, 'predict_proba'):
        cal_probs = calibrator.predict_proba(raw_probs.reshape(-1, 1))[:, 1]
    else:
        cal_probs = calibrator.predict(raw_probs)
    df_test['pred'] = cal_probs
    
    # Compute Gating Rule for Test Set based on policy lock
    r_name = policy_lock['rule_name']
    si = df_test['Shock_Index'].values
    hr_d3 = df_test['HR_delta_3h'].values
    map_d3 = df_test['MAP_delta_3h'].values
    qsofa = df_test['qSOFA_Causal'].values
    sirs = df_test['SIRS_Causal'].values
    pp = df_test['Pulse_Pressure'].values
    pp_d3 = df_test['PP_delta_3h'].values
    
    gating_rules = {
        "Rule_A_Baseline_Ungated": np.ones(len(df_test), dtype=int),
        "Rule_B_ShockIndex_070": (si >= 0.70).astype(int),
        "Rule_C_ShockIndex_075": (si >= 0.75).astype(int),
        "Rule_D_HR_Trend": ((df_test['HR'] >= 90) | (hr_d3 >= 3)).astype(int),
        "Rule_E_MAP_Trend": ((df_test['MAP'] <= 75) | (map_d3 <= -3)).astype(int),
        "Rule_F_qSOFA_1": (qsofa >= 1).astype(int),
        "Rule_G_SIRS_2": (sirs >= 2).astype(int),
        "Rule_H_Composite_Instability": ((si >= 0.70) | (hr_d3 >= 3) | (qsofa >= 1) | (map_d3 <= -3)).astype(int),
        "Rule_I_Strict_Instability": ((si >= 0.75) & ((qsofa >= 1) | (sirs >= 2))).astype(int),
        "Rule_J_PulsePressure_Drop": ((pp <= 45) | (pp_d3 <= -5)).astype(int)
    }
    
    test_gate = gating_rules[r_name]
    
    print("\nRunning single locked-test evaluation pass with 1,000 bootstrap replicates (seed=42)...", flush=True)
    res_test = evaluate_policy(
        predictions=df_test['pred'].values,
        patient_ids=df_test['Patient_Key'].values,
        timestamps=df_test['ICULOS'].values,
        sepsis_labels=df_test['SepsisLabel'].values,
        s_next4=df_test['S_next4'].values,
        tau_screening=policy_lock['tau_screening'],
        tau_confirmation=policy_lock['tau_confirmation'],
        persistence_windows=policy_lock['persistence_windows'],
        trajectory_gate=test_gate,
        onset_definition='SepsisLabel',
        run_bootstrap_cis=True,
        n_bootstrap=1000,
        seed=42
    )
    
    res_test['validation_lock_reference'] = policy_lock
    res_test['evaluation_timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Save json result
    with open(os.path.join(out_dir, "TASK5_FINAL_LOCKED_TEST_RESULT.json"), "w", encoding='utf-8') as f:
        json.dump(res_test, f, indent=2)
        
    m = res_test['metrics']
    ci = res_test['bootstrap_cis']
    lt = m['lead_time_statistics']
    pc = m['patient_counts']
    
    # Generate Markdown Report for Phase 9
    md_lines = []
    md_lines.append("# BioMarkerX Task 5 — Phase 9: Single-Pass Locked-Test Evaluation Report\n")
    md_lines.append(f"**Evaluation Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    md_lines.append(f"**Locked Cohort**: {pc['total_patients']:,} patients, {len(df_test):,} windows, {pc['tp_patients']+pc['fn_patients']} sepsis episodes\n\n")
    
    md_lines.append("## Frozen Policy Configuration\n\n")
    md_lines.append(f"- **Policy ID**: `{policy_lock['policy_id']}`\n")
    md_lines.append(f"- **Physiological Confirmation Rule**: `{r_name}`\n")
    md_lines.append(f"- **Screening Threshold ($\\tau_s$)**: {policy_lock['tau_screening']:.4f}\n")
    md_lines.append(f"- **Confirmation Threshold ($\\tau_c$)**: {policy_lock['tau_confirmation']:.4f}\n")
    md_lines.append(f"- **Persistence Windows ($p$)**: {policy_lock['persistence_windows']}\n")
    md_lines.append(f"- **Onset Definition**: `first SepsisLabel == 1`\n\n")
    
    md_lines.append("## Locked Test Performance Summary (Point Estimates & 95% CIs)\n\n")
    md_lines.append("| Metric | Point Estimate | 95% Confidence Interval |\n")
    md_lines.append("|---|---|---|\n")
    md_lines.append(f"| **Patient Sensitivity** | **{m['patient_sensitivity']*100:.2f}%** ({pc['tp_patients']}/{pc['tp_patients']+pc['fn_patients']}) | [{ci['patient_sensitivity']['ci_lower_95']*100:.2f}%, {ci['patient_sensitivity']['ci_upper_95']*100:.2f}%] |\n")
    md_lines.append(f"| **Patient PPV** | {m['patient_ppv']*100:.2f}% | [{ci['patient_ppv']['ci_lower_95']*100:.2f}%, {ci['patient_ppv']['ci_upper_95']*100:.2f}%] |\n")
    md_lines.append(f"| **Window Confirmation PPV** | **{m['window_confirmation_ppv']*100:.2f}%** | [{ci['window_confirmation_ppv']['ci_lower_95']*100:.2f}%, {ci['window_confirmation_ppv']['ci_upper_95']*100:.2f}%] |\n")
    md_lines.append(f"| **Window Confirmation Sensitivity** | {m['window_confirmation_sens']*100:.2f}% | [{ci['window_confirmation_sens']['ci_lower_95']*100:.2f}%, {ci['window_confirmation_sens']['ci_upper_95']*100:.2f}%] |\n")
    md_lines.append(f"| **Window Screening PPV** | {m['window_screening_ppv']*100:.2f}% | [{ci['window_screening_ppv']['ci_lower_95']*100:.2f}%, {ci['window_screening_ppv']['ci_upper_95']*100:.2f}%] |\n")
    md_lines.append(f"| **AUROC** | {m['auroc']:.4f} | [{ci['auroc']['ci_lower_95']:.4f}, {ci['auroc']['ci_upper_95']:.4f}] |\n")
    md_lines.append(f"| **AUPRC** | {m['auprc']:.4f} | [{ci['auprc']['ci_lower_95']:.4f}, {ci['auprc']['ci_upper_95']:.4f}] |\n")
    md_lines.append(f"| **Brier Score** | {m['brier']:.5f} | N/A |\n\n")
    
    md_lines.append("## Alert Burden & Lead Time\n\n")
    md_lines.append(f"- **Screening Alert Burden**: {m['screening_alert_burden_per_day']:.2f} alerts/patient-day\n")
    md_lines.append(f"- **Confirmation Alert Burden**: {m['confirmation_alert_burden_per_day']:.2f} alerts/patient-day\n")
    md_lines.append(f"- **Median Lead Time**: {lt.get('median', 0.0):.1f} hours (IQR: {lt.get('p25', 0.0):.1f}–{lt.get('p75', 0.0):.1f} h)\n\n")
    
    with open(os.path.join(out_dir, "TASK5_FINAL_LOCKED_TEST_REPORT.md"), "w", encoding='utf-8') as f:
        f.writelines(md_lines)
        
    print(f"Phase 9 evaluation completed in {time.time()-t0:.2f} seconds.", flush=True)

if __name__ == "__main__":
    main()
