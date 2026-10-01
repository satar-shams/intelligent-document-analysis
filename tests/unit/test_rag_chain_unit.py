import pytest
from unittest.mock import Mock

from src.rag.rag_chain import RAGChain
from src.schemas import SearchResultData


@pytest.fixture
def mock_retriever():
    mock = Mock()

    mock.retrieve.return_value = [
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
    ]

    return mock


@pytest.fixture
def mock_context_builder():
    mock = Mock()

    mock.build.return_value = (
        "chunk_id: 1\n"
        "document_id: doc-1\n"
        "page_start: 1\n"
        "page_end: 1\n"
        "text: Some text 1"
    )

    return mock


@pytest.fixture
def mock_prompt_builder():
    mock = Mock()

    mock.build.return_value = "FAKE PROMPT"

    return mock


@pytest.fixture
def mock_llm_client():
    mock = Mock()

    mock.generate.return_value = "FAKE ANSWER"

    return mock


@pytest.fixture
def rag_chain(
    mock_retriever,
    mock_context_builder,
    mock_prompt_builder,
    mock_llm_client,
):
    return RAGChain(
        retriever=mock_retriever,
        context_builder=mock_context_builder,
        llm_client=mock_llm_client,
        prompt_builder=mock_prompt_builder,
    )


def test_run_retrieves_search_results(
    rag_chain,
    mock_retriever,
):
    rag_chain.run(
        query="some question",
        top_k=3,
    )

    mock_retriever.retrieve.assert_called_once_with(
        query="some question",
        top_k=3,
    )


def test_run_builds_context_from_search_results(
    rag_chain,
    mock_retriever,
    mock_context_builder,
):
    rag_chain.run(
        query="some question",
        top_k=3,
    )

    mock_context_builder.build.assert_called_once_with(
        search_results=mock_retriever.retrieve.return_value,
    )


def test_run_builds_prompt_and_generates_answer(
    rag_chain,
    mock_context_builder,
    mock_prompt_builder,
    mock_llm_client,
):
    result = rag_chain.run(
        query="some question",
        top_k=3,
    )

    mock_prompt_builder.build.assert_called_once_with(
        instruction=(
            "Answer the question using only the provided context. "
            "Do not add or invent information that is not supported "
            "by the context. If the context does not contain enough "
            "information to answer the question, say that the "
            "available context does not provide enough information."
        ),
        context=mock_context_builder.build.return_value,
        query="some question",
    )

    mock_llm_client.generate.assert_called_once_with(
        prompt=mock_prompt_builder.build.return_value,
    )

    assert result == "FAKE ANSWER"
