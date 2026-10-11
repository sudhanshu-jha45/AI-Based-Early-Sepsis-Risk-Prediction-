import os, glob, json, numpy as np, pandas as pd

def audit_entire_project_problems():
    print("=========================================================================")
    print("RUNNING EXHAUSTIVE PROJECT PROBLEM DISCOVERY & FORENSIC AUDIT")
    print("=========================================================================")
    
    dev_path = r"FINAL_CLEANED_DATASETS\dataset_v2_unified_2115_patients_6h.csv"
    dev_df = pd.read_csv(dev_path)
    
    problems = []
    
    # 1. Feature Level Missingness Audit
    missing_series = dev_df.isnull().mean()
    high_missing = missing_series[missing_series > 0.50]
    problems.append({
        "category": "Data Quality & Missingness",
        "issue": f"{len(high_missing)} out of {dev_df.shape[1]} features have >50% missing values in development cohort.",
        "details": list(high_missing.index[:10])
    })
    
    # 2. Physiological Outliers & Boundary Violations
    outliers = {}
    if 'HR_max' in dev_df.columns:
        hr_out = (dev_df['HR_max'] > 250) | (dev_df['HR_min'] < 20)
        outliers['HR_extreme'] = int(hr_out.sum())
    if 'Temp_max' in dev_df.columns:
        temp_out = (dev_df['Temp_max'] > 45) | (dev_df['Temp_min'] < 25)
        outliers['Temp_extreme'] = int(temp_out.sum())
    if 'SBP_min' in dev_df.columns and 'DBP_min' in dev_df.columns:
        bp_inv = dev_df['SBP_min'] < dev_df['DBP_min']
        outliers['BP_inversion'] = int(bp_inv.sum())
        
    problems.append({
        "category": "Raw Sensor Noise & Physiological Violations",
        "issue": f"Raw vitals contain physiological sensor artifacts (Extreme HR: {outliers.get('HR_extreme', 0)}, Extreme Temp: {outliers.get('Temp_extreme', 0)}, BP Inversion: {outliers.get('BP_inversion', 0)}).",
        "details": outliers
    })
    
    # 3. Short ICU Stays Truncation
    stay_lengths = dev_df.groupby('Patient_Key').size()
    short_stays = (stay_lengths < 2).sum()
    problems.append({
        "category": "Cohort Inclusion & Window Truncation",
        "issue": f"{short_stays} patients have < 2 observation windows (< 12 hours stay), preventing meaningful trajectory velocity computation.",
        "details": f"Total patients: {len(stay_lengths)}"
    })
    
    # 4. Absence of Non-Structured Modalities
    problems.append({
        "category": "Multimodal EHR Data Deficit",
        "issue": "Model is restricted to structured tabular vitals/labs. Clinical nursing notes (NLP), Medication Administration Records (MAR), and ECG waveforms are missing.",
        "details": "Only 6-hour binned tabular vitals and lab values available."
    })
    
    # 5. Class Imbalance Ratio
    dev_df['S_next'] = dev_df.groupby('Patient_Key')['Slabel_max'].shift(-1)
    dev_valid = dev_df.dropna(subset=['S_next'])
    pos_rate = dev_valid['S_next'].mean()
    problems.append({
        "category": "Class Imbalance",
        "issue": f"Positive Sepsis-3 transition windows represent only {pos_rate*100:.2f}% of windows in dev cohort (and ~1.20% in external test).",
        "details": f"Positive windows: {dev_valid['S_next'].sum()}, Negative windows: {(dev_valid['S_next']==0).sum()}"
    })

    # Save Audit Summary
    with open("scratch/exhaustive_problem_discovery.json", "w") as f:
        json.dump(problems, f, indent=2)
        
    print(f"Discovered {len(problems)} major programmatic project problem categories.")
    print("Saved audit to scratch/exhaustive_problem_discovery.json")

if __name__ == "__main__":
    audit_entire_project_problems()
