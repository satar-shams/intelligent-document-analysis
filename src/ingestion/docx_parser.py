from docx import Document
from pathlib import Path



def extract_docx_text(docx_path: str |Path) -> list[dict]:
    paragraphs = []

    document = Document(docx_path)

    for paragraph_number, paragraph in enumerate(
        document.paragraphs,
        start=1,
    ):
        paragraphs.append(
            {
                "paragraph_number": paragraph_number,
                "text": paragraph.text,
            }
        )

    return paragraphs