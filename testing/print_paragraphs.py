import docx

doc = docx.Document(r"c:\Users\LENOVO\Downloads\spesis dataset\REVIEW-2 DOCUMENT FORMAT-Corrected.docx")

for i, p in enumerate(doc.paragraphs):
    print(f"P[{i:02d}] ({p.style.name}): {p.text}")
