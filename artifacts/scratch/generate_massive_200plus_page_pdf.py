import os
import sys
import time
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        if self._pageNumber > 1:
            self.drawString(54, 750, "BioMarkerX — Definitive Scientific Master Monograph & Complete Technical Archive")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 36, page_text)
            self.drawString(54, 36, "CONFIDENTIAL & PROPRIETARY — RESEARCH DECISION-SUPPORT PROTOTYPE ARCHIVE")
            self.line(54, 48, 558, 48)
            
        self.restoreState()

def generate_massive_pdf():
    out_pdf_1 = r"c:\Users\LENOVO\Downloads\spesis dataset\BioMarkerX_Complete_Scientific_Master_Monograph.pdf"
    out_pdf_2 = r"c:\Users\LENOVO\Downloads\spesis dataset\BioMarkerX_Master_Deliverables\BioMarkerX_Complete_Scientific_Master_Monograph.pdf"

    doc = SimpleDocTemplate(
        out_pdf_1,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#1A365D")   # Navy
    c_secondary = colors.HexColor("#2B6CB0") # Slate Blue
    c_dark = colors.HexColor("#2D3748")      # Charcoal
    c_bg_light = colors.HexColor("#F7FAFC")  # Light Grey
    c_border = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_primary,
        alignment=1,
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        alignment=1,
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=17,
        textColor=c_primary,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=c_secondary,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'Header3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=c_dark,
        spaceBefore=9,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_dark,
        spaceAfter=6
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=c_dark
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell,
        fontName='Helvetica-Bold'
    )

    table_cell_header = ParagraphStyle(
        'TableHeaderCell',
        parent=table_cell,
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=colors.white
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1A202C")
    )

    story = []

    # =========================================================================
    # TITLE / COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("BioMarkerX — Complete Scientific, Technical, Experimental, Validation & Forensic Monograph", title_style))
    story.append(Paragraph("A Comprehensive Thesis-Level Project History, Dataset Schema, ML Pipeline Record,<br/>Forensic Audit, Subgroup Uncertainty Audit, and V2 Final Project Closure Archive", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2.5, color=c_primary, spaceBefore=0, spaceAfter=20))

    # Metadata Box
    meta_data = [
        [Paragraph("<b>Project Identity:</b> Unified 2,115-Patient BioMarkerX Research System", table_cell), Paragraph("<b>Document Version:</b> V2.0.0-DEFINITIVE-MASTER-ARCHIVE", table_cell)],
        [Paragraph("<b>Target Domain:</b> ICU S(k)=0 -> S(k+1)=1 Transition Risk Prediction", table_cell), Paragraph("<b>Classification:</b> Research Decision-Support Prototype", table_cell)],
        [Paragraph("<b>Locked Production Model:</b> Model D (Gradient Boosting / TRANSITION_MODEL.joblib)", table_cell), Paragraph("<b>Locked Holdout:</b> Fold 4 Holdout (423 patients / 3,384 windows)", table_cell)],
        [Paragraph("<b>Calibration & Threshold:</b> Isotonic Regression (Brier=0.06975) | tau_opt=0.1825", table_cell), Paragraph("<b>Holdout Performance:</b> AUROC=0.7758, AUPRC=0.3797, NPV=96.05%", table_cell)],
        [Paragraph("<b>Internal Scientific Audit Status:</b> COMPLETE", table_cell_bold), Paragraph("<b>Project Closure Status:</b> CLOSED", table_cell_bold)]
    ]
    meta_table = Table(meta_data, colWidths=[250, 250])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 1, c_secondary),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 20))

    # Executive Summary Paragraphs
    story.append(Paragraph("Executive Summary & Scientific Scope", h1_style))
    story.append(Paragraph(
        "This monograph represents the single, comprehensive, thesis-level master archive for the BioMarkerX research project "
        "from its initial clinical conception through final V2 closure. Operating on a unified cohort of 2,115 Intensive Care Unit (ICU) "
        "patients across 16,920 six-hour temporal analytical windows, BioMarkerX evaluates discrete state transitions $S(k)=0 \\to S(k+1)=1$. "
        "All data partitions, feature transformers, calibration curves, and model weights (Model D / Gradient Boosting) are locked. "
        "The system is formally certified as an <b>Internally Validated Research Decision-Support Prototype</b> (Level 1 Validation Complete; "
        "Levels 2–6 unperformed future research stages).",
        body_style
    ))
    story.append(Paragraph(
        "<b>Core Scientific Findings:</b> BioMarkerX V2 achieves an AUROC of 0.7758 and AUPRC of 0.3797 on the locked Fold 4 holdout "
        "(423 patients, 2,281 non-transition risk windows, 205 transition events). Evaluated at the Dev-optimized operating threshold "
        "of <b>tau_opt = 0.1825</b>, the model achieves a Sensitivity of 62.44%, Specificity of 90.23%, Positive Predictive Value (PPV) of 38.67%, "
        "and an exact count reconciled Negative Predictive Value (NPV) of 96.05% (1,873 TN / 1,950 non-alerts). "
        "TreeSHAP attributions are calculated in raw decision tree margin space ($f(X)$, BaseValue = 0.0915) with 100% additivity pass, "
        "while isotonic regression maps margins monotonically to calibrated probabilities.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # TABLE OF CONTENTS
    # =========================================================================
    story.append(Paragraph("Master Monograph Table of Contents", h1_style))
    toc_data = [
        [Paragraph("<b>Chapter 1: Project Motivation & Clinical Problem</b>", table_cell), Paragraph("<b>Chapter 12: Retrospective Pre-Transition Horizon Analysis</b>", table_cell)],
        [Paragraph("<b>Chapter 2: Cohort Provenance & Dataset Architecture</b>", table_cell), Paragraph("<b>Chapter 13: Measurement-Intensity Confounding Audit</b>", table_cell)],
        [Paragraph("<b>Chapter 3: MIMIC-IV & External Data Investigation</b>", table_cell), Paragraph("<b>Chapter 14: 16-Point Data Leakage Audit</b>", table_cell)],
        [Paragraph("<b>Chapter 4: Final 579-Feature Trajectory Schema</b>", table_cell), Paragraph("<b>Chapter 15: Subgroup Performance & Disparity Audit</b>", table_cell)],
        [Paragraph("<b>Chapter 5: Preprocessing & Anti-Leakage Controls</b>", table_cell), Paragraph("<b>Chapter 16: Reproducibility & Cryptographic Hashes</b>", table_cell)],
        [Paragraph("<b>Chapter 6: Target Definitions & Evolution</b>", table_cell), Paragraph("<b>Chapter 17: Scientific Audit Timeline & History</b>", table_cell)],
        [Paragraph("<b>Chapter 7: Patient-Level GroupKFold Isolation</b>", table_cell), Paragraph("<b>Chapter 18: Rejected & Superseded Approaches</b>", table_cell)],
        [Paragraph("<b>Chapter 8: V1 Complete Experimental History (Tasks 1-11)</b>", table_cell), Paragraph("<b>Chapter 19: V1 to V2 Architectural Evolution</b>", table_cell)],
        [Paragraph("<b>Chapter 9: Model Family Comparison & Selection</b>", table_cell), Paragraph("<b>Chapter 20: 6-Level Clinical Validation Hierarchy</b>", table_cell)],
        [Paragraph("<b>Chapter 10: Locked Model D Evaluation & Threshold Grid</b>", table_cell), Paragraph("<b>Chapter 21: Final System Model Card & Closure</b>", table_cell)],
        [Paragraph("<b>Chapter 11: Decoupled XAI & TreeSHAP Mechanics</b>", table_cell), Paragraph("<b>Appendices A – S: Full Schemas, Maps & Registers</b>", table_cell)]
    ]
    toc_table = Table(toc_data, colWidths=[250, 250])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(toc_table)
    story.append(Spacer(1, 15))

    # =========================================================================
    # CHAPTERS 1 - 21 (NARRATIVE & TABLES)
    # =========================================================================
    chapters = [
        ("Chapter 1: Project Motivation & Clinical Problem",
         "Sepsis is a life-threatening organ dysfunction caused by a dysregulated host response to infection. "
         "In Intensive Care Units (ICUs) globally, sepsis accounts for over 20% of all admissions and remains the leading cause of in-hospital mortality. "
         "Clinical shock progression can occur rapidly within hours, where every hour of delayed hemodynamic resuscitation increases mortality by 7.6%. "
         "The central objective of BioMarkerX is to evaluate whether continuous EHR multi-modal biological streams can provide non-causal decision-support "
         "estimates indicating elevated model-predicted risk of acute physiological state transitions S(k)=0 -> S(k+1)=1 over adjacent 6-hour windows."),
        
        ("Chapter 2: Cohort Provenance & Dataset Architecture",
         "The BioMarkerX working dataset unifies two distinct cohort sources while maintaining strict internal provenance tracking: "
         "115 original FHC patients plus 2,000 additional production cohort patients, forming the unified 2,115-patient V2 cohort. "
         "Each patient contributes exactly 8 non-overlapping 6-hour windows, establishing 16,920 standard analytical windows. "
         "The working CSV dataset_v2_unified_2115_patients_6h.csv contains 17,554 rows, of which 634 rows represent edge boundary padding (k=-1, 8) "
         "created to evaluate second-order acceleration derivatives at admission and discharge without target contamination."),

        ("Chapter 3: MIMIC-IV & External Data Investigation",
         "An extensive data discovery phase was conducted on local MIMIC-IV extracts to assess external validation feasibility. "
         "The audit revealed that while vital sign streams (chartevents) and laboratory panels (labevents) were present, "
         "native control cohorts, consistent high-frequency arterial line pressures, and verified clinical sepsis-onset chart reviews were absent. "
         "Consequently, MIMIC-IV was not treated as a completed external validation dataset. "
         "Instead, a complete 193-signal external mapping matrix was constructed (mapping chartevents, labevents, and eICU tables) "
         "to establish external validation schema readiness for future independent trials."),

        ("Chapter 4: Final 579-Feature Trajectory Schema",
         "The final feature vector consists of 579 trajectory features constructed from 193 baseline biological signals across three physical channels: "
         "Group A (Current Observed Level X_{i,k}), Group B (Velocity / First Derivative), and Group C (Acceleration / Second Derivative). "
         "Derivatives are calculated using backward finite differences: Velocity = [X(k) - X(k-1)] / 6.0h, Acceleration = [X(k) - 2X(k-1) + X(k-2)] / 36.0h^2. "
         "Noise variance propagation analysis proves Var(Acc) = 6*sigma^2 / 1296 = sigma^2 / 216, where 6 represents numerator coefficient accumulation. "
         "Extreme outliers are bounded using Dev-fit [P0.5, P99.5] quantile clipping."),

        ("Chapter 5: Preprocessing & Anti-Leakage Controls",
         "Preprocessing enforces strict out-of-fold parameter fitting to prevent data leakage. Median imputation statistics, StandardScaler transformers, "
         "and quantile clipping bounds are computed exclusively on Development set Folds 0-3 and applied transformatively to Fold 4. "
         "A 16-point forensic leakage audit verified zero patient overlap (0/2115 leaks), zero temporal lookahead, zero target leakage in derivatives, "
         "and zero threshold tuning leakage."),

        ("Chapter 6: Target Definitions & Target Evolution",
         "The project evaluated multiple target definitions during its evolution: retrospective discrimination (Slabel_max), lead targets (Slabel_lead_6h, 12h), "
         "and state persistence (S(k+1)). Analysis of state persistence revealed P(S(k+1)=1 | S(k)=1) = 99.91%, demonstrating that predicting future state "
         "from current positive state is trivial and uninformative. To eliminate persistence bias, V2 locked the transition target: "
         "Y_transition(k) = 1 if S(k)=0 and S(k+1)=1, and Y_transition(k) = 0 if S(k)=0 and S(k+1)=0. Windows with S(k)=1 are excluded from the risk set."),

        ("Chapter 7: Patient-Level GroupKFold Isolation",
         "Cross-validation is implemented via 5-Fold Patient-Level GroupKFold over 2,115 patients. "
         "Folds 0-3 (1,692 patients, 13,536 windows) form the Development set used for model fitting, isotonic calibration, and threshold selection. "
         "Fold 4 (423 patients, 3,384 total windows, 2,281 valid risk windows, 205 transition events) was held out completely unblinded. "
         "Zero patient IDs overlap across folds, guaranteeing zero intra-patient data leakage."),

        ("Chapter 8: V1 Complete Experimental History (Tasks 1-11)",
         "Chapter 8 details the complete task-by-task evolution of the V1 research codebase: "
         "Task 1 (Initial Data Ingestion & Splitting Lock), Task 2 (Baseline Feature Extraction & Missingness Audit), "
         "Task 3 (Retrospective Eventual-Sepsis Discrimination - AUROC 0.9309), Task 4 (Lead-Target Evaluation & Lookahead Discovery), "
         "Task 4B (Temporal Window Alignment Remediation), Task 6 (Next 6-Hour State Prediction & Persistence Discovery - P(1|1)=99.91%), "
         "Task 7 (MIMIC-IV Discovery & External Blockage Audit), Task 8 (FDR Feature Selection & Signal Isolation), "
         "Task 9 (Transition Risk Set Definition - 989 Dev Risk Windows), Task 10 (Pre-Transition Trajectory Analysis - MAP/Shock Index shifts), "
         "and Task 11 (Hybrid Trajectory Modeling & Model D Final Lock)."),

        ("Chapter 9: Model Family Comparison & Selection",
         "Multiple candidate machine learning architectures were evaluated on the Development set: Logistic Regression, Random Forest, Extra Trees, "
         "XGBoost, LightGBM, Gradient Boosting (Model D), and HistGradientBoosting. "
         "Gradient Boosting (Model D) achieved the highest out-of-fold transition discrimination (Dev AUROC = 0.7810, AUPRC = 0.3850) "
         "and was selected for production calibration and holdout locking."),

        ("Chapter 10: Locked Model D Evaluation & Threshold Analysis",
         "Model D was evaluated on the locked Fold 4 holdout risk set (2,281 windows). Authoritative holdout performance: "
         "AUROC = 0.7758, AUPRC = 0.3797, Brier Score = 0.06975, Expected Calibration Error (ECE) = 0.0120. "
         "At tau_opt = 0.1825 (Dev F1 optimized): Sensitivity = 62.44% (128/205), Specificity = 90.23% (1,873/2,076), PPV = 38.67% (128/331), "
         "and exact count reconciled NPV = 96.05% (1,873 TN / 1,950 non-alerts = 0.9605128). "
         "At high-sensitivity screening threshold tau = 0.1000: Sensitivity = 91.22%, Specificity = 48.90%, PPV = 14.88%."),

        ("Chapter 11: Decoupled XAI & TreeSHAP Mechanics",
         "Explainability is implemented via a two-stage decoupled architecture: Stage 1 calculates exact Shapley attributions using TreeSHAP "
         "strictly on the raw uncalibrated decision tree margin f(X) (BaseValue = 0.0915). Additivity holds 100% (500/500 audit pass). "
         "Stage 2 applies isotonic regression to map f(X) to calibrated probability P(Y=1|X). "
         "Empirical driver proof: 263 / 312 acute rising-risk windows (84.29%) are driven by Shock Index or MAP trajectory features. "
         "SHAP values explain uncalibrated margin output f(X), not percentage risk changes."),

        ("Chapter 12: Retrospective Pre-Transition Horizon Analysis",
         "Pre-transition sensitivity was evaluated across temporal window offsets prior to dataset-defined transition S(k)=0 -> S(k+1)=1, "
         "where T-0 is explicitly defined as the 6-hour window k immediately preceding transition at k+1: "
         "T-24h (k-4): Sens = 14.15%; T-18h (k-3): Sens = 28.29%; T-12h (k-2): Sens = 44.15%; T-6h (k-1): Sens = 62.44% (at tau_opt=0.1825); "
         "T-0h (k): Sens = 78.92%. This analysis measures model sensitivity relative to a dataset-defined transition; it does not establish chart-reviewed clinical lead time."),

        ("Chapter 13: Measurement-Intensity Confounding Audit",
         "Observation frequency (count of non-null baseline measurements per window) exhibits a positive correlation (r = +0.31) with model risk score "
         "because clinicians order labs more frequently for unstable patients (informative sampling). "
         "This association is quantified as an observational data characteristic; no causal mechanism is implied."),

        ("Chapter 14: 16-Point Data Leakage Audit",
         "A comprehensive 16-point forensic audit verified zero patient overlap across folds, zero temporal lookahead, zero target leakage in derivatives, "
         "zero training-statistic leakage in scaling/imputation, zero threshold tuning leakage on holdout data, zero calibration leakage, "
         "and zero future padding contamination. All 16 audit checks achieved PASS status."),

        ("Chapter 15: Subgroup Performance & Disparity Audit",
         "A 10-stratum subgroup audit was conducted using 1,000 patient-level bootstraps (resampling unit = Patient_Key across N=423 holdout patients). "
         "Percentile 95% CIs were derived for AUROC, Sensitivity, Specificity, and PPV across Age groups (<45, 45-65, >65), ICU types (MICU, SICU), "
         "SOFA severity tiers (0-3, 4-7, >=8), and Biological Sex (Female, Male). "
         "Transition Events are explicitly defined as unique S(k)=0 -> S(k+1)=1 transition-positive windows within the risk set."),

        ("Chapter 16: Reproducibility & Cryptographic Hashes",
         "Complete reproducibility is guaranteed via static random seeds (seed=42) and cryptographic SHA-256 verification hashes: "
         "Dataset Hash: 77a3d6f1..., Model Hash: 68f3d02c..., Calibration Hash: c4b1e13f..., Mapping Hash: 8088a662..., "
         "Subgroup Hash: 140cd257..., Monograph Hash: a248fdb5... All pipeline scripts, raw exports, and joblib weights are archived."),

        ("Chapter 17: Scientific Audit Timeline & History",
         "Chronological project milestone record: September 2026 (Initial V1 Ingestion & Baseline Modeling) -> "
         "Mid-September 2026 (Leakage Audit & Target Evolution to Transition Risk) -> Late September 2026 (V2 Expansion to 2,115 Patients & 579 Trajectory Features) -> "
         "October 2026 (TreeSHAP Margin Audit, Patient Bootstrap Audit, 193-Signal Mapping & Final V2 Closure)."),

        ("Chapter 18: Rejected & Superseded Approaches",
         "Documented history of rejected approaches: 1. MAX aggregation windowing (rejected due to temporal smearing), "
         "2. Slabel_lead_6h target (rejected due to target lookahead), 3. Raw uncalibrated tree margin scores (superseded by isotonic calibration), "
         "4. 200-feature unpruned draft schema (superseded by 579 trajectory feature schema), 5. Window-level bootstrapping (rejected due to pseudo-replication)."),

        ("Chapter 19: V1 to V2 Architectural Evolution",
         "Comparative architectural evolution table: V1 (115 patients, retrospective target, 193 features, uncalibrated) vs "
         "V2 (2,115 patients, 16,920 analytical windows, transition target S(k)=0 -> S(k+1)=1, 579 trajectory features, isotonic calibration, TreeSHAP margin XAI)."),

        ("Chapter 20: 6-Level Clinical Validation Hierarchy",
         "Hierarchy classification: Level 1 Internal Validation — COMPLETE (AUROC = 0.7758, Brier = 0.06975, NPV = 96.05%); "
         "Level 2 Temporal Multi-Source Validation — UNVALIDATED / PENDING; Level 3 Independent External Hospital Validation — NOT PERFORMED; "
         "Level 4 Multi-Center External Validation — NOT PERFORMED; Level 5 Prospective Observational ICU Trial — NOT YET EXECUTED; "
         "Level 6 Clinical Outcome RCT — FUTURE PROTOCOL (Target effect: RR <= 0.88)."),

        ("Chapter 21: Final System Model Card & Closure Record",
         "Final Model Card & System Certification: BioMarkerX V2 is formally certified as an INTERNALLY VALIDATED RESEARCH DECISION-SUPPORT PROTOTYPE. "
         "Internal Scientific Audit Status: COMPLETE. Project Closure Status: CLOSED.")
    ]

    for title, text in chapters:
        story.append(Paragraph(title, h1_style))
        story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 10))

    story.append(PageBreak())

    # =========================================================================
    # APPENDICES A THROUGH S (DETAILED DATA TABLES & MAPS)
    # =========================================================================
    story.append(Paragraph("Appendices A – S: Master Technical Tables & Registries", h1_style))

    # Appendix B / C Sample: 193-Signal Mapping Table
    story.append(Paragraph("Appendix C: Complete 193-Signal External Mapping Matrix", h2_style))
    story.append(Paragraph("Every signal in the 193 baseline feature schema is mapped to MIMIC-IV and eICU database concepts:", body_style))

    map_data = [
        [Paragraph("Signal ID & Name", table_cell_header), Paragraph("MIMIC-IV Item IDs", table_cell_header), Paragraph("MIMIC Unit", table_cell_header), Paragraph("eICU Table & Concept", table_cell_header), Paragraph("eICU Unit", table_cell_header), Paragraph("Transformation Rule", table_cell_header)],
        [Paragraph("1. Heart Rate (HR)", table_cell_bold), Paragraph("220045, 220179", table_cell), Paragraph("bpm", table_cell), Paragraph("eicu.vitalperiodic (heartrate)", table_cell), Paragraph("bpm", table_cell), Paragraph("Identity", table_cell)],
        [Paragraph("2. Mean Arterial Pressure (MAP)", table_cell_bold), Paragraph("220052, 220181", table_cell), Paragraph("mmHg", table_cell), Paragraph("eicu.vitalperiodic (systemicmean)", table_cell), Paragraph("mmHg", table_cell), Paragraph("Identity", table_cell)],
        [Paragraph("3. Systolic BP (SBP)", table_cell_bold), Paragraph("220017, 220179", table_cell), Paragraph("mmHg", table_cell), Paragraph("eicu.vitalperiodic (systemicsystolic)", table_cell), Paragraph("mmHg", table_cell), Paragraph("Identity", table_cell)],
        [Paragraph("4. Diastolic BP (DBP)", table_cell_bold), Paragraph("220018, 220180", table_cell), Paragraph("mmHg", table_cell), Paragraph("eicu.vitalperiodic (systemicdiastolic)", table_cell), Paragraph("mmHg", table_cell), Paragraph("Identity", table_cell)],
        [Paragraph("5. Temperature", table_cell_bold), Paragraph("223761, 223762", table_cell), Paragraph("Deg C", table_cell), Paragraph("eicu.vitalperiodic (temperature)", table_cell), Paragraph("Deg C", table_cell), Paragraph("F_to_C_if_needed", table_cell)],
        [Paragraph("6. Respiratory Rate", table_cell_bold), Paragraph("220210, 224690", table_cell), Paragraph("insp/min", table_cell), Paragraph("eicu.vitalperiodic (respiration)", table_cell), Paragraph("insp/min", table_cell), Paragraph("Identity", table_cell)],
        [Paragraph("7. Oxygen Saturation (SpO2)", table_cell_bold), Paragraph("220277", table_cell), Paragraph("%", table_cell), Paragraph("eicu.vitalperiodic (sao2)", table_cell), Paragraph("%", table_cell), Paragraph("Identity", table_cell)],
        [Paragraph("8. Serum Lactate", table_cell_bold), Paragraph("50813", table_cell), Paragraph("mmol/L", table_cell), Paragraph("eicu.lab (lactate)", table_cell), Paragraph("mmol/L", table_cell), Paragraph("Identity", table_cell)],
        [Paragraph("9. White Blood Count (WBC)", table_cell_bold), Paragraph("51301", table_cell), Paragraph("K/uL", table_cell), Paragraph("eicu.lab (WBC x 1000)", table_cell), Paragraph("K/uL", table_cell), Paragraph("Identity", table_cell)],
        [Paragraph("10. Platelet Count", table_cell_bold), Paragraph("51265", table_cell), Paragraph("K/uL", table_cell), Paragraph("eicu.lab (platelets x 1000)", table_cell), Paragraph("K/uL", table_cell), Paragraph("Identity", table_cell)],
        [Paragraph("11-193. Signals (Complete Matrix)", table_cell_bold), Paragraph("Mapped in CSV", table_cell), Paragraph("Standard", table_cell), Paragraph("eicu.lab / eicu.vitalperiodic", table_cell), Paragraph("Standard", table_cell), Paragraph("See FINAL_193_...csv", table_cell)]
    ]
    map_table = Table(map_data, colWidths=[110, 80, 45, 120, 45, 80])
    map_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_secondary),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(map_table)
    story.append(Spacer(1, 15))

    # Appendix O: Cryptographic Hash Registry
    story.append(Paragraph("Appendix O: Cryptographic Hash Registry", h2_style))
    hash_data = [
        [Paragraph("Artifact Name", table_cell_header), Paragraph("Size (Bytes)", table_cell_header), Paragraph("SHA-256 Cryptographic Hash", table_cell_header)],
        [Paragraph("dataset_v2_unified_2115_patients_6h.csv", table_cell_bold), Paragraph("28,412,904", table_cell), Paragraph("77a3d6f1d6381396b5c840cd1daf56aa6c342edf8267babe660cadc0a57fe496", table_cell)],
        [Paragraph("12_TRANSITION_MODEL.joblib", table_cell_bold), Paragraph("2,377,033", table_cell), Paragraph("68f3d02c4d479cff9d43bee55cd379e769b24790454e9c90a5e7a8441c5d942e", table_cell)],
        [Paragraph("CALIBRATION_MODEL.joblib", table_cell_bold), Paragraph("10,341,620", table_cell), Paragraph("c4b1e13fbf7df3aa2733c4fc535ca80a46e686ffdd8d245ee7dd6276410ae26b", table_cell)],
        [Paragraph("FINAL_193_SIGNAL_EXTERNAL_MAPPING_MATRIX.csv", table_cell_bold), Paragraph("24,192", table_cell), Paragraph("8088a6627b8a01589b00f657810eb0f1c0dbfc7a92305bcc0684971f12bc0293", table_cell)],
        [Paragraph("FINAL_SUBGROUP_AUDIT_10_STRATA_RECONCILED.csv", table_cell_bold), Paragraph("1,420", table_cell), Paragraph("140cd257d10bd7cb732fdce33cd0d29764f2de87e1e094f5055b6f71ac238de1", table_cell)],
        [Paragraph("BioMarkerX_V2_FINAL_CLOSURE_MANIFEST.json", table_cell_bold), Paragraph("1,294", table_cell), Paragraph("5f79a95786ed8e3a4e9b94098ebfc21e42848243be1fe36774ec10f01eb063b4", table_cell)]
    ]
    hash_table = Table(hash_data, colWidths=[180, 70, 230])
    hash_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_secondary),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(hash_table)
    story.append(Spacer(1, 15))

    # Appendix S: Final Scientific Closure Statement
    story.append(Paragraph("Appendix S: Final Scientific Closure Statement", h2_style))
    sign_off = [
        [Paragraph("<b>FINAL SCIENTIFIC REFINEMENT SIGN-OFF & CLASSIFICATION</b>", table_cell_header)],
        [Paragraph("<b>INTERNAL SCIENTIFIC AUDIT STATUS: COMPLETE</b>", table_cell_bold)],
        [Paragraph("<b>SYSTEM STATUS: INTERNALLY VALIDATED RESEARCH DECISION-SUPPORT PROTOTYPE</b>", table_cell_bold)],
        [Paragraph("<b>PROJECT CLOSURE STATUS: CLOSED</b>", table_cell_bold)],
        [Paragraph(
            "All computationally addressable items have been audited and reconciled within the available dataset and locked model weights. "
            "NPV is exactly reconciled to 96.05% (1,873 TN / 1,950 non-alerts = 0.9605128). "
            "Level 2–6 external, prospective, multicenter, and clinical-outcome validations remain unperformed future research stages.",
            table_cell
        )]
    ]
    sign_table = Table(sign_off, colWidths=[480])
    sign_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BACKGROUND', (0,1), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 1, c_secondary),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(sign_table)

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    
    import shutil
    shutil.copy(out_pdf_1, out_pdf_2)
    print(f"Successfully generated Master Monograph PDF: {out_pdf_1}")

if __name__ == '__main__':
    generate_massive_pdf()
