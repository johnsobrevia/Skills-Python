import streamlit as st
import os
import glob
from dotenv import load_dotenv
from fpdf import FPDF
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- CONFIGURACIÓN INICIAL ---
load_dotenv()
st.set_page_config(page_title="CV Optimizer AI", page_icon="📝", layout="wide")

# Validar API Key
api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

# --- FUNCIONES DE SOPORTE ---

def load_context(folder_path="mis_cvs", md_file="perfil_maestro.md"):
    """Carga el contexto desde el archivo Markdown y complementa con PDFs si existen."""
    combined_text = ""
    sources = []
    
    # 1. Cargar Perfil Maestro (Prioridad)
    if os.path.exists(md_file):
        with open(md_file, "r", encoding="utf-8") as f:
            combined_text += f"# CONTEXTO DESDE {md_file.upper()}\n"
            combined_text += f.read()
            sources.append(f"✅ {md_file}")
    
    # 2. Cargar PDFs complementarios
    if os.path.exists(folder_path):
        pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
        for pdf in pdf_files:
            try:
                loader = PyPDFLoader(pdf)
                pages = loader.load()
                pdf_text = "\n".join([p.page_content for p in pages])
                combined_text += f"\n\n# CONTENIDO ADICIONAL (PDF: {os.path.basename(pdf)})\n"
                combined_text += pdf_text
                sources.append(f"📄 {os.path.basename(pdf)}")
            except Exception as e:
                st.error(f"Error cargando {pdf}: {e}")
            
    return combined_text, sources

def generate_optimized_cv(user_context, job_description):
    """Usa LangChain y Gemini para generar el CV optimizado."""
    if not api_key:
        return "Error: No se encontró la API KEY de Google Gemini.", 0
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)
    
    template = """
    Eres un experto en reclutamiento y optimización de CVs para sistemas ATS.
    
    CONTEXTO PROFESIONAL DEL USUARIO:
    {user_context}
    
    DESCRIPCIÓN DEL TRABAJO OBJETIVO:
    {job_description}
    
    INSTRUCCIONES DE FORMATO (CRÍTICO):
    1. La primera línea DEBE ser el nombre completo del usuario.
    2. La segunda línea DEBE ser la información de contacto (email, teléfono, link).
    3. Usa títulos de sección claros en MAYÚSCULAS: SUMMARY, SKILLS, EXPERIENCE, EDUCATION.
    4. Usa un formato lineal, sin tablas ni columnas.
    5. No uses caracteres especiales de markdown como ** o ### en el cuerpo del texto.
    6. Al final, después de todo el CV, añade la etiqueta 'ANALYSIS_METRICS' y debajo:
       - Match Score: (0-100)
       - Missing Elements: (breve explicación)
    
    Redacta un CV potente, optimizado con palabras clave del anuncio y orientado a logros.
    """
    
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    response = chain.invoke({
        "user_context": user_context,
        "job_description": job_description
    })
    
    return response

