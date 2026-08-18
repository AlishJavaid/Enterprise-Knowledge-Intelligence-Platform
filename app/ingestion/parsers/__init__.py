from app.ingestion.parsers.csv_parser import parse_csv
from app.ingestion.parsers.docx_parser import parse_docx
from app.ingestion.parsers.html_parser import parse_html
from app.ingestion.parsers.pdf_parser import parse_pdf

PARSERS = {
    "pdf": parse_pdf,
    "docx": parse_docx,
    "doc": parse_docx,
    "html": parse_html,
    "htm": parse_html,
    "csv": parse_csv,
    "txt": lambda b: b.decode("utf-8", errors="ignore"),
    "md": lambda b: b.decode("utf-8", errors="ignore"),
}


def parse_document(data: bytes, ext: str) -> str:
    parser = PARSERS.get(ext.lower().lstrip("."))
    if parser is None:
        raise ValueError(f"Unsupported file type: {ext}")
    return parser(data)