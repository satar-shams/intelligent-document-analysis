from src.rag.context_builder import ContextBuilder
from src.rag.retriever import Retriever
from src.rag.llm_client import LLMClient
from src.rag.prompt_templates import PromptBuilder


class RAGChain:
    def __init__(
        self,
        retriever: Retriever,
        context_builder: ContextBuilder,
        llm_client: LLMClient,
        prompt_builder: PromptBuilder 
    ) -> None:
        self.retriever = retriever
        self.context_builder = context_builder
        self.llm_client = llm_client
        self.prompt_builder = prompt_builder

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

        prompt = self.prompt_builder.build(instruction="Answer the question using only the provided context. Do not add or invent information that is not supported by the context. If the context does not contain enough information to answer the question, say that the available context does not provide enough information.",
                                           context=context,
                                           query=query)

        answer =  self.llm_client.generate(prompt=prompt)

        return answer
        

if __name__ == "__main__":
    from unittest.mock import Mock

    from src.embeddings.embedding_pipeline import EmbeddingPipeline
    from src.vectorstore.chroma_store import ChromaStore

    embedding_pipeline = EmbeddingPipeline()
    chroma_store = ChromaStore()

    retriever = Retriever(
        embedding_pipeline=embedding_pipeline,
        chroma_store=chroma_store,
    )

    context_builder = ContextBuilder()
    prompt_builder = PromptBuilder()

    mock_llm = Mock()
    mock_llm.generate.return_value = "FAKE ANSWER"

    rag_chain = RAGChain(
        retriever=retriever,
        context_builder=context_builder,
        llm_client=mock_llm,
        prompt_builder=prompt_builder,
    )

    query = "2025 revenue"
    top_k = 10

    search_results = retriever.retrieve(
        query=query,
        top_k=top_k,
    )

    context = context_builder.build(
        search_results=search_results,
    )

    instruction = (
        "Answer the question using only the provided context. "
        "Do not add or invent information that is not supported by "
        "the context. If the context does not contain enough "
        "information to answer the question, say that the available "
        "context does not provide enough information."
    )

    prompt = prompt_builder.build(
        instruction=instruction,
        context=context,
        query=query,
    )

    answer = rag_chain.run(
        query=query,
        top_k=top_k,
    )

    print("=" * 80)
    print("RAG CHAIN TEST")
    print("=" * 80)

    print(f"\nQuery: {query}")
    print(f"Top K: {top_k}")

    print("\n" + "-" * 80)
    print("RETRIEVED RESULTS")
    print("-" * 80)

    for rank, result in enumerate(search_results, start=1):
        print(f"\nResult {rank}")
        print(f"  Document : {result.document_id}")
        print(f"  Chunk ID : {result.chunk_id}")
        print(f"  Pages    : {result.page_start}-{result.page_end}")
        print(f"  Distance : {result.distance:.4f}")

    print("\n" + "-" * 80)
    print("PROMPT SENT TO LLM")
    print("-" * 80)
    print(prompt)

    print("\n" + "-" * 80)
    print("GENERATED ANSWER")
    print("-" * 80)
    print(answer)