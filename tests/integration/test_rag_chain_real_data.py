from unittest.mock import Mock

from src.embeddings.embedding_pipeline import EmbeddingPipeline
from src.rag.context_builder import ContextBuilder
from src.rag.prompt_templates import PromptBuilder
from src.rag.rag_chain import RAGChain
from src.rag.retriever import Retriever
from src.vectorstore.chroma_store import ChromaStore


def test_rag_chain_real_data():
    embedding_pipeline = EmbeddingPipeline()
    chroma_store = ChromaStore()

    retriever = Retriever(
        embedding_pipeline=embedding_pipeline,
        chroma_store=chroma_store,
    )

    context_builder = ContextBuilder()
    prompt_builder = PromptBuilder()

    mock_llm_client = Mock()
    mock_llm_client.generate.return_value = "FAKE ANSWER"

    rag_chain = RAGChain(
        retriever=retriever,
        context_builder=context_builder,
        llm_client=mock_llm_client,
        prompt_builder=prompt_builder,
    )

    result = rag_chain.run(
        query="When he came to the war he was barely eighteen",
        top_k=5,
    )

    assert isinstance(result, str)
    assert result.strip()

    mock_llm_client.generate.assert_called_once()