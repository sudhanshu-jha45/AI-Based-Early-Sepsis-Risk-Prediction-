import os
import glob
import json
import time
import hashlib
import numpy as np
import pandas as pd
import joblib

def compute_patient_hash(patient_id):
    return int(hashlib.sha256(str(patient_id).encode('utf-8')).hexdigest(), 16) % 100000

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def run_phase1_inventory():
    print("=========================================================================")
    print("PHASE 1: LOCATING AND INVENTORYING ALL RELEVANT ARTIFACTS")
    print("=========================================================================")
    
    # 1. Search for scripts containing 82.44 or 79.93 or relevant search strings
    search_keywords = ['82.44', '79.93', '0.8244', '0.7993', '230', '223', 'tau_screening', 'tau_s']
    matched_files = {}
    
    all_py_files = glob.glob('scratch/*.py') + glob.glob('*.py')
    all_json_files = glob.glob('**/*.json', recursive=True)
    all_md_files = glob.glob('**/*.md', recursive=True)
    
    files_to_check = set(all_py_files + all_json_files + all_md_files)
    
    inventory = []
    
    for fpath in files_to_check:
        if 'node_modules' in fpath or '.git' in fpath or '.gemini' in fpath:
            continue
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                matches = [kw for kw in search_keywords if kw in content]
                if matches:
                    stat = os.stat(fpath)
                    inventory.append({
                        'filepath': fpath,
                        'filename': os.path.basename(fpath),
                        'size_bytes': stat.st_size,
                        'mtime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime)),
                        'sha256': sha256_file(fpath),
                        'matched_keywords': matches
                    })
        except Exception as e:
            pass
            
    inventory_df = pd.DataFrame(inventory)
    print(f"Found {len(inventory)} relevant files matching keywords.")
    print(inventory_df[['filename', 'mtime', 'matched_keywords']].to_string())
    
    out_dir = "FINAL_BIOMARKERX/forensic_sensitivity_audit"
    os.makedirs(out_dir, exist_ok=True)
    inventory_df.to_csv(os.path.join(out_dir, "PHASE1_ARTIFACT_INVENTORY.csv"), index=False)
    return inventory_df

if __name__ == '__main__':
    run_phase1_inventory()
