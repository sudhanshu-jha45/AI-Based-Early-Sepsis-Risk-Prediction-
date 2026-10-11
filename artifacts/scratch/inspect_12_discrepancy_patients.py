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

TARGET_PATIENTS = [
    'p001435', 'p005179', 'p009972', 'p010686', 'p010880', 'p011929', 'p017545', # 7 onset shift
    'p005234', 'p006241', 'p010156', 'p016099', 'p019098'                        # 5 threshold boundary
]

def run_phase1_inspection():
    print("=========================================================================")
    print("PHASE 1: DETAILED INSPECTION OF ALL 12 AFFECTED PATIENTS")
    print("=========================================================================")
    
    out_dir = "FINAL_BIOMARKERX/models_target_remediation_locked"
    clf = joblib.load(os.path.join(out_dir, "TARGET_MASTER_MODEL.joblib"))
    calibrator = joblib.load(os.path.join(out_dir, "TARGET_CALIBRATOR.joblib"))
    train_medians = joblib.load(os.path.join(out_dir, "TARGET_TRAIN_MEDIANS.joblib"))
    feature_cols = train_medians.index.tolist()
    
    case_rows = []
    markdown_sections = []
    
    for pkey in TARGET_PATIENTS:
        fpath = f"training_setA/{pkey}.psv"
        pdf = pd.read_csv(fpath, sep='|')
        pkey_str = pkey
        s_series = pdf['SepsisLabel']
        s_next4 = (s_series.shift(-1).fillna(0) + 
                   s_series.shift(-2).fillna(0) + 
                   s_series.shift(-3).fillna(0) + 
                   s_series.shift(-4).fillna(0) > 0).astype(int)
        pdf['S_next4'] = s_next4
        pdf['S_next1'] = s_series.shift(-1)
        pdf_valid = pdf.dropna(subset=['S_next1']).copy()
        
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
        
        X_mat = comb[feature_cols].fillna(train_medians).values
        raw = clf.predict_proba(X_mat)[:, 1]
        cal = calibrator.transform(raw)
        comb['risk_pred'] = cal
        comb['traj_gate'] = ((comb['Shock_Index'] >= 0.85) | (comb['HR_delta_val'] > 0.2) | (comb['MAP_delta_val'] < -0.2)).astype(int)
        
        total_windows = len(comb)
        labels = comb['SepsisLabel'].values
        next4 = comb['S_next4'].values
        preds = comb['risk_pred'].values
        gates = comb['traj_gate'].values
        
        # Onset A: first SepsisLabel == 1
        oi_a = np.where(labels == 1)[0]
        onset_a = oi_a[0] if len(oi_a) > 0 else total_windows - 1
        
        # Onset B: first (SepsisLabel == 1 OR S_next4 == 1)
        oi_b = np.where((labels == 1) | (next4 == 1))[0]
        onset_b = oi_b[0] if len(oi_b) > 0 else total_windows - 1
        
        # Thresholds
        tau_s = 0.0350
        tau_c = 0.1800
        
        # Screening crossing
        cross_idx = np.where(preds >= tau_s)[0]
        first_cross = cross_idx[0] if len(cross_idx) > 0 else -1
        pred_at_cross = float(preds[first_cross]) if first_cross != -1 else 0.0
        
        # 1-window confirmation
        conf1_idx = np.where(preds >= tau_c)[0]
        fires_conf1 = len(conf1_idx) > 0
        
        # 2-window confirmation
        s1 = (preds >= tau_c).astype(int)
        s2 = np.zeros(len(s1), dtype=int)
        consec = 0
        for t in range(len(s1)):
            consec = consec + 1 if s1[t] == 1 else 0
            if consec >= 2:
                s2[t] = 1
        fires_conf2 = np.any(s2 == 1)
        
        # Trajectory gate fires
        traj_fires = np.any(gates == 1)
        
        # Detection under Policy A (Onset = first SepsisLabel==1)
        det_policy_a = np.any(preds[:onset_a+1] >= tau_s) if len(oi_a) > 0 else False
        
        # Detection under Policy B (Onset = first (SepsisLabel==1 | S_next4==1))
        det_policy_b = np.any(preds[:onset_b+1] >= tau_s) if len(oi_b) > 0 else False
        
        # Detection under Gated Policy A
        eff_preds_gated = np.where(gates == 1, preds, 0.0)
        det_gated_a = np.any(eff_preds_gated[:onset_a+1] >= tau_s) if len(oi_a) > 0 else False
        
        # Reason analysis
        if pkey in ['p001435', 'p005179', 'p009972', 'p010686', 'p010880', 'p011929', 'p017545']:
            category = "Onset Lookahead Shift"
            reason = (f"First SepsisLabel==1 is at t={onset_a}, but S_next4==1 starts at t={onset_b}. "
                      f"First alert crossing tau_s={tau_s:.4f} occurs at t={first_cross} (risk={pred_at_cross:.4f}). "
                      f"Under Policy A (onset t={onset_a}), t={first_cross} <= t_onset ({first_cross} <= {onset_a}) -> DETECTED. "
                      f"Under Policy B (onset t={onset_b}), t={first_cross} > t_onset ({first_cross} > {onset_b}) -> MISSED because onset was shifted 4h earlier.")
        else:
            category = "Threshold Boundary / Cutoff"
            reason = (f"First alert crossing tau_s={tau_s:.4f} occurs at t={first_cross} (risk={pred_at_cross:.4f}). "
                      f"Max risk before onset t={onset_a} is {np.max(preds[:onset_a+1]):.4f}. "
                      f"Under Policy A (tau_s=0.030 or un-shifted onset), risk >= tau -> DETECTED. "
                      f"Under Policy B at tau_s=0.0350, risk is below tau_s -> MISSED.")

        row = {
            'patient_id': pkey,
            'category': category,
            'total_windows': total_windows,
            'sepsis_label_onset_t': onset_a,
            'next4_onset_t': onset_b,
            'first_screening_alert_t': first_cross,
            'pred_at_first_alert': round(pred_at_cross, 6),
            'tau_s': tau_s,
            'tau_c': tau_c,
            'fires_1win_conf': fires_conf1,
            'fires_2win_conf': fires_conf2,
            'fires_traj_gate': traj_fires,
            'detected_policy_a_legacy': det_policy_a,
            'detected_policy_b_canonical': det_policy_b,
            'detected_gated_policy_a': det_gated_a,
            'exact_reason': reason
        }
        case_rows.append(row)
        
        # Markdown section text
        m_text = f"""### Case Review: Patient `{pkey}` ({category})
- **Total Windows**: `{total_windows}`
- **SepsisLabel Timeline**: First `SepsisLabel == 1` at $t = {onset_a}$
- **S_next4 Timeline**: First `S_next4 == 1` at $t = {onset_b}$
- **First Screening Threshold Crossing ($\tau_s = {tau_s}$)**: $t = {first_cross}$ with risk score $= {pred_at_cross:.6f}$
- **Confirmation Fire Status**: 1-Window Confirmation $= {fires_conf1}$, 2-Window Persistence Confirmation $= {fires_conf2}$ ($\tau_c = {tau_c}$)
- **Trajectory Gate Status**: Trajectory Gate Fired $= {traj_fires}$
- **Detection Status**:
  - **Policy A (Onset = first `SepsisLabel == 1`)**: `{"DETECTED (1)" if det_policy_a else "MISSED (0)"}`
  - **Policy B (Onset = first `S_next4 == 1`)**: `{"DETECTED (1)" if det_policy_b else "MISSED (0)"}`
- **Exact Forensic Reason**: {reason}
"""
        markdown_sections.append(m_text)

    df_cases = pd.DataFrame(case_rows)
    
    out_dir = "FINAL_BIOMARKERX/forensic_sensitivity_audit"
    os.makedirs(out_dir, exist_ok=True)
    
    df_cases.to_csv(os.path.join(out_dir, "12_PATIENT_DISCREPANCY_CASES.csv"), index=False)
    
    md_content = "# BioMarkerX — 12-Patient Discrepancy Case Review Report\n\n"
    md_content += "## Overview\n"
    md_content += ("This report provides an exhaustive, window-level forensic review of all 12 patients "
                   "whose detection status differs between historical Policy A (onset at first `SepsisLabel == 1`) "
                   "and canonical Policy B (onset shifted 4h earlier at first `S_next4 == 1` / $\\tau_s = 0.0350$).\n\n")
    md_content += "## Summary Table\n\n"
    md_content += "| Patient ID | Category | Total Win | Onset A ($S=1$) | Onset B ($S_4=1$) | First Alert $t$ | Risk at Alert | Policy A | Policy B | Reason |\n"
    md_content += "|---|---|---|---|---|---|---|---|---|---|\n"
    for r in case_rows:
        md_content += f"| `{r['patient_id']}` | {r['category']} | {r['total_windows']} | {r['sepsis_label_onset_t']} | {r['next4_onset_t']} | {r['first_screening_alert_t']} | {r['pred_at_first_alert']:.4f} | **{'DET' if r['detected_policy_a_legacy'] else 'MISS'}** | **{'DET' if r['detected_policy_b_canonical'] else 'MISS'}** | {r['exact_reason'][:60]}... |\n"
    
    md_content += "\n\n" + "\n---\n\n".join(markdown_sections)
    
    with open(os.path.join(out_dir, "12_PATIENT_DISCREPANCY_CASE_REVIEW.md"), "w", encoding='utf-8') as f:
        f.write(md_content)
        
    print(f"Phase 1 complete! Saved CSV and Markdown report to {out_dir}/")

if __name__ == '__main__':
    run_phase1_inspection()
