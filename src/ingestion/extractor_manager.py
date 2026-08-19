from pathlib import Path

import fitz

from src.ingestion.docx_parser import DOCXExtractor
from src.ingestion.ocr_engine import OCRExtractor
from src.ingestion.pdf_parser import PyMuPDFExtractor
from src.schemas import Document
from src.utils.logger import get_logger


logger = get_logger(__name__)


class UnsupportedDocumentTypeError(Exception):
    """Raised when no extractor supports a document type."""


class ExtractorManager:
    """Select and run the appropriate extractor for documents."""

    def __init__(self) -> None:
        self.pdf_extractor = PyMuPDFExtractor()
        self.docx_extractor = DOCXExtractor()
        self.ocr_extractor = OCRExtractor()

    def extract_file(self, document: Path) -> Document:
        """Extract a single document using the appropriate extractor."""
        document = Path(document)

        if not document.is_file():
            raise FileNotFoundError(
                f"Document not found: {document}"
            )

        if document.suffix.lower() == ".pdf":
            extracted_document = self.pdf_extractor.extract(document)

            if any(
                page.raw_text.strip()
                for page in extracted_document.pages
            ):
                logger.info(
                    "Extracted file successfully: %s",
                    document,
                )
                return extracted_document

            logger.info(
                "No extractable text found in PDF; "
                "falling back to OCR: %s",
                document,
            )

            extracted_document = self.ocr_extractor.extract(document)

            logger.info(
                "Extracted file successfully using OCR: %s",
                document,
            )

            return extracted_document

        if self.docx_extractor.can_process(document):
            extracted_document = self.docx_extractor.extract(document)

            logger.info(
                "Extracted file successfully: %s",
                document,
            )

            return extracted_document

        if self.ocr_extractor.can_process(document):
            extracted_document = self.ocr_extractor.extract(document)

            logger.info(
                "Extracted file successfully using OCR: %s",
                document,
            )

            return extracted_document

        raise UnsupportedDocumentTypeError(
            f"Unsupported document type: "
            f"{document.suffix.lower() or '[no extension]'}"
        )

    def extract_directory(
        self,
        directory: Path,
    ) -> list[Document]:
        """Extract all supported documents in a directory."""
        directory = Path(directory)

        if not directory.is_dir():
            raise NotADirectoryError(
                f"Directory not found: {directory}"
            )

        logger.info(
            "Starting document extraction from directory: %s",
            directory,
        )

        documents: list[Document] = []

        for document in sorted(directory.rglob("*")):
            if not document.is_file():
                continue

            try:
                extracted_document = self.extract_file(document)
                documents.append(extracted_document)

            except UnsupportedDocumentTypeError as exc:
                logger.warning(
                    "Skipping unsupported file %s: %s",
                    document,
                    exc,
                )

            except Exception:
                logger.exception(
                    "Failed to extract file: %s",
                    document,
                )

        logger.info(
            "Document extraction completed. "
            "Successfully extracted: %d file(s).",
            len(documents),
        )

        return documents

if __name__ == "__main__":
    import json
    from dataclasses import asdict

    from src.config import (
        DOCX_TEST_FILE,
        INGESTION_INPUT_DIRECTORY,
        OCR_TEST_FILE,
        PDF_TEST_FILE,
    )

    manager = ExtractorManager()

    # =========================================================
    # Test extracting individual files
    # =========================================================

    test_files = [
        PDF_TEST_FILE,
        DOCX_TEST_FILE,
        OCR_TEST_FILE,
    ]

    for file_path in test_files:
        print(f"\n{'=' * 60}")
        print(f"FILE: {file_path}")
        print(f"{'=' * 60}")

        result = manager.extract_file(
            Path(file_path)
        )

        print(f"Document ID: {result.document_id}")
        print(f"File type: {result.file_type}")
        print(f"Pages: {len(result.pages)}")

    # =========================================================
    # Test extracting all supported files from a directory
    # =========================================================

    print(f"\n{'=' * 60}")
    print(f"DIRECTORY: {INGESTION_INPUT_DIRECTORY}")
    print(f"{'=' * 60}")

    results = manager.extract_directory(
        Path(INGESTION_INPUT_DIRECTORY)
    )

    for result in results:
        print(
            f"{result.document_id} | "
            f"{result.file_type} | "
            f"{len(result.pages)} pages"
        )

    # =========================================================
    # Inspect returned Document objects
    # Print the first document and then every 10th document.
    # =========================================================

    print(f"\n{'=' * 60}")
    print("DOCUMENT OUTPUT PREVIEW")
    print(f"{'=' * 60}")

    for index, result in enumerate(
        results,
        start=1,
    ):
        if index == 1 or index % 10 == 0:
            print(f"\n{'=' * 60}")
            print(f"DOCUMENT {index}")
            print(f"{'=' * 60}")

            print(
                json.dumps(
                    asdict(result),
                    indent=2,
                    ensure_ascii=False,
                )
            )