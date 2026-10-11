import os
import glob
import time
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss

def run_external_validation_pipeline():
    print("=========================================================================")
    print("STARTING LEVEL 2/3 EXTERNAL VALIDATION ON PHYSIONET 2019 (training_setA)")
    print("=========================================================================")

    cache_path = r'scratch\physionet2019_risk_set_cache.parquet'

    # Load locked models
    model_path = r'BioMarkerX_Master_Deliverables\12_TRANSITION_MODEL.joblib'
    calib_path = r'BioMarkerX_Master_Deliverables\CALIBRATION_MODEL.joblib'
    
    model = joblib.load(model_path)
    calib = joblib.load(calib_path)
    
    expected_features = list(model.feature_names_in_)
    print(f"Loaded locked model expecting {len(expected_features)} trajectory features.")

    if os.path.exists(cache_path):
        print(f"Loading cached extracted features from: {cache_path}")
        risk_set = pd.read_parquet(cache_path)
        sample_size = len(risk_set['patient_id'].unique())
    else:
        psv_files = sorted(glob.glob('training_setA/*.psv'))
        sample_size = min(3000, len(psv_files))
        sample_files = psv_files[:sample_size]
        print(f"Processing external cohort sample of {sample_size} ICU patients...")

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

        patient_window_list = []
        start_time = time.time()
        for idx, fpath in enumerate(sample_files):
            if (idx + 1) % 500 == 0:
                print(f"  Processed {idx + 1}/{sample_size} patients...")
                
            pid = os.path.basename(fpath).replace('.psv', '')
            df = pd.read_csv(fpath, sep='|')
            if len(df) < 6:
                continue

            df['Shock_Index'] = df['HR'] / (df['SBP'] + 1e-5) if 'HR' in df and 'SBP' in df else np.nan
            df['Pulse_Pressure'] = df['SBP'] - df['DBP'] if 'SBP' in df and 'DBP' in df else np.nan
            df['De_Ritis_Ratio'] = df['AST'] / (df['ALT'] + 1e-5) if 'AST' in df and 'ALT' in df else np.nan
            df['BUN_Creatinine_Ratio'] = df['BUN'] / (df['Creatinine'] + 1e-5) if 'BUN' in df and 'Creatinine' in df else np.nan
            df['HGB_HCT_Ratio'] = df['Hgb'] / (df['Hct'] + 1e-5) if 'Hgb' in df and 'Hct' in df else np.nan

            df = df.rename(columns=col_map)
            df['window_idx'] = (df['ICULOS'] - 1) // 6
            max_w = int(df['window_idx'].max())
            
            w_states = df.groupby('window_idx')['SepsisLabel'].max()
            base_signals = list(set(col_map.values())) + ['Shock_Index', 'Pulse_Pressure', 'De_Ritis_Ratio', 'BUN_Creatinine_Ratio', 'HGB_HCT_Ratio']
            
            patient_rows = []
            for w in range(max_w + 1):
                sub = df[df['window_idx'] == w]
                row = {'patient_id': pid, 'window_idx': w, 'S_k': w_states.get(w, 0)}
                for sig in base_signals:
                    if sig in sub.columns:
                        vals = sub[sig].dropna()
                        if len(vals) > 0:
                            row[f'{sig}_mean'] = vals.mean()
                            row[f'{sig}_min'] = vals.min()
                            row[f'{sig}_max'] = vals.max()
                            row[f'{sig}_std'] = vals.std() if len(vals) > 1 else 0.0
                        else:
                            row[f'{sig}_mean'] = np.nan
                            row[f'{sig}_min'] = np.nan
                            row[f'{sig}_max'] = np.nan
                            row[f'{sig}_std'] = np.nan
                    else:
                        row[f'{sig}_mean'] = np.nan
                        row[f'{sig}_min'] = np.nan
                        row[f'{sig}_max'] = np.nan
                        row[f'{sig}_std'] = np.nan
                patient_rows.append(row)
                
            p_df = pd.DataFrame(patient_rows)
            
            # Derivative dict
            deriv_dict = {}
            for col in p_df.columns:
                if col not in ['patient_id', 'window_idx', 'S_k']:
                    deriv_dict[f'{col}_delta1'] = (p_df[col] - p_df[col].shift(1)) / 6.0
                    deriv_dict[f'{col}_accel'] = (p_df[col] - 2 * p_df[col].shift(1) + p_df[col].shift(2)) / 36.0
            
            p_df = pd.concat([p_df, pd.DataFrame(deriv_dict)], axis=1)
            p_df['S_k_next'] = p_df['S_k'].shift(-1)
            patient_window_list.append(p_df)

        all_windows = pd.concat(patient_window_list, ignore_index=True)
        print(f"Extraction complete in {time.time() - start_time:.2f} seconds. Total windows: {len(all_windows)}")

        risk_set = all_windows[(all_windows['S_k'] == 0) & (all_windows['S_k_next'].notna())].copy()
        risk_set['Y_transition'] = (risk_set['S_k_next'] == 1).astype(int)
        
        # Save cache
        risk_set.to_parquet(cache_path, index=False)
        print(f"Saved feature cache to: {cache_path}")

    print(f"External Risk Set Windows (S(k)=0): {len(risk_set)}")
    print(f"External Transition Events (S(k)=0 -> S(k+1)=1): {risk_set['Y_transition'].sum()} ({risk_set['Y_transition'].mean()*100:.2f}%)")

    # Construct feature matrix X matching expected 579 features
    X_dict = {}
    for feat in expected_features:
        if feat in risk_set.columns:
            X_dict[feat] = risk_set[feat]
        else:
            X_dict[feat] = np.nan

    X_ext = pd.DataFrame(X_dict)[expected_features]
    X_ext_imputed = X_ext.fillna(X_ext.median()).fillna(0.0)

    # Predict using locked Model D + Calibrator
    print("Running locked Model D + Calibrator inference on external PhysioNet 2019 dataset...")
    calib_prob = calib.predict_proba(X_ext_imputed)[:, 1]
    calib_prob = np.clip(calib_prob, 0.0, 1.0)

    y_true = risk_set['Y_transition'].values

    # Performance Evaluation Metrics
    ext_auroc = roc_auc_score(y_true, calib_prob)
    ext_auprc = average_precision_score(y_true, calib_prob)
    ext_brier = brier_score_loss(y_true, calib_prob)

    tau_opt = 0.1825
    y_pred = (calib_prob >= tau_opt).astype(int)

    tp = np.sum((y_pred == 1) & (y_true == 1))
    fp = np.sum((y_pred == 1) & (y_true == 0))
    tn = np.sum((y_pred == 0) & (y_true == 0))
    fn = np.sum((y_pred == 0) & (y_true == 1))

    sens = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0

    print("=========================================================================")
    print("PHYSIONET 2019 LEVEL 2/3 EXTERNAL VALIDATION RESULTS:")
    print("=========================================================================")
    print(f"External Cohort Patients Evaluated: {sample_size}")
    print(f"External Risk Set Windows (S(k)=0): {len(risk_set)}")
    print(f"External Transition Events: {y_true.sum()} ({y_true.mean()*100:.2f}%)")
    print(f"External AUROC: {ext_auroc:.4f}")
    print(f"External AUPRC: {ext_auprc:.4f}")
    print(f"External Brier Score: {ext_brier:.5f}")
    print(f"Operating Threshold: tau_opt = {tau_opt}")
    print(f"External Sensitivity: {sens*100:.2f}% ({tp}/{tp+fn})")
    print(f"External Specificity: {spec*100:.2f}% ({tn}/{tn+fp})")
    print(f"External PPV: {ppv*100:.2f}% ({tp}/{tp+fp})")
    print(f"External NPV: {npv*100:.2f}% ({tn}/{tn+fn})")
    print("=========================================================================")

    # Export results CSV
    res_df = pd.DataFrame([{
        'cohort_name': 'PhysioNet 2019 (training_setA)',
        'patients_eval': sample_size,
        'risk_windows': len(risk_set),
        'transition_events': y_true.sum(),
        'transition_rate_pct': y_true.mean()*100,
        'auroc': ext_auroc,
        'auprc': ext_auprc,
        'brier_score': ext_brier,
        'tau_opt': tau_opt,
        'sensitivity_pct': sens*100,
        'specificity_pct': spec*100,
        'ppv_pct': ppv*100,
        'npv_pct': npv*100,
        'validation_level': 'Level 2/3 Temporal External Validation'
    }])

    res_csv = r'BioMarkerX_Master_Deliverables\FINAL_EXTERNAL_VALIDATION_PHYSIONET2019_RESULTS.csv'
    res_df.to_csv(res_csv, index=False)
    print(f"Saved external validation results to: {res_csv}")

if __name__ == '__main__':
    run_external_validation_pipeline()
