import pytest

from src.embeddings.embedding_pipeline import EmbeddingPipeline
from src.vectorstore.chroma_store import ChromaStore
from src.config import EMBEDDING_MODEL_NAME

@pytest.fixture
def store():
    store = ChromaStore()
    store.delete_collection()
    yield store
    store.delete_collection()


@pytest.fixture
def pipeline():
    return EmbeddingPipeline(
        model_name=EMBEDDING_MODEL_NAME,
    )


def test_add_increases_document_count(
    store,
    pipeline,
):
    chunks = [
        {
            "chunk_id": 1,
            "page": 1,
            "text": "Machine learning is a subset of artificial intelligence.",
        },
        {
            "chunk_id": 2,
            "page": 1,
            "text": "Deep learning uses neural networks.",
        },
    ]

    embeddings = pipeline.embed(
        [chunk["text"] for chunk in chunks]
    )

    store.add(
        chunks,
        embeddings,
    )

    assert store.count() == 2


def test_add_raises_for_mismatched_lengths(
    store,
):
    chunks = [
        {
            "chunk_id": 1,
            "page": 1,
            "text": "Hello",
        }
    ]

    embeddings = []

    with pytest.raises(ValueError):
        store.add(
            chunks,
            embeddings,
        )


def test_search_returns_expected_chunk(
    store,
    pipeline,
):
    chunks = [
        {
            "chunk_id": 1,
            "page": 1,
            "text": "Cats are domestic animals.",
        },
        {
            "chunk_id": 2,
            "page": 1,
            "text": "Python is a programming language.",
        },
    ]

    embeddings = pipeline.embed(
        [chunk["text"] for chunk in chunks]
    )

    store.add(
        chunks,
        embeddings,
    )

    query_embedding = pipeline.embed(
        [
            "Programming with Python"
        ]
    )[0]

    results = store.search(
        query_embedding=query_embedding,
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["chunk_id"] == 2


def test_delete_collection_removes_all_documents(
    store,
    pipeline,
):
    chunks = [
        {
            "chunk_id": 1,
            "page": 1,
            "text": "Artificial intelligence",
        }
    ]

    embeddings = pipeline.embed(
        [chunk["text"] for chunk in chunks]
    )

    store.add(
        chunks,
        embeddings,
    )

    assert store.count() == 1

    store.delete_collection()

    assert store.count() == 0


def test_search_returns_requested_number_of_results(
    store,
    pipeline,
):
    chunks = [
        {
            "chunk_id": 1,
            "page": 1,
            "text": "Apple is a fruit.",
        },
        {
            "chunk_id": 2,
            "page": 1,
            "text": "Orange is a fruit.",
        },
        {
            "chunk_id": 3,
            "page": 1,
            "text": "Car engines use fuel.",
        },
    ]

    embeddings = pipeline.embed(
        [chunk["text"] for chunk in chunks]
    )

    store.add(
        chunks,
        embeddings,
    )

    query_embedding = pipeline.embed(
        [
            "Fruit"
        ]
    )[0]

    results = store.search(
        query_embedding=query_embedding,
        top_k=2,
    )

    assert len(results) == 2