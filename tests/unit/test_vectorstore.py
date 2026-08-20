import pytest

from src.schemas import Chunk
from src.vectorstore.chroma_store import ChromaStore


@pytest.fixture
def store(tmp_path):
    store = ChromaStore()
    store.delete_collection()

    yield store

    store.delete_collection()


def test_add_increases_document_count(store):
    chunks = [
        Chunk(
            chunk_id="1",
            document_id="document-1",
            text="Machine learning is a subset of artificial intelligence.",
            page_start=1,
            page_end=1,
            section_title=None,
        ),
        Chunk(
            chunk_id="2",
            document_id="document-1",
            text="Deep learning uses neural networks.",
            page_start=1,
            page_end=1,
            section_title=None,
        ),
    ]

    embeddings = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]

    store.add(
        chunks,
        embeddings,
    )

    assert store.count() == 2


def test_add_raises_for_mismatched_lengths(store):
    chunks = [
        Chunk(
            chunk_id="1",
            document_id="document-1",
            text="Hello",
            page_start=1,
            page_end=1,
            section_title=None,
        )
    ]

    embeddings = []

    with pytest.raises(ValueError):
        store.add(
            chunks,
            embeddings,
        )


def test_search_returns_expected_chunk(store):
    chunks = [
        Chunk(
            chunk_id="1",
            document_id="document-1",
            text="Cats are domestic animals.",
            page_start=1,
            page_end=1,
            section_title=None,
        ),
        Chunk(
            chunk_id="2",
            document_id="document-1",
            text="Python is a programming language.",
            page_start=1,
            page_end=1,
            section_title=None,
        ),
    ]

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]

    store.add(
        chunks,
        embeddings,
    )

    query_embedding = [0.0, 1.0, 0.0]

    results = store.search(
        query_embedding=query_embedding,
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].chunk_id == "2"
    assert results[0].document_id == "document-1"
    assert results[0].text == "Python is a programming language."


def test_search_returns_search_result_data(store):
    chunks = [
        Chunk(
            chunk_id="1",
            document_id="document-1",
            text="Artificial intelligence",
            page_start=3,
            page_end=4,
            section_title="Introduction",
        )
    ]

    embeddings = [
        [1.0, 0.0, 0.0],
    ]

    store.add(
        chunks,
        embeddings,
    )

    results = store.search(
        query_embedding=[1.0, 0.0, 0.0],
        top_k=1,
    )

    result = results[0]

    assert result.chunk_id == "1"
    assert result.document_id == "document-1"
    assert result.text == "Artificial intelligence"
    assert result.page_start == 3
    assert result.page_end == 4
    assert isinstance(result.distance, float)


def test_delete_collection_removes_all_documents(store):
    chunks = [
        Chunk(
            chunk_id="1",
            document_id="document-1",
            text="Artificial intelligence",
            page_start=1,
            page_end=1,
            section_title=None,
        )
    ]

    embeddings = [
        [0.1, 0.2, 0.3],
    ]

    store.add(
        chunks,
        embeddings,
    )

    assert store.count() == 1

    store.delete_collection()

    assert store.count() == 0


def test_search_returns_requested_number_of_results(store):
    chunks = [
        Chunk(
            chunk_id="1",
            document_id="document-1",
            text="Apple is a fruit.",
            page_start=1,
            page_end=1,
            section_title=None,
        ),
        Chunk(
            chunk_id="2",
            document_id="document-1",
            text="Orange is a fruit.",
            page_start=1,
            page_end=1,
            section_title=None,
        ),
        Chunk(
            chunk_id="3",
            document_id="document-1",
            text="Car engines use fuel.",
            page_start=1,
            page_end=1,
            section_title=None,
        ),
    ]

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.9, 0.1, 0.0],
        [0.0, 0.0, 1.0],
    ]

    store.add(
        chunks,
        embeddings,
    )

    query_embedding = [1.0, 0.0, 0.0]

    results = store.search(
        query_embedding=query_embedding,
        top_k=2,
    )

    assert len(results) == 2