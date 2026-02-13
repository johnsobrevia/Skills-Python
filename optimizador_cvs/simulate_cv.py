import os
from dotenv import load_dotenv
from fpdf import FPDF
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

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
    lines = [line.strip() for line in main_cv_text.split('\n')]
    header_lines = []
    body_start_index = 0
    for i, line in enumerate(lines):
        if line:
            header_lines.append(line)
            if len(header_lines) >= 2:
                body_start_index = i + 1
                break
    if header_lines:
        pdf.set_font("Helvetica", style='B', size=16)
        pdf.multi_cell(epw, 10, header_lines[0], align='C')
        pdf.set_font("Helvetica", size=10)
        if len(header_lines) > 1:
            pdf.multi_cell(epw, 6, header_lines[1], align='C')
        pdf.ln(4)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(6)
    for i in range(body_start_index, len(lines)):
        line = lines[i]
        if not line:
            pdf.ln(3)
            continue
        upper_line = line.upper()
        section_headers = ["SUMMARY", "SKILLS", "EXPERIENCE", "EDUCATION", "RESUMEN", "HABILIDADES", "EXPERIENCIA", "EDUCACIÓN"]
        if any(h in upper_line for h in section_headers) and len(line) < 35:
            pdf.ln(3)
            pdf.set_font("Helvetica", style='B', size=12)
            pdf.multi_cell(epw, 8, upper_line)
            pdf.line(pdf.get_x(), pdf.get_y() - 1, pdf.get_x() + 30, pdf.get_y() - 1)
            pdf.set_font("Helvetica", size=11)
            pdf.ln(1)
        else:
            pdf.set_font("Helvetica", size=11)
            if line.startswith(('*', '-', '>')):
                pdf.multi_cell(epw, 6, f"  {line}")
            else:
                pdf.multi_cell(epw, 6, line)
    return pdf.output()

def test_flow():
    with open("perfil_maestro.md", "r", encoding="utf-8") as f:
        user_context = f.read()
    job_description = "Buscamos un Ingeniero Civil Industrial para administración de contratos en minería."
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)
    template = """
    Eres un experto en reclutamiento y optimización de CVs para sistemas ATS.
    CONTEXTO PROFESIONAL DEL USUARIO: {user_context}
    DESCRIPCIÓN DEL TRABAJO OBJETIVO: {job_description}
    INSTRUCCIONES DE FORMATO:
    1. Primera línea: Nombre completo.
    2. Segunda línea: Info contacto.
    3. Títulos en MAYÚSCULAS: SUMMARY, SKILLS, EXPERIENCE, EDUCATION.
    4. Sin ** ni ###.
    5. Termina con ANALYSIS_METRICS.
    """
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"user_context": user_context, "job_description": job_description})
    pdf_bytes = create_pdf(result)
    with open("test_output.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("Test PDF generated: test_output.pdf")

if __name__ == "__main__":
    test_flow()
