from unittest.mock import Mock

import pytest

from src.rag.retriever import Retriever
from src.schemas import SearchResultData


@pytest.fixture
def mock_embedding_pipeline():
    mock = Mock()

    mock.embed_texts.return_value = [
        [0.1, 0.2, 0.3],
    ]

    return mock


@pytest.fixture
def mock_chroma_store():
    mock = Mock()

    mock.search.return_value = [
        SearchResultData(
            chunk_id="1",
            document_id="doc-1",
            text="Some text 1",
            page_start=1,
            page_end=1,
            distance=0.1,
        ),
        SearchResultData(
            chunk_id="2",
            document_id="doc-1",
            text="Some text 2",
            page_start=2,
            page_end=2,
            distance=0.2,
        ),
        SearchResultData(
            chunk_id="3",
            document_id="doc-1",
            text="Some text 3",
            page_start=3,
            page_end=3,
            distance=0.3,
        ),
    ]

    return mock


@pytest.fixture
def retriever(
    mock_embedding_pipeline,
    mock_chroma_store,
):
    return Retriever(
        embedding_pipeline=mock_embedding_pipeline,
        chroma_store=mock_chroma_store,
    )


def test_retrieve_returns_search_results(retriever):
    result = retriever.retrieve(
        query="some question",
        top_k=3,
    )

    assert isinstance(result, list)
    assert len(result) == 3
    assert isinstance(result[0], SearchResultData)


def test_retrieve_embeds_query(
    retriever,
    mock_embedding_pipeline,
):
    retriever.retrieve(
        query="some question",
        top_k=2,
    )

    mock_embedding_pipeline.embed_texts.assert_called_once_with(
        ["some question"],
    )

def test_retrieve_searches_chroma_with_embedding(
    retriever,
    mock_chroma_store,
):
    retriever.retrieve(
        query="some question",
        top_k=2,
    )

    mock_chroma_store.search.assert_called_once_with(
        query_embedding=[0.1, 0.2, 0.3],
        top_k=2,
    )
    
def test_retrieve_returns_chroma_results(
    retriever,
    mock_chroma_store,
):
    result = retriever.retrieve(
        query="some question",
        top_k=2,
    )

    assert result == mock_chroma_store.search.return_value