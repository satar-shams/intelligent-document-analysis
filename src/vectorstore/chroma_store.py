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

    BATCH_SIZE = 5000

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
        Store chunks and their embeddings in batches.

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

        for start in range(
            0,
            len(chunks),
            self.BATCH_SIZE,
        ):
            end = start + self.BATCH_SIZE

            self.collection.add(
                ids=ids[start:end],
                documents=documents[start:end],
                metadatas=metadatas[start:end],
                embeddings=embeddings[start:end],
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

    def get_chunks(
        self,
        limit: int | None = None,
    ) -> list[Chunk]:
        """
        Retrieve stored document chunks from ChromaDB.

        Args:
            limit: Maximum number of chunks to retrieve.
                If None, retrieve all chunks.

        Returns:
            List of Chunk objects reconstructed from ChromaDB.
        """
        results = self.collection.get(
            limit=limit,
            include=["documents", "metadatas"],
        )

        chunks: list[Chunk] = []

        for (
            chunk_id,
            text,
            metadata,
        ) in zip(
            results["ids"],
            results["documents"],
            results["metadatas"],
        ):
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    document_id=metadata["document_id"],
                    text=text,
                    page_start=metadata["page_start"],
                    page_end=metadata["page_end"],
                    section_title=metadata.get("section_title") or None,
                )
            )

        return chunks

    def get_chunks(self) -> list[Chunk]:
        """Retrieve all stored document chunks from ChromaDB."""

        results = self.collection.get(
            include=[
                "documents",
                "metadatas",
            ],
        )

        chunks: list[Chunk] = []

        for (
            chunk_id,
            text,
            metadata,
        ) in zip(
            results["ids"],
            results["documents"],
            results["metadatas"],
        ):
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    document_id=metadata["document_id"],
                    text=text,
                    page_start=metadata["page_start"],
                    page_end=metadata["page_end"],
                    section_title=metadata.get("section_title") or None,
                )
            )

        return chunks

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

if __name__ == "__main__":
    chroma_store = ChromaStore()

    chunks = chroma_store.get_chunks()

    print(f"Total chunks: {len(chunks)}")

    for chunk in chunks[:5]:
        print("\n" + "=" * 80)
        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Document: {chunk.document_id}")
        print(f"Pages: {chunk.page_start}-{chunk.page_end}")
        print(f"Section: {chunk.section_title}")
        print(f"Text: {chunk.text}")