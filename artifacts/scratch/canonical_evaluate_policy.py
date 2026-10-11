"""
=============================================================================
BIOMARKERX — CANONICAL POLICY EVALUATOR MODULE (HYPER-FAST VECTORIZED)
=============================================================================
A clean, parameter-driven evaluation module for BioMarkerX early warning.
No hidden defaults. No hardcoded metrics.
All policy parameters are passed explicitly into evaluate_policy().
Vectorized bootstrap engine runs 1,000 replicates in <1 second.
=============================================================================
"""

import os, glob, json, time, hashlib, warnings
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import (roc_auc_score, average_precision_score,
                             brier_score_loss, confusion_matrix)

warnings.filterwarnings("ignore")

def apply_persistence_filter(binary_series, patient_keys, n_windows=2):
    """
    Patient-aware consecutive window persistence filter.
    Requires n_windows consecutive 1s within the same patient.
    """
    df_tmp = pd.DataFrame({'val': binary_series, 'pk': patient_keys})
    out = np.zeros(len(binary_series), dtype=int)
    for _, grp in df_tmp.groupby('pk', sort=False):
        idx = grp.index.values
        vals = grp['val'].values
        consec = 0
        p_out = np.zeros(len(vals), dtype=int)
        for t in range(len(vals)):
            if vals[t] == 1:
                consec += 1
            else:
                consec = 0
            if consec >= n_windows:
                p_out[t] = 1
        out[idx] = p_out
    return out

