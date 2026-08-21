from src.embeddings.embedding_pipeline import EmbeddingPipeline
from src.rag.context_builder import ContextBuilder
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

    rag_chain = RAGChain(
        retriever=retriever,
        context_builder=context_builder,
    )

    result = rag_chain.run(
        query="When he came to the war he was barely eighteen",
        top_k=5,
    )

    assert isinstance(result, str)
    assert result.strip()