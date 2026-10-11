#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
MASTER END-TO-END CLINICAL SEPSIS AI PIPELINE (FIXED)
================================================================================
Author: AI Critical Care Research Group
Dataset: Fuwai Hospital China (FHC) + US MIMIC-IV ICU Database

This master script executes the complete 6-stage clinical ML pipeline:
1. RAW DATA LOADING & FORMAT REMEDIATION (European comma decimal fix, PID collision fix)
2. MULTI-COHORT HARMONIZATION (FHC + MIMIC-IV alignment, synthetic isolation)
3. CLINICAL FEATURE ENGINEERING (Shock Index, MAP, De Ritis Ratio, BUN/Cr, Vital Deltas)
4. 6-HOUR TEMPORAL WINDOWING & LEAD-TIME TARGET FORMULATION (Instantaneous & T-6h Prior)
5. LEAK-FREE 5-FOLD STRATIFIED GROUPKFOLD CROSS-VALIDATION
6. MODEL TRAINING, EVALUATION & CLINICAL EXPLAINABILITY (GBDT, Random Forest, MLP, Logistic)
================================================================================
"""

import os
import sys
import json
import warnings
from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    roc_auc_score, average_precision_score, accuracy_score, f1_score,
    recall_score, precision_score, confusion_matrix
)

warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

# ── 0. PATH DEFINITIONS ───────────────────────────────────────────────────────
BASE_DIR   = Path(r"c:\Users\LENOVO\Downloads\spesis dataset")
FHC_DIR    = BASE_DIR / "FHC_Dataset" / "FHC_Dataset"
ARCHIVE_DIR= BASE_DIR / "archive (3)"
MIMIC_XLSX = BASE_DIR / "Sepsis" / "Sepsis" / "mimiciv20230306.xlsx"
SYNTH_CSV  = ARCHIVE_DIR / "sepsis_icu_synthetic.csv"

OUT_DIR    = BASE_DIR / "FINAL_CLEANED_DATASETS"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print("="*80)
print("STARTING MASTER END-TO-END SEPSIS AI PIPELINE")
print("="*80)

# ==============================================================================
# STAGE 1: RAW DATA LOADING & EUROPEAN COMMA-DECIMAL REMEDIATION
# ==============================================================================
print("\n--- STAGE 1: Cleaning FHC Sepsis Dataset ---")

def load_and_clean_fhc_file(filepath, cohort):
    filename = filepath.name
    pid = filename.replace(f"{cohort}_", "").replace(".csv", "")
    patient_key = f"{cohort}_{pid}"
    
    df_raw = pd.read_csv(filepath, low_memory=False)
    df_clean = pd.DataFrame(index=df_raw.index)
    
    df_clean['Dataset_Source'] = 'FHC'
    df_clean['Cohort']         = cohort
    df_clean['Original_PID']   = str(pid)
    df_clean['Patient_Key']    = patient_key

    col_rename = {
        'Troponinl': 'Troponin',
        'urine output': 'Urine',
        'ID': 'Source_ID'
    }
    
    for col in df_raw.columns:
        clean_col_name = col_rename.get(col, col)
        val_series = df_raw[col]
        
        if val_series.dtype == object:
            val_converted = val_series.astype(str).str.replace(',', '.', regex=False)
            numeric_attempt = pd.to_numeric(val_converted, errors='coerce')
            n_non_null = val_series.notna().sum()
            n_parsed   = numeric_attempt.notna().sum()
            if n_non_null > 0 and (n_parsed / n_non_null >= 0.80):
                df_clean[clean_col_name] = numeric_attempt
            else:
                df_clean[clean_col_name] = val_series
        else:
            df_clean[clean_col_name] = pd.to_numeric(val_series, errors='coerce')

    if 'ICULOS' in df_clean.columns:
        df_clean['Is_Pre_ICU'] = (df_clean['ICULOS'] < 0).astype(int)
    
    return df_clean

sep_files  = sorted((FHC_DIR / "sepsis").glob("*.csv"))
nons_files = sorted((FHC_DIR / "nonsepsis").glob("*.csv"))

fhc_records = []
for fp in sep_files:
    fhc_records.append(load_and_clean_fhc_file(fp, "sepsis"))
for fp in nons_files:
    fhc_records.append(load_and_clean_fhc_file(fp, "nonsepsis"))

fhc_long_df = pd.concat(fhc_records, ignore_index=True, sort=False)

# Flag zero-label sepsis patients
sepsis_keys = fhc_long_df[fhc_long_df['Cohort'] == 'sepsis']['Patient_Key'].unique()
zero_label_keys = set()
for key in sepsis_keys:
    pat_data = fhc_long_df[fhc_long_df['Patient_Key'] == key]
    if 'Slabel' in pat_data.columns:
        if not (pat_data['Slabel'] == 1).any():
            zero_label_keys.add(key)

fhc_long_df['Has_Positive_Label_Flag'] = ~fhc_long_df['Patient_Key'].isin(zero_label_keys)

fhc_long_path = OUT_DIR / "4_fhc_cleaned_long.csv"
fhc_long_df.to_csv(fhc_long_path, index=False)
print(f"✅ Exported 4_fhc_cleaned_long.csv ({len(fhc_long_df):,} rows × {len(fhc_long_df.columns)} cols)")

# Generate FHC Patient Summary
patient_summaries = []
for pkey, pdf in fhc_long_df.groupby('Patient_Key'):
    cohort = pdf['Cohort'].iloc[0]
    pid    = pdf['Original_PID'].iloc[0]
    slabel_vals = pdf['Slabel'].dropna() if 'Slabel' in pdf.columns else pd.Series()
    min_iculos  = pdf['ICULOS'].min() if 'ICULOS' in pdf.columns else np.nan
    max_iculos  = pdf['ICULOS'].max() if 'ICULOS' in pdf.columns else np.nan
    
    patient_summaries.append({
        'Patient_Key': pkey,
        'Cohort': cohort,
        'Original_PID': pid,
        'N_Observations': len(pdf),
        'Has_Positive_Label': bool((slabel_vals == 1).any()),
        'Min_ICULOS_min': min_iculos,
        'Max_ICULOS_min': max_iculos,
        'Age': pdf['Age'].dropna().iloc[0] if 'Age' in pdf.columns and pdf['Age'].notna().any() else np.nan,
        'Gender': pdf['Gender'].dropna().iloc[0] if 'Gender' in pdf.columns and pdf['Gender'].notna().any() else np.nan
    })

fhc_patient_df = pd.DataFrame(patient_summaries)
fhc_pat_path = OUT_DIR / "5_fhc_cleaned_patient_level.csv"
fhc_patient_df.to_csv(fhc_pat_path, index=False)
print(f"✅ Exported 5_fhc_cleaned_patient_level.csv ({len(fhc_patient_df)} patients)")

# ==============================================================================
# STAGE 2: MULTI-COHORT HARMONIZATION & SYNTHETIC ISOLATION
# ==============================================================================
print("\n--- STAGE 2: Processing MIMIC-IV & Building Multi-Cohort Master ---")

xl_file = pd.ExcelFile(MIMIC_XLSX)
mimic_dfs = []
for sheet in xl_file.sheet_names:
    sdf = xl_file.parse(sheet)
    sdf['Sheet_Name'] = sheet
    mimic_dfs.append(sdf)

mimic_combined = pd.concat(mimic_dfs, ignore_index=True, sort=False)
mimic_combined['Dataset_Source'] = 'MIMIC_IV'
mimic_combined['Cohort']         = 'sepsis'
mimic_combined['Slabel']         = 1

mimic_rename = {
    'subject_id': 'Original_PID',
    'anchor_age': 'Age',
    'gender': 'Gender',
    'temp_celsius_mean': 'Temp',
    'hr_mean': 'HR',
    'sbp_mean': 'SBP',
    'dbp_mean': 'DBP',
    'spo2_mean': 'SaO2',
    'wbc': 'WBC',
    'platelet_count': 'Platelets',
    'creatinine': 'Creatinine',
    'bilirubin_total': 'Bilirubin_total',
    'glucose': 'GLU',
    'ph_arterial': 'pH',
    'sodium': 'Na',
    'potassium': 'K',
    'chloride': 'CL',
    'bicarbonate': 'HCO3',
    'hematocrit': 'HCT',
    'hemoglobin': 'HGB',
    'inr': 'INR',
    'lactate_mmol': 'Lactate',
    'icu_los_hours': 'ICULOS_hours'
}

for old_col, new_col in mimic_rename.items():
    if old_col in mimic_combined.columns:
        mimic_combined.rename(columns={old_col: new_col}, inplace=True)

if 'ICULOS_hours' in mimic_combined.columns and 'ICULOS' not in mimic_combined.columns:
    mimic_combined['ICULOS'] = mimic_combined['ICULOS_hours'] * 60

if 'Original_PID' in mimic_combined.columns:
    mimic_combined['Patient_Key'] = 'MIMIC_' + mimic_combined['Original_PID'].astype(str)

mimic_long_path = OUT_DIR / "8_mimiciv_cleaned_long.csv"
mimic_combined.to_csv(mimic_long_path, index=False)
print(f"✅ Exported 8_mimiciv_cleaned_long.csv ({len(mimic_combined):,} rows × {len(mimic_combined.columns)} cols)")

# Clean & Isolate Synthetic Data
synth_raw = pd.read_csv(SYNTH_CSV, low_memory=False)
synth_raw['Dataset_Source'] = 'SYNTHETIC_SANDBOX'
synth_path = OUT_DIR / "9_synthetic_sandbox_cleaned.csv"
synth_raw.to_csv(synth_path, index=False)
print(f"✅ Exported 9_synthetic_sandbox_cleaned.csv ({len(synth_raw):,} rows)")

# Build Harmonized Multi-Cohort Master Dataset
shared_cols = [
    'Dataset_Source', 'Cohort', 'Patient_Key', 'Original_PID', 'ICULOS', 'Slabel',
    'Temp', 'HR', 'SBP', 'DBP', 'HCT', 'HGB', 'WBC', 'Platelets',
    'K', 'Na', 'CL', 'pH', 'AST', 'ALT', 'Creatinine', 'Bilirubin_total',
    'INR', 'PT', 'BEb', 'PaCO2', 'PO2', 'SaO2', 'HCO3', 'GLU', 'Age', 'Gender'
]

fhc_subset = fhc_long_df.copy()
fhc_subset.rename(columns={'Bilirubin total': 'Bilirubin_total'}, inplace=True)

fhc_aligned = pd.DataFrame()
for col in shared_cols:
    fhc_aligned[col] = fhc_subset[col] if col in fhc_subset.columns else np.nan

mimic_aligned = pd.DataFrame()
for col in shared_cols:
    mimic_aligned[col] = mimic_combined[col] if col in mimic_combined.columns else np.nan

master_df = pd.concat([fhc_aligned, mimic_aligned], ignore_index=True, sort=False)
master_path = OUT_DIR / "1_harmonized_sepsis_master.csv"
master_df.to_csv(master_path, index=False)
print(f"✅ Exported 1_harmonized_sepsis_master.csv ({len(master_df):,} rows × {len(master_df.columns)} cols)")

# ==============================================================================
# STAGE 3: CLINICAL FEATURE ENGINEERING & VITAL DELTAS
# ==============================================================================
print("\n--- STAGE 3: Engineering Derived Physiological Signals ---")

def engineer_features(df):
    df_feat = df.copy()
    
    if 'HR' in df_feat.columns and 'SBP' in df_feat.columns:
        df_feat['Shock_Index'] = df_feat['HR'] / df_feat['SBP'].replace(0, np.nan)
    if 'SBP' in df_feat.columns and 'DBP' in df_feat.columns:
        df_feat['Pulse_Pressure'] = df_feat['SBP'] - df_feat['DBP']
        df_feat['MAP'] = df_feat['DBP'] + (1.0 / 3.0) * (df_feat['SBP'] - df_feat['DBP'])
    if 'AST' in df_feat.columns and 'ALT' in df_feat.columns:
        df_feat['De_Ritis_Ratio'] = df_feat['AST'] / df_feat['ALT'].replace(0, np.nan)
    if 'BUN' in df_feat.columns and 'Creatinine' in df_feat.columns:
        df_feat['BUN_Creatinine_Ratio'] = df_feat['BUN'] / df_feat['Creatinine'].replace(0, np.nan)
    if 'HGB' in df_feat.columns and 'HCT' in df_feat.columns:
        df_feat['HGB_HCT_Ratio'] = df_feat['HGB'] / df_feat['HCT'].replace(0, np.nan)

    vital_cols = [c for c in ['HR', 'Temp', 'SBP', 'DBP', 'Shock_Index', 'MAP'] if c in df_feat.columns]
    df_feat = df_feat.sort_values(['Patient_Key', 'ICULOS']) if 'ICULOS' in df_feat.columns else df_feat.sort_values('Patient_Key')
    
    for vc in vital_cols:
        df_feat[f"{vc}_delta"] = df_feat.groupby('Patient_Key')[vc].diff()

    return df_feat

fhc_eng    = engineer_features(fhc_long_df)
master_eng = engineer_features(master_df)

print(f"✅ Engineered FHC features: {len(fhc_eng.columns)} columns")
print(f"✅ Engineered Harmonized Master features: {len(master_eng.columns)} columns")

# ==============================================================================
# STAGE 4: 6-HOUR TIME-SERIES WINDOWING & LEAD-TIME LABELS
# ==============================================================================
print("\n--- STAGE 4: Building 6-Hour Temporal Window Aggregations ---")

def build_6h_windows(df_eng):
    df_win = df_eng.copy()
    if 'ICULOS' in df_win.columns and df_win['ICULOS'].notna().any():
        iculos_filled = df_win.groupby('Patient_Key')['ICULOS'].ffill().bfill().fillna(0)
        df_win['Window_6h_Idx'] = np.floor(iculos_filled / 360.0).astype('Int64')
    else:
        df_win['Window_6h_Idx'] = (df_win.groupby('Patient_Key').cumcount() // 6).astype('Int64')

    df_win['Window_6h_Idx'] = df_win['Window_6h_Idx'].fillna(0)

    numeric_cols = [
        c for c in df_win.select_dtypes(include=[np.number]).columns
        if c not in ['Slabel', 'Is_Pre_ICU', 'Has_Positive_Label_Flag', 'Window_6h_Idx']
    ]

    agg_dict = {col: ['mean', 'min', 'max', 'std'] for col in numeric_cols}
    if 'Slabel' in df_win.columns:
        agg_dict['Slabel'] = 'max'
    if 'Dataset_Source' in df_win.columns:
        agg_dict['Dataset_Source'] = 'first'
    if 'Cohort' in df_win.columns:
        agg_dict['Cohort'] = 'first'
    if 'Original_PID' in df_win.columns:
        agg_dict['Original_PID'] = 'first'

    grouped = df_win.groupby(['Patient_Key', 'Window_6h_Idx']).agg(agg_dict)
    
    flattened_cols = []
    for col_tuple in grouped.columns:
        if isinstance(col_tuple, tuple):
            base_col, stat = col_tuple
            if stat in ['mean', 'min', 'max', 'std']:
                flattened_cols.append(f"{base_col}_{stat}")
            elif stat == 'max' and base_col == 'Slabel':
                flattened_cols.append('Slabel_max')
            else:
                flattened_cols.append(base_col)
        else:
            flattened_cols.append(col_tuple)
            
    grouped.columns = flattened_cols
    grouped = grouped.reset_index()

    if 'Slabel_max' in grouped.columns:
        grouped = grouped.sort_values(['Patient_Key', 'Window_6h_Idx'])
        grouped['Slabel_lead_6h'] = grouped.groupby('Patient_Key')['Slabel_max'].shift(-1)
        grouped['Slabel_lead_12h'] = grouped.groupby('Patient_Key')['Slabel_max'].shift(-2)

    return grouped

fhc_win6h    = build_6h_windows(fhc_eng)
master_win6h = build_6h_windows(master_eng)

fhc_win_path    = OUT_DIR / "6_fhc_windowed_features_6h.csv"
master_win_path = OUT_DIR / "2_harmonized_windowed_features_6h.csv"

fhc_win6h.to_csv(fhc_win_path, index=False)
master_win6h.to_csv(master_win_path, index=False)

print(f"✅ Exported 6_fhc_windowed_features_6h.csv ({len(fhc_win6h):,} windows)")
print(f"✅ Exported 2_harmonized_windowed_features_6h.csv ({len(master_win6h):,} windows)")

# ==============================================================================
# STAGE 5: LEAK-FREE PATIENT-STRATIFIED 5-FOLD CV SPLITTING
# ==============================================================================
print("\n--- STAGE 5: Generating Leak-Free 5-Fold Stratified GroupKFold ---")

def generate_5fold_splits(df_win, dataset_name):
    label_col = 'Slabel_max' if 'Slabel_max' in df_win.columns else [c for c in df_win.columns if 'slabel' in c.lower()][0]
    cohort_col= 'Cohort' if 'Cohort' in df_win.columns else [c for c in df_win.columns if 'cohort' in c.lower()][0]

    pat_df = df_win.groupby('Patient_Key').agg({
        cohort_col: 'first',
        label_col: 'max'
    }).reset_index()
    
    pat_df['Stratify_Target'] = pat_df[label_col].fillna(0).astype(int)
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    pat_df['Fold'] = -1
    
    for fold, (train_idx, val_idx) in enumerate(sgkf.split(pat_df, pat_df['Stratify_Target'], groups=pat_df['Patient_Key'])):
        pat_df.loc[val_idx, 'Fold'] = fold
        
    df_win_split = df_win.merge(pat_df[['Patient_Key', 'Fold']], on='Patient_Key', how='left')
    return pat_df, df_win_split

fhc_pat_splits, fhc_win_split       = generate_5fold_splits(fhc_win6h, "FHC Dataset")
master_pat_splits, master_win_split = generate_5fold_splits(master_win6h, "Harmonized Master")

fhc_splits_path    = OUT_DIR / "7_fhc_5fold_splits.csv"
master_splits_path = OUT_DIR / "3_harmonized_5fold_splits.csv"

fhc_pat_splits.to_csv(fhc_splits_path, index=False)
master_pat_splits.to_csv(master_splits_path, index=False)

fhc_win_split.to_csv(fhc_win_path, index=False)
master_win_split.to_csv(master_win_path, index=False)

print(f"✅ Exported 7_fhc_5fold_splits.csv & 3_harmonized_5fold_splits.csv")

# ==============================================================================
# STAGE 6: MODEL TRAINING & CLINICAL EXPLAINABILITY BENCHMARKING
# ==============================================================================
print("\n--- STAGE 6: Training Models & Extracting Feature Importances ---")

def train_and_evaluate_models(df_win, dataset_name, target_col='Slabel_max'):
    if target_col not in df_win.columns or 'Fold' not in df_win.columns:
        return [], []
        
    valid_mask = df_win[target_col].notna() & df_win['Fold'].notna()
    df_eval = df_win[valid_mask].copy()
    
    ignore_cols = [
        'Patient_Key', 'Window_6h_Idx', 'Original_PID', 'Cohort', 'Dataset_Source',
        'Fold', 'Slabel', 'Slabel_max', 'Slabel_lead_6h', 'Slabel_lead_12h', 'Slabel_lead_24h'
    ]
    feature_cols = [c for c in df_eval.columns if c not in ignore_cols and df_eval[c].dtype != object]
    
    models = {
        'GradientBoosting': GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42),
        'RandomForest': RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42),
        'HistGradientBoosting': HistGradientBoostingClassifier(max_iter=100, class_weight='balanced', random_state=42),
        'LogisticRegression': LogisticRegression(max_iter=500, class_weight='balanced', random_state=42),
        'MLP_NeuralNet': MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=300, random_state=42)
    }
    
    results = []
    feature_importances_list = []
    
    for model_name, model_obj in models.items():
        fold_aurocs, fold_auprcs, fold_accs, fold_f1s = [], [], [], []
        fold_recalls, fold_specs = [], []
        
        for fold in range(5):
            train_mask = df_eval['Fold'] != fold
            val_mask   = df_eval['Fold'] == fold
            
            X_train_raw = df_eval.loc[train_mask, feature_cols]
            y_train     = df_eval.loc[train_mask, target_col].astype(int)
            
            X_val_raw   = df_eval.loc[val_mask, feature_cols]
            y_val       = df_eval.loc[val_mask, target_col].astype(int)
            
            if y_val.nunique() < 2 or y_train.nunique() < 2:
                continue
            
            # Fold-strict imputation & scaling
            imputer = SimpleImputer(strategy='median')
            scaler  = StandardScaler()
            
            X_train_imp = imputer.fit_transform(X_train_raw)
            X_train_scaled = scaler.fit_transform(X_train_imp)
            
            X_val_imp   = imputer.transform(X_val_raw)
            X_val_scaled = scaler.transform(X_val_imp)
            
            X_train_scaled = np.nan_to_num(X_train_scaled, nan=0.0)
            X_val_scaled   = np.nan_to_num(X_val_scaled, nan=0.0)
            
            model_obj.fit(X_train_scaled, y_train)
            
            if hasattr(model_obj, "predict_proba"):
                y_probs = model_obj.predict_proba(X_val_scaled)[:, 1]
            else:
                y_probs = model_obj.predict(X_val_scaled)
                
            y_preds = (y_probs >= 0.5).astype(int)
            
            auroc = roc_auc_score(y_val, y_probs)
            auprc = average_precision_score(y_val, y_probs)
            acc   = accuracy_score(y_val, y_preds)
            f1    = f1_score(y_val, y_preds, zero_division=0)
            rec   = recall_score(y_val, y_preds, zero_division=0)
            
            tn, fp, fn, tp = confusion_matrix(y_val, y_preds, labels=[0, 1]).ravel()
            spec  = tn / (tn + fp) if (tn + fp) > 0 else 0.0
            
            fold_aurocs.append(auroc)
            fold_auprcs.append(auprc)
            fold_accs.append(acc)
            fold_f1s.append(f1)
            fold_recalls.append(rec)
            fold_specs.append(spec)
            
            if hasattr(model_obj, 'feature_importances_'):
                for col_name, imp in zip(feature_cols, model_obj.feature_importances_):
                    feature_importances_list.append({
                        'dataset': dataset_name,
                        'target': target_col,
                        'model': model_name,
                        'fold': fold,
                        'feature': col_name,
                        'importance': float(imp)
                    })

        mean_auroc = np.mean(fold_aurocs) if fold_aurocs else 0.0
        std_auroc  = np.std(fold_aurocs) if fold_aurocs else 0.0
        mean_auprc = np.mean(fold_auprcs) if fold_auprcs else 0.0
        mean_acc   = np.mean(fold_accs) if fold_accs else 0.0
        mean_f1    = np.mean(fold_f1s) if fold_f1s else 0.0
        mean_rec   = np.mean(fold_recalls) if fold_recalls else 0.0
        mean_spec  = np.mean(fold_specs) if fold_specs else 0.0
        
        print(f"  {dataset_name:<28s} | {model_name:<20s} | AUROC: {mean_auroc:.4f} ± {std_auroc:.4f} | AUPRC: {mean_auprc:.4f} | F1: {mean_f1:.4f}")
        
        results.append({
            'dataset': dataset_name,
            'target': target_col,
            'model': model_name,
            'mean_auroc': round(mean_auroc, 4),
            'std_auroc': round(std_auroc, 4),
            'mean_auprc': round(mean_auprc, 4),
            'mean_accuracy': round(mean_acc, 4),
            'mean_sensitivity_recall': round(mean_rec, 4),
            'mean_specificity': round(mean_spec, 4),
            'mean_f1': round(mean_f1, 4)
        })
        
    return results, feature_importances_list

all_results = []
all_importances = []

res_a, imp_a = train_and_evaluate_models(fhc_win_split, "FHC Dataset", "Slabel_max")
res_b, imp_b = train_and_evaluate_models(fhc_win_split, "FHC Dataset (Early 6h Onset)", "Slabel_lead_6h")
res_c, imp_c = train_and_evaluate_models(master_win_split, "Harmonized Master", "Slabel_max")

all_results.extend(res_a + res_b + res_c)
all_importances.extend(imp_a + imp_b + imp_c)

# Save Final Evaluation Results
res_df = pd.DataFrame(all_results)
res_export_path = OUT_DIR / "11_final_model_evaluations.csv"
res_df.to_csv(res_export_path, index=False)

# Save Feature Importances
imp_df = pd.DataFrame(all_importances)
if not imp_df.empty:
    top_imp = imp_df.groupby(['dataset', 'model', 'feature'])['importance'].mean().reset_index()
    top_imp = top_imp.sort_values(['dataset', 'model', 'importance'], ascending=[True, True, False])
    imp_export_path = OUT_DIR / "12_feature_importance_leaderboard.csv"
    top_imp.to_csv(imp_export_path, index=False)

print("\n" + "="*80)
print("MASTER SEPSIS AI PIPELINE FINISHED SUCCESSFULLY!")
print(f"✅ All 12 final clean datasets & benchmarks exported to: {OUT_DIR}")
print("="*80)
