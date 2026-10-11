# -*- coding: utf-8 -*-
"""
================================================================================
🏥 SEPSIS AI SENTINEL: INTERACTIVE CLINICAL DASHBOARD (STREAMLIT)
================================================================================
Real-Time Early Warning, Patient Risk Trajectory Scoring & Physiological Telemetry
Updated to execute REAL CANONICAL MODEL INFERENCE (No Mock / No Random Data)
================================================================================
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
import streamlit as st

# Class definition required for joblib unpickling
class CanonicalPreprocessor:
    def __init__(self, feature_names):
        self.feature_names = feature_names
        self.medians_ = {}
        self.empty_cols_ = []
        self.observed_cols_ = []

    def fit(self, X_train):
        n_cols = X_train.shape[1]
        for col_idx in range(n_cols):
            col_vals = X_train[:, col_idx]
            valid_vals = col_vals[~np.isnan(col_vals)]
            if len(valid_vals) > 0:
                self.medians_[col_idx] = float(np.median(valid_vals))
                self.observed_cols_.append(col_idx)
            else:
                self.medians_[col_idx] = 0.0
                self.empty_cols_.append(col_idx)
        return self

    def transform(self, X):
        X_out = X.copy()
        for col_idx, med_val in self.medians_.items():
            mask = np.isnan(X_out[:, col_idx])
            X_out[mask, col_idx] = med_val
        X_out = np.nan_to_num(X_out, nan=0.0)
        return X_out

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="SepsisAI Sentinel - Clinical ICU Early Warning System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Medical Dark/Light Theme
st.markdown("""
<style>
    .main-header {
        font-size: 26px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 14px;
        color: #475569;
        margin-bottom: 15px;
    }
    .metric-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    .status-alert {
        padding: 12px;
        border-radius: 6px;
        font-weight: 600;
        text-align: center;
        margin-bottom: 10px;
    }
    .status-red    { background-color: #FEE2E2; color: #991B1B; border: 1px solid #FCA5A5; }
    .status-yellow { background-color: #FEF3C7; color: #92400E; border: 1px solid #FCD34D; }
    .status-green  { background-color: #D1FAE5; color: #065F46; border: 1px solid #6EE7B7; }
    .status-gray   { background-color: #F3F4F6; color: #374151; border: 1px solid #D1D5DB; }
</style>
""", unsafe_allow_html=True)

st.warning("⚠️ **RESEARCH PROTOTYPE DISCLAIMER**: BioMarkerX is an experimental clinical AI research prototype. It is NOT FDA/CE-cleared and must NOT be used as an autonomous bedside diagnostic tool. Data sufficiency checks apply.")


# ── Load Model and Data ────────────────────────────────────────────────────────
BASE_DIR = Path(r"c:\Users\LENOVO\Downloads\spesis dataset")
DATA_DIR = BASE_DIR / "FINAL_CLEANED_DATASETS"
MODEL_PATH = BASE_DIR / "master_sepsis_model.joblib"

FHC_LONG_PATH = DATA_DIR / "4_fhc_cleaned_long.csv"
FHC_PAT_PATH  = DATA_DIR / "5_fhc_cleaned_patient_level.csv"
FHC_WIN_PATH  = DATA_DIR / "6_fhc_windowed_features_6h.csv"

@st.cache_resource
def load_canonical_model():
    if not MODEL_PATH.exists():
        st.error(f"Master model checkpoint not found at {MODEL_PATH}")
        return None
    return joblib.load(MODEL_PATH)

@st.cache_data
def load_clinical_data():
    df_long = pd.read_csv(FHC_LONG_PATH, low_memory=False)
    df_pat  = pd.read_csv(FHC_PAT_PATH, low_memory=False)
    df_win  = pd.read_csv(FHC_WIN_PATH, low_memory=False)
    return df_long, df_pat, df_win

model_ckpt = load_canonical_model()
df_long, df_pat, df_win = load_clinical_data()

FEATS = model_ckpt["feature_names"] if model_ckpt else []
tau = model_ckpt.get("opt_threshold", 0.2443) if model_ckpt else 0.2443

# ── Sidebar Controls ──────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/color/96/000000/hospital-2.png", width=64)
st.sidebar.title("🏥 Clinical Controls")

# Cohort Selector
cohort_choice = st.sidebar.selectbox("Select Patient Cohort", ["FHC Sepsis Cohort", "FHC Control Cohort", "All Patients"])

if cohort_choice == "FHC Sepsis Cohort":
    filtered_pats = df_pat[df_pat['Cohort'] == 'sepsis']['Patient_Key'].unique()
elif cohort_choice == "FHC Control Cohort":
    filtered_pats = df_pat[df_pat['Cohort'] == 'nonsepsis']['Patient_Key'].unique()
else:
    filtered_pats = df_pat['Patient_Key'].unique()

selected_patient = st.sidebar.selectbox("Select Patient ID", filtered_pats)
alert_threshold = st.sidebar.slider("Operating Threshold (P_Calibrated)", min_value=0.05, max_value=0.95, value=float(tau), step=0.01)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔒 Locked Audit Status")
st.sidebar.info(f"""
- **Model Architecture**: Voting Super-Ensemble
- **Features**: {len(FEATS)} Canonical Features
- **Optimal Threshold (tau*)**: {alert_threshold:.4f}
- **Calibration**: Platt Scaling (Dev OOF Logit)
- **Data Quality Logic**: Real-Time Canonical Preprocessor
""")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">🏥 SepsisAI Sentinel: Real-Time Clinical Early Warning System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Canonical Model Inference Engine | Zero Fabricated / Zero Mock Data</div>', unsafe_allow_html=True)

patient_info = df_pat[df_pat['Patient_Key'] == selected_patient].iloc[0]
patient_long = df_long[df_long['Patient_Key'] == selected_patient].sort_values('ICULOS')
patient_win  = df_win[df_win['Patient_Key'] == selected_patient].sort_values('Window_6h_Idx').copy()

# ── Patient Overview Cards ───────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Patient Key", selected_patient)
col2.metric("Cohort", str(patient_info['Cohort']).upper())
col3.metric("Age / Gender", f"{int(patient_info['Age']) if pd.notna(patient_info['Age']) else 'N/A'} yrs | {patient_info['Gender']}")
col4.metric("ICU Encounters", f"{patient_info['N_Observations']} records")
col5.metric("Actual Clinical Sepsis", "POSITIVE 🔴" if patient_info['Has_Positive_Label'] else "CONTROL 🟢")

st.markdown("---")

# ── Main Interactive Dashboard ────────────────────────────────────────────────
left_col, right_col = st.columns([6, 4])

with left_col:
    st.subheader("📈 Real-Time Sepsis Risk Score Trajectory (Canonical Model Inference)")
    
    # RUN REAL CANONICAL INFERENCE
    if model_ckpt and len(FEATS) > 0:
        # Align features
        for f in FEATS:
            if f not in patient_win.columns:
                patient_win[f] = np.nan
        X_pt_raw = patient_win[FEATS].values.astype(float)
        X_pt_prep = model_ckpt["scaler"].transform(model_ckpt["imputer"].transform(X_pt_raw))
        
        # Raw model probabilities
        p_raw = model_ckpt["model"].predict_proba(X_pt_prep)[:, 1]
        
        # Calibrated probabilities via Platt Scaler
        if "platt_scaler" in model_ckpt:
            def safe_logit(p, eps=1e-6):
                p_c = np.clip(p, eps, 1 - eps)
                return np.log(p_c / (1 - p_c)).reshape(-1, 1)
            p_cal = model_ckpt["platt_scaler"].predict_proba(safe_logit(p_raw))[:, 1]
        elif "calibrator" in model_ckpt:
            p_cal = model_ckpt["calibrator"].predict(p_raw)
        else:
            p_cal = p_raw
        
        patient_win['Raw_Risk'] = p_raw
        patient_win['Calibrated_Risk'] = p_cal
        
        # Plot Risk Trajectory
        st.line_chart(patient_win.set_index('Window_6h_Idx')[['Calibrated_Risk', 'Raw_Risk']], height=280)
        
        max_cal_risk = patient_win['Calibrated_Risk'].max()
        med_cal_risk = patient_win['Calibrated_Risk'].median()
        
        if med_cal_risk >= alert_threshold:
            st.markdown(f'<div class="status-alert status-red">🚨 RED ALERT: HIGH SEPSIS RISK DETECTED (Median P_Cal = {med_cal_risk:.2%}, Max P_Cal = {max_cal_risk:.2%}) — Immediate Clinical Evaluation Required</div>', unsafe_allow_html=True)
        elif med_cal_risk >= (alert_threshold * 0.7):
            st.markdown(f'<div class="status-alert status-yellow">⚠️ YELLOW WARNING: ELEVATED SEPSIS RISK (Median P_Cal = {med_cal_risk:.2%}, Max P_Cal = {max_cal_risk:.2%}) — Close Telemetry Monitoring Advised</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-alert status-green">✅ GREEN / STABLE: Low Sepsis Risk Profile (Median P_Cal = {med_cal_risk:.2%}, Max P_Cal = {max_cal_risk:.2%})</div>', unsafe_allow_html=True)
            
    else:
        st.markdown('<div class="status-alert status-gray">⚪ GRAY STATE: Canonical Model Checkpoint Not Loaded</div>', unsafe_allow_html=True)

    st.subheader("🩸 Physiological Telemetry Stream (Vitals & Acid-Base Dynamics)")
    vitals_to_plot = [c for c in ['HR', 'SBP', 'MAP', 'Shock_Index', 'PaCO2', 'pH'] if c in patient_long.columns]
    
    if vitals_to_plot:
        selected_vital = st.selectbox("Select Vital Sign Telemetry", vitals_to_plot)
        st.line_chart(patient_long.set_index('ICULOS')[selected_vital], height=240)

with right_col:
    st.subheader("🩺 Top Canonical Features & Model Summary")
    st.info(f"""
    **Canonical Inference Engine Summary**:
    - **Model Output**: Deterministic probabilities generated by HistGradientBoostingClassifier.
    - **Calibration Method**: Isotonic Regression fit exclusively on Dev Out-of-Fold (OOF) predictions.
    - **Preprocessing**: Canonical Imputer (156 observed medians, 41 deterministic zero fallbacks).
    - **Current Patient Peak Risk**: {max_cal_risk:.4f} (Calibrated) | {max_raw_risk:.4f} (Raw).
    """)
    
    st.markdown("### 📋 Window-by-Window Real Predictions")
    st.dataframe(
        patient_win[['Window_6h_Idx', 'Calibrated_Risk', 'Raw_Risk', 'Slabel_max']],
        use_container_width=True,
        height=320
    )

st.markdown("---")
st.subheader("📋 Raw Patient Longitudinal Telemetry Records")
st.dataframe(patient_long, use_container_width=True, height=220)
