from pathlib import Path

from src.ingestion.pdf_parser import extract_pdf_text
from src.ingestion.docx_parser import extract_docx_text
from src.ingestion.ocr_engine import extract_ocr_text
PDF_PATH = Path("data/raw/pdf/sample-10-page-pdf-a4-size.pdf")
DOCX_PATH = Path("data/raw/docx/sample-files.com-basic-text.docx")
OCR_PDF_PATH = Path("data/raw/pdf/sample-ocr.pdf")

def test_extrct_pdf_text():
    pages =  extract_pdf_text(PDF_PATH)

    assert len(pages) == 10

def test_extract_pdf_text_page_numbers_start_at_one():
    pages = extract_pdf_text(PDF_PATH)

    assert pages[0]["page_number"] == 1
    assert pages[-1]["page_number"] == 10

def test_extract_pdf_text_returns_text():
    pages = extract_pdf_text(PDF_PATH)

    for page in pages:
        assert page["text"]
        assert isinstance(page["text"], str)

def test_extract_pdf_text_contains_expected_content():
    pages = extract_pdf_text(PDF_PATH)

    assert "SmartHome Hub" in pages[0]["text"]



def test_extract_docx_text_returns_paragraphs():
    paragraphs = extract_docx_text(DOCX_PATH)

    assert len(paragraphs) > 0

def test_extract_docx_text_paragraph_numbers_start_at_one():
    paragraphs = extract_docx_text(DOCX_PATH)

    assert paragraphs[0]["paragraph_number"] == 1
    assert paragraphs[-1]["paragraph_number"] == len(paragraphs)

def test_extract_docx_text_returns_text_for_all_paragraphs():
    paragraphs = extract_docx_text(DOCX_PATH)

    for paragraph in paragraphs:
        assert isinstance(paragraph["text"], str)

def test_extract_docx_text_contains_expected_content():
    paragraphs = extract_docx_text(DOCX_PATH)

    assert paragraphs[0]["text"] == "Sample Document"


def test_extract_ocr_text_returns_expected_page_data():
    pages = extract_ocr_text(OCR_PDF_PATH, max_pages=3)
    assert isinstance(pages, list)
    assert len(pages) == 3

    for page_number, page in enumerate(pages, start=1):
        assert isinstance(page, dict)
        assert page["page_number"] == page_number
        assert "text" in page
        assert isinstance(page["text"], str)
    
