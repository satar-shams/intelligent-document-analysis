from src.annotation.annotator import (
    AnnotationContext,
    AutomaticAnnotator,
)


def create_context() -> AnnotationContext:
    return AnnotationContext(
        chunk_id="1",
        document_id="test-document",
        page_start=1,
        page_end=1,
    )


def test_money_annotation():

    text = "Microsoft generated $143 billion in revenue."

    annotator = AutomaticAnnotator()

    entities = annotator.annotate(
        text=text,
        context=create_context(),
    )

    money = [
        entity
        for entity in entities
        if entity.label == "MONEY"
    ]

    assert len(money) == 1
    assert money[0].text == "$143 billion"


def test_percentage_annotation():

    text = "Revenue increased by 36 percent."

    annotator = AutomaticAnnotator()

    entities = annotator.annotate(
        text=text,
        context=create_context(),
    )

    percentage = [
        entity
        for entity in entities
        if entity.label == "PERCENTAGE"
    ]

    assert len(percentage) == 1
    assert percentage[0].text == "36 percent"


def test_product_over_organization():

    text = "Microsoft 365 helps organizations."

    annotator = AutomaticAnnotator()

    entities = annotator.annotate(
        text=text,
        context=create_context(),
    )

    assert len(entities) == 1
    assert entities[0].text == "Microsoft 365"
    assert entities[0].label == "PRODUCT"


def test_entity_offsets():

    text = "Microsoft generated $143 billion."

    annotator = AutomaticAnnotator()

    entities = annotator.annotate(
        text=text,
        context=create_context(),
    )

    for entity in entities:
        assert text[entity.start:entity.end] == entity.text