def sanitize_text(text):
    """Limpia el texto para evitar errores de codificación en FPDF (Latin-1)."""
    replacements = {
        '\u2013': '-', '\u2014': '-', '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"', '\u2022': '*', '\u2026': '...',
        '\u00a0': ' ', '\u200b': ''
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Eliminar otros caracteres no Latin-1
    return text.encode('latin-1', 'replace').decode('latin-1')

def create_pdf(text):
    """Genera un PDF limpio y altamente legible, optimizado para ATS."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    epw = pdf.epw

    # 1. Limpieza y Sanitización
    text = text.replace("**", "").replace("###", "").replace("##", "").replace("#", "")
    text = sanitize_text(text)
    
    # Separar CV de las métricas
    main_cv_text = text.split("ANALYSIS_METRICS")[0].strip()
    
    # Procesar línea por línea
    lines = main_cv_text.splitlines()
    
    for i, line in enumerate(lines):
        clean_line = line.strip()
        
        # Saltos de línea vacíos
        if not clean_line:
            pdf.ln(2)
            continue
            
        # Resaltar Nombre (asumiendo que es la primera línea con contenido)
        if i == 0:
            pdf.set_font("Helvetica", style='B', size=14)
            pdf.multi_cell(epw, 8, clean_line, align='C')
            pdf.set_font("Helvetica", size=11)
            pdf.ln(2)
            continue

        # Detectar Secciones (SUMMARY, SKILLS, EXPERIENCE, etc.)
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
            # Estilo para el resto del texto
            pdf.set_font("Helvetica", size=11)
            # Indentar viñetas
            if clean_line.startswith(('*', '-', '>')):
                pdf.multi_cell(epw, 6, f"  {clean_line}")
            else:
                pdf.multi_cell(epw, 6, clean_line)
            
    return bytes(pdf.output())

def create_txt(text):
    """Limpia el texto y lo prepara para descarga en TXT."""
    main_cv_text = text.split("ANALYSIS_METRICS")[0].strip()
    # Eliminar posibles restos de markdown para un TXT limpio
    main_cv_text = main_cv_text.replace("**", "").replace("###", "").replace("##", "").replace("#", "")
    return main_cv_text

# --- INTERFAZ DE USUARIO (STREAMLIT) ---

st.title("🚀 CV Optimizer: Gemini + LangChain")
st.markdown("Optimiza tu perfil profesional para cualquier vacante en segundos.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    if api_key:
        st.success("API Key detectada ✅")
    else:
        st.error("API Key no configurada ❌")
        st.info("Añade GOOGLE_API_KEY a tu archivo .env o st.secrets")
    
    st.divider()
    st.subheader("📁 Fuentes de Información")
    context_text, sources = load_context()
    if sources:
        for s in sources:
            st.text(s)
        if "perfil_maestro.md" in "".join(sources):
            st.info("💡 Editando 'perfil_maestro.md' puedes mejorar tu Match Score.")
    else:
        st.warning("No se detectaron fuentes de datos.")
        st.info("Edita 'perfil_maestro.md' o sube PDFs a 'mis_cvs'.")

# Main Area
st.subheader("🎯 Paso 1: Pega el Anuncio de Trabajo")
job_desc = st.text_area("Descripción de la vacante (Job Description):", height=250, placeholder="Pega aquí los requisitos del puesto...", key="job_desc_input")

# Inicializar estado si no existe
if 'cv_result' not in st.session_state:
    st.session_state.cv_result = None

col_gen, col_reset = st.columns([3, 1])

with col_gen:
    if st.button("🔥 Generar CV Optimizado para ATS", use_container_width=True):
        if not job_desc:
            st.warning("Por favor, pega una descripción de trabajo.")
        elif not context_text:
            st.error("No hay contexto profesional. Configura 'perfil_maestro.md' o sube PDFs.")
        elif not api_key:
            st.error("Configure su API Key en el sidebar.")
        else:
            with st.spinner("🤖 La IA está analizando tu perfil y redactando tu nuevo CV..."):
                st.session_state.cv_result = generate_optimized_cv(context_text, job_desc)

with col_reset:
    if st.button("🗑️ Nuevo Análisis", use_container_width=True, type="secondary"):
        st.session_state.cv_result = None
        st.rerun()

# Mostrar resultados si existen
if st.session_state.cv_result:
    result = st.session_state.cv_result
    # Procesar el resultado
    if "ANALYSIS_METRICS" in result:
        cv_content, metrics_content = result.split("ANALYSIS_METRICS")
        
        # Mostrar Métricas
        st.divider()
        st.subheader("📊 Análisis de Match")
        st.info(metrics_content.strip())
        
        # Mostrar el CV generado
        st.subheader("📝 Vista Previa del CV Optimizado")
        st.text_area("Contenido:", cv_content.strip(), height=400)
        
        # Opción de descarga
        col1, col2 = st.columns(2)
        
        with col1:
            txt_content = create_txt(result)
            st.download_button(
                label="📄 Descargar CV en TXT (Recomendado)",
                data=txt_content,
                file_name="CV_Optimizado_ATS.txt",
                mime="text/plain"
            )
        
        with col2:
            try:
                pdf_bytes = create_pdf(result)
                st.download_button(
                    label="📥 Descargar CV en PDF",
                    data=pdf_bytes,
                    file_name="CV_Optimizado_ATS.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.warning("El PDF no se pudo generar correctamente. Usa la versión TXT.")
    else:
        st.write(result)

st.divider()
st.caption("Hecho con ❤️ usando Streamlit, LangChain y Google Gemini (Flash 1.5)")
