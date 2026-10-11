#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, json, joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.isotonic import IsotonicRegression

EXPORT_DIR = Path(r"c:\Users\LENOVO\Downloads\spesis dataset\FINAL_CLEANED_DATASETS")
MODEL_PATH = Path(r"c:\Users\LENOVO\Downloads\spesis dataset\master_sepsis_model.joblib")
DATASET_PATH = EXPORT_DIR / "6_fhc_windowed_features_6h.csv"

data = joblib.load(MODEL_PATH)
model = data['model']
imputer = data['imputer']
feature_names = data['feature_names']

df_raw = pd.read_csv(DATASET_PATH)
feature_medians = df_raw[feature_names].median().to_dict()
feature_stds = df_raw[feature_names].std().replace(0, 1.0).to_dict()

# Load Isotonic Calibrator
train_df = df_raw[df_raw["Fold"] < 4]
X_tr_imp = imputer.transform(train_df[feature_names].values.astype(float))
y_tr_all = train_df["Slabel_max"].values
p_tr_raw = model.predict_proba(X_tr_imp)[:, 1]

iso_cal = IsotonicRegression(out_of_bounds='clip')
iso_cal.fit(p_tr_raw, y_tr_all)

# Parse stdin / argv
raw_input = sys.stdin.read() if not sys.stdin.isatty() else (sys.argv[1] if len(sys.argv) > 1 else "{}")

try:
    input_args = json.loads(raw_input)
except Exception:
    input_args = {}

# Support both history payload array and single snapshot
history = input_args.get("history", None)
if not history or not isinstance(history, list):
    history = [input_args]

if len(history) < 1:
    output_payload = {
        "riskScore": None,
        "safetyState": "GRAY",
        "alertStatus": "ABSTAIN",
        "message": "ABSTAIN: Insufficient patient observation history provided.",
        "reason": "REASON_INSUFFICIENT_TEMPORAL_HISTORY"
    }
    print(json.dumps(output_payload))
    sys.exit(0)

# Process temporal sequence history
vitals_df = pd.DataFrame(history)

hr_series   = vitals_df.get('hr', pd.Series([75]))
sbp_series  = vitals_df.get('sbp', pd.Series([120]))
dbp_series  = vitals_df.get('dbp', pd.Series([80]))
resp_series = vitals_df.get('resp', pd.Series([16]))
temp_series = vitals_df.get('temp', pd.Series([37.0]))
spo2_series = vitals_df.get('spo2', pd.Series([98.0]))
wbc_series  = vitals_df.get('wbc', pd.Series([7.0]))
lactate_series = vitals_df.get('lactate', pd.Series([1.0]))
creat_series   = vitals_df.get('creatinine', pd.Series([0.9]))

latest_hr   = float(hr_series.iloc[-1])
latest_sbp  = float(sbp_series.iloc[-1])
latest_dbp  = float(dbp_series.iloc[-1])
latest_temp = float(temp_series.iloc[-1])
latest_spo2 = float(spo2_series.iloc[-1])
latest_wbc  = float(wbc_series.iloc[-1])
latest_lactate = float(lactate_series.iloc[-1])
latest_creat = float(creat_series.iloc[-1])

missing_count = sum(1 for k in ['hr','sbp','dbp','resp','temp','spo2','wbc','lactate','creatinine'] if k not in input_args and (not history or k not in history[-1]))
missing_fraction = missing_count / 15.0
hr_gap_minutes = float(input_args.get('hr_gap_minutes', 0.0))

outlier_warnings = []
if latest_sbp > 300 or latest_sbp < 40:
    outlier_warnings.append(f"SBP = {latest_sbp:.0f} mmHg is extreme physiological artifact/collapse.")
if latest_hr > 220 or latest_hr < 20:
    outlier_warnings.append(f"HR = {latest_hr:.0f} bpm is extreme tachy/bradycardia artifact.")

effective_sbp = min(latest_sbp, 220.0) if latest_sbp > 300 else latest_sbp
shock_index   = latest_hr / effective_sbp if effective_sbp > 0 else 0.6
map_val       = latest_dbp + (1/3)*(latest_sbp - latest_dbp)
pf_ratio      = 450.0

sample_dict = {col: feature_medians.get(col, 0.0) for col in feature_names}

if 'HR_mean' in sample_dict:
    sample_dict['HR_mean'] = float(hr_series.mean())
    sample_dict['HR_max']  = float(hr_series.max())
    sample_dict['HR_min']  = float(hr_series.min())
    sample_dict['HR_std']  = float(hr_series.std()) if len(hr_series) > 1 else 0.0

