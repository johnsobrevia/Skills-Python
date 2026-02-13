import os
from fpdf import FPDF
from dotenv import load_dotenv

def sanitize_text(text):
    replacements = {
        '\u2013': '-', '\u2014': '-', '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"', '\u2022': '*', '\u2026': '...',
        '\u00a0': ' ', '\u200b': ''
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode('latin-1', 'replace').decode('latin-1')

def create_pdf(text):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    epw = pdf.epw
    text = text.replace("**", "").replace("###", "").replace("##", "").replace("#", "")
    text = sanitize_text(text)
    main_cv_text = text.split("ANALYSIS_METRICS")[0].strip()
    lines = main_cv_text.splitlines()
    for i, line in enumerate(lines):
        clean_line = line.strip()
        if not clean_line:
            pdf.ln(2)
            continue
        if i == 0:
            pdf.set_font("Helvetica", style='B', size=14)
            pdf.multi_cell(epw, 8, clean_line, align='C')
            pdf.set_font("Helvetica", size=11)
            pdf.ln(2)
            continue
        upper_line = clean_line.upper()
        headers = ["SUMMARY", "SKILLS", "EXPERIENCE", "EDUCATION", "RESUMEN", "HABILIDADES", "EXPERIENCIA", "EDUCACION"]
        is_header = any(h in upper_line for h in headers) and len(clean_line) < 30
        if is_header:
            pdf.ln(4)
            pdf.set_font("Helvetica", style='B', size=12)
            pdf.multi_cell(epw, 8, upper_line)
            pdf.set_font("Helvetica", size=11)
            pdf.ln(1)
        else:
            pdf.set_font("Helvetica", size=11)
            if clean_line.startswith(('*', '-', '>')):
                pdf.multi_cell(epw, 6, f"  {clean_line}")
            else:
                pdf.multi_cell(epw, 6, clean_line)
    return pdf.output()

sample_text = """JUAN PEREZ
juan.perez@email.com | +56912345678
SUMMARY
Experto en ingenieria con mas de 10 anos de experiencia.
EXPERIENCE
- Liderazgo de proyectos.
- Gestion de presupuestos.
ANALYSIS_METRICS
Match Score: 95
"""

pdf_bytes = create_pdf(sample_text)
with open("final_test.pdf", "wb") as f:
    f.write(pdf_bytes)
print("Final test PDF generated.")
