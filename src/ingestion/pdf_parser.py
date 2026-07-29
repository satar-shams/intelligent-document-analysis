import fitz
from pathlib import Path

def extract_pdf_text(pdf_path: str | Path) -> list[dict]:

    pages = []
    with fitz.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text()

            pages.append(
                {
                    "page_number": page_number,
                    "text": text,
                }
            )

    return pages