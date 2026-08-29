from unittest.mock import Mock, patch

from src.annotation.annotator import AnnotationContext
from src.extraction.ner_model import NERModel


def create_context() -> AnnotationContext:
    return AnnotationContext(
        chunk_id="chunk_001",
        document_id="document_001",
        page_start=3,
        page_end=4,
    )


@patch("src.extraction.ner_model.pipeline")
@patch(
    "src.extraction.ner_model."
    "AutoModelForTokenClassification"
)
@patch("src.extraction.ner_model.AutoTokenizer")
def test_predict_maps_ner_entities(
    mock_tokenizer,
    mock_model,
    mock_pipeline,
):
    mock_ner = Mock()

    mock_ner.return_value = [
        {
            "entity_group": "ORG",
            "score": 0.99,
            "word": "Microsoft",
            "start": 0,
            "end": 9,
        },
        {
            "entity_group": "PER",
            "score": 0.97,
            "word": "Satya Nadella",
            "start": 14,
            "end": 27,
        },
        {
            "entity_group": "LOC",
            "score": 0.98,
            "word": "New York",
            "start": 37,
            "end": 45,
        },
    ]

    mock_pipeline.return_value = mock_ner

    model = NERModel()

    entities = model.predict(
        text=(
            "Microsoft CEO Satya Nadella "
            "lives in New York."
        ),
        context=create_context(),
    )

    assert len(entities) == 3

    assert entities[0].text == "Microsoft"
    assert entities[0].label == "ORGANIZATION"
    assert entities[0].confidence == 0.99

    assert entities[1].text == "Satya Nadella"
    assert entities[1].label == "PERSON"

    assert entities[2].text == "New York"
    assert entities[2].label == "LOCATION"


@patch("src.extraction.ner_model.pipeline")
@patch(
    "src.extraction.ner_model."
    "AutoModelForTokenClassification"
)
@patch("src.extraction.ner_model.AutoTokenizer")
def test_predict_preserves_context(
    mock_tokenizer,
    mock_model,
    mock_pipeline,
):
    mock_ner = Mock()

    mock_ner.return_value = [
        {
            "entity_group": "ORG",
            "score": 0.99,
            "word": "Microsoft",
            "start": 0,
            "end": 9,
        },
    ]

    mock_pipeline.return_value = mock_ner

    model = NERModel()

    entities = model.predict(
        text="Microsoft",
        context=create_context(),
    )

    entity = entities[0]

    assert entity.chunk_id == "chunk_001"
    assert entity.document_id == "document_001"
    assert entity.page_start == 3
    assert entity.page_end == 4


@patch("src.extraction.ner_model.pipeline")
@patch(
    "src.extraction.ner_model."
    "AutoModelForTokenClassification"
)
@patch("src.extraction.ner_model.AutoTokenizer")
def test_predict_ignores_misc_entities(
    mock_tokenizer,
    mock_model,
    mock_pipeline,
):
    mock_ner = Mock()

    mock_ner.return_value = [
        {
            "entity_group": "MISC",
            "score": 0.93,
            "word": "Azure",
            "start": 0,
            "end": 5,
        },
    ]

    mock_pipeline.return_value = mock_ner

    model = NERModel()

    entities = model.predict(
        text="Azure",
        context=create_context(),
    )

    assert entities == []


@patch("src.extraction.ner_model.pipeline")
@patch(
    "src.extraction.ner_model."
    "AutoModelForTokenClassification"
)
@patch("src.extraction.ner_model.AutoTokenizer")
def test_predict_empty_text(
    mock_tokenizer,
    mock_model,
    mock_pipeline,
):
    model = NERModel()

    entities = model.predict(
        text="",
        context=create_context(),
    )

    assert entities == []

    mock_pipeline.return_value.assert_not_called()

@patch("src.extraction.ner_model.pipeline")
@patch(
    "src.extraction.ner_model."
    "AutoModelForTokenClassification"
)
@patch("src.extraction.ner_model.AutoTokenizer")
def test_model_name_can_be_overridden(
    mock_tokenizer,
    mock_model,
    mock_pipeline,
):
    NERModel(
        model_name="test-model"
    )

    mock_tokenizer.from_pretrained.assert_called_once_with(
        "test-model"
    )

    mock_model.from_pretrained.assert_called_once_with(
        "test-model"
    )