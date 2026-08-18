import fitz  # PyMuPDF

def parse_pdf(data: bytes) -> str:
    try:
        doc = fitz.open(stream=data, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text() + "\n\n"
        doc.close()
        return text.strip()
    except Exception as e:
        raise ValueError(f"Could not read PDF (it may be corrupted, password-protected, or purely image-based): {str(e)}")