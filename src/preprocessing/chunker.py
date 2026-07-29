class Chunker:
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
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

    def chunk_pages(self, pages: list[dict]) -> list[dict]:
        results = []
        chunk_id = 1

        for page in pages:
            chunks = self._split_text(page["text"])

            for chunk in chunks:
                results.append(
                    self._create_chunk(
                        chunk_id=chunk_id,
                        page=page["page"],
                        text=chunk,
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
        chunk_id: int,
        page: int,
        text: str,
    ) -> dict:
        return {
            "chunk_id": chunk_id,
            "page": page,
            "text": text,
        }