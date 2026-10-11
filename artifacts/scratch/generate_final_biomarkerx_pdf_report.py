import os
import sys
import json
import time
import pandas as pd
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
            self.drawString(54, 750, "BioMarkerX — Final Scientific Validation Report & Audit Monograph")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 36, page_text)
            self.drawString(54, 36, "CONFIDENTIAL & PROPRIETARY — RESEARCH DECISION-SUPPORT PROTOTYPE")
            self.line(54, 48, 558, 48)
            
        self.restoreState()

def build_final_pdf_report():
    print("=========================================================================")
    print("BUILDING FINAL BIOMARKERX SCIENTIFIC VALIDATION REPORT PDF (REFINED)")
    print("=========================================================================")

    out_pdf = r"FINAL_BIOMARKERX\reports\BioMarkerX_FINAL_SCIENTIFIC_VALIDATION_REPORT.pdf"
    os.makedirs(os.path.dirname(out_pdf), exist_ok=True)

    doc = SimpleDocTemplate(
        out_pdf,
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
    c_bg_light = colors.HexColor("#F7FAFC")  # Light Background
    c_border = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=20, leading=24,
        textColor=c_primary, alignment=1, spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, leading=13.5,
        textColor=c_secondary, alignment=1, spaceAfter=14
    )
    h1_style = ParagraphStyle(
        'Header1', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=13, leading=16.5,
        textColor=c_primary, spaceBefore=14, spaceAfter=8, keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Header2', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10.5, leading=13.5,
        textColor=c_secondary, spaceBefore=10, spaceAfter=5, keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyTextCustom', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12,
        textColor=c_dark, spaceAfter=7
    )
    code_style = ParagraphStyle(
        'CodeStyle', parent=styles['Normal'],
        fontName='Courier', fontSize=7.5, leading=9.5,
        textColor=colors.HexColor("#1A202C")
    )

    story = []

    story.append(Spacer(1, 15))
    story.append(Paragraph("BioMarkerX — Final Scientific Validation Report", title_style))
    story.append(Paragraph("A Rigorous Methodological Audit, Causal Feature Architecture, Patient-Grouped Development, and Historical External Re-Evaluation of Early Sepsis Transition Prediction", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=4, spaceAfter=12))

    meta_table_data = [
        [Paragraph("<b>Authoritative Model Artifact:</b> HistGradientBoostingClassifier (.joblib)", body_style), Paragraph("<b>Pipeline Lock Status:</b> LOCKED & FREEZE COMPLETE", body_style)],
        [Paragraph("<b>Target Boundary Windows:</b> k ∈ [0..6] (where k+1 ≤ 7)", body_style), Paragraph("<b>Reproducibility Status:</b> 100% VERIFIED PASS", body_style)],
        [Paragraph("<b>Development Dataset:</b> Dev Unified Cohort (2,115 Patients)", body_style), Paragraph("<b>Historical External Cohort:</b> PhysioNet 2019 (Test A, 3,000 Patients)", body_style)]
    ]
    t_meta = Table(meta_table_data, colWidths=[250, 250])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 12))

    # SECTION 1: EXECUTIVE SUMMARY & REFINEMENTS
    story.append(Paragraph("1. Executive Summary & Methodological Refinements", h1_style))
    
    corrections_text = """
    • <b>Provenance of Threshold τ=0.1825:</b> τ=0.1825 is a historical benchmark threshold carried over from locked Model D operating policy; it is evaluated purely to benchmark policy transportability across iterations.<br/>
    • <b>Observational Non-Causal Wording:</b> External AUROC drop is described as <i>associated with cross-site distributional shifts in patient characteristics and measurement practices</i>.<br/>
    • <b>External Probabilistic Performance:</b> External predictions demonstrate poor overall probabilistic accuracy (Brier score 0.02922 vs constant prevalence baseline 0.01182), and formal external calibration is not established.<br/>
    • <b>Recalibration Requirement Language:</b> Operational deployment would require target-population recalibration and prospective validation in the specific clinical environment.<br/>
    • <b>Measurement Context Nuance:</b> Measurement context alone yielded modest discrimination (AUROC 0.5448) in evaluated tree models.<br/>
    • <b>Baseline AUROC Clarification:</b> 0.8288 is uncalibrated raw model prediction AUROC; 0.8268 is nested calibrated prediction AUROC.<br/>
    • <b>External AUROC CI Includes 0.50:</b> 95% Patient-Level Bootstrap CI for External AUROC is <b>[0.4911, 0.5591]</b>, which explicitly includes 0.50 (chance-level discrimination).<br/>
    • <b>Definition of Baseline Window X_j(k=0):</b> Defined as the mean value of signal j recorded during the patient's first 6-hour ICU window (k=0).<br/>
    • <b>Final Frozen Calibrator Fitting:</b> Trained Isotonic Regression on out-of-fold raw probability predictions from full 5-fold GroupKFold development model.<br/>
    • <b>Target Definition Distinction:</b> Retrospective dataset state transition S(k)=0 -> S(k+1)=1 is explicitly distinguished from clinical Sepsis-3 onset.
    """
    story.append(Paragraph(corrections_text, body_style))
    story.append(Spacer(1, 10))

    # SECTION 2: INTERNAL DEVELOPMENT METRICS TABLE
    story.append(Paragraph("2. Internal Development Validation (Model-Development CV)", h1_style))
    int_metrics_path = r"FINAL_BIOMARKERX\validation\INTERNAL_METRICS.csv"
    if os.path.exists(int_metrics_path):
        m_df = pd.read_csv(int_metrics_path)
        m_row = m_df.iloc[0]
        m_table_data = [
            [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Model-Development CV Estimate</b>", body_style), Paragraph("<b>95% Patient-Level CI</b>", body_style)],
            [Paragraph("AUROC (Nested Calibrated)", body_style), Paragraph(str(m_row['AUROC']), body_style), Paragraph("[0.8116, 0.8417]", body_style)],
            [Paragraph("AUPRC", body_style), Paragraph(str(m_row['AUPRC']), body_style), Paragraph("[0.3805, 0.4464]", body_style)],
            [Paragraph("Brier Score", body_style), Paragraph(str(m_row['Brier_Score']), body_style), Paragraph("[0.0633, 0.0713]", body_style)],
            [Paragraph("Prevalence Baseline Brier", body_style), Paragraph(str(m_row['Brier_Baseline_Prevalence']), body_style), Paragraph("N/A", body_style)]
        ]
        t_m = Table(m_table_data, colWidths=[150, 175, 175])
        t_m.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), c_bg_light),
            ('BOX', (0,0), (-1,-1), 0.5, c_border),
            ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
            ('PADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        story.append(t_m)

    story.append(Spacer(1, 10))

    # SECTION 3: HISTORICAL EXTERNAL RE-EVALUATION TABLE
    story.append(Paragraph("3. Historical External Re-Evaluation (PhysioNet 2019 / Test A)", h1_style))
    ext_metrics_path = r"FINAL_BIOMARKERX\external\EXTERNAL_METRICS.csv"
    if os.path.exists(ext_metrics_path):
        e_df = pd.read_csv(ext_metrics_path)
        e_row = e_df.iloc[0]
        ext_table_data = [
            [Paragraph("<b>Performance Metric</b>", body_style), Paragraph("<b>Historical External Test A Estimate</b>", body_style), Paragraph("<b>Audit Interpretation</b>", body_style)],
            [Paragraph("External AUROC", body_style), Paragraph(str(e_row['AUROC']), body_style), Paragraph("<font color='red'><b>95% CI [0.4911, 0.5591] includes 0.50</b></font>", body_style)],
            [Paragraph("External AUPRC", body_style), Paragraph(str(e_row['AUPRC']), body_style), Paragraph("Reflects 1.2% transition prevalence", body_style)],
            [Paragraph("External Brier Score", body_style), Paragraph(str(e_row['Brier_Score']), body_style), Paragraph("<font color='red'><b>Poor accuracy (Worse than prevalence baseline 0.01182)</b></font>", body_style)],
            [Paragraph("External Specificity (&tau;=0.1825)", body_style), Paragraph(f"{e_row['specificity_pct']}%", body_style), Paragraph("Substantially reduced false alerts", body_style)],
            [Paragraph("External Sensitivity (&tau;=0.1825)", body_style), Paragraph(f"{e_row['sensitivity_pct']}%", body_style), Paragraph("<font color='red'><b>Severe drop from 54.04% (Dev) to 13.21%</b></font>", body_style)],
            [Paragraph("External NPV", body_style), Paragraph(f"{e_row['NPV_pct']}%", body_style), Paragraph("Driven by low prevalence (1.2%)", body_style)]
        ]
        t_ext = Table(ext_table_data, colWidths=[150, 175, 175])
        t_ext.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), c_bg_light),
            ('BOX', (0,0), (-1,-1), 0.5, c_border),
            ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
            ('PADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        story.append(t_ext)

    story.append(Spacer(1, 10))

    # SECTION 4: FINAL CONCLUSION
    story.append(Paragraph("4. Final Conclusion & System Classification", h1_style))
    conclusion_text = """
    <b>BioMarkerX Final Scientific Conclusion (Refined & Audited):</b><br/>
    BioMarkerX was developed as a retrospective ICU transition-risk prediction system using patient-level temporal validation and causal feature construction. The final model was evaluated using patient-grouped development validation and historical external re-evaluation on PhysioNet 2019.<br/><br/>
    Internal model-development performance achieved an AUROC of 0.8268 (nested calibrated) and AUPRC of 0.4129 (subject to selection optimism). Historical external re-evaluation demonstrated substantial external discrimination degradation (AUROC 0.5261, 95% CI [0.4911, 0.5591] which includes 0.50), associated with cross-site distributional shifts in patient characteristics and measurement practices.<br/><br/>
    Feature redesign substantially reduced healthcare-process shortcuts (r = +0.0602), retained 99.61% of baseline AUROC under 50% lab measurement dropout, and increased external specificity to 84.55% (accompanied by a severe sensitivity drop to 13.21% at historical benchmark τ = 0.1825). External probabilistic predictions demonstrate poor accuracy (Brier 0.02922 vs baseline 0.01182), and formal external calibration is not established.<br/><br/>
    The system is classified as a <b>Research Decision-Support Prototype</b>. Prospective clinical effectiveness, operational deployment readiness, and mortality benefits are unsupported. Target-population recalibration and prospective validation would be required prior to operational use.
    """
    story.append(Paragraph(conclusion_text, body_style))
    story.append(Spacer(1, 10))

    doc.build(story, canvasmaker=NumberedCanvas)
    print("Report generated successfully at:", out_pdf)

if __name__ == '__main__':
    build_final_pdf_report()
