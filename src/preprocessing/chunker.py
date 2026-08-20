from src.config import CHUNK_SIZE, CHUNK_OVERLAP
from src.schemas import Document, Chunk


class Chunker:
    """Split cleaned document text into overlapping chunks."""

    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
    ):
        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than 0."
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative."
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_documents(
        self,
        documents: list[Document],
    ) -> list[Chunk]:

        results: list[Chunk] = []
        chunk_id = 1

        for document in documents:
            for page in document.pages:

                if page.cleaned_text is None:
                    raise ValueError(
                        f"Page {page.page_number} of document "
                        f"{document.document_id} has no cleaned text."
                    )

                chunks = self._split_text(page.cleaned_text)

                for chunk in chunks:
                    results.append(
                        self._create_chunk(
                            chunk_id=str(chunk_id),
                            document_id=document.document_id,
                            text=chunk,
                            page_start=page.page_number,
                            page_end=page.page_number,
                        )
                    )

                    chunk_id += 1

        return results

    def _split_text(self, text: str) -> list[str]:
        step = self.chunk_size - self.chunk_overlap
        chunks = []

        for start in range(0, len(text), step):
            end = start + self.chunk_size
            chunk = text[start:end]

            if chunk:
                chunks.append(chunk)

        return chunks

    def _create_chunk(
        self,
        chunk_id: str,
        document_id: str,
        text: str,
        page_start: int,
        page_end: int,
        section_title: str | None = None,
    ) -> Chunk:

        return Chunk(
            chunk_id=chunk_id,
            document_id=document_id,
            text=text,
            page_start=page_start,
            page_end=page_end,
            section_title=section_title,
        )