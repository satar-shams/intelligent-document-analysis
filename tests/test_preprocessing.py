import pytest

from src.preprocessing.chunker import Chunker
from src.preprocessing.cleaner import TextCleaner


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


def test_clean_pages_preserves_page_number():
    cleaner = TextCleaner()

    pages = [
        {
            "page": 5,
            "text": "Hello",
        }
    ]

    cleaned = cleaner.clean_pages(pages)

    assert cleaned[0]["page"] == 5


def test_clean_pages_returns_expected_structure():
    cleaner = TextCleaner()

    pages = [
        {
            "page": 1,
            "text": "Hello",
        }
    ]

    cleaned = cleaner.clean_pages(pages)

    assert len(cleaned) == 1

    page = cleaned[0]

    assert "page" in page
    assert "text" in page
    assert page["text"] == "Hello"


# ==================================================
# Chunker Tests
# ==================================================

def test_chunk_pages_returns_single_chunk_for_short_text():
    chunker = Chunker()

    pages = [
        {
            "page": 1,
            "text": "Hello World",
        }
    ]

    chunks = chunker.chunk_pages(pages)

    assert len(chunks) == 1
    assert chunks[0]["text"] == "Hello World"


def test_chunk_pages_splits_long_text():
    chunker = Chunker(
        chunk_size=500,
        chunk_overlap=50,
    )

    pages = [
        {
            "page": 1,
            "text": "A" * 1200,
        }
    ]

    chunks = chunker.chunk_pages(pages)

    assert len(chunks) == 3

    chunk_ids = [chunk["chunk_id"] for chunk in chunks]

    assert chunk_ids == [1, 2, 3]

    assert len(chunks[0]["text"]) == 500
    assert len(chunks[1]["text"]) == 500
    assert len(chunks[2]["text"]) == 300


def test_chunk_pages_preserves_overlap():
    chunker = Chunker(
        chunk_size=10,
        chunk_overlap=2,
    )

    pages = [
        {
            "page": 1,
            "text": "abcdefghijklmno",
        }
    ]

    chunks = chunker.chunk_pages(pages)

    assert chunks[0]["text"] == "abcdefghij"
    assert chunks[1]["text"] == "ijklmno"


def test_chunk_pages_preserves_page_number():
    chunker = Chunker(
        chunk_size=100,
        chunk_overlap=0,
    )

    pages = [
        {
            "page": 7,
            "text": "A" * 150,
        }
    ]

    chunks = chunker.chunk_pages(pages)

    for chunk in chunks:
        assert chunk["page"] == 7


def test_chunk_pages_assigns_unique_chunk_ids():
    chunker = Chunker(
        chunk_size=100,
        chunk_overlap=0,
    )

    pages = [
        {
            "page": 1,
            "text": "A" * 150,
        },
        {
            "page": 2,
            "text": "B" * 150,
        },
    ]

    chunks = chunker.chunk_pages(pages)

    chunk_ids = [chunk["chunk_id"] for chunk in chunks]

    assert chunk_ids == [1, 2, 3, 4]


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