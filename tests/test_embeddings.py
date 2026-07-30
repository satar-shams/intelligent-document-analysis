from unittest.mock import Mock

import pytest

from src.embeddings.embedding_pipeline import EmbeddingPipeline


def test_embed_returns_one_embedding_per_text():

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

    embeddings = pipeline.embed(texts)

    assert len(embeddings) == len(texts)


def test_embed_returns_python_lists():

    mock_model = Mock()
    mock_model.encode.return_value.tolist.return_value = [
        [1.0, 2.0],
    ]

    pipeline = EmbeddingPipeline(
        model_name="unused",
        model=mock_model,
    )

    embeddings = pipeline.embed(
        [
            "Hello",
        ]
    )

    assert isinstance(embeddings, list)
    assert isinstance(embeddings[0], list)


def test_embed_returns_empty_list_for_empty_input():

    mock_model = Mock()

    pipeline = EmbeddingPipeline(
        model_name="unused",
        model=mock_model,
    )

    embeddings = pipeline.embed([])

    assert embeddings == []

    mock_model.encode.assert_not_called()


def test_embed_raises_for_non_list_input():

    pipeline = EmbeddingPipeline(
        model_name="unused",
        model=Mock(),
    )

    with pytest.raises(TypeError):
        pipeline.embed("Hello")


def test_embed_raises_for_non_string_items():

    pipeline = EmbeddingPipeline(
        model_name="unused",
        model=Mock(),
    )

    with pytest.raises(TypeError):
        pipeline.embed(
            [
                "Hello",
                123,
            ]
        )


def test_embed_calls_encode_once_with_original_texts():

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

    pipeline.embed(texts)

    mock_model.encode.assert_called_once_with(texts)