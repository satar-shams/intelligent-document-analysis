from src.rag.context_builder import ContextBuilder
from src.rag.retriever import Retriever


class RAGChain:
    def __init__(
        self,
        retriever: Retriever,
        context_builder: ContextBuilder,
    ) -> None:
        self.retriever = retriever
        self.context_builder = context_builder

    def run(
        self,
        query: str,
        top_k: int = 5,
    ) -> str:
        search_results = self.retriever.retrieve(
            query=query,
            top_k=top_k,
        )

        context = self.context_builder.build(
            search_results=search_results,
        )

        return context


if __name__ == "__main__":
    from src.embeddings.embedding_pipeline import EmbeddingPipeline
    from src.vectorstore.chroma_store import ChromaStore

    embedding_pipeline = EmbeddingPipeline()
    chroma_store = ChromaStore()

    retriever = Retriever(
        embedding_pipeline=embedding_pipeline,
        chroma_store=chroma_store,
    )

    context_builder = ContextBuilder()

    rag_chain = RAGChain(
        retriever=retriever,
        context_builder=context_builder,
    )

    query = (
        "2025 revenue"
    )

    top_k = 10

    search_results = retriever.retrieve(
        query=query,
        top_k=top_k,
    )

    print("=" * 80)
    print("RAG RETRIEVAL TEST")
    print("=" * 80)
    print(f"\nQuery: {query}")
    print(f"Top K: {top_k}")

    print("\n" + "-" * 80)
    print("RETRIEVED RESULTS")
    print("-" * 80)

    for rank, result in enumerate(search_results, start=1):
        print(f"\nResult {rank}")
        print(f"  Chunk ID : {result.chunk_id}")
        print(f"  Document : {result.document_id}")
        print(f"  Pages    : {result.page_start}-{result.page_end}")
        print(f"  Distance : {result.distance:.4f}")
        print(f"  Text     : {result.text}")

    context = context_builder.build(
        search_results=search_results,
    )

    print("\n" + "=" * 80)
    print("CONTEXT SENT TO LLM")
    print("=" * 80)
    print(context)