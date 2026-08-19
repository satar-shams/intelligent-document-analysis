import fitz
from pathlib import Path

from src.schemas import Document, Page


class PyMuPDFExtractor:

    def can_process(self, document: Path) -> bool:
        return document.suffix.lower() == ".pdf"

    def extract(self, document: Path) -> Document:
        pages: list[Page] = []

        with fitz.open(document) as pdf_document:
            for page_number, page in enumerate(
                pdf_document,
                start=1,
            ):
                text = page.get_text()

                pages.append(
                    Page(
                        page_number=page_number,
                        raw_text=text.strip(),
                        extraction_method="pymupdf",
                    )
                )

        return Document(
            document_id=document.stem,
            source_path=str(document),
            file_type="pdf",
            pages=pages,
            metadata={},
        )


if __name__ == "__main__":
    from pathlib import Path

    from src.config import PDF_TEST_FILE

    pdf_extractor = PyMuPDFExtractor()
    document_path = Path(PDF_TEST_FILE)

    if pdf_extractor.can_process(document_path):
        result = pdf_extractor.extract(document_path)

        for page in result.pages:
            print(f"\n{'=' * 60}")
            print(f"SOURCE {page.page_number}")
            print(f"{'=' * 60}")
            print(page.raw_text)
    else:
        print("File is not .pdf")