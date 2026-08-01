from src.embeddings.embedding_pipeline import EmbeddingPipeline
from src.schemas import (
    ChunkData,
    SearchResultData,
)
from src.vectorstore.chroma_store import ChromaStore


class RAGChain:
    """Coordinate semantic retrieval for Retrieval-Augmented Generation."""

    def __init__(
        self,
        embedding_pipeline: EmbeddingPipeline,
        vector_store: ChromaStore,
    ) -> None:
        self.embedding_pipeline = embedding_pipeline
        self.vector_store = vector_store

    def retrieve(
        self,
        question: str,
        top_k: int = 5,
    ) -> list[SearchResultData]:
        """
        Retrieve the most relevant document chunks.

        Args:
            question: User query.
            top_k: Maximum number of chunks to return.

        Returns:
            Ranked search results.
        """
        query_embedding = self.embedding_pipeline.embed(
            [question],
        )[0]

        return self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )

    def build_context(
        self,
        search_results: list[SearchResultData],
    ) -> str:
        """
        Build a context string from retrieved chunks.

        Args:
            search_results: Retrieved document chunks.

        Returns:
            Context string ready for an LLM.
        """
        return "\n\n".join(
            result["text"]
            for result in search_results
        )