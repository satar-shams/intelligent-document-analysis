import pytest

from src.rag.context_builder import ContextBuilder
from src.schemas import SearchResultData


@pytest.fixture
def search_results():
    return [
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


def test_build_returns_string(search_results):
    context_builder = ContextBuilder()

    result = context_builder.build(
        search_results=search_results
    )

    assert isinstance(result, str)


def test_build_formats_search_results(search_results):
    context_builder = ContextBuilder()

    result = context_builder.build(
        search_results=search_results
    )

    expected = (
        "chunk_id: 1\n"
        "document_id: doc-1\n"
        "page_start: 1\n"
        "page_end: 1\n"
        "text: Some text 1\n"
        "\n"
        "chunk_id: 2\n"
        "document_id: doc-1\n"
        "page_start: 2\n"
        "page_end: 2\n"
        "text: Some text 2"
    )

    assert result == expected