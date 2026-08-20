import chromadb

from src.config import (
    COLLECTION_NAME,
    VECTOR_DB_PATH,
)
from src.schemas import (
    Chunk,
    SearchResultData,
)


class ChromaStore:
    """Persistent storage and retrieval of document embeddings."""

    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(
            path=VECTOR_DB_PATH,
        )

        self.collection_name = COLLECTION_NAME

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
        )

    def add(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        """
        Store chunks and their embeddings.

        Args:
            chunks: Document chunks.
            embeddings: Embedding vectors corresponding to each chunk.
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                "chunks and embeddings must have the same length."
            )

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []

        for chunk in chunks:
            ids.append(chunk.chunk_id)

            documents.append(chunk.text)

            metadatas.append(
                {
                    "document_id": chunk.document_id,
                    "page_start": chunk.page_start,
                    "page_end": chunk.page_end,
                    "section_title": chunk.section_title or "",
                }
            )

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[SearchResultData]:
        """
        Search for the most relevant chunks.

        Args:
            query_embedding: Embedding of the query.
            top_k: Number of results to return.

        Returns:
            Ranked search results.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        search_results: list[SearchResultData] = []

        for (
            chunk_id,
            text,
            metadata,
            distance,
        ) in zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            search_results.append(
                SearchResultData(
                    chunk_id=chunk_id,
                    document_id=metadata["document_id"],
                    text=text,
                    page_start=metadata["page_start"],
                    page_end=metadata["page_end"],
                    distance=float(distance),
                )
            )

        return search_results

    def count(self) -> int:
        """Return the number of stored chunks."""
        return self.collection.count()

    def delete_collection(self) -> None:
        """Delete and recreate the collection."""
        self.client.delete_collection(
            self.collection_name,
        )

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
        )