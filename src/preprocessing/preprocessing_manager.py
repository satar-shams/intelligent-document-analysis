from src.schemas import Document, Chunk
from src.preprocessing.cleaner import TextCleaner
from src.preprocessing.chunker import Chunker


class PreprocessorManager:
    """Coordinate document cleaning and chunking."""

    def __init__(self) -> None:
        self.text_cleaner = TextCleaner()
        self.chunker = Chunker()

    def preprocess(
        self,
        documents: list[Document],
    ) -> list[Chunk]:
        """
        Clean all document pages and create chunks.

        The input documents are updated in place with cleaned text.
        The resulting chunks are returned for the next pipeline stage.
        """
        for document in documents:
            for page in document.pages:
                page.cleaned_text = self.text_cleaner.clean_text(
                    page.raw_text
                )

        return self.chunker.chunk_documents(documents)