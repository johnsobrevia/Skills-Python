from langchain_community.document_loaders import PyPDFLoader
import os

pdf_path = "test_output.pdf"
if os.path.exists(pdf_path):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    for i, page in enumerate(pages):
        print(f"--- Page {i+1} ---")
        print(page.page_content)
else:
    print("File not found.")
