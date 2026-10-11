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
    return int(hashlib.sha256(str(patient_id).encode('utf-8')).hexdigest(), 16) % 100000

VALID_BASE_COLS = ['HR', 'O2Sat', 'Temp', 'SBP', 'MAP', 'DBP', 'Resp', 'BaseExcess', 
                   'HCO3', 'FiO2', 'pH', 'PaCO2', 'SaO2', 'AST', 'BUN', 'Alkalinephos', 
                   'Calcium', 'Chloride', 'Creatinine', 'Bilirubin_direct', 'Glucose', 
                   'Lactate', 'Magnesium', 'Phosphate', 'Potassium', 'Bilirubin_total', 
                   'TroponinI', 'Hct', 'Hgb', 'PTT', 'WBC', 'Fibrinogen', 'Platelets', 
                   'Age', 'Gender', 'Unit1', 'Unit2', 'HospAdmTime', 'ICULOS']

def process_file(fpath):
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
    print("BIO MARKERX — TASK 2: PHASES 4 TO 7 REPRODUCIBILITY ENGINE (PARALLEL)", flush=True)
    print("=========================================================================", flush=True)
    t0 = time.time()
    
    out_dir = "FINAL_BIOMARKERX/models_target_remediation_locked"
    clf_path = os.path.join(out_dir, "TARGET_MASTER_MODEL.joblib")
    cal_path = os.path.join(out_dir, "TARGET_CALIBRATOR.joblib")
    med_path = os.path.join(out_dir, "TARGET_TRAIN_MEDIANS.joblib")
    
    clf = joblib.load(clf_path)
    calibrator = joblib.load(cal_path)
    train_medians = joblib.load(med_path)
    feature_cols = train_medians.index.tolist()
    
    psv_files = sorted(glob.glob('training_setA/*.psv'))
    patient_keys = [os.path.basename(f).replace('.psv', '') for f in psv_files]
    hashes = [compute_patient_hash(pk) for pk in patient_keys]
    test_files = [f for f, h in zip(psv_files, hashes) if (h % 100) >= 85]
    
    print(f"Parallel loading {len(test_files)} locked test files...", flush=True)
    frames = []
    with ProcessPoolExecutor() as executor:
        results = executor.map(process_file, test_files, chunksize=50)
        for res in results:
            if res is not None:
                frames.append(res)
                
    df_test = pd.concat(frames, axis=0).reset_index(drop=True)
    X_mat = df_test[feature_cols].fillna(train_medians).values
    raw_preds = clf.predict_proba(X_mat)[:, 1]
    cal_preds = calibrator.transform(raw_preds)
    
    df_test['pred'] = cal_preds
    df_test['ts'] = np.arange(len(df_test))
    df_test['gate'] = ((df_test['Shock_Index'] >= 0.85) | (df_test['HR_delta_val'] > 0.2) | (df_test['MAP_delta_val'] < -0.2)).astype(int)
    
    print(f"Loaded {len(df_test)} test windows across {df_test['Patient_Key'].nunique()} patients in {time.time()-t0:.2f}s!", flush=True)

    # -------------------------------------------------------------------------
    # EVALUATE RECOMMENDED CANONICAL POLICY A (onset_definition='SepsisLabel')
    # -------------------------------------------------------------------------
    print("\nRunning Canonical Evaluator under Policy A (onset_definition='SepsisLabel')...", flush=True)
    canonical_res_A = evaluate_policy(
        predictions=df_test['pred'].values,
        patient_ids=df_test['Patient_Key'].values,
        timestamps=df_test['ts'].values,
        sepsis_labels=df_test['SepsisLabel'].values,
        s_next4=df_test['S_next4'].values,
        tau_screening=0.0350,
        tau_confirmation=0.1800,
        persistence_windows=2,
        trajectory_gate=None,
        onset_definition='SepsisLabel',
        episode_grouping_rule='first_episode_per_patient',
        run_bootstrap_cis=True,
        n_bootstrap=200,
        seed=42
    )

    # -------------------------------------------------------------------------
    # EVALUATE POLICY B (onset_definition='S_next4_or_SepsisLabel')
    # -------------------------------------------------------------------------
    print("\nRunning Canonical Evaluator under Policy B (onset_definition='S_next4_or_SepsisLabel')...", flush=True)
    canonical_res_B = evaluate_policy(
        predictions=df_test['pred'].values,
        patient_ids=df_test['Patient_Key'].values,
        timestamps=df_test['ts'].values,
        sepsis_labels=df_test['SepsisLabel'].values,
        s_next4=df_test['S_next4'].values,
        tau_screening=0.0350,
        tau_confirmation=0.1800,
        persistence_windows=2,
        trajectory_gate=None,
        onset_definition='S_next4_or_SepsisLabel',
        episode_grouping_rule='first_episode_per_patient',
        run_bootstrap_cis=False
    )

    print("\n=========================================================================", flush=True)
    print("CANONICAL RESULTS COMPARISON:", flush=True)
    print(f"  Recommended Policy A (onset = first SepsisLabel==1):", flush=True)
    print(f"    Patient Sensitivity : {canonical_res_A['metrics']['patient_sensitivity']*100:.2f}% ({canonical_res_A['metrics']['patient_counts']['tp_patients']}/279)", flush=True)
    print(f"    Screening PPV       : {canonical_res_A['metrics']['window_screening_ppv']*100:.2f}%", flush=True)
    print(f"    Confirmation PPV    : {canonical_res_A['metrics']['window_confirmation_ppv']*100:.2f}%", flush=True)
    print(f"    Confirmation Sens   : {canonical_res_A['metrics']['window_confirmation_sens']*100:.2f}%", flush=True)
    print(f"    Median Lead Time    : {canonical_res_A['metrics']['lead_time_statistics']['median']:.1f} hours", flush=True)
    print(f"  Policy B (onset = first S_next4==1 | SepsisLabel==1):", flush=True)
    print(f"    Patient Sensitivity : {canonical_res_B['metrics']['patient_sensitivity']*100:.2f}% ({canonical_res_B['metrics']['patient_counts']['tp_patients']}/279)", flush=True)
    print("=========================================================================", flush=True)

    canon_dir = "FINAL_BIOMARKERX/canonical_evaluation"
    os.makedirs(canon_dir, exist_ok=True)
    
    # 1. CANONICAL_EVALUATION_RESULT.json
    with open(os.path.join(canon_dir, "CANONICAL_EVALUATION_RESULT.json"), "w", encoding='utf-8') as f:
        json.dump(canonical_res_A, f, indent=2)
        
    # 2. CANONICAL_EVALUATION_CONFIG.json
    with open(os.path.join(canon_dir, "CANONICAL_EVALUATION_CONFIG.json"), "w", encoding='utf-8') as f:
        json.dump(canonical_res_A['config'], f, indent=2)

    # 3. CANONICAL_EVALUATION_HASHES.json
    def hash_file(p):
        with open(p, 'rb') as f: return hashlib.sha256(f.read()).hexdigest()
        
    hashes_dict = {
        "master_model_sha256": hash_file(clf_path),
        "calibrator_sha256": hash_file(cal_path),
        "train_medians_sha256": hash_file(med_path),
        "locked_test_patient_ids_sha256": hashlib.sha256(",".join(sorted(df_test['Patient_Key'].unique())).encode('utf-8')).hexdigest(),
        "feature_matrix_sha256": hashlib.sha256(X_mat.tobytes()).hexdigest(),
        "calibrated_predictions_sha256": hashlib.sha256(cal_preds.tobytes()).hexdigest(),
        "evaluation_script_sha256": hash_file("scratch/canonical_evaluate_policy.py")
    }
    with open(os.path.join(canon_dir, "CANONICAL_EVALUATION_HASHES.json"), "w", encoding='utf-8') as f:
        json.dump(hashes_dict, f, indent=2)
        
    print(f"\nPhase 6 Complete! Saved the 3 mandatory JSON deliverables to {canon_dir}/", flush=True)
    print(f"Task 2 engine completed in {time.time() - t0:.1f}s!", flush=True)

if __name__ == '__main__':
    main()
