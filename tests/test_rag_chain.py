import pytest

from src.config import EMBEDDING_MODEL_NAME
from src.embeddings.embedding_pipeline import EmbeddingPipeline
from src.rag.rag_chain import RAGChain
from src.vectorstore.chroma_store import ChromaStore


@pytest.fixture
def embedding_pipeline():
    return EmbeddingPipeline(
        model_name=EMBEDDING_MODEL_NAME,
    )


@pytest.fixture
def vector_store():
    store = ChromaStore()
    store.delete_collection()
    yield store
    store.delete_collection()


@pytest.fixture
def rag_chain(
    embedding_pipeline,
    populated_store,
):
    return RAGChain(
        embedding_pipeline=embedding_pipeline,
        vector_store=populated_store,
    )


@pytest.fixture
def sample_chunks():
    return [
        {
            "chunk_id": 1,
            "page": 1,
            "text": "Machine learning is a subset of artificial intelligence.",
        },
        {
            "chunk_id": 2,
            "page": 2,
            "text": "Neural networks are widely used in deep learning.",
        },
        {
            "chunk_id": 3,
            "page": 3,
            "text": "Cats are common household pets.",
        },
    ]


@pytest.fixture
def sample_search_results():
    return [
        {
            "chunk_id": 1,
            "page": 1,
            "text": "Chunk one.",
            "distance": 0.1,
        },
        {
            "chunk_id": 2,
            "page": 2,
            "text": "Chunk two.",
            "distance": 0.2,
        },
    ]

@pytest.fixture
def populated_store(
    embedding_pipeline,
    vector_store,
    sample_chunks,
):
    embeddings = embedding_pipeline.embed(
        [chunk["text"] for chunk in sample_chunks]
    )

    vector_store.add(
        chunks=sample_chunks,
        embeddings=embeddings,
    )

    return vector_store


def test_retrieve_returns_results(rag_chain):

    results = rag_chain.retrieve(
        question="What is deep learning?",
        top_k=2,
    )

    assert len(results) == 2


def test_retrieve_returns_relevant_chunk(
    embedding_pipeline,
    populated_store,
):
    rag = RAGChain(
        embedding_pipeline=embedding_pipeline,
        vector_store=populated_store,
    )

    results = rag.retrieve(
        question="Neural networks",
        top_k=1,
    )

    assert "Neural networks" in results[0]["text"]


def test_build_context_returns_string(
    rag_chain, sample_search_results
):

    context = rag_chain.build_context(
        sample_search_results,
    )

    assert isinstance(context, str)


def test_build_context_contains_all_chunks(
    rag_chain, sample_search_results
):

    context = rag_chain.build_context(
        sample_search_results,
    )

    assert "Chunk one." in context
    assert "Chunk two." in context


def test_build_context_separates_chunks(
    rag_chain, sample_search_results
):

    context = rag_chain.build_context(
        sample_search_results,
    )

    assert context == "Chunk one.\n\nChunk two."