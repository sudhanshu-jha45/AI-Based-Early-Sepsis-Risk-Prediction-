import os
import glob
import json
import hashlib
import pandas as pd

def compute_sha256(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def run_project_discovery():
    print("=========================================================================")
    print("STEP 1: EXECUTING COMPLETE BIOMARKERX PROJECT DISCOVERY & INVENTORY AUDIT")
    print("=========================================================================")
    
    inventory = []
    root_dir = os.getcwd()
    
    # Patterns to discover
    patterns = ['**/*.csv', '**/*.psv', '**/*.joblib', '**/*.json', '**/*.py', '**/*.pdf', '**/*.md']
    
    discovered_files = []
    for p in patterns:
        discovered_files.extend(glob.glob(p, recursive=True))
        
    discovered_files = sorted(list(set(discovered_files)))
    
    for rel_path in discovered_files:
        abs_path = os.path.abspath(rel_path)
        if not os.path.isfile(abs_path):
            continue
            
        size_bytes = os.path.getsize(abs_path)
        mtime = os.path.getmtime(abs_path)
        
        # Role determination
        role = "Script / Code"
        if rel_path.endswith('.joblib'):
            role = "Model / Calibrator Artifact"
        elif rel_path.endswith('.json'):
            role = "Metadata / Config / Schema"
        elif rel_path.endswith('.csv') or rel_path.endswith('.psv'):
            role = "Dataset / Tabular Data"
        elif rel_path.endswith('.pdf') or rel_path.endswith('.md'):
            role = "Report / Monograph / Audit Documentation"
            
        # Lock status
        is_locked = "FINAL_BIOMARKERX" in rel_path or "external_test_A" in rel_path
        
        item = {
            "relative_path": rel_path,
            "absolute_path": abs_path,
            "size_kb": round(size_bytes / 1024.0, 2),
            "last_modified": pd.to_datetime(mtime, unit='s').strftime("%Y-%m-%d %H:%M:%S"),
            "role": role,
            "is_locked": is_locked
        }
        inventory.append(item)
        
    print(f"Total Discovered Project Files: {len(inventory)}")
    
    # Save Inventory JSON & MD
    with open("BIOMARKERX_PROJECT_INVENTORY.json", "w") as f:
        json.dump(inventory, f, indent=2)
        
    with open("BIOMARKERX_PROJECT_INVENTORY.md", "w") as f:
        f.write("# BioMarkerX Complete Project Inventory\n\n")
        f.write(f"**Total Discovered Files**: {len(inventory)}\n\n")
        f.write("| Path | Role | Size (KB) | Last Modified | Locked Status |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for item in inventory[:50]: # top 50 in MD summary
            f.write(f"| `{item['relative_path']}` | {item['role']} | {item['size_kb']} | {item['last_modified']} | {'🔒 Locked' if item['is_locked'] else 'Writable'} |\n")
        if len(inventory) > 50:
            f.write(f"\n*... and {len(inventory)-50} more files logged in JSON inventory.*\n")
            
    print("Saved BIOMARKERX_PROJECT_INVENTORY.json and BIOMARKERX_PROJECT_INVENTORY.md")

if __name__ == "__main__":
    run_project_discovery()
