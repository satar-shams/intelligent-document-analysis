from src.rag.context_builder import ContextBuilder
from src.rag.retriever import Retriever


class RAGChain:
    def __init__(
        self,
        retriever:Retriever,
        context_builder: ContextBuilder,
        # llm: ...,
    ) -> None:
        self.retriever = retriever
        self.context_builder = context_builder

    def run(
        self,
        query: str,
        top_k: int = 5
    ) -> str:
        search_result = self.retriever.retrieve(query=query, top_k=top_k)
        context_result = self.context_builder.build(search_results=search_result)

        return context_result
