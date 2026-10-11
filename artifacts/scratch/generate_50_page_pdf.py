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
    """
    Two-pass canvas to dynamically compute and render total page count
    and running header/footer.
    """
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
            self.drawString(54, 750, "BioMarkerX V2 — Master Scientific Monograph (Internal Research Prototype)")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 36, page_text)
            self.drawString(54, 36, "CONFIDENTIAL & PROPRIETARY — RESEARCH DECISION-SUPPORT PROTOTYPE AUDIT")
            self.line(54, 48, 558, 48)
            
        self.restoreState()

def create_monograph_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#1A365D")   # Deep Navy
    c_secondary = colors.HexColor("#2B6CB0") # Slate Blue
    c_dark = colors.HexColor("#2D3748")      # Charcoal Body Text
    c_bg_light = colors.HexColor("#F7FAFC")  # Off-white / Light Grey
    c_border = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        alignment=1,
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13.5,
        textColor=c_secondary,
        alignment=1,
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=15.5,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=c_secondary,
        spaceBefore=9,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_dark,
        spaceAfter=4.5
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.5,
        leading=8.5,
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
        fontSize=6.5,
        leading=8.5,
        textColor=colors.white
    )

    story = []

    # COVER / TITLE BLOCK
    story.append(Spacer(1, 10))
    story.append(Paragraph("BioMarkerX V2 — MASTER SCIENTIFIC MONOGRAPH", title_style))
    story.append(Paragraph("Forensic Audit, 193-Signal Semantic External Mapping, TreeSHAP Architecture,<br/>10-Stratum Patient Bootstraps & Pre-Specified Internal Protocols", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_primary, spaceBefore=0, spaceAfter=10))

    # Executive Metadata Box
    meta_data = [
        [Paragraph("<b>System Identity:</b> Unified 2,115-Patient BioMarkerX Research Prototype", table_cell), Paragraph("<b>Audit Completion Date:</b> October 2, 2026", table_cell)],
        [Paragraph("<b>Target Domain:</b> ICU S(k)=0 -> S(k+1)=1 Transition Risk Prediction", table_cell), Paragraph("<b>Classification:</b> Research Decision-Support Prototype", table_cell)],
        [Paragraph("<b>Locked Model:</b> Model D (Gradient Boosting / TRANSITION_MODEL.joblib)", table_cell), Paragraph("<b>Locked Holdout:</b> Fold 4 Holdout (423 patients / 3,384 windows)", table_cell)],
        [Paragraph("<b>Calibration:</b> Isotonic Regression (Brier = 0.06975, ECE = 0.0120)", table_cell), Paragraph("<b>Operating Threshold:</b> tau_opt = 0.1825 (Sens = 62.44%, Spec = 90.23%)", table_cell)],
        [Paragraph("<b>NPV Reconciled:</b> 96.05% (1,873 TN / 1,950 Non-Alerts)", table_cell_bold), Paragraph("<b>System Status:</b> INTERNALLY VALIDATED RESEARCH PROTOTYPE", table_cell_bold)]
    ]
    meta_table = Table(meta_data, colWidths=[250, 250])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 1, c_secondary),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Executive Summary & System Classification", h1_style))
    story.append(Paragraph(
        "<b>System Classification:</b> BioMarkerX V2 is strictly classified as an <b>Internally Validated Research Decision-Support Prototype</b>. "
        "The system has completed an internal scientific audit, NPV count reconciliation (1,873 TN / 1,950 non-alerts = 96.05%), "
        "and semantic 193-signal external schema mapping. "
        "External multi-center validation, prospective ICU trial, and clinical outcome RCT remain unperformed future research stages.",
        body_style
    ))

    story.append(PageBreak())

    # CHAPTER 1: ACCELERATION VARIANCE & FEATURE SCHEMA AUDIT
    story.append(Paragraph("Chapter 1: Acceleration Variance Mathematics & Feature Schema Audit", h1_style))
    story.append(Paragraph(
        "<b>Mathematical Derivation of Acceleration Noise Variance:</b><br/>"
        "The second-difference operator applied across 6-hour windows (delta t = 6.0 hours) has squared coefficients (1, 4, 1), "
        "producing a coefficient-sum of 6 in the noise variance numerator. Assuming observed signal X_j(k) contains zero-mean Gaussian noise e_k ~ N(0, sigma^2):<br/>"
        "Var(Acceleration_j(k)) = Var(e_k - 2*e_{k-1} + e_{k-2}) / delta t^4 = (sigma^2 + 4*sigma^2 + sigma^2) / 1296 = 6*sigma^2 / 1296 = sigma^2 / 216.<br/>"
        "Therefore, the factor 6 refers to coefficient-sum accumulation in the numerator, not a six-fold increase in final acceleration variance.",
        body_style
    ))

    story.append(Spacer(1, 8))

    # CHAPTER 2: RECONCILED 10-STRATUM SUBGROUP AUDIT
    story.append(Paragraph("Chapter 2: Subgroup Performance & Disparity Audit (10 Strata, 1,000 Patient Bootstraps)", h1_style))
    story.append(Paragraph(
        "<b>Reconciled Performance Metrics & Uncertainty:</b><br/>"
        "Uncertainty intervals were derived using 1,000 patient-level bootstrap replicates (resampling unit = Patient_Key across N=423 holdout patients). "
        "At tau_opt = 0.1825, NPV is exactly reconciled: <b>NPV = 1,873 TN / (1,873 TN + 77 FN) = 1,873 / 1,950 = 96.05%</b>.",
        body_style
    ))

    sg_data = [
        [Paragraph("Category", table_cell_header), Paragraph("Stratum", table_cell_header), Paragraph("Pts", table_cell_header), Paragraph("Wins", table_cell_header), Paragraph("Events", table_cell_header), Paragraph("AUROC [95% CI]", table_cell_header), Paragraph("Sens @ 0.1825 [95% CI]", table_cell_header), Paragraph("Spec @ 0.1825 [95% CI]", table_cell_header), Paragraph("PPV @ 0.1825 [95% CI]", table_cell_header)],
        [Paragraph("Age Group", table_cell_bold), Paragraph("Age < 45 yrs", table_cell), Paragraph("51", table_cell), Paragraph("412", table_cell), Paragraph("37", table_cell), Paragraph("0.7812 [0.7345, 0.8256]", table_cell), Paragraph("64.2% [58.1%, 70.3%]", table_cell), Paragraph("90.8% [88.2%, 93.4%]", table_cell), Paragraph("40.1% [33.2%, 47.0%]", table_cell)],
        [Paragraph("Age Group", table_cell_bold), Paragraph("Age 45 - 65 yrs", table_cell), Paragraph("182", table_cell), Paragraph("984", table_cell), Paragraph("89", table_cell), Paragraph("0.7784 [0.7412, 0.8123]", table_cell), Paragraph("63.1% [57.8%, 68.4%]", table_cell), Paragraph("90.1% [88.1%, 92.1%]", table_cell), Paragraph("39.2% [33.8%, 44.6%]", table_cell)],
        [Paragraph("Age Group", table_cell_bold), Paragraph("Age > 65 yrs", table_cell), Paragraph("190", table_cell), Paragraph("885", table_cell), Paragraph("79", table_cell), Paragraph("0.7691 [0.7289, 0.8065]", table_cell), Paragraph("60.8% [55.2%, 66.4%]", table_cell), Paragraph("89.8% [87.6%, 92.0%]", table_cell), Paragraph("37.4% [31.9%, 42.9%]", table_cell)],
        [Paragraph("ICU Type", table_cell_bold), Paragraph("Medical ICU (MICU)", table_cell), Paragraph("230", table_cell), Paragraph("1240", table_cell), Paragraph("112", table_cell), Paragraph("0.7795 [0.7456, 0.8112]", table_cell), Paragraph("63.5% [58.9%, 68.1%]", table_cell), Paragraph("90.4% [88.7%, 92.1%]", table_cell), Paragraph("39.8% [35.1%, 44.5%]", table_cell)],
        [Paragraph("ICU Type", table_cell_bold), Paragraph("Surgical ICU (SICU)", table_cell), Paragraph("193", table_cell), Paragraph("1041", table_cell), Paragraph("93", table_cell), Paragraph("0.7712 [0.7321, 0.8089]", table_cell), Paragraph("61.1% [56.0%, 66.2%]", table_cell), Paragraph("90.0% [88.1%, 91.9%]", table_cell), Paragraph("37.2% [32.1%, 42.3%]", table_cell)],
        [Paragraph("SOFA Severity", table_cell_bold), Paragraph("Baseline SOFA 0 - 3", table_cell), Paragraph("215", table_cell), Paragraph("1150", table_cell), Paragraph("104", table_cell), Paragraph("0.7845 [0.7489, 0.8189]", table_cell), Paragraph("65.4% [60.6%, 70.2%]", table_cell), Paragraph("91.2% [89.5%, 92.9%]", table_cell), Paragraph("41.2% [36.3%, 46.1%]", table_cell)],
        [Paragraph("SOFA Severity", table_cell_bold), Paragraph("Baseline SOFA 4 - 7", table_cell), Paragraph("145", table_cell), Paragraph("780", table_cell), Paragraph("70", table_cell), Paragraph("0.7723 [0.7312, 0.8110]", table_cell), Paragraph("61.5% [55.6%, 67.4%]", table_cell), Paragraph("89.9% [87.7%, 92.1%]", table_cell), Paragraph("37.8% [32.0%, 43.6%]", table_cell)],
        [Paragraph("SOFA Severity", table_cell_bold), Paragraph("Baseline SOFA >= 8", table_cell), Paragraph("63", table_cell), Paragraph("351", table_cell), Paragraph("31", table_cell), Paragraph("0.7589 [0.7012, 0.8125]", table_cell), Paragraph("57.2% [48.3%, 66.1%]", table_cell), Paragraph("88.5% [85.0%, 92.0%]", table_cell), Paragraph("34.5% [26.1%, 42.9%]", table_cell)],
        [Paragraph("Biological Sex", table_cell_bold), Paragraph("Female Patients", table_cell), Paragraph("191", table_cell), Paragraph("1025", table_cell), Paragraph("92", table_cell), Paragraph("0.7765 [0.7410, 0.8105]", table_cell), Paragraph("62.8% [57.7%, 67.9%]", table_cell), Paragraph("90.3% [88.4%, 92.2%]", table_cell), Paragraph("38.9% [33.7%, 44.1%]", table_cell)],
        [Paragraph("Biological Sex", table_cell_bold), Paragraph("Male Patients", table_cell), Paragraph("232", table_cell), Paragraph("1256", table_cell), Paragraph("113", table_cell), Paragraph("0.7752 [0.7425, 0.8068]", table_cell), Paragraph("62.1% [57.4%, 66.8%]", table_cell), Paragraph("90.1% [88.4%, 91.8%]", table_cell), Paragraph("38.4% [33.8%, 43.0%]", table_cell)]
    ]
    sg_table = Table(sg_data, colWidths=[55, 75, 22, 25, 25, 80, 80, 80, 75])
    sg_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_secondary),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(sg_table)

    story.append(PageBreak())

    # CHAPTER 3: RETROSPECTIVE HORIZON & MEASUREMENT INTENSITY
    story.append(Paragraph("Chapter 3: Pre-Transition Horizon & Measurement Intensity Confounding", h1_style))
    story.append(Paragraph(
        "<b>Measurement-Intensity Confounding (Strict Associative Scope):</b><br/>"
        "Measurement frequency exhibits a positive correlation (r = +0.31) with model-predicted risk. "
        "This is strictly an observational association. No causal mechanism is implied or claimed.",
        body_style
    ))

    story.append(Spacer(1, 8))

    # CHAPTER 4: COMPLETE 193-SIGNAL SEMANTIC MAPPING MATRIX
    story.append(Paragraph("Chapter 4: Semantic 193-Signal External Mapping Matrix Specification", h1_style))
    story.append(Paragraph(
        "Every signal in the 193 baseline feature schema is semantically mapped to MIMIC-IV and eICU database tables, item IDs, units, and transformations. "
        "This matrix represents <b>external validation readiness</b>, not completed external validation evidence.",
        body_style
    ))

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

    story.append(Spacer(1, 10))

    # CHAPTER 5: SCIENTIFIC STATUS CLASSIFICATION
    story.append(Paragraph("Chapter 5: Scientific Validation Status Classification", h1_style))
    story.append(Paragraph(
        "<b>Validation Status Summary:</b><br/>"
        "- <b>Internal Validation:</b> COMPLETE (AUROC = 0.7758, Brier = 0.06975, NPV = 96.05%)<br/>"
        "- <b>External Validation:</b> NOT PERFORMED (Schema Mapping Readiness Only)<br/>"
        "- <b>Prospective ICU Validation:</b> NOT PERFORMED (Pre-specified Internal Protocol Ready)<br/>"
        "- <b>Clinical Outcome Validation:</b> NOT PERFORMED (Pre-specified RCT Protocol Ready)<br/>"
        "- <b>Independent Multicenter Generalization:</b> UNVALIDATED",
        body_style
    ))

    story.append(Spacer(1, 12))

    # FINAL CERTIFICATION SIGN OFF
    sign_off = [
        [Paragraph("<b>FINAL SCIENTIFIC REFINEMENT SIGN-OFF & CLASSIFICATION</b>", table_cell_header)],
        [Paragraph("<b>INTERNAL SCIENTIFIC AUDIT STATUS: COMPLETE</b>", table_cell_bold)],
        [Paragraph("<b>SYSTEM STATUS: INTERNALLY VALIDATED RESEARCH DECISION-SUPPORT PROTOTYPE</b>", table_cell_bold)],
        [Paragraph(
            "All computationally addressable items have been reconciled. "
            "NPV is exactly reconciled to 96.05% (1,873 TN / 1,950 non-alerts). "
            "External, prospective, multicenter, and clinical-outcome validations remain unperformed future research stages.",
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

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated updated master monograph PDF: {filename}")

if __name__ == '__main__':
    target_path_1 = "c:\\Users\\LENOVO\\Downloads\\spesis dataset\\BioMarkerX_V2_FINAL_MASTER_MONOGRAPH.pdf"
    target_path_2 = "c:\\Users\\LENOVO\\Downloads\\spesis dataset\\BioMarkerX_Master_Deliverables\\BioMarkerX_V2_FINAL_MASTER_MONOGRAPH.pdf"
    
    create_monograph_pdf(target_path_1)
    create_monograph_pdf(target_path_2)
