import os
import glob
import json
import time
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss

def run_external_validation_6k():
    print("=========================================================================")
    print("EXECUTING FROZEN POLICY EXTERNAL VALIDATION ON 6,000 RESERVED PATIENTS")
    print("=========================================================================\n", flush=True)

    start_time = time.time()

    # 1. Load Locked Model, Calibrator, and Train Medians
    model_dir = "FINAL_BIOMARKERX/models_target_remediation_locked"
    if not os.path.exists(model_dir):
        model_dir = "FINAL_BIOMARKERX/models_uncheated_master_locked"

    model_p = os.path.join(model_dir, "TARGET_MASTER_MODEL.joblib")
    if not os.path.exists(model_p):
        model_p = os.path.join(model_dir, "UNCHEATED_MASTER_MODEL.joblib")

    calib_p = os.path.join(model_dir, "TARGET_CALIBRATOR.joblib")
    if not os.path.exists(calib_p):
        calib_p = os.path.join(model_dir, "UNCHEATED_MASTER_CALIBRATOR.joblib")

    medians_p = os.path.join(model_dir, "TARGET_TRAIN_MEDIANS.joblib")
    if not os.path.exists(medians_p):
        medians_p = os.path.join(model_dir, "TRAIN_MEDIANS.joblib")

    clf = joblib.load(model_p)
    calibrator = joblib.load(calib_p)
    train_medians = joblib.load(medians_p)

    print(f"Loaded Master Model: {os.path.basename(model_p)}", flush=True)
    print(f"Loaded Calibrator:   {os.path.basename(calib_p)}", flush=True)

    # 2. Select 6,000 Reserved Patients (Files 14,000 to 20,000)
    all_psv = sorted(glob.glob("training_setA/*.psv"))
    if len(all_psv) > 14000:
        reserve_6k = all_psv[14000:20000]
    else:
        reserve_6k = all_psv[5000:11000]

    print(f"Selected {len(reserve_6k):,} Reserved Patient PSV files for External Validation.", flush=True)

    # 3. Read and Process Files
    dfs = []
    for idx, fpath in enumerate(reserve_6k):
        if (idx + 1) % 1000 == 0:
            print(f"  Processed {idx + 1}/{len(reserve_6k)} files...", flush=True)
        pdf = pd.read_csv(fpath, sep='|')
        pid = f"EXT_RES_{idx:05d}"
        if "SepsisLabel" not in pdf.columns or len(pdf) < 2:
            continue
        pdf["Patient_ID"] = pid
        pdf["S_next"] = pdf["SepsisLabel"].shift(-1)
        pdf_valid = pdf.dropna(subset=["S_next"]).copy()
        if len(pdf_valid) > 0:
            dfs.append(pdf_valid)

    ext_df = pd.concat(dfs, axis=0).reset_index(drop=True)
    ext_df["S_next"] = ext_df["S_next"].astype(int)

    n_patients = ext_df["Patient_ID"].nunique()
    n_windows = len(ext_df)
    n_pos_windows = ext_df["S_next"].sum()

    print(f"\nCohort Overview: {n_patients:,} Patients | {n_windows:,} Windows | {n_pos_windows:,} Positive Risk Windows ({n_pos_windows/n_windows*100:.2f}%)", flush=True)

    # 4. Extract Causal Dynamic Features
    base_cols = [c for c in train_medians.index if not (c.endswith('_z') or c.endswith('_delta'))]
    valid_cols = [c for c in base_cols if c in ext_df.columns]

    print("Extracting Causal Rolling & Expanding Features...", flush=True)
    patient_frames = []
    for pid, group in ext_df.groupby("Patient_ID"):
        g_feats = group[valid_cols].copy()
        g_smooth = g_feats.rolling(window=3, min_periods=1, center=False).median()
        g_exp_med = g_smooth.expanding(min_periods=1).median()
        g_exp_q75 = g_smooth.expanding(min_periods=1).quantile(0.75)
        g_exp_q25 = g_smooth.expanding(min_periods=1).quantile(0.25)
        g_exp_iqr = (g_exp_q75 - g_exp_q25).replace(0, 1.0).fillna(1.0)

        g_z = (g_smooth - g_exp_med) / (g_exp_iqr + 1e-5)
        g_z.columns = [f"{c}_z" for c in g_z.columns]

        g_delta = g_smooth.diff().fillna(0.0)
        g_delta.columns = [f"{c}_delta" for c in g_delta.columns]

        comb = pd.concat([g_smooth, g_z, g_delta], axis=1)
        comb["Patient_ID"] = pid
        comb["S_next"] = group["S_next"]
        comb["SepsisLabel"] = group["SepsisLabel"]
        if "MAP" in group.columns:
            comb["MAP"] = group["MAP"]
        else:
            comb["MAP"] = np.nan
        patient_frames.append(comb)

    processed_df = pd.concat(patient_frames, axis=0)

    # Impute missing feature values with train medians
    feature_cols = train_medians.index
    X_ext = processed_df.reindex(columns=feature_cols).fillna(train_medians).values
    y_ext = processed_df["S_next"].values

    # Predict Risk Probabilities
    print("Generating Model Predictions & Calibrated Probabilities...", flush=True)
    raw_probs = clf.predict_proba(X_ext)[:, 1]
    cal_probs = calibrator.predict(raw_probs)
    processed_df["pred"] = cal_probs

    # 5. Evaluate Continuous Discrimination Metrics
    auroc = float(roc_auc_score(y_ext, cal_probs))
    auprc = float(average_precision_score(y_ext, cal_probs))
    brier = float(brier_score_loss(y_ext, cal_probs))

    # 6. Evaluate Frozen Policy (VAL_POL_0450)
    # Rule_E_MAP_Trend: MAP <= 75 OR MAP_delta_3h <= -3
    processed_df["MAP_delta_3h"] = processed_df.groupby("Patient_ID")["MAP"].diff(3).fillna(0.0)
    gate = ((processed_df["MAP"] <= 75.0) | (processed_df["MAP_delta_3h"] <= -3.0)).astype(int)
    processed_df["gate"] = gate

    processed_df["eff_pred"] = np.where(processed_df["gate"] == 1, processed_df["pred"], 0.0)
    gated_auroc = float(roc_auc_score(y_ext, processed_df["eff_pred"].values))
    gated_auprc = float(average_precision_score(y_ext, processed_df["eff_pred"].values))
    gated_brier = float(brier_score_loss(y_ext, processed_df["eff_pred"].values))

    # Evaluate Patient Sensitivity under Frozen Policy (tau_screening = 0.015, p = 3)
    tau_scr = 0.015
    tau_conf = 0.300
    p_win = 3

    patient_results = []
    for pid, pgroup in processed_df.groupby("Patient_ID"):
        has_sepsis = (pgroup["SepsisLabel"].max() == 1) or (pgroup["S_next"].max() == 1)
        
        # Screening alerts
        scr_raw = (pgroup["pred"] >= tau_scr).astype(int)
        scr_pers = (scr_raw.rolling(window=p_win, min_periods=p_win).sum() == p_win).astype(int)
        
        # Confirmation alerts
        conf_raw = (pgroup["eff_pred"] >= tau_conf).astype(int)
        conf_pers = (conf_raw.rolling(window=p_win, min_periods=p_win).sum() == p_win).astype(int)

        detected_scr = scr_pers.max() == 1
        detected_conf = conf_pers.max() == 1

        patient_results.append({
            "Patient_ID": pid,
            "has_sepsis": has_sepsis,
            "detected_scr": detected_scr,
            "detected_conf": detected_conf
        })

    p_df = pd.DataFrame(patient_results)
    sepsis_pts = p_df[p_df["has_sepsis"]]
    n_sepsis_pts = len(sepsis_pts)
    det_scr_cnt = sepsis_pts["detected_scr"].sum()
    det_conf_cnt = sepsis_pts["detected_conf"].sum()

    patient_sens_scr = det_scr_cnt / max(1, n_sepsis_pts)
    patient_sens_conf = det_conf_cnt / max(1, n_sepsis_pts)

    elapsed = time.time() - start_time

    # SAVE RESULTS
    results = {
        "dataset_name": "PhysioNet 2019 Reserved External Validation (6,000 Patients)",
        "n_patients": n_patients,
        "n_windows": n_windows,
        "n_sepsis_patients": n_sepsis_pts,
        "raw_auroc": auroc,
        "raw_auprc": auprc,
        "raw_brier": brier,
        "gated_auroc": gated_auroc,
        "gated_auprc": gated_auprc,
        "gated_brier": gated_brier,
        "patient_screening_sensitivity": patient_sens_scr,
        "patient_confirmation_sensitivity": patient_sens_conf,
        "execution_time_sec": round(elapsed, 2)
    }

    output_path = "FINAL_BIOMARKERX/external/RESERVED_6K_EXTERNAL_VALIDATION_RESULTS.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print("\n=========================================================================")
    print("EXTERNAL VALIDATION RESULTS (6,000 RESERVED PATIENTS)")
    print("=========================================================================")
    print(f"Cohort Size                    : {n_patients:,} Patients ({n_sepsis_pts} Sepsis Episodes)")
    print(f"Raw Model AUROC                : {auroc:.4f}")
    print(f"Raw Model AUPRC                : {auprc:.4f}")
    print(f"Raw Model Brier Score          : {brier:.4f}")
    print(f"Gated Effective AUROC          : {gated_auroc:.4f}")
    print(f"Patient Screening Sensitivity  : {patient_sens_scr*100:.2f}% ({det_scr_cnt}/{n_sepsis_pts})")
    print(f"Patient Confirmation Sensitivity: {patient_sens_conf*100:.2f}% ({det_conf_cnt}/{n_sepsis_pts})")
    print(f"Execution Completed In         : {elapsed:.2f} seconds")
    print(f"Saved Results To               : {output_path}")
    print("=========================================================================\n", flush=True)

if __name__ == "__main__":
    run_external_validation_6k()