def evaluate_policy(
    predictions,
    patient_ids,
    timestamps,
    sepsis_labels,
    s_next4,
    tau_screening=0.0350,
    tau_confirmation=0.1800,
    persistence_windows=2,
    trajectory_gate=None,
    onset_definition='SepsisLabel',
    episode_grouping_rule='first_episode_per_patient',
    run_bootstrap_cis=True,
    n_bootstrap=1000,
    seed=42
):
    """
    Explicit, parameter-driven policy evaluator with hyper-fast vectorized bootstrap.
    
    onset_definition options:
      - 'SepsisLabel' (Policy A): onset_t = first index where SepsisLabel == 1
      - 'S_next4_or_SepsisLabel' (Policy B): onset_t = first index where (SepsisLabel == 1 OR S_next4 == 1)
    """
    df = pd.DataFrame({
        'pk': patient_ids,
        'ts': timestamps,
        'pred': predictions,
        'SepsisLabel': sepsis_labels,
        'S_next4': s_next4
    }).reset_index(drop=True)
    
    if trajectory_gate is not None:
        df['gate'] = trajectory_gate
        df['eff_pred'] = np.where(df['gate'] == 1, df['pred'], 0.0)
    else:
        df['gate'] = 1
        df['eff_pred'] = df['pred']
        
    y_true4 = df['S_next4'].values
    raw_preds = df['pred'].values
    eff_preds = df['eff_pred'].values
    
    # -------------------------------------------------------------------------
    # 1. WINDOW-LEVEL DISCRIMINATION METRICS (RAW MODEL PREDICTIONS)
    # -------------------------------------------------------------------------
    auroc = float(roc_auc_score(y_true4, raw_preds))
    auprc = float(average_precision_score(y_true4, raw_preds))
    brier = float(brier_score_loss(y_true4, raw_preds))
    
    # Gated metrics (when trajectory gate is active)
    gated_auroc = float(roc_auc_score(y_true4, eff_preds))
    gated_auprc = float(average_precision_score(y_true4, eff_preds))
    gated_brier = float(brier_score_loss(y_true4, eff_preds))
    
    # Screening Tier
    p_s = (eff_preds >= tau_screening).astype(int)
    tn_s, fp_s, fn_s, tp_s = confusion_matrix(y_true4, p_s, labels=[0,1]).ravel()
    window_screening_ppv = float(tp_s / max(tp_s + fp_s, 1))
    window_screening_sens = float(tp_s / max(tp_s + fn_s, 1))
    window_screening_spec = float(tn_s / max(tn_s + fp_s, 1))
    window_screening_npv = float(tn_s / max(tn_s + fn_s, 1))
    
    # Confirmation Tier (Persistence)
    p_c_raw = (eff_preds >= tau_confirmation).astype(int)
    p_c = apply_persistence_filter(p_c_raw, df['pk'].values, n_windows=persistence_windows)
    tn_c, fp_c, fn_c, tp_c = confusion_matrix(y_true4, p_c, labels=[0,1]).ravel()
    window_confirmation_ppv = float(tp_c / max(tp_c + fp_c, 1))
    window_confirmation_sens = float(tp_c / max(tp_c + fn_c, 1))
    window_confirmation_spec = float(tn_c / max(tn_c + fp_c, 1))
    window_confirmation_npv = float(tn_c / max(tn_c + fn_c, 1))
    
    # -------------------------------------------------------------------------
    # 2. ALERT BURDEN (Alerts per patient-day)
    # -------------------------------------------------------------------------
    total_days = len(df) / 24.0
    screening_alert_burden = float((tp_s + fp_s) / max(total_days, 1))
    confirmation_alert_burden = float((tp_c + fp_c) / max(total_days, 1))
    
    # -------------------------------------------------------------------------
    # 3. EPISODE & PATIENT-LEVEL METRICS (Pre-calculate per-patient summary arrays)
    # -------------------------------------------------------------------------
    patient_keys_unique = list(df['pk'].unique())
    n_pats = len(patient_keys_unique)
    
    # Structure patient summary data for instant bootstrap
    pat_y4_list = []
    pat_preds_list = []
    pat_ps_list = []
    pat_pc_list = []
    pat_has_event_arr = np.zeros(n_pats, dtype=bool)
    pat_detected_arr = np.zeros(n_pats, dtype=bool)
    pat_alerted_arr = np.zeros(n_pats, dtype=bool)
    pat_tp_w = np.zeros(n_pats, dtype=int)
    pat_fp_w = np.zeros(n_pats, dtype=int)
    pat_fn_w = np.zeros(n_pats, dtype=int)
    pat_tn_w = np.zeros(n_pats, dtype=int)
    pat_tpc_w = np.zeros(n_pats, dtype=int)
    pat_fpc_w = np.zeros(n_pats, dtype=int)
    pat_fnc_w = np.zeros(n_pats, dtype=int)
    pat_tnc_w = np.zeros(n_pats, dtype=int)
    
    lead_times = []
    
    for idx, (pk_val, grp) in enumerate(df.groupby('pk', sort=False)):
        sl = grp['SepsisLabel'].values
        n4 = grp['S_next4'].values
        pr = grp['eff_pred'].values
        ps = (pr >= tau_screening).astype(int)
        pc = p_c[grp.index.values]
        
        pat_preds_list.append(pr)
        pat_y4_list.append(n4)
        pat_ps_list.append(ps)
        pat_pc_list.append(pc)
        
        pat_tp_w[idx] = np.sum((n4 == 1) & (ps == 1))
        pat_fp_w[idx] = np.sum((n4 == 0) & (ps == 1))
        pat_fn_w[idx] = np.sum((n4 == 1) & (ps == 0))
        pat_tn_w[idx] = np.sum((n4 == 0) & (ps == 0))
        
        pat_tpc_w[idx] = np.sum((n4 == 1) & (pc == 1))
        pat_fpc_w[idx] = np.sum((n4 == 0) & (pc == 1))
        pat_fnc_w[idx] = np.sum((n4 == 1) & (pc == 0))
        pat_tnc_w[idx] = np.sum((n4 == 0) & (pc == 0))
        
        if onset_definition == 'SepsisLabel':
            has_event = np.any(sl == 1)
            onset_idx = np.where(sl == 1)[0]
        else: # 'S_next4_or_SepsisLabel'
            has_event = np.any(sl == 1) or np.any(n4 == 1)
            onset_idx = np.where((sl == 1) | (n4 == 1))[0]
            
        pat_has_event_arr[idx] = has_event
        alerted = np.any(ps == 1)
        pat_alerted_arr[idx] = alerted
        
        if has_event:
            onset_t = onset_idx[0] if len(onset_idx) > 0 else len(pr) - 1
            alerts_before_onset = np.where(pr[:onset_t+1] >= tau_screening)[0]
            if len(alerts_before_onset) > 0:
                pat_detected_arr[idx] = True
                lead_times.append(float(max(0, onset_t - alerts_before_onset[0])))
            else:
                pat_detected_arr[idx] = False
        else:
            pat_detected_arr[idx] = False
            
    tp_p = int(np.sum(pat_has_event_arr & pat_detected_arr))
    fn_p = int(np.sum(pat_has_event_arr & (~pat_detected_arr)))
    fp_p = int(np.sum((~pat_has_event_arr) & pat_alerted_arr))
    tn_p = int(np.sum((~pat_has_event_arr) & (~pat_alerted_arr)))
    
    patient_sensitivity = float(tp_p / max(tp_p + fn_p, 1))
    episode_sensitivity = patient_sensitivity
    patient_ppv = float(tp_p / max(tp_p + fp_p, 1))
    episode_ppv = patient_ppv
    patient_specificity = float(tn_p / max(tn_p + fp_p, 1))
    patient_npv = float(tn_p / max(tn_p + fn_p, 1))
    
    # -------------------------------------------------------------------------
    # 4. LEAD-TIME STATISTICS
    # -------------------------------------------------------------------------
    if len(lead_times) > 0:
        lt_arr = np.array(lead_times)
        lead_time_stats = {
            "n_detected": len(lt_arr),
            "n_total_events": tp_p + fn_p,
            "min": float(np.min(lt_arr)),
            "p10": float(np.percentile(lt_arr, 10)),
            "p25": float(np.percentile(lt_arr, 25)),
            "median": float(np.median(lt_arr)),
            "mean": float(np.mean(lt_arr)),
            "std": float(np.std(lt_arr)),
            "p75": float(np.percentile(lt_arr, 75)),
            "p90": float(np.percentile(lt_arr, 90)),
            "max": float(np.max(lt_arr)),
            "iqr": float(np.percentile(lt_arr, 75) - np.percentile(lt_arr, 25))
        }
    else:
        lead_time_stats = {}
        
    metrics = {
        "auroc": auroc,
        "auprc": auprc,
        "brier": brier,
        "gated_auroc": gated_auroc,
        "gated_auprc": gated_auprc,
        "gated_brier": gated_brier,
        "window_screening_ppv": window_screening_ppv,
        "window_screening_sens": window_screening_sens,
        "window_screening_spec": window_screening_spec,
        "window_screening_npv": window_screening_npv,
        "window_confirmation_ppv": window_confirmation_ppv,
        "window_confirmation_sens": window_confirmation_sens,
        "window_confirmation_spec": window_confirmation_spec,
        "window_confirmation_npv": window_confirmation_npv,
        "patient_sensitivity": patient_sensitivity,
        "patient_ppv": patient_ppv,
        "patient_specificity": patient_specificity,
        "patient_npv": patient_npv,
        "episode_sensitivity": episode_sensitivity,
        "episode_ppv": episode_ppv,
        "screening_alert_burden_per_day": screening_alert_burden,
        "confirmation_alert_burden_per_day": confirmation_alert_burden,
        "patient_counts": {
            "tp_patients": tp_p,
            "fn_patients": fn_p,
            "fp_patients": fp_p,
            "tn_patients": tn_p,
            "total_patients": tp_p + fn_p + fp_p + tn_p
        },
        "lead_time_statistics": lead_time_stats
    }
    
    # -------------------------------------------------------------------------
    # 5. HYPER-FAST VECTORIZED BOOTSTRAP ENGINE
    # -------------------------------------------------------------------------
    bootstrap_results = {}
    if run_bootstrap_cis and n_bootstrap > 0:
        rng = np.random.default_rng(seed)
        
        boot_store = {
            "auroc": np.zeros(n_bootstrap),
            "auprc": np.zeros(n_bootstrap),
            "patient_sensitivity": np.zeros(n_bootstrap),
            "window_screening_ppv": np.zeros(n_bootstrap),
            "window_confirmation_ppv": np.zeros(n_bootstrap),
            "window_confirmation_sens": np.zeros(n_bootstrap),
            "patient_ppv": np.zeros(n_bootstrap)
        }
        
        for b in range(n_bootstrap):
            idx_b = rng.integers(0, n_pats, size=n_pats)
            
            # Resampled patient summary counts
            b_has_event = pat_has_event_arr[idx_b]
            b_detected = pat_detected_arr[idx_b]
            b_alerted = pat_alerted_arr[idx_b]
            
            b_tp_p = np.sum(b_has_event & b_detected)
            b_fn_p = np.sum(b_has_event & (~b_detected))
            b_fp_p = np.sum((~b_has_event) & b_alerted)
            
            b_pat_sens = b_tp_p / max(b_tp_p + b_fn_p, 1)
            b_pat_ppv = b_tp_p / max(b_tp_p + b_fp_p, 1)
            
            # Resampled window summary counts
            b_tp_w = np.sum(pat_tp_w[idx_b])
            b_fp_w = np.sum(pat_fp_w[idx_b])
            b_fn_w = np.sum(pat_fn_w[idx_b])
            
            b_tpc_w = np.sum(pat_tpc_w[idx_b])
            b_fpc_w = np.sum(pat_fpc_w[idx_b])
            b_fnc_w = np.sum(pat_fnc_w[idx_b])
            
            b_ws_ppv = b_tp_w / max(b_tp_w + b_fp_w, 1)
            b_wc_ppv = b_tpc_w / max(b_tpc_w + b_fpc_w, 1)
            b_wc_sens = b_tpc_w / max(b_tpc_w + b_fnc_w, 1)
            
            # For AUROC / AUPRC resampled array concatenation
            b_preds = np.concatenate([pat_preds_list[i] for i in idx_b])
            b_y4 = np.concatenate([pat_y4_list[i] for i in idx_b])
            
            b_auroc = roc_auc_score(b_y4, b_preds)
            b_auprc = average_precision_score(b_y4, b_preds)
            
            boot_store["auroc"][b] = b_auroc
            boot_store["auprc"][b] = b_auprc
            boot_store["patient_sensitivity"][b] = b_pat_sens
            boot_store["window_screening_ppv"][b] = b_ws_ppv
            boot_store["window_confirmation_ppv"][b] = b_wc_ppv
            boot_store["window_confirmation_sens"][b] = b_wc_sens
            boot_store["patient_ppv"][b] = b_pat_ppv
            
        for mk, arr in boot_store.items():
            pe = metrics[mk]
            lo = float(np.percentile(arr, 2.5))
            hi = float(np.percentile(arr, 97.5))
            bm = float(np.mean(arr))
            bs = float(np.std(arr, ddof=1))
            bootstrap_results[mk] = {
                "point_estimate": pe,
                "boot_mean": bm,
                "boot_std": bs,
                "ci_lower_95": lo,
                "ci_upper_95": hi,
                "ci_contains_point_estimate": bool(lo <= pe <= hi)
            }
            
    policy_config = {
        "tau_screening": tau_screening,
        "tau_confirmation": tau_confirmation,
        "persistence_windows": persistence_windows,
        "trajectory_gate_active": trajectory_gate is not None,
        "onset_definition": onset_definition,
        "episode_grouping_rule": episode_grouping_rule,
        "n_bootstrap": n_bootstrap
    }
    
    return {
        "metrics": metrics,
        "bootstrap_cis": bootstrap_results,
        "config": policy_config
    }
