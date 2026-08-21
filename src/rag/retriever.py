from src.embeddings.embedding_pipeline import EmbeddingPipeline
from src.schemas import SearchResultData
from src.vectorstore.chroma_store import ChromaStore


class Retriever:
    def __init__(
        self,
        embedding_pipeline: EmbeddingPipeline,
        chroma_store: ChromaStore,
    ) -> None:
        self.embedding_pipeline = embedding_pipeline
        self.chroma_store = chroma_store

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[SearchResultData]:
        query_embedding = self.embedding_pipeline.embed_texts(
            [query]
        )[0]

        return self.chroma_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )