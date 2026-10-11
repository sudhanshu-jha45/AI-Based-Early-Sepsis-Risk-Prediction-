import os
import shutil
import glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

target_figures_dir = r"c:\Users\LENOVO\Downloads\spesis dataset\figures"
os.makedirs(target_figures_dir, exist_ok=True)

print(f"Target figures directory: {target_figures_dir}")

# 1. Copy figures from documents/FINAL_NOVELTY_PACKAGE/figures/
pkg_figures = r"c:\Users\LENOVO\Downloads\spesis dataset\documents\FINAL_NOVELTY_PACKAGE\figures"
if os.path.exists(pkg_figures):
    for f in os.listdir(pkg_figures):
        src = os.path.join(pkg_figures, f)
        dst = os.path.join(target_figures_dir, f)
        shutil.copy2(src, dst)
        print(f"Copied package figure: {f}")

# 2. Copy XAI figures from documents/FINAL_BIOMARKERX/xai/
xai_figures = r"c:\Users\LENOVO\Downloads\spesis dataset\documents\FINAL_BIOMARKERX\xai"
if os.path.exists(xai_figures):
    for f in os.listdir(xai_figures):
        src = os.path.join(xai_figures, f)
        dst = os.path.join(target_figures_dir, f)
        shutil.copy2(src, dst)
        print(f"Copied XAI figure: {f}")

# 3. Copy user uploaded figures
uploaded_dir = r"C:\Users\LENOVO\.gemini\antigravity\brain\1aae94fc-ee66-4401-a9e3-b61c7a3ef552\.user_uploaded"
if os.path.exists(uploaded_dir):
    for f in os.listdir(uploaded_dir):
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg')):
            src = os.path.join(uploaded_dir, f)
            dst = os.path.join(target_figures_dir, f)
            shutil.copy2(src, dst)
            print(f"Copied uploaded figure: {f}")

print("Pre-existing figures copied successfully.")
