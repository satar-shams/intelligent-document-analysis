from pathlib import Path

from src import config
from src.ingestion.extractor_manager import ExtractorManager
from src.schemas import Document, Page


DATA_DIRECTORY = Path(config.INGESTION_INPUT_DIRECTORY)


def test_extract_pdf_real_data():
    manager = ExtractorManager()

    document = manager.extract_file(
        Path(config.PDF_TEST_FILE)
    )

    assert isinstance(document, Document)
    assert document.pages

    extracted_text = "\n".join(
        page.raw_text
        for page in document.pages
    )

    assert extracted_text.strip()
    assert "SmartHome Hub" in extracted_text

    for page in document.pages:
        assert isinstance(page, Page)
        assert page.page_number >= 1
        assert isinstance(page.raw_text, str)
        assert page.raw_text.strip()
        assert page.extraction_method == "pymupdf"


def test_extract_docx_real_data():
    manager = ExtractorManager()

    document = manager.extract_file(
        Path(config.DOCX_TEST_FILE)
    )

    assert isinstance(document, Document)
    assert document.pages

    extracted_text = "\n".join(
        page.raw_text
        for page in document.pages
    )

    assert extracted_text.strip()
    assert "Sample Document" in extracted_text

    for page in document.pages:
        assert isinstance(page, Page)
        assert page.page_number >= 1
        assert isinstance(page.raw_text, str)
        assert page.extraction_method == "docx"


def test_extract_ocr_real_data():
    manager = ExtractorManager()

    document = manager.extract_file(
        Path(config.OCR_TEST_FILE)
    )

    assert isinstance(document, Document)
    assert document.pages

    extracted_text = "\n".join(
        page.raw_text
        for page in document.pages
    )

    assert extracted_text.strip()
    assert "OCR" in extracted_text
    assert "Invoice" in extracted_text
    assert "12345" in extracted_text

    for page in document.pages:
        assert isinstance(page, Page)
        assert page.page_number >= 1
        assert isinstance(page.raw_text, str)
        assert page.raw_text.strip()
        assert page.extraction_method == "ocr"


def test_extract_directory_real_data():
    manager = ExtractorManager()

    documents = manager.extract_directory(
        DATA_DIRECTORY
    )

    assert documents

    for document in documents:
        assert isinstance(document, Document)
        assert document.pages