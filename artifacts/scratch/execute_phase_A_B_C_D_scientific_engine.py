import os
import json
import time
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import HistGradientBoostingClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss

def run_phase_A_B_C_D_engine():
    print("=========================================================================")
    print("STARTING PHASES A, B, C, D: SCIENTIFIC FORENSICS, FEATURE REDESIGN & ABLATIONS")
    print("=========================================================================")

    out_dir = r"scientific_audit"
    os.makedirs(out_dir, exist_ok=True)

    # 1. Load Development Dataset (dataset_v2_unified_2115_patients_6h.csv)
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

    print(f"Dev Risk Set Windows: {len(dev_risk)}, Transition Events: {y_dev.sum()} ({y_dev.mean()*100:.2f}%)")

    # -------------------------------------------------------------------------
    # PHASE B — FEATURE REDESIGN & CLEAN FEATURE BLOCK DEFINITIONS
    # -------------------------------------------------------------------------
    print("\n--- PHASE B: Feature Redesign & Old-to-New Feature Mapping ---")

    # Base biological signals
    base_vitals = ['HR', 'MAP', 'SBP', 'DBP', 'Temp', 'SO2']
    base_labs = ['WBC', 'HCT', 'HGB', 'Platelets', 'PT', 'INR', 'AST', 'Creatinine', 'BUN', 'K', 'Na', 'BEb', 'pH', 'PaCO2', 'CL', 'HCO3', 'FiO2']
    derived_ratios = ['Shock_Index', 'Pulse_Pressure'] # Excluded De_Ritis_Ratio due to missing ALT in PhysioNet
    static_demos = ['Age_mean', 'Gender_mean']

    # Identify clean features
    # 1. Block A: Physiology Only (Level summary statistics for vitals, labs, derived ratios, static demos)
    block_A_cols = [c for c in dev_risk.columns if any(c.startswith(f"{s}_") and not ('_delta' in c or '_accel' in c) for s in base_vitals + base_labs + derived_ratios)] + static_demos
    block_A_cols = sorted(list(set([c for c in block_A_cols if c in dev_risk.columns])))

    # 2. Block B: Temporal Dynamics (Velocity & Acceleration for dynamic signals ONLY, excluding Gender/Age)
    vel_cols = [c for c in dev_risk.columns if '_delta1' in c and not any(s in c for s in ['Gender', 'Age', 'De_Ritis_Ratio'])]
    acc_cols = [c for c in dev_risk.columns if '_accel' in c and not any(s in c for s in ['Gender', 'Age', 'De_Ritis_Ratio'])]
    block_B_cols = sorted(list(set(block_A_cols + vel_cols + acc_cols)))

    # 3. Block C: Patient-Relative Physiology (Baseline-relative deviations X(k) - X(0))
    dev_k0 = dev_df[dev_df['Window_6h_Idx'] == 0].set_index('Patient_Key')
    patient_rel_dict = {}
    for sig in base_vitals + base_labs + derived_ratios:
        col_m = f"{sig}_mean"
        if col_m in dev_risk.columns:
            k0_vals = dev_risk['Patient_Key'].map(dev_k0[col_m] if col_m in dev_k0.columns else pd.Series(dtype=float))
            patient_rel_dict[f"{sig}_base_diff"] = dev_risk[col_m] - k0_vals
            patient_rel_dict[f"{sig}_base_rel"] = (dev_risk[col_m] - k0_vals) / (np.abs(k0_vals) + 1e-5)

    patient_rel_df = pd.DataFrame(patient_rel_dict, index=dev_risk.index)
    block_C_cols = sorted(list(set(block_A_cols + list(patient_rel_df.columns))))

    # 4. Block D: Measurement & Missingness Context Only (Counts of non-null signals per window)
    obs_count_col = dev_risk[block_A_cols].notna().sum(axis=1)
    obs_missing_mask = dev_risk[block_A_cols].isna().astype(float)
    obs_missing_mask.columns = [f"{c}_missing" for c in block_A_cols]
    
    measurement_context_df = pd.concat([pd.DataFrame({'obs_total_count': obs_count_col}, index=dev_risk.index), obs_missing_mask], axis=1)
    block_D_cols = list(measurement_context_df.columns)

    # Export OLD -> NEW Feature Mapping
    mapping_record = {
        'removed_features': [
            'De_Ritis_Ratio_mean', 'De_Ritis_Ratio_min', 'De_Ritis_Ratio_max', 'De_Ritis_Ratio_std',
            'Gender_mean_delta1', 'Gender_min_delta1', 'Gender_max_delta1',
            'Gender_mean_accel', 'Gender_min_accel', 'Gender_max_accel',
            'Age_mean_delta1', 'Age_mean_accel'
        ],
        'removal_reasons': {
            'De_Ritis_Ratio': 'ALT missing in external PhysioNet 2019 dataset causing NaN evaluation',
            'Gender_derivatives': 'Static demographic variable - velocity and acceleration are scientifically invalid',
            'Age_derivatives': 'Static demographic variable - velocity and acceleration are scientifically invalid'
        },
        'feature_blocks': {
            'Block_A_Physiology_Only': len(block_A_cols),
            'Block_B_Physiology_Plus_Temporal_Dynamics': len(block_B_cols),
            'Block_C_Patient_Relative_Physiology': len(block_C_cols),
            'Block_D_Measurement_Context_Only': len(block_D_cols)
        }
    }

    mapping_json = os.path.join(out_dir, 'OLD_TO_NEW_FEATURE_MAPPING.json')
    with open(mapping_json, 'w') as f:
        json.dump(mapping_record, f, indent=2)
    print(f"Exported scientific_audit/OLD_TO_NEW_FEATURE_MAPPING.json")

    # -------------------------------------------------------------------------
    # PHASE C & PHASE D — CONTROLLED ABLATIONS & MEASUREMENT-CONFOUND TEST
    # -------------------------------------------------------------------------
    print("\n--- PHASE C & D: Controlled Ablations & Measurement-Confound Test ---")

    gkf = GroupKFold(n_splits=5)

    def evaluate_feature_block(X_df, block_name):
        medians = X_df.median()
        X_imp = X_df.fillna(medians).fillna(0.0)

        oof_raw = np.zeros(len(dev_risk))
        for train_idx, val_idx in gkf.split(X_imp, y_dev, groups=groups_dev):
            X_tr, y_tr = X_imp.iloc[train_idx], y_dev[train_idx]
            X_va = X_imp.iloc[val_idx]

            m = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.03, max_depth=4, random_state=42)
            m.fit(X_tr, y_tr)
            oof_raw[val_idx] = m.predict_proba(X_va)[:, 1]

        # Isotonic calibration on Dev OOF
        iso = IsotonicRegression(out_of_bounds='clip', y_min=0.0, y_max=1.0)
        iso.fit(oof_raw, y_dev)
        oof_calib = iso.predict(oof_raw)

        auroc = roc_auc_score(y_dev, oof_calib)
        auprc = average_precision_score(y_dev, oof_calib)
        brier = brier_score_loss(y_dev, oof_calib)

        # Correlation between risk score and total measurement count
        r_confound = np.corrcoef(obs_count_col, oof_calib)[0, 1]

        return {
            'Block': block_name,
            'Feature Count': X_df.shape[1],
            'Dev AUROC': round(auroc, 4),
            'Dev AUPRC': round(auprc, 4),
            'Dev Brier Score': round(brier, 5),
            'Measurement Confound r': round(r_confound, 4)
        }

    ablation_results = []

    # Block A: Physiology Only
    X_A = dev_risk[block_A_cols]
    ablation_results.append(evaluate_feature_block(X_A, "Block A: Physiology Only"))

    # Block B: Physiology + Temporal Dynamics
    X_B = dev_risk[block_B_cols]
    ablation_results.append(evaluate_feature_block(X_B, "Block B: Physiology + Temporal Dynamics"))

    # Block C: Patient-Relative Physiology
    X_C = pd.concat([dev_risk[block_A_cols], patient_rel_df], axis=1)
    ablation_results.append(evaluate_feature_block(X_C, "Block C: Patient-Relative Physiology"))

    # Block D / Model 2: Measurement & Missingness Context ONLY
    X_D = measurement_context_df
    ablation_results.append(evaluate_feature_block(X_D, "Model 2 (Phase D): Measurement Context ONLY"))

    # Model 3: Physiology + Measurement Context
    X_M3 = pd.concat([dev_risk[block_A_cols], measurement_context_df], axis=1)
    ablation_results.append(evaluate_feature_block(X_M3, "Model 3 (Phase D): Physiology + Measurement Context"))

    # Full Transportable Model (Block B + Block C)
    X_Full = pd.concat([dev_risk[block_B_cols], patient_rel_df], axis=1)
    X_Full = X_Full.loc[:, ~X_Full.columns.duplicated()]
    ablation_results.append(evaluate_feature_block(X_Full, "Block F: Full Transportable Physiology Model"))

    ablation_df = pd.DataFrame(ablation_results)
    ablation_csv = os.path.join(out_dir, 'PHASE_C_D_ABLATION_AND_CONFOUND_RESULTS.csv')
    ablation_df.to_csv(ablation_csv, index=False)

    print("\n=========================================================================")
    print("PHASE C & D ABLATION & MEASUREMENT-CONFOUND RESULTS:")
    print("=========================================================================")
    print(ablation_df.to_string(index=False))
    print("=========================================================================\n")

if __name__ == '__main__':
    run_phase_A_B_C_D_engine()
