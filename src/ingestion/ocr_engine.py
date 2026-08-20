import io
from pathlib import Path

import fitz
import pytesseract
from PIL import Image

from src.schemas import Document, Page


class OCRExtractor:

    def can_process(self, document: Path) -> bool:
        return document.suffix.lower() in {
            ".png",
            ".jpg",
            ".jpeg",
            ".tiff",
        }

    def extract(
        self,
        document: Path,
        start_page: int = 1,
        end_page: int | None = None,
    ) -> Document:
        pages: list[Page] = []

        if start_page < 1:
            raise ValueError(
                "start_page must be greater than or equal to 1."
            )

        if end_page is not None and end_page < start_page:
            raise ValueError(
                "end_page must be greater than or equal to start_page."
            )

        with fitz.open(document) as ocr_document:

            total_pages = len(ocr_document)

            if start_page > total_pages:
                raise ValueError(
                    f"start_page ({start_page}) exceeds the document "
                    f"length ({total_pages} pages)."
                )

            if end_page is None:
                end_page = total_pages

            if end_page > total_pages:
                raise ValueError(
                    f"end_page ({end_page}) exceeds the document "
                    f"length ({total_pages} pages)."
                )

            for page_number in range(
                start_page,
                end_page + 1,
            ):
                page = ocr_document.load_page(page_number - 1)

                pixmap = page.get_pixmap(
                    dpi=300,
                    colorspace=fitz.csRGB,
                )

                image = Image.open(
                    io.BytesIO(
                        pixmap.tobytes("png")
                    )
                )

                text = pytesseract.image_to_string(image)

                pages.append(
                    Page(
                        page_number=page_number,
                        raw_text=text.strip(),
                        extraction_method="ocr",
                    )
                )

        return Document(
            document_id=document.stem,
            source_path=str(document),
            file_type=document.suffix.lower().lstrip("."),
            pages=pages,
            metadata={},
        )


if __name__ == "__main__":
    import json
    from dataclasses import asdict

    from src.config import OCR_TEST_FILE

    ocr_test_file = Path(OCR_TEST_FILE)

    ocr_extractor = OCRExtractor()

    result = ocr_extractor.extract(
        document=ocr_test_file,
        # start_page=20,
        # end_page=30,
    )

    print(f"\n{'=' * 60}")
    print("COMPLETE DOCUMENT")
    print(f"{'=' * 60}")

    print(
        json.dumps(
            asdict(result),
            indent=2,
            ensure_ascii=False,
        )
    )