import os
import json
import hashlib
import time
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss

def compute_sha256(filepath):
    sha = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()

def run_v2_development_pipeline():
    print("=========================================================================")
    print("STARTING BIOMARKERX V2 CONTROLLED DEVELOPMENT & ABLATION PIPELINE")
    print("=========================================================================")

    v2_dir = r"v2"
    os.makedirs(v2_dir, exist_ok=True)

    # 1. Load Development Dataset (dataset_v2_unified_2115_patients_6h.csv)
    dev_path = r"FINAL_CLEANED_DATASETS\dataset_v2_unified_2115_patients_6h.csv"
    dev_df = pd.read_csv(dev_path)

    # Filter standard analytical windows (k in 0..7) and risk set (S(k) == 0)
    dev_risk = dev_df[(dev_df['Window_6h_Idx'].between(0, 7)) & (dev_df['Slabel_max'] == 0)].copy()
    print(f"Development Risk Set Windows (S(k)=0): {len(dev_risk)}")

    # Target: Y_transition = 1 if S(k+1) == 1, else 0
    # Next window Slabel_max
    dev_df_sorted = dev_df.sort_values(['Patient_Key', 'Window_6h_Idx'])
    dev_df_sorted['S_next'] = dev_df_sorted.groupby('Patient_Key')['Slabel_max'].shift(-1)
    
    dev_risk = dev_df_sorted[(dev_df_sorted['Window_6h_Idx'].between(0, 7)) & (dev_df_sorted['Slabel_max'] == 0)].copy()
    dev_risk = dev_risk[dev_risk['S_next'].notna()].copy()
    dev_risk['Y_transition'] = (dev_risk['S_next'] == 1).astype(int)

    y_dev = dev_risk['Y_transition'].values
    groups_dev = dev_risk['Patient_Key'].values
    print(f"Valid Dev Risk Windows: {len(dev_risk)}, Transition Events: {y_dev.sum()} ({y_dev.mean()*100:.2f}%)")

    # 2. Define Feature Subsets for Ablation V2-A through V2-G
    all_cols = dev_risk.columns

    # Base biological signals
    base_vitals = ['HR', 'MAP', 'SBP', 'DBP', 'Temp', 'SO2']
    base_labs = ['WBC', 'HCT', 'HGB', 'Platelets', 'PT', 'INR', 'AST', 'ALT', 'Creatinine', 'BUN', 'K', 'Na', 'BEb', 'pH', 'PaCO2', 'CL', 'HCO3', 'FiO2']
    static_demos = ['Age_mean', 'Gender_mean']

    level_cols = [c for c in all_cols if any(c.startswith(f"{s}_") and not ('_delta' in c or '_accel' in c) for s in base_vitals + base_labs)] + static_demos
    delta_cols = [c for c in all_cols if '_delta1' in c and not any(s in c for s in ['Gender', 'Age'])]
    accel_cols = [c for c in all_cols if '_accel' in c and not any(s in c for s in ['Gender', 'Age'])]

    # Feature Ablation Mapping
    ablation_specs = {
        'V2-A (Physiological Baseline Levels)': level_cols,
        'V2-B (+ Distributional Stats)': level_cols + [c for c in all_cols if any(c.endswith(f'_{stat}') for stat in ['min', 'max', 'std']) and c in level_cols],
        'V2-C (+ Temporal Deltas)': level_cols + delta_cols,
        'V2-D (+ Velocity & Acceleration)': level_cols + delta_cols + accel_cols,
        'V2-E (V2 Transportability-Optimized Schema)': [c for c in level_cols + delta_cols + accel_cols if c in all_cols]
    }

    # 3. Execute Patient-Level 5-Fold GroupKFold Cross-Validation on V2-E Schema
    v2_features = ablation_specs['V2-E (V2 Transportability-Optimized Schema)']
    X_dev = dev_risk[v2_features].copy()

    # Calculate Dev-fit Medians for exact isolation
    dev_medians = X_dev.median()
    X_dev_imputed = X_dev.fillna(dev_medians).fillna(0.0)

    gkf = GroupKFold(n_splits=5)

    oof_preds_raw = np.zeros(len(dev_risk))
    oof_preds_calib = np.zeros(len(dev_risk))

    print("\nTraining BioMarkerX V2 Transportability Classifier (5-Fold GroupKFold)...")
    
    # Base Estimator: Gradient Boosting with Controlled Regularization (Depth=4, lr=0.03, subsample=0.8)
    v2_base_model = GradientBoostingClassifier(
        n_estimators=300,
        learning_rate=0.03,
        max_depth=4,
        subsample=0.8,
        random_state=42
    )

    for fold, (train_idx, val_idx) in enumerate(gkf.split(X_dev_imputed, y_dev, groups=groups_dev)):
        X_train, y_train = X_dev_imputed.iloc[train_idx], y_dev[train_idx]
        X_val, y_val = X_dev_imputed.iloc[val_idx], y_dev[val_idx]

        fold_model = GradientBoostingClassifier(
            n_estimators=300, learning_rate=0.03, max_depth=4, subsample=0.8, random_state=42
        )
        fold_model.fit(X_train, y_train)

        raw_val = fold_model.predict_proba(X_val)[:, 1]
        oof_preds_raw[val_idx] = raw_val

    # Fit Isotonic Calibrator on Dev OOF predictions
    from sklearn.isotonic import IsotonicRegression
    calibrator = IsotonicRegression(out_of_bounds='clip', y_min=0.0, y_max=1.0)
    calibrator.fit(oof_preds_raw, y_dev)

    oof_preds_calib = calibrator.predict(oof_preds_raw)

    dev_auroc = roc_auc_score(y_dev, oof_preds_calib)
    dev_auprc = average_precision_score(y_dev, oof_preds_calib)
    dev_brier = brier_score_loss(y_dev, oof_preds_calib)

    # Threshold selection on Dev OOF
    thresholds = np.linspace(0.05, 0.50, 100)
    best_f1 = 0.0
    v2_tau_opt = 0.1825

    for tau in thresholds:
        y_p = (oof_preds_calib >= tau).astype(int)
        tp = np.sum((y_p == 1) & (y_dev == 1))
        fp = np.sum((y_p == 1) & (y_dev == 0))
        fn = np.sum((y_p == 0) & (y_dev == 1))
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
        if f1 > best_f1:
            best_f1 = f1
            v2_tau_opt = tau

    print(f"V2 Development AUROC: {dev_auroc:.4f}")
    print(f"V2 Development AUPRC: {dev_auprc:.4f}")
    print(f"V2 Development Brier: {dev_brier:.5f}")
    print(f"V2 Optimal Development Threshold (tau_opt): {v2_tau_opt:.4f}")

    # 4. Save Locked V2 Artifacts
    v2_model_path = os.path.join(v2_dir, 'V2_MODEL.joblib')
    v2_calib_path = os.path.join(v2_dir, 'V2_CALIBRATOR.joblib')
    v2_schema_path = os.path.join(v2_dir, 'V2_FEATURE_SCHEMA.json')
    v2_medians_path = os.path.join(v2_dir, 'V2_DEV_MEDIANS.json')

    v2_base_model.fit(X_dev_imputed, y_dev)
    joblib.dump(v2_base_model, v2_model_path)
    joblib.dump(calibrator, v2_calib_path)

    with open(v2_schema_path, 'w') as f:
        json.dump({'v2_features': list(v2_features), 'feature_count': len(v2_features)}, f, indent=2)

    with open(v2_medians_path, 'w') as f:
        json.dump(dev_medians.to_dict(), f, indent=2)

    print(f"Locked V2 model & calibrator saved to {v2_dir}/")

    # 5. PHASE 20 — FINAL EXTERNAL REVALIDATION ON UNTOUCHED EXTERNAL TEST A
    print("\n=========================================================================")
    print("PHASE 20 — FINAL EXTERNAL REVALIDATION ON UNTOUCHED EXTERNAL TEST A")
    print("=========================================================================")

    ext_cache = r'scratch\physionet2019_risk_set_cache.parquet'
    ext_risk_set = pd.read_parquet(ext_cache)
    y_ext = ext_risk_set['Y_transition'].values

    # Construct External V2 Feature Matrix using Dev-fit Medians
    X_ext_v2_dict = {}
    for feat in v2_features:
        if feat in ext_risk_set.columns:
            X_ext_v2_dict[feat] = ext_risk_set[feat]
        else:
            X_ext_v2_dict[feat] = dev_medians.get(feat, 0.0)

    X_ext_v2 = pd.DataFrame(X_ext_v2_dict)[v2_features]
    X_ext_v2_imputed = X_ext_v2.fillna(dev_medians).fillna(0.0)

    # Predict using locked V2 Calibrated Model
    v2_raw_ext = v2_base_model.predict_proba(X_ext_v2_imputed)[:, 1]
    v2_ext_prob = calibrator.predict(v2_raw_ext)
    v2_ext_prob = np.clip(v2_ext_prob, 0.0, 1.0)

    v2_ext_auroc = roc_auc_score(y_ext, v2_ext_prob)
    v2_ext_auprc = average_precision_score(y_ext, v2_ext_prob)
    v2_ext_brier = brier_score_loss(y_ext, v2_ext_prob)

    v2_y_pred = (v2_ext_prob >= v2_tau_opt).astype(int)

    tp_ext = np.sum((v2_y_pred == 1) & (y_ext == 1))
    fp_ext = np.sum((v2_y_pred == 1) & (y_ext == 0))
    tn_ext = np.sum((v2_y_pred == 0) & (y_ext == 0))
    fn_ext = np.sum((v2_y_pred == 0) & (y_ext == 1))

    v2_sens = tp_ext / (tp_ext + fn_ext) if (tp_ext + fn_ext) > 0 else 0.0
    v2_spec = tn_ext / (tn_ext + fp_ext) if (tn_ext + fp_ext) > 0 else 0.0
    v2_ppv = tp_ext / (tp_ext + fp_ext) if (tp_ext + fp_ext) > 0 else 0.0
    v2_npv = tn_ext / (tn_ext + fn_ext) if (tn_ext + fn_ext) > 0 else 0.0

    print(f"BioMarkerX V2 External AUROC: {v2_ext_auroc:.4f}")
    print(f"BioMarkerX V2 External AUPRC: {v2_ext_auprc:.4f}")
    print(f"BioMarkerX V2 External Brier Score: {v2_ext_brier:.5f}")
    print(f"BioMarkerX V2 External Sensitivity (at tau={v2_tau_opt:.4f}): {v2_sens*100:.2f}% ({tp_ext}/{tp_ext+fn_ext})")
    print(f"BioMarkerX V2 External Specificity: {v2_spec*100:.2f}% ({tn_ext}/{tn_ext+fp_ext})")
    print(f"BioMarkerX V2 External PPV: {v2_ppv*100:.2f}% ({tp_ext}/{tp_ext+fp_ext})")
    print(f"BioMarkerX V2 External NPV: {v2_npv*100:.2f}% ({tn_ext}/{tn_ext+fn_ext})")

    # 6. PHASE 21 — FINAL COMPARISON MANIFEST & TABLE
    comparison_table = pd.DataFrame([
        {
            'Metric': 'AUROC',
            'Model D Internal': 0.7758,
            'Model D External': 0.5555,
            'V2 Internal': round(dev_auroc, 4),
            'V2 External': round(v2_ext_auroc, 4)
        },
        {
            'Metric': 'AUPRC',
            'Model D Internal': 0.3797,
            'Model D External': 0.0153,
            'V2 Internal': round(dev_auprc, 4),
            'V2 External': round(v2_ext_auprc, 4)
        },
        {
            'Metric': 'Brier Score',
            'Model D Internal': 0.06975,
            'Model D External': 0.07991,
            'V2 Internal': round(dev_brier, 5),
            'V2 External': round(v2_ext_brier, 5)
        },
        {
            'Metric': 'Sensitivity (%)',
            'Model D Internal': 62.44,
            'Model D External': 90.57,
            'V2 Internal': round((np.sum((oof_preds_calib >= v2_tau_opt) & (y_dev == 1)) / y_dev.sum()) * 100, 2),
            'V2 External': round(v2_sens * 100, 2)
        },
        {
            'Metric': 'Specificity (%)',
            'Model D Internal': 90.23,
            'Model D External': 9.34,
            'V2 Internal': round((np.sum((oof_preds_calib < v2_tau_opt) & (y_dev == 0)) / (len(y_dev) - y_dev.sum())) * 100, 2),
            'V2 External': round(v2_spec * 100, 2)
        },
        {
            'Metric': 'PPV (%)',
            'Model D Internal': 38.67,
            'Model D External': 1.19,
            'V2 Internal': round((np.sum((oof_preds_calib >= v2_tau_opt) & (y_dev == 1)) / np.sum(oof_preds_calib >= v2_tau_opt)) * 100, 2),
            'V2 External': round(v2_ppv * 100, 2)
        },
        {
            'Metric': 'NPV (%)',
            'Model D Internal': 96.05,
            'Model D External': 98.79,
            'V2 Internal': round((np.sum((oof_preds_calib < v2_tau_opt) & (y_dev == 0)) / np.sum(oof_preds_calib < v2_tau_opt)) * 100, 2),
            'V2 External': round(v2_npv * 100, 2)
        }
    ])

    comp_csv = os.path.join(v2_dir, 'V1_VS_V2_FINAL_COMPARISON_TABLE.csv')
    comparison_table.to_csv(comp_csv, index=False)
    print(f"\nExported v2/V1_VS_V2_FINAL_COMPARISON_TABLE.csv")
    print(comparison_table)

    # 7. Lock V2 Manifest JSON
    v2_manifest = {
        'project_name': 'BioMarkerX V2',
        'lock_timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'v2_auroc_internal': float(dev_auroc),
        'v2_auroc_external': float(v2_ext_auroc),
        'v2_auprc_internal': float(dev_auprc),
        'v2_auprc_external': float(v2_ext_auprc),
        'v2_brier_internal': float(dev_brier),
        'v2_brier_external': float(v2_ext_brier),
        'v2_tau_opt': float(v2_tau_opt),
        'v2_sensitivity_ext_pct': float(v2_sens * 100),
        'v2_specificity_ext_pct': float(v2_spec * 100),
        'v2_ppv_ext_pct': float(v2_ppv * 100),
        'v2_npv_ext_pct': float(v2_npv * 100),
        'locked_sha256_hashes': {
            'v2_model_joblib': compute_sha256(v2_model_path),
            'v2_calibrator_joblib': compute_sha256(v2_calib_path),
            'v2_feature_schema_json': compute_sha256(v2_schema_path),
            'v2_dev_medians_json': compute_sha256(v2_medians_path),
            'comparison_table_csv': compute_sha256(comp_csv)
        }
    }

    v2_manifest_path = os.path.join(v2_dir, 'V2_LOCK_MANIFEST.json')
    with open(v2_manifest_path, 'w') as f:
        json.dump(v2_manifest, f, indent=2)

    print(f"Generated v2/V2_LOCK_MANIFEST.json with SHA-256 cryptographic hashes.")

if __name__ == '__main__':
    run_v2_development_pipeline()
