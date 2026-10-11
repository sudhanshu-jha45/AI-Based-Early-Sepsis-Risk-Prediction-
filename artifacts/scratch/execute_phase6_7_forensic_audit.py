import os
import glob
import json
import numpy as np
import pandas as pd
import joblib
from scipy.stats import ks_2samp
from sklearn.metrics import roc_auc_score

def calculate_psi(expected, actual, num_bins=10):
    exp_clean = expected.dropna()
    act_clean = actual.dropna()
    if len(exp_clean) < 10 or len(act_clean) < 10:
        return 0.0
    
    percentiles = np.linspace(0, 100, num_bins + 1)
    bin_edges = np.percentile(exp_clean, percentiles)
    bin_edges[0] = -np.inf
    bin_edges[-1] = np.inf
    
    exp_counts, _ = np.histogram(exp_clean, bins=bin_edges)
    act_counts, _ = np.histogram(act_clean, bins=bin_edges)
    
    exp_pct = np.maximum(exp_counts / len(exp_clean), 1e-4)
    act_pct = np.maximum(act_counts / len(act_clean), 1e-4)
    
    psi_val = np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct))
    return float(psi_val)

def run_phase6_7_forensic_audit():
    print("=========================================================================")
    print("EXECUTING PHASE 6 FORENSIC AUDIT & PHASE 7 DOMAIN SHIFT DIAGNOSTICS")
    print("=========================================================================")

    audit_dir = r"audit"
    os.makedirs(audit_dir, exist_ok=True)

    # 1. Load Datasets
    dev_path = r"FINAL_CLEANED_DATASETS\dataset_v2_unified_2115_patients_6h.csv"
    dev_df = pd.read_csv(dev_path)
    
    # Filter Dev standard analytical windows (k in 0..7)
    dev_risk_set = dev_df[(dev_df['Window_6h_Idx'].between(0, 7)) & (dev_df['Slabel_max'] == 0)].copy()

    cache_path = r'scratch\physionet2019_risk_set_cache.parquet'
    ext_risk_set = pd.read_parquet(cache_path)

    print(f"Internal Dev Risk Windows (S(k)=0): {len(dev_risk_set)}")
    print(f"External Test A Risk Windows (S(k)=0): {len(ext_risk_set)}")

    # Load locked Model D
    model_path = r'BioMarkerX_Master_Deliverables\12_TRANSITION_MODEL.joblib'
    calib_path = r'BioMarkerX_Master_Deliverables\CALIBRATION_MODEL.joblib'
    model = joblib.load(model_path)
    calib = joblib.load(calib_path)

    expected_features = list(model.feature_names_in_)

    # -------------------------------------------------------------------------
    # PHASE 6.3: AUDIT RAW PHYSIONET SCHEMA (physionet_schema_audit.csv)
    # -------------------------------------------------------------------------
    print("\n--- PHASE 6.3: Raw PhysioNet Schema Audit ---")
    psv_files = sorted(glob.glob('training_setA/*.psv'))
    sample_100_files = psv_files[:100]

    sample_psv_dfs = [pd.read_csv(f, sep='|') for f in sample_100_files]
    concat_psv = pd.concat(sample_psv_dfs, ignore_index=True)

    col_map = {
        'Temp': 'Temp', 'HR': 'HR', 'SBP': 'SBP', 'DBP': 'DBP',
        'Hct': 'HCT', 'Hgb': 'HGB', 'WBC': 'WBC', 'Platelets': 'Platelets',
        'PTT': 'PTT', 'Bilirubin_direct': 'Bilirubin direct', 'Bilirubin_total': 'Bilirubin total',
        'AST': 'AST', 'K': 'K', 'Na': 'Na', 'BaseExcess': 'BEb', 'pH': 'pH',
        'PaCO2': 'PaCO2', 'Gender': 'Gender', 'Chloride': 'CL', 'BUN': 'BUN',
        'TroponinI': 'Troponin', 'Creatinine': 'Creatinine', 'Calcium': 'Ca++',
        'Fibrinogen': 'Fibrinogen', 'SaO2': 'SaO2', 'O2Sat': 'SO2', 'HCO3': 'HCO3',
        'FiO2': 'FiO2', 'MAP': 'MAP'
    }

    schema_rows = []
    for col in concat_psv.columns:
        vals = concat_psv[col].dropna()
        schema_rows.append({
            'raw_variable': col,
            'dtype': str(concat_psv[col].dtype),
            'missing_percent': float(concat_psv[col].isna().mean() * 100),
            'min': float(vals.min()) if len(vals) > 0 else np.nan,
            'max': float(vals.max()) if len(vals) > 0 else np.nan,
            'median': float(vals.median()) if len(vals) > 0 else np.nan,
            'BioMarkerX_mapping': col_map.get(col, 'Unmapped/Operational/Demographic')
        })

    schema_df = pd.DataFrame(schema_rows)
    schema_csv = os.path.join(audit_dir, 'physionet_schema_audit.csv')
    schema_df.to_csv(schema_csv, index=False)
    print(f"Exported audit/physionet_schema_audit.csv ({len(schema_df)} columns).")

    # -------------------------------------------------------------------------
    # PHASE 6.8 & 6.9: AST/ALT & GENDER DERIVATIVE AUDIT
    # -------------------------------------------------------------------------
    print("\n--- PHASE 6.8 & 6.9: AST/ALT & Gender Derivative Forensic Audit ---")
    alt_exists = 'ALT' in concat_psv.columns
    print(f"Does ALT exist in raw PhysioNet PSV files? {alt_exists}")
    
    gender_vel_in_model = 'Gender_mean_delta1' in expected_features
    gender_acc_in_model = 'Gender_mean_accel' in expected_features
    print(f"Is Gender_mean_delta1 in Model D expected features? {gender_vel_in_model}")
    print(f"Is Gender_mean_accel in Model D expected features? {gender_acc_in_model}")

    # Inspect tree feature importances for gender velocity/accel
    tree_importances = model.feature_importances_
    feat_imp_df = pd.DataFrame({'feature': expected_features, 'importance': tree_importances})
    gender_imp = feat_imp_df[feat_imp_df['feature'].str.contains('Gender', case=False)]
    print("Gender Feature Importances in Model D:")
    for _, r in gender_imp.iterrows():
        print(f"  {r['feature']}: {r['importance']:.6f}")

    # -------------------------------------------------------------------------
    # PHASE 6.10: IMPUTATION AUDIT (DEV-FIT VS EXTERNAL MEDIANS)
    # -------------------------------------------------------------------------
    print("\n--- PHASE 6.10: Imputation Isolation Audit ---")
    # Extract Dev-fit medians for the 579 features from dev_df
    dev_feature_medians = {}
    for feat in expected_features:
        if feat in dev_df.columns:
            dev_feature_medians[feat] = dev_df[feat].median()
        else:
            dev_feature_medians[feat] = 0.0

    dev_medians_series = pd.Series(dev_feature_medians)

    # Predict using Dev-fit medians vs Test-fit medians
    X_dict = {feat: ext_risk_set[feat] if feat in ext_risk_set.columns else np.nan for feat in expected_features}
    X_ext_raw = pd.DataFrame(X_dict)[expected_features]

    X_ext_test_med = X_ext_raw.fillna(X_ext_raw.median()).fillna(0.0)
    X_ext_dev_med = X_ext_raw.fillna(dev_medians_series).fillna(0.0)

    p_test_med = calib.predict_proba(X_ext_test_med)[:, 1]
    p_dev_med = calib.predict_proba(X_ext_dev_med)[:, 1]

    pred_diff = np.abs(p_test_med - p_dev_med)
    print(f"Mean risk score absolute difference (Dev medians vs Test medians): {pred_diff.mean():.6f}")
    print(f"Max risk score absolute difference: {pred_diff.max():.6f}")
    
    auroc_test_med = roc_auc_score(ext_risk_set['Y_transition'], p_test_med)
    auroc_dev_med = roc_auc_score(ext_risk_set['Y_transition'], p_dev_med)
    print(f"External AUROC with Test-fit Medians: {auroc_test_med:.4f}")
    print(f"External AUROC with Dev-fit Medians: {auroc_dev_med:.4f}")

    # -------------------------------------------------------------------------
    # PHASE 7.1 & 7.2: DOMAIN SHIFT FORENSICS (KS STATISTIC, PSI, MISSINGNESS SHIFT)
    # -------------------------------------------------------------------------
    print("\n--- PHASE 7: Domain Shift Forensics (Internal vs External) ---")
    shift_rows = []

    key_signals = [
        'HR_mean', 'MAP_mean', 'SBP_mean', 'DBP_mean', 'Temp_mean',
        'WBC_mean', 'Creatinine_mean', 'Lactate_mean', 'Shock_Index_mean',
        'BUN_mean', 'Platelets_mean', 'HGB_mean', 'K_mean', 'Na_mean'
    ]

    for sig in key_signals:
        if sig in dev_risk_set.columns and sig in ext_risk_set.columns:
            dev_vals = dev_risk_set[sig].dropna()
            ext_vals = ext_risk_set[sig].dropna()

            dev_miss = dev_risk_set[sig].isna().mean() * 100
            ext_miss = ext_risk_set[sig].isna().mean() * 100

            ks_stat, ks_pval = ks_2samp(dev_vals, ext_vals) if len(dev_vals) > 0 and len(ext_vals) > 0 else (np.nan, np.nan)
            psi_val = calculate_psi(dev_vals, ext_vals)

            shift_rows.append({
                'feature': sig,
                'dev_mean': float(dev_vals.mean()) if len(dev_vals) > 0 else np.nan,
                'ext_mean': float(ext_vals.mean()) if len(ext_vals) > 0 else np.nan,
                'dev_missing_pct': float(dev_miss),
                'ext_missing_pct': float(ext_miss),
                'missingness_shift_pct': float(ext_miss - dev_miss),
                'ks_statistic': float(ks_stat),
                'ks_pvalue': float(ks_pval),
                'psi_value': float(psi_val),
                'shift_severity': 'SEVERE' if psi_val > 0.25 or abs(ext_miss - dev_miss) > 20 else ('MODERATE' if psi_val > 0.1 else 'LOW')
            })

    shift_df = pd.DataFrame(shift_rows)
    shift_csv = os.path.join(audit_dir, 'domain_shift_features.csv')
    shift_df.to_csv(shift_csv, index=False)
    print(f"Exported audit/domain_shift_features.csv ({len(shift_df)} key features evaluated).")
    print(shift_df[['feature', 'dev_missing_pct', 'ext_missing_pct', 'ks_statistic', 'psi_value', 'shift_severity']])

    # -------------------------------------------------------------------------
    # PHASE 7.3: MEASUREMENT INTENSITY CORRELATION AUDIT
    # -------------------------------------------------------------------------
    print("\n--- PHASE 7.3: Measurement Intensity Correlation Audit ---")
    valid_key_signals = [sig for sig in key_signals if sig in ext_risk_set.columns]
    ext_obs_counts = ext_risk_set[valid_key_signals].notna().sum(axis=1)
    r_ext = np.corrcoef(ext_obs_counts, p_dev_med)[0, 1]
    print(f"External Measurement Count vs Risk Score Pearson Correlation (r): {r_ext:+.4f}")

    # -------------------------------------------------------------------------
    # EXPORT FORENSIC SUMMARY AUDIT MANIFEST
    # -------------------------------------------------------------------------
    summary_audit = {
        'alt_in_raw_data': alt_exists,
        'gender_velocity_in_model': gender_vel_in_model,
        'auroc_test_fit_medians': float(auroc_test_med),
        'auroc_dev_fit_medians': float(auroc_dev_med),
        'measurement_intensity_r_ext': float(r_ext),
        'severe_shifted_features_count': int((shift_df['shift_severity'] == 'SEVERE').sum()),
        'audit_status': 'PHASE_6_7_COMPLETE'
    }

    summary_json = os.path.join(audit_dir, 'phase6_7_forensic_summary.json')
    with open(summary_json, 'w') as f:
        json.dump(summary_audit, f, indent=2)

    print("\n=========================================================================")
    print("PHASE 6 & 7 AUDIT PASS: Forensic Diagnostics Complete.")
    print("=========================================================================\n")

if __name__ == '__main__':
    run_phase6_7_forensic_audit()
