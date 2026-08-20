import pytest

from src.preprocessing.chunker import Chunker
from src.preprocessing.cleaner import TextCleaner
from src.preprocessing.preprocessing_manager import PreprocessorManager
from src.schemas import Chunk, Document, Page


# ==================================================
# TextCleaner Tests
# ==================================================


def test_clean_text_normalizes_whitespace():
    cleaner = TextCleaner()

    text = "Hello     World"

    assert cleaner.clean_text(text) == "Hello World"


def test_clean_text_normalizes_line_endings():
    cleaner = TextCleaner()

    text = "A\r\nB\rC"

    assert cleaner.clean_text(text) == "A\nB\nC"


def test_clean_text_removes_extra_blank_lines():
    cleaner = TextCleaner()

    text = "A\n\n\nB\n\n\n\nC"

    assert cleaner.clean_text(text) == "A\n\nB\n\nC"


# ==================================================
# Chunker Tests
# ==================================================


def test_chunk_documents_returns_single_chunk_for_short_text():
    chunker = Chunker()

    documents = [
        Document(
            document_id="test-document",
            source_path="test.txt",
            file_type="txt",
            pages=[
                Page(
                    page_number=1,
                    raw_text="Hello World",
                    cleaned_text="Hello World",
                )
            ],
            metadata={},
        )
    ]

    chunks = chunker.chunk_documents(documents)

    assert len(chunks) == 1
    assert isinstance(chunks[0], Chunk)
    assert chunks[0].text == "Hello World"


def test_chunk_documents_splits_long_text():
    chunker = Chunker(
        chunk_size=500,
        chunk_overlap=50,
    )

    documents = [
        Document(
            document_id="test-document",
            source_path="test.txt",
            file_type="txt",
            pages=[
                Page(
                    page_number=1,
                    raw_text="A" * 1200,
                    cleaned_text="A" * 1200,
                )
            ],
            metadata={},
        )
    ]

    chunks = chunker.chunk_documents(documents)

    assert len(chunks) == 3

    chunk_ids = [chunk.chunk_id for chunk in chunks]

    assert chunk_ids == ["1", "2", "3"]

    assert len(chunks[0].text) == 500
    assert len(chunks[1].text) == 500
    assert len(chunks[2].text) == 300


def test_chunk_documents_preserves_overlap():
    chunker = Chunker(
        chunk_size=10,
        chunk_overlap=2,
    )

    documents = [
        Document(
            document_id="test-document",
            source_path="test.txt",
            file_type="txt",
            pages=[
                Page(
                    page_number=1,
                    raw_text="abcdefghijklmno",
                    cleaned_text="abcdefghijklmno",
                )
            ],
            metadata={},
        )
    ]

    chunks = chunker.chunk_documents(documents)

    assert chunks[0].text == "abcdefghij"
    assert chunks[1].text == "ijklmno"


def test_chunk_documents_preserves_page_number():
    chunker = Chunker(
        chunk_size=100,
        chunk_overlap=0,
    )

    documents = [
        Document(
            document_id="test-document",
            source_path="test.txt",
            file_type="txt",
            pages=[
                Page(
                    page_number=7,
                    raw_text="A" * 150,
                    cleaned_text="A" * 150,
                )
            ],
            metadata={},
        )
    ]

    chunks = chunker.chunk_documents(documents)

    for chunk in chunks:
        assert chunk.page_start == 7
        assert chunk.page_end == 7


def test_chunk_documents_assigns_unique_chunk_ids():
    chunker = Chunker(
        chunk_size=100,
        chunk_overlap=0,
    )

    documents = [
        Document(
            document_id="test-document",
            source_path="test.txt",
            file_type="txt",
            pages=[
                Page(
                    page_number=1,
                    raw_text="A" * 150,
                    cleaned_text="A" * 150,
                ),
                Page(
                    page_number=2,
                    raw_text="B" * 150,
                    cleaned_text="B" * 150,
                ),
            ],
            metadata={},
        )
    ]

    chunks = chunker.chunk_documents(documents)

    chunk_ids = [chunk.chunk_id for chunk in chunks]

    assert chunk_ids == ["1", "2", "3", "4"]


def test_chunker_raises_when_cleaned_text_is_missing():
    chunker = Chunker()

    documents = [
        Document(
            document_id="test-document",
            source_path="test.txt",
            file_type="txt",
            pages=[
                Page(
                    page_number=1,
                    raw_text="Hello World",
                    cleaned_text=None,
                )
            ],
            metadata={},
        )
    ]

    with pytest.raises(ValueError):
        chunker.chunk_documents(documents)


def test_chunker_raises_for_invalid_chunk_size():
    with pytest.raises(ValueError):
        Chunker(chunk_size=0)


def test_chunker_raises_for_negative_overlap():
    with pytest.raises(ValueError):
        Chunker(chunk_overlap=-1)


def test_chunker_raises_when_overlap_is_too_large():
    with pytest.raises(ValueError):
        Chunker(
            chunk_size=100,
            chunk_overlap=100,
        )


# ==================================================
# PreprocessorManager Tests
# ==================================================


def test_preprocessor_cleans_pages_and_creates_chunks():
    manager = PreprocessorManager()

    documents = [
        Document(
            document_id="test-document",
            source_path="test.txt",
            file_type="txt",
            pages=[
                Page(
                    page_number=1,
                    raw_text="Hello     World",
                )
            ],
            metadata={},
        )
    ]

    chunks = manager.preprocess(documents)

    assert len(chunks) == 1

    assert documents[0].pages[0].raw_text == "Hello     World"
    assert documents[0].pages[0].cleaned_text == "Hello World"

    assert isinstance(chunks[0], Chunk)
    assert chunks[0].text == "Hello World"
    assert chunks[0].document_id == "test-document"
    assert chunks[0].page_start == 1
    assert chunks[0].page_end == 1


def test_preprocessor_processes_multiple_documents():
    manager = PreprocessorManager()

    documents = [
        Document(
            document_id="document-1",
            source_path="document1.txt",
            file_type="txt",
            pages=[
                Page(
                    page_number=1,
                    raw_text="First     document",
                )
            ],
            metadata={},
        ),
        Document(
            document_id="document-2",
            source_path="document2.txt",
            file_type="txt",
            pages=[
                Page(
                    page_number=1,
                    raw_text="Second     document",
                )
            ],
            metadata={},
        ),
    ]

    chunks = manager.preprocess(documents)

    assert len(chunks) == 2

    assert (
        documents[0].pages[0].cleaned_text
        == "First document"
    )

    assert (
        documents[1].pages[0].cleaned_text
        == "Second document"
    )

    assert chunks[0].document_id == "document-1"
    assert chunks[1].document_id == "document-2"