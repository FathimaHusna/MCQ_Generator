import json
from ast import literal_eval
from PyPDF2 import PdfReader

def clean_json(text):
    return text.replace("```json", "").replace("```", "").strip()

def safe_parse_json(text):
    text = clean_json(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return literal_eval(text)

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
