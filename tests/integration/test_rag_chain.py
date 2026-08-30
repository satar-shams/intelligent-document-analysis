from unittest.mock import Mock

from src.embeddings.embedding_pipeline import EmbeddingPipeline
from src.vectorstore.chroma_store import ChromaStore
from src.rag.context_builder import ContextBuilder
from src.rag.retriever import Retriever
from src.rag.prompt_templates import PromptBuilder
from src.rag.rag_chain import RAGChain


def test_rag_chain_with_real_retrieval():
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

    answer = rag_chain.run(
        query=query,
        top_k=top_k,
    )

    assert isinstance(answer, str)
    assert answer.strip() == "FAKE ANSWER"

    mock_llm.generate.assert_called_once()

    prompt = mock_llm.generate.call_args.kwargs["prompt"]

    assert query in prompt