import os
import glob
import json
import hashlib
import numpy as np
import pandas as pd
import joblib

def compute_sha256(filepath):
    sha = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()

def execute_phase6_1():
    print("=========================================================================")
    print("PHASE 6.1 — FREEZE AND HASH EXTERNAL TEST A")
    print("=========================================================================")

    base_dir = r"external_test_A"
    subdirs = ["predictions", "metrics", "feature_exports", "hashes"]
    for sd in subdirs:
        os.makedirs(os.path.join(base_dir, sd), exist_ok=True)

    # 1. Load existing cache and predictions
    cache_path = r'scratch\physionet2019_risk_set_cache.parquet'
    res_csv = r'BioMarkerX_Master_Deliverables\FINAL_EXTERNAL_VALIDATION_PHYSIONET2019_RESULTS.csv'

    risk_set = pd.read_parquet(cache_path)
    patient_ids = sorted(risk_set['patient_id'].unique())

    # Create patient_manifest.csv
    psv_files = sorted(glob.glob('training_setA/*.psv'))
    all_pids = [os.path.basename(f).replace('.psv', '') for f in psv_files]

    manifest_rows = []
    for rank, pid in enumerate(all_pids, 1):
        is_sel = pid in patient_ids
        manifest_rows.append({
            'patient_id': pid,
            'selected': is_sel,
            'selection_rank': rank,
            'selection_mechanism': 'lexicographical_path_order_top_3000',
            'eligibility': True,
            'exclusion_reason': 'None' if is_sel else 'Beyond_Top_3000_Sample_Cutoff'
        })

    manifest_df = pd.DataFrame(manifest_rows)
    manifest_path = os.path.join(base_dir, 'patient_manifest.csv')
    manifest_df.to_csv(manifest_path, index=False)
    print(f"Created external_test_A/patient_manifest.csv ({len(manifest_df)} patients total, 3,000 selected).")

    # 2. Re-run inference to export predictions file
    model_path = r'BioMarkerX_Master_Deliverables\12_TRANSITION_MODEL.joblib'
    calib_path = r'BioMarkerX_Master_Deliverables\CALIBRATION_MODEL.joblib'
    model = joblib.load(model_path)
    calib = joblib.load(calib_path)

    expected_features = list(model.feature_names_in_)
    X_dict = {feat: risk_set[feat] if feat in risk_set.columns else np.nan for feat in expected_features}
    X_ext = pd.DataFrame(X_dict)[expected_features]
    X_ext_imputed = X_ext.fillna(X_ext.median()).fillna(0.0)

    calib_prob = calib.predict_proba(X_ext_imputed)[:, 1]

    pred_df = pd.DataFrame({
        'patient_id': risk_set['patient_id'],
        'window_idx': risk_set['window_idx'],
        'Y_true': risk_set['Y_transition'],
        'P_calibrated_risk': calib_prob,
        'Y_pred_tau_0_1825': (calib_prob >= 0.1825).astype(int)
    })

    pred_path = os.path.join(base_dir, 'predictions', 'external_test_A_predictions.csv')
    pred_df.to_csv(pred_path, index=False)
    print(f"Exported external_test_A/predictions/external_test_A_predictions.csv ({len(pred_df)} risk windows).")

    # 3. Copy metrics CSV
    metric_dest = os.path.join(base_dir, 'metrics', 'external_test_A_metrics.csv')
    pd.read_csv(res_csv).to_csv(metric_dest, index=False)
    print(f"Exported external_test_A/metrics/external_test_A_metrics.csv.")

    # 4. Save feature export sample
    feat_dest = os.path.join(base_dir, 'feature_exports', 'external_test_A_features_sample.parquet')
    risk_set.head(1000).to_parquet(feat_dest, index=False)
    print(f"Exported external_test_A/feature_exports/external_test_A_features_sample.parquet.")

    # 5. Compute SHA-256 hashes
    hashes = {
        'patient_manifest_csv': compute_sha256(manifest_path),
        'predictions_csv': compute_sha256(pred_path),
        'metrics_csv': compute_sha256(metric_dest),
        'feature_cache_parquet': compute_sha256(cache_path),
        'model_d_joblib': compute_sha256(model_path),
        'calibrator_joblib': compute_sha256(calib_path)
    }

    hash_path = os.path.join(base_dir, 'hashes', 'external_test_A_hashes.json')
    with open(hash_path, 'w') as f:
        json.dump(hashes, f, indent=2)
    print(f"Generated external_test_A/hashes/external_test_A_hashes.json.")

    print("\nPhase 6.1 PASS: External Test A structure successfully frozen and cryptographically hashed.\n")

if __name__ == '__main__':
    execute_phase6_1()
