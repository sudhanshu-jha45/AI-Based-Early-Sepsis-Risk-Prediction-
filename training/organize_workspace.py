import os
import shutil

base_dir = r"c:\Users\LENOVO\Downloads\spesis dataset"

# Target Folders
backend_dir = os.path.join(base_dir, "backend")
frontend_dir = os.path.join(base_dir, "frontend")
models_dir = os.path.join(base_dir, "models")
dataset_dir = os.path.join(base_dir, "dataset")
documents_dir = os.path.join(base_dir, "documents")
training_dir = os.path.join(base_dir, "training")
testing_dir = os.path.join(base_dir, "testing")
artifacts_dir = os.path.join(base_dir, "artifacts")

for d in [backend_dir, frontend_dir, models_dir, dataset_dir, documents_dir, training_dir, testing_dir, artifacts_dir]:
    os.makedirs(d, exist_ok=True)

# Mapping rules
backend_files = ["server.py", "predict_ml_single.py", "clinical_dashboard.py"]
frontend_files = ["index.html"]
models_files = ["master_sepsis_model.joblib", "master_sepsis_pipeline.py"]

dataset_items = [
    "dataset_v2_unified_2115_patients_6h.csv",
    "FINAL_CLEANED_DATASETS",
    "training_setA",
    "training_setB",
    "external_test_A"
]

documents_items = [
    "review 2",
    "REVIEW-2 DOCUMENT FORMAT-Corrected.docx",
    "ABSTRACT_merged_fixed.docx",
    "AegisSepsis_AI_Full_Manuscript.docx",
    "AegisSepsis_AI_300Page_Scientific_Master_Monograph.pdf",
    "AegisSepsis_AI_Full_Manuscript.pdf",
    "AegisSepsis_AI_IEEE_Revised.pdf",
    "BioMarkerX_300Page_Scientific_Master_Monograph.pdf",
    "FULL_MANUSCRIPT.pdf",
    "FULL_MONOGRAPH_300PAGE.pdf",
    "Sepsis_Review1_PPT (6).pptx",
    "Sepsis_Review1_PPT (7).pptx",
    "README.txt",
    "FINAL_NOVELTY_PACKAGE",
    "FINAL_BIOMARKERX"
]

training_files = [
    "build_300page_master_monograph.py",
    "build_10page_ieee_pdf.py",
    "build_real_ieee_pdf.py",
    "build_all_scientific_artifacts.py",
    "execute_claim_forensics_audit.py",
    "execute_final_statistical_lock.py",
    "execute_observation_process_validation.py",
    "generate_manuscript_pdf.py",
    "generate_showcase_data.py",
    "generate_patient_pdf.py",
    "expand_manuscript_md.py",
    "update_sudhanshu_review2_35page.py",
    "update_review2_docx_indepth.py",
    "update_review2_docx.py",
    "update_abstract_docx.py",
    "update_full_abstract_docx.py",
    "builder_base.py",
    "generator_helpers.py",
    "sudhanshu_builder_base.py"
]

testing_items = [
    "audit",
    "inspect_full_docx.py",
    "inspect_review2.py",
    "inspect_sudhanshu_docx.py",
    "inspect_sudhanshu_safe.py",
    "inspect_sudhanshu_top.py",
    "print_paragraphs.py",
    "print_sudhanshu_headings.py",
    "test_docx.py",
    "test_docx_helpers.py",
    "verify_sudhanshu_docx.py",
    "verify_updated_docx.py"
]

artifacts_items = [
    "test_patient_report.pdf",
    "scratch"
]

def move_item(item_name, target_folder):
    src = os.path.join(base_dir, item_name)
    dst = os.path.join(target_folder, item_name)
    if os.path.exists(src):
        if os.path.exists(dst):
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            else:
                os.remove(dst)
        shutil.move(src, dst)
        print(f"Moved: {item_name} -> {os.path.basename(target_folder)}/")

for f in backend_files: move_item(f, backend_dir)
for f in frontend_files: move_item(f, frontend_dir)
for f in models_files: move_item(f, models_dir)
for f in dataset_items: move_item(f, dataset_dir)
for f in documents_items: move_item(f, documents_dir)
for f in training_files: move_item(f, training_dir)
for f in testing_items: move_item(f, testing_dir)
for f in artifacts_items: move_item(f, artifacts_dir)

print("\nFolder organization complete!")
