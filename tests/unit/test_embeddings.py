from unittest.mock import Mock

import pytest

from src.embeddings.embedding_pipeline import EmbeddingPipeline
from src.schemas import Chunk


# ==================================================
# embed_texts Tests
# ==================================================


def test_embed_texts_returns_one_embedding_per_text():

    mock_model = Mock()
    mock_model.encode.return_value.tolist.return_value = [
        [1.0, 2.0],
        [3.0, 4.0],
    ]

    pipeline = EmbeddingPipeline(
        model_name="unused",
        model=mock_model,
    )

    texts = [
        "Hello",
        "World",
    ]

    embeddings = pipeline.embed_texts(texts)

    assert len(embeddings) == len(texts)


def test_embed_texts_returns_python_lists():

    mock_model = Mock()
    mock_model.encode.return_value.tolist.return_value = [
        [1.0, 2.0],
    ]

    pipeline = EmbeddingPipeline(
        model_name="unused",
        model=mock_model,
    )

    embeddings = pipeline.embed_texts(
        [
            "Hello",
        ]
    )

    assert isinstance(embeddings, list)
    assert isinstance(embeddings[0], list)


def test_embed_texts_returns_empty_list_for_empty_input():

    mock_model = Mock()

    pipeline = EmbeddingPipeline(
        model_name="unused",
        model=mock_model,
    )

    embeddings = pipeline.embed_texts([])

    assert embeddings == []

    mock_model.encode.assert_not_called()


def test_embed_texts_raises_for_non_list_input():

    pipeline = EmbeddingPipeline(
        model_name="unused",
        model=Mock(),
    )

    with pytest.raises(TypeError):
        pipeline.embed_texts("Hello")


def test_embed_texts_raises_for_non_string_items():

    pipeline = EmbeddingPipeline(
        model_name="unused",
        model=Mock(),
    )

    with pytest.raises(TypeError):
        pipeline.embed_texts(
            [
                "Hello",
                123,
            ]
        )


def test_embed_texts_calls_encode_once_with_original_texts():

    mock_model = Mock()
    mock_model.encode.return_value.tolist.return_value = [
        [1.0],
        [2.0],
    ]

    pipeline = EmbeddingPipeline(
        model_name="unused",
        model=mock_model,
    )

    texts = [
        "Hello",
        "World",
    ]

    pipeline.embed_texts(texts)

    mock_model.encode.assert_called_once_with(texts)


# ==================================================
# embed_chunks Tests
# ==================================================


def test_embed_chunks_uses_chunk_text():

    mock_model = Mock()
    mock_model.encode.return_value.tolist.return_value = [
        [1.0, 2.0],
        [3.0, 4.0],
    ]

    pipeline = EmbeddingPipeline(
        model_name="unused",
        model=mock_model,
    )

    chunks = [
        Chunk(
            chunk_id="1",
            document_id="document-1",
            text="Hello",
            page_start=1,
            page_end=1,
        ),
        Chunk(
            chunk_id="2",
            document_id="document-1",
            text="World",
            page_start=1,
            page_end=1,
        ),
    ]

    embeddings = pipeline.embed_chunks(chunks)

    assert len(embeddings) == len(chunks)

    mock_model.encode.assert_called_once_with(
        ["Hello", "World"]
    )


def test_embed_chunks_returns_empty_list_for_empty_input():

    mock_model = Mock()

    pipeline = EmbeddingPipeline(
        model_name="unused",
        model=mock_model,
    )

    embeddings = pipeline.embed_chunks([])

    assert embeddings == []

    mock_model.encode.assert_not_called()