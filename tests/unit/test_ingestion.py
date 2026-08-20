from pathlib import Path

from src.ingestion.docx_parser import DOCXExtractor
from src.ingestion.extractor_manager import (
    ExtractorManager,
    UnsupportedDocumentTypeError,
)
from src.ingestion.ocr_engine import OCRExtractor
from src.ingestion.pdf_parser import PyMuPDFExtractor
from src.schemas import Document, Page


PDF_PATH = Path(
    "data/raw/pdf/sample-10-page-pdf-a4-size.pdf"
)
DOCX_PATH = Path(
    "data/raw/docx/sample-files.com-basic-text.docx"
)
OCR_PDF_PATH = Path(
    "data/raw/pdf/sample-ocr.pdf"
)


def test_pdf_extractor_returns_document():
    extractor = PyMuPDFExtractor()

    document = extractor.extract(PDF_PATH)

    assert isinstance(document, Document)
    assert document.file_type == "pdf"
    assert document.source_path == str(PDF_PATH)
    assert document.pages
    assert all(
        isinstance(page, Page)
        for page in document.pages
    )


def test_pdf_extractor_page_numbers_start_at_one():
    extractor = PyMuPDFExtractor()

    document = extractor.extract(PDF_PATH)

    assert document.pages[0].page_number == 1
    assert document.pages[-1].page_number == 10


def test_pdf_extractor_returns_text():
    extractor = PyMuPDFExtractor()

    document = extractor.extract(PDF_PATH)

    for page in document.pages:
        assert isinstance(page.raw_text, str)
        assert page.raw_text


def test_pdf_extractor_contains_expected_content():
    extractor = PyMuPDFExtractor()

    document = extractor.extract(PDF_PATH)

    assert "SmartHome Hub" in document.pages[0].raw_text


def test_docx_extractor_returns_document():
    extractor = DOCXExtractor()

    document = extractor.extract(DOCX_PATH)

    assert isinstance(document, Document)
    assert document.file_type == "docx"
    assert document.pages
    assert all(
        isinstance(page, Page)
        for page in document.pages
    )


def test_docx_extractor_page_numbers_start_at_one():
    extractor = DOCXExtractor()

    document = extractor.extract(DOCX_PATH)

    assert document.pages[0].page_number == 1
    assert document.pages[-1].page_number == len(
        document.pages
    )


def test_docx_extractor_returns_text():
    extractor = DOCXExtractor()

    document = extractor.extract(DOCX_PATH)

    for page in document.pages:
        assert isinstance(page.raw_text, str)


def test_docx_extractor_contains_expected_content():
    extractor = DOCXExtractor()

    document = extractor.extract(DOCX_PATH)

    assert document.pages[0].raw_text == "Sample Document"


def test_ocr_extractor_returns_document():
    extractor = OCRExtractor()

    document = extractor.extract(
        OCR_PDF_PATH,
        start_page=1,
        end_page=1,
    )

    assert isinstance(document, Document)
    assert document.file_type == "pdf"
    assert len(document.pages) == 1


def test_ocr_extractor_page_numbers_start_at_one():
    extractor = OCRExtractor()

    document = extractor.extract(
        OCR_PDF_PATH,
        start_page=1,
        end_page=1,
    )

    assert document.pages[0].page_number == 1
    assert document.pages[-1].page_number == 1


def test_ocr_extractor_returns_text():
    extractor = OCRExtractor()

    document = extractor.extract(
        OCR_PDF_PATH,
        start_page=1,
        end_page=1,
    )

    for page in document.pages:
        assert isinstance(page.raw_text, str)


def test_extractor_manager_returns_document():
    manager = ExtractorManager()

    document = manager.extract_file(DOCX_PATH)

    assert isinstance(document, Document)
    assert document.pages


def test_extractor_manager_skips_unsupported_files(
    tmp_path: Path,
):
    unsupported_file = tmp_path / "unsupported.txt"
    unsupported_file.write_text("unsupported")

    manager = ExtractorManager()

    documents = manager.extract_directory(tmp_path)

    assert documents == []


def test_extractor_manager_raises_for_unsupported_file():
    manager = ExtractorManager()

    unsupported_file = Path("data/raw/unsupported.txt")

    try:
        manager.extract_file(unsupported_file)
    except UnsupportedDocumentTypeError:
        pass
    else:
        raise AssertionError(
            "Expected UnsupportedDocumentTypeError"
        )