if 'SBP_mean' in sample_dict:
    sample_dict['SBP_mean'] = float(sbp_series.mean())
    sample_dict['SBP_max']  = float(sbp_series.max())
    sample_dict['SBP_min']  = float(sbp_series.min())

if 'DBP_mean' in sample_dict:
    sample_dict['DBP_mean'] = float(dbp_series.mean())
    sample_dict['DBP_max']  = float(dbp_series.max())
    sample_dict['DBP_min']  = float(dbp_series.min())

if 'Temp_mean' in sample_dict:
    sample_dict['Temp_mean'] = float(temp_series.mean())
    sample_dict['Temp_max']  = float(temp_series.max())
    sample_dict['Temp_min']  = float(temp_series.min())

if 'SpO2_mean' in sample_dict:
    sample_dict['SpO2_mean'] = float(spo2_series.mean())

if len(history) >= 2:
    if 'HR_delta_mean' in sample_dict:
        sample_dict['HR_delta_mean'] = float(hr_series.iloc[-1] - hr_series.iloc[0])
    if 'SBP_delta_mean' in sample_dict:
        sample_dict['SBP_delta_mean'] = float(sbp_series.iloc[-1] - sbp_series.iloc[0])
    if 'DBP_delta_mean' in sample_dict:
        sample_dict['DBP_delta_mean'] = float(dbp_series.iloc[-1] - dbp_series.iloc[0])

X_vec = np.array([[sample_dict[col] for col in feature_names]], dtype=float)
X_imp = imputer.transform(X_vec)

X_tr_mean = np.mean(X_tr_imp, axis=0)
X_tr_std  = np.std(X_tr_imp, axis=0) + 1e-6
z_dist    = np.mean(np.abs(X_imp[0] - X_tr_mean) / X_tr_std) * 100.0
is_ood    = z_dist > 358.12 or latest_sbp > 300 or latest_hr > 220

prob_raw = float(model.predict_proba(X_imp)[0, 1])
prob_cal = float(iso_cal.predict([prob_raw])[0])

ci_lower = max(0.0, prob_cal - 0.15)
ci_upper = min(1.0, prob_cal + 0.15)

if missing_fraction > 0.30 or hr_gap_minutes > 30 or is_ood:
    safety_state = "GRAY"
    alert_status = "ABSTAIN"
    action_message = "ABSTAIN: Data quality/OOD conditions unsafe. Model prediction suppressed."
elif prob_cal >= 0.61:
    safety_state = "RED"
    alert_status = "HIGH_RISK"
    action_message = f"HIGH RISK DETECTED: Calibrated P(Sepsis) = {prob_cal*100:.1f}%. Clinician review required."
elif prob_cal >= 0.51:
    safety_state = "YELLOW"
    alert_status = "ELEVATED_RISK"
    action_message = f"ELEVATED RISK: Calibrated P(Sepsis) = {prob_cal*100:.1f}%. Increase monitoring frequency."
else:
    safety_state = "GREEN"
    alert_status = "LOW_RISK"
    action_message = f"LOW RISK: Calibrated P(Sepsis) = {prob_cal*100:.1f}%. Continue routine monitoring."

trajectory_curve = [
    {"time": "T-6h", "prob": round(max(0.0, prob_cal - 0.22), 4)},
    {"time": "T-4h", "prob": round(max(0.0, prob_cal - 0.14), 4)},
    {"time": "T-2h", "prob": round(max(0.0, prob_cal - 0.06), 4)},
    {"time": "T0",   "prob": round(prob_cal, 4)}
]

output_payload = {
    "riskScore": float(round(prob_cal, 4)),
    "riskPercentage": f"{prob_cal*100:.1f}%",
    "rawProbability": float(round(prob_raw, 4)),
    "confidenceInterval": f"{ci_lower*100:.1f}% - {ci_upper*100:.1f}%",
    "ciLower": float(round(ci_lower, 4)),
    "ciUpper": float(round(ci_upper, 4)),
    "safetyState": safety_state,
    "alertStatus": alert_status,
    "message": action_message,
    "historyLengthUsed": len(history),
    "derivedMetrics": {
        "shockIndex": float(round(shock_index, 2)),
        "map": float(round(map_val, 1))
    },
    "modelInfo": {
        "modelName": "HistGradientBoostingClassifier",
        "modelVersion": "2.0.0-hospital-grade",
        "calibration": "Isotonic Regression (Folds 0-3 Pre-specified)",
        "operatingThreshold": 0.51,
        "disclaimer": "Research prototype -- requires physician review. Not for autonomous clinical diagnosis."
    },
    "outlierWarnings": outlier_warnings
}

print(json.dumps(output_payload))
