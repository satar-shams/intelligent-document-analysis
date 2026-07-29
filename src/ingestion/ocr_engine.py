import io
import json 
from pathlib import Path

import fitz
import pytesseract
from PIL import Image


def extract_ocr_text(
    pdf_path: str | Path,
    max_pages: int | None = None,
) -> list[dict[str, str | int]]:
    """
    Extract text from a scanned PDF using Tesseract OCR.

    Each PDF page is rendered at 300 DPI and passed to Tesseract
    for text recognition.

    Args:
        pdf_path: Path to the PDF file.
        max_pages: Maximum number of pages to process.
            If None, all pages are processed.

    Returns:
        A list of dictionaries containing the page number and
        extracted OCR text.
    """
    pdf_path = Path(pdf_path)
    pages = []

    with fitz.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            if max_pages is not None and page_number > max_pages:
                break

            pixmap = page.get_pixmap(
                dpi=300,
                colorspace=fitz.csRGB,
            )

            image = Image.open(
                io.BytesIO(pixmap.tobytes("png"))
            )

            text = pytesseract.image_to_string(image)

            pages.append(
                {
                    "page_number": page_number,
                    "text": text.strip(),
                }
            )

    return pages


def save_ocr_results(
    pages: list[dict[str, str | int]],
    output_path: str | Path,
) -> None:
    """
    Save OCR results to a JSON file.

    Args:
        pages: OCR results containing page numbers and extracted text.
        output_path: Path where the JSON file will be saved.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(pages, file, ensure_ascii=False, indent=2)

