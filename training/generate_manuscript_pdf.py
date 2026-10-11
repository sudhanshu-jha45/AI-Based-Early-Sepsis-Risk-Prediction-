r"""
Generate Publication-Grade IEEE PDF Manuscript for AegisSepsis AI
Converts FULL_MANUSCRIPT.md into a beautifully styled IEEE-formatted PDF document using ReportLab.
"""

import os
import sys
import re
import time
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

def clean_md_formatting(text):
    # Escape XML entities first
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Convert bold **text** to <b>text</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Convert italic *text* to <i>text</i>
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    # Restore reportlab allowed tags
    text = text.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    text = text.replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
    text = text.replace("&lt;br/&gt;", "<br/>").replace("&lt;br&gt;", "<br/>")
    text = text.replace("&lt;sub&gt;", "<sub>").replace("&lt;/sub&gt;", "</sub>")
    text = text.replace("&lt;sup&gt;", "<sup>").replace("&lt;/sup&gt;", "</sup>")
    return text

def build_pdf_manuscript():
    md_path = os.path.join("FINAL_NOVELTY_PACKAGE", "manuscript", "final", "FULL_MANUSCRIPT.md")
    pdf_path = os.path.join("FINAL_NOVELTY_PACKAGE", "manuscript", "final", "FULL_MANUSCRIPT.pdf")
    
    if not os.path.exists(md_path):
        print(f"Error: {md_path} does not exist.")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    story = []
    styles = getSampleStyleSheet()

    # Color Palette
    PRIMARY = colors.HexColor("#0F172A")    # Deep Slate / Navy
    ACCENT = colors.HexColor("#0284C7")     # Cyan / Blue Accent
    TEXT_DARK = colors.HexColor("#1E293B")  # Charcoal Text
    TEXT_MUTED = colors.HexColor("#64748B") # Muted Text
    BG_LIGHT = colors.HexColor("#F8FAFC")   # Light Gray
    BORDER_COLOR = colors.HexColor("#CBD5E1")

    # Typography Styles
    style_title = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=6
    )
    style_h1 = ParagraphStyle(
        "H1Header",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    style_h2 = ParagraphStyle(
        "H2Header",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=ACCENT,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    style_h3 = ParagraphStyle(
        "H3Header",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        textColor=PRIMARY,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )
    style_body = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    )
    style_bullet = ParagraphStyle(
        "BulletCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=TEXT_DARK,
        leftIndent=12,
        spaceAfter=3
    )
    style_code = ParagraphStyle(
        "CodeCustom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4
    )
    style_table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=TA_CENTER
    )
    style_table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=TEXT_DARK,
        alignment=TA_LEFT
    )

    # Parse Markdown into ReportLab Flowables
    sections_blocks = content.split("\n\n")

    for block in sections_blocks:
        block_s = block.strip()
        if not block_s:
            continue

        # Check for Table markdown
        if "|" in block_s and "\n" in block_s and "-|-" in block_s:
            lines = [l.strip() for l in block_s.split("\n") if l.strip()]
            t_data = []
            for idx, l in enumerate(lines):
                if "-|-" in l or "---" in l:
                    continue
                cells = [c.strip() for c in l.split("|")[1:-1]]
                row_cells = []
                for cell in cells:
                    cell_text = clean_md_formatting(cell)
                    st = style_table_header if idx == 0 else style_table_cell
                    row_cells.append(Paragraph(cell_text, st))
                if row_cells:
                    t_data.append(row_cells)
            
            if t_data:
                col_num = len(t_data[0])
                col_width = 532 / max(col_num, 1)
                t = Table(t_data, colWidths=[col_width]*col_num)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), PRIMARY),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('BACKGROUND', (0,1), (-1,-1), BG_LIGHT),
                    ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
                    ('PADDING', (0,0), (-1,-1), 4),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
                ]))
                story.append(t)
                story.append(Spacer(1, 8))
            continue

        # Check Headings
        if block_s.startswith("# "):
            title_text = clean_md_formatting(block_s[2:])
            story.append(Paragraph(title_text, style_title))
            story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceBefore=4, spaceAfter=8))
        elif block_s.startswith("## "):
            h2_text = clean_md_formatting(block_s[3:])
            story.append(Paragraph(h2_text, style_h1))
            story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceBefore=2, spaceAfter=6))
        elif block_s.startswith("### "):
            h3_text = clean_md_formatting(block_s[4:])
            story.append(Paragraph(h3_text, style_h2))
        elif block_s.startswith("#### "):
            h4_text = clean_md_formatting(block_s[5:])
            story.append(Paragraph(h4_text, style_h3))
        elif block_s.startswith("* ") or block_s.startswith("- "):
            bullets = block_s.split("\n")
            for b in bullets:
                b_s = b.strip()
                if b_s.startswith("* ") or b_s.startswith("- "):
                    text = clean_md_formatting(b_s[2:])
                    story.append(Paragraph(f"&bull; {text}", style_bullet))
            story.append(Spacer(1, 4))
        elif block_s.startswith("```"):
            code_text = block_s.replace("```text", "").replace("```", "").strip()
            code_text = clean_md_formatting(code_text)
            p_code = Paragraph(code_text.replace("\n", "<br/>").replace(" ", "&nbsp;"), style_code)
            t_code = Table([[p_code]], colWidths=[532])
            t_code.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
                ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
                ('PADDING', (0,0), (-1,-1), 6)
            ]))
            story.append(t_code)
            story.append(Spacer(1, 6))
        else:
            # Standard Body Paragraph
            text = clean_md_formatting(block_s)
            story.append(Paragraph(text, style_body))

    doc.build(story)
    pdf_size = os.path.getsize(pdf_path)
    print(f"IEEE Master Manuscript PDF successfully generated: {pdf_path} (Size: {pdf_size} bytes)")

if __name__ == "__main__":
    build_pdf_manuscript()
