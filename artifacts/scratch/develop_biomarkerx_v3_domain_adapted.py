import os
import glob
import json
import time
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import HistGradientBoostingClassifier, ExtraTreesClassifier, RandomTreesEmbedding
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss

def run_v3_domain_adapted_pipeline():
    print("=========================================================================")
    print("DEVELOPING BIOMARKERX V3-DOMAIN-ADAPTED: PATIENT Z-SCORE STANDARDIZATION")
    print("=========================================================================")

    v3_dir = r"v3_engine"
    os.makedirs(v3_dir, exist_ok=True)

    # 1. Load Development Dataset
    dev_path = r"FINAL_CLEANED_DATASETS\dataset_v2_unified_2115_patients_6h.csv"
    dev_df = pd.read_csv(dev_path)

    # Sort patient stay windows
    dev_df = dev_df.sort_values(['Patient_Key', 'Window_6h_Idx'])
    dev_df['S_next'] = dev_df.groupby('Patient_Key')['Slabel_max'].shift(-1)

    # Filter standard risk set: Window_6h_Idx in 0..7, S(k) == 0, valid S(k+1)
    dev_risk = dev_df[(dev_df['Window_6h_Idx'].between(0, 7)) & (dev_df['Slabel_max'] == 0) & (dev_df['S_next'].notna())].copy()
    dev_risk['Y_transition'] = (dev_risk['S_next'] == 1).astype(int)

    y_dev = dev_risk['Y_transition'].values
    groups_dev = dev_risk['Patient_Key'].values

    # Base biological signals
    base_signals = ['HR', 'MAP', 'SBP', 'DBP', 'Temp', 'SO2', 'WBC', 'HCT', 'HGB', 'Platelets', 'Creatinine', 'BUN', 'K', 'Na', 'BEb', 'pH', 'PaCO2', 'CL', 'HCO3', 'FiO2', 'Shock_Index', 'Pulse_Pressure']

    level_cols = [c for c in dev_risk.columns if any(c.startswith(f"{s}_") and not ('_delta' in c or '_accel' in c) for s in base_signals)]

    # Compute Intra-Patient Z-Score Standardization for Dev set
    # Z(x_i, k) = (x_i(k) - mean_patient(x_i)) / (std_patient(x_i) + 1e-5)
    print("Computing Intra-Patient Z-Score Standardization for Dev set...")
    patient_means = dev_risk.groupby('Patient_Key')[level_cols].transform('mean')
    patient_stds = dev_risk.groupby('Patient_Key')[level_cols].transform('std').fillna(1.0)
    
    dev_z_levels = (dev_risk[level_cols] - patient_means) / (patient_stds + 1e-5)
    dev_z_levels.columns = [f"{c}_zscore" for c in level_cols]

    # Compute Velocity & Acceleration for dynamic signals
    vel_cols = [c for c in dev_risk.columns if '_delta1' in c and not any(s in c for s in ['Gender', 'Age'])]
    acc_cols = [c for c in dev_risk.columns if '_accel' in c and not any(s in c for s in ['Gender', 'Age'])]

    # Combine Z-score features, Levels, Velocities, and Accelerations
    X_dev_list = [dev_risk[level_cols], dev_z_levels, dev_risk[vel_cols], dev_risk[acc_cols]]
    X_dev = pd.concat(X_dev_list, axis=1)
    X_dev = X_dev.loc[:, ~X_dev.columns.duplicated()]
    v3_features = list(X_dev.columns)

    print(f"BioMarkerX V3-DA Feature Dimension: {len(v3_features)} features.")

    dev_medians = X_dev.median()
    X_dev_imputed = X_dev.fillna(dev_medians).fillna(0.0)

    # 2. Patient-Level 5-Fold GroupKFold Cross Validation
    gkf = GroupKFold(n_splits=5)
    oof_preds_raw = np.zeros(len(dev_risk))

    print("\nTraining BioMarkerX V3-DA Ensemble (5-Fold GroupKFold)...")

    v3_da_model = HistGradientBoostingClassifier(
        max_iter=300,
        learning_rate=0.03,
        max_depth=5,
        l2_regularization=2.0,
        early_stopping=True,
        n_iter_no_change=15,
        random_state=42
    )

    for fold, (train_idx, val_idx) in enumerate(gkf.split(X_dev_imputed, y_dev, groups=groups_dev)):
        X_tr, y_tr = X_dev_imputed.iloc[train_idx], y_dev[train_idx]
        X_va, y_va = X_dev_imputed.iloc[val_idx], y_dev[val_idx]

        fold_m = HistGradientBoostingClassifier(
            max_iter=300, learning_rate=0.03, max_depth=5, l2_regularization=2.0, early_stopping=True, n_iter_no_change=15, random_state=42
        )
        fold_m.fit(X_tr, y_tr)
        oof_preds_raw[val_idx] = fold_m.predict_proba(X_va)[:, 1]

    # Fit Isotonic Calibrator
    calibrator = IsotonicRegression(out_of_bounds='clip', y_min=0.0, y_max=1.0)
    calibrator.fit(oof_preds_raw, y_dev)
    oof_preds_calib = calibrator.predict(oof_preds_raw)

    dev_auroc = roc_auc_score(y_dev, oof_preds_calib)
    dev_auprc = average_precision_score(y_dev, oof_preds_calib)
    dev_brier = brier_score_loss(y_dev, oof_preds_calib)

    v3_tau_opt = 0.1825
    best_f1 = 0.0
    for tau in np.linspace(0.05, 0.40, 100):
        y_p = (oof_preds_calib >= tau).astype(int)
        tp = np.sum((y_p == 1) & (y_dev == 1))
        fp = np.sum((y_p == 1) & (y_dev == 0))
        fn = np.sum((y_p == 0) & (y_dev == 1))
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
        if f1 > best_f1:
            best_f1 = f1
            v3_tau_opt = tau

    print(f"V3-DA Dev AUROC: {dev_auroc:.4f}")
    print(f"V3-DA Dev AUPRC: {dev_auprc:.4f}")
    print(f"V3-DA Dev Brier: {dev_brier:.5f}")
    print(f"V3-DA Dev Optimal Threshold (tau_opt): {v3_tau_opt:.4f}")

    v3_da_model.fit(X_dev_imputed, y_dev)

    # Save Artifacts
    joblib.dump(v3_da_model, os.path.join(v3_dir, 'V3_DA_MODEL.joblib'))
    joblib.dump(calibrator, os.path.join(v3_dir, 'V3_DA_CALIBRATOR.joblib'))

    # 3. EXTERNAL EVALUATION ON PHYSIONET 2019 (training_setA)
    print("\n=========================================================================")
    print("EVALUATING BIOMARKERX V3-DA ON EXTERNAL PHYSIONET 2019 DATASET")
    print("=========================================================================")

    ext_cache = r'scratch\physionet2019_risk_set_cache.parquet'
    ext_risk = pd.read_parquet(ext_cache)
    y_ext = ext_risk['Y_transition'].values

    # Compute Intra-Patient Z-Score Standardization for External set
    print("Computing Intra-Patient Z-Score Standardization for External set...")
    ext_level_cols = [c for c in level_cols if c in ext_risk.columns]
    ext_patient_means = ext_risk.groupby('patient_id')[ext_level_cols].transform('mean')
    ext_patient_stds = ext_risk.groupby('patient_id')[ext_level_cols].transform('std').fillna(1.0)

    ext_z_levels = (ext_risk[ext_level_cols] - ext_patient_means) / (ext_patient_stds + 1e-5)
    ext_z_levels.columns = [f"{c}_zscore" for c in ext_level_cols]

    # Combine external features
    X_ext_v3_dict = {}
    for feat in v3_features:
        if feat in ext_risk.columns:
            X_ext_v3_dict[feat] = ext_risk[feat]
        elif feat in ext_z_levels.columns:
            X_ext_v3_dict[feat] = ext_z_levels[feat]
        else:
            X_ext_v3_dict[feat] = dev_medians.get(feat, 0.0)

    X_ext_v3 = pd.DataFrame(X_ext_v3_dict)[v3_features]
    X_ext_v3_imputed = X_ext_v3.fillna(dev_medians).fillna(0.0)

    v3_raw_ext = v3_da_model.predict_proba(X_ext_v3_imputed)[:, 1]
    v3_ext_prob = calibrator.predict(v3_raw_ext)
    v3_ext_prob = np.clip(v3_ext_prob, 0.0, 1.0)

    v3_ext_auroc = roc_auc_score(y_ext, v3_ext_prob)
    v3_ext_auprc = average_precision_score(y_ext, v3_ext_prob)
    v3_ext_brier = brier_score_loss(y_ext, v3_ext_prob)

    v3_y_pred = (v3_ext_prob >= v3_tau_opt).astype(int)

    tp_ext = np.sum((v3_y_pred == 1) & (y_ext == 1))
    fp_ext = np.sum((v3_y_pred == 1) & (y_ext == 0))
    tn_ext = np.sum((v3_y_pred == 0) & (y_ext == 0))
    fn_ext = np.sum((v3_y_pred == 0) & (y_ext == 1))

    v3_sens = tp_ext / (tp_ext + fn_ext) if (tp_ext + fn_ext) > 0 else 0.0
    v3_spec = tn_ext / (tn_ext + fp_ext) if (tn_ext + fp_ext) > 0 else 0.0
    v3_ppv = tp_ext / (tp_ext + fp_ext) if (tp_ext + fp_ext) > 0 else 0.0
    v3_npv = tn_ext / (tn_ext + fn_ext) if (tn_ext + fn_ext) > 0 else 0.0

    valid_keys = [s for s in ['HR_mean', 'MAP_mean', 'SBP_mean', 'Temp_mean', 'WBC_mean', 'Creatinine_mean'] if s in ext_risk.columns]
    obs_cnt = ext_risk[valid_keys].notna().sum(axis=1)
    r_v3_da = np.corrcoef(obs_cnt, v3_ext_prob)[0, 1]

    print("=========================================================================")
    print("BIOMARKERX V3-DOMAIN-ADAPTED EXTERNAL RESULTS (PhysioNet 2019):")
    print("=========================================================================")
    print(f"BioMarkerX V3-DA External AUROC: {v3_ext_auroc:.4f}")
    print(f"BioMarkerX V3-DA External AUPRC: {v3_ext_auprc:.4f}")
    print(f"BioMarkerX V3-DA External Brier Score: {v3_ext_brier:.5f}")
    print(f"BioMarkerX V3-DA External Sensitivity (at tau={v3_tau_opt:.4f}): {v3_sens*100:.2f}% ({tp_ext}/{tp_ext+fn_ext})")
    print(f"BioMarkerX V3-DA External Specificity: {v3_spec*100:.2f}% ({tn_ext}/{tn_ext+fp_ext})")
    print(f"BioMarkerX V3-DA External PPV: {v3_ppv*100:.2f}% ({tp_ext}/{tp_ext+fp_ext})")
    print(f"BioMarkerX V3-DA External NPV: {v3_npv*100:.2f}% ({tn_ext}/{tn_ext+fn_ext})")
    print(f"BioMarkerX V3-DA Measurement Count vs Risk Score Correlation (r): {r_v3_da:+.4f}")
    print("=========================================================================")

if __name__ == '__main__':
    run_v3_domain_adapted_pipeline()
