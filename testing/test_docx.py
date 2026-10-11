import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

doc = docx.Document(r"c:\Users\LENOVO\Downloads\spesis dataset\REVIEW-2 DOCUMENT FORMAT-Corrected.docx")
print("Successfully loaded docx.")
