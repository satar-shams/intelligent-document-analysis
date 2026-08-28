from unittest.mock import Mock

from src.annotation.annotator import AnnotationContext
from src.extraction.entity_extractor import EntityExtractor
from src.schemas import ExtractedEntity


def make_entity(
    text: str,
    label: str,
    start: int,
    end: int,
    confidence: float = 0.9,
) -> ExtractedEntity:

    return ExtractedEntity(
        text=text,
        label=label,
        start=start,
        end=end,
        confidence=confidence,
        chunk_id="chunk_001",
        document_id="document_001",
        page_start=1,
        page_end=1,
    )


def make_context() -> AnnotationContext:

    return AnnotationContext(
        chunk_id="chunk_001",
        document_id="document_001",
        page_start=1,
        page_end=1,
    )


def make_extractor(
    rule_entities: list[ExtractedEntity],
    ner_entities: list[ExtractedEntity],
) -> EntityExtractor:

    extractor = EntityExtractor.__new__(
        EntityExtractor
    )

    extractor.rule_based_extractor = Mock()
    extractor.ner_model = Mock()

    extractor.rule_based_extractor.annotate.return_value = (
        rule_entities
    )

    extractor.ner_model.predict.return_value = (
        ner_entities
    )

    return extractor


def test_extract_combines_rule_and_ner_entities():

    rule_entity = make_entity(
        text="Azure",
        label="PRODUCT",
        start=0,
        end=5,
    )

    ner_entity = make_entity(
        text="Microsoft",
        label="ORGANIZATION",
        start=10,
        end=19,
    )

    extractor = make_extractor(
        rule_entities=[rule_entity],
        ner_entities=[ner_entity],
    )

    entities = extractor.extract(
        text="Azure and Microsoft",
        context=make_context(),
    )

    assert entities == [
        rule_entity,
        ner_entity,
    ]


def test_extract_removes_exact_duplicates():

    rule_entity = make_entity(
        text="Microsoft",
        label="ORGANIZATION",
        start=0,
        end=9,
        confidence=0.90,
    )

    ner_entity = make_entity(
        text="Microsoft",
        label="ORGANIZATION",
        start=0,
        end=9,
        confidence=0.99,
    )

    extractor = make_extractor(
        rule_entities=[rule_entity],
        ner_entities=[ner_entity],
    )

    entities = extractor.extract(
        text="Microsoft",
        context=make_context(),
    )

    assert entities == [rule_entity]


def test_rule_priority_entity_wins_overlap():

    rule_entity = make_entity(
        text="$10 million",
        label="MONEY",
        start=0,
        end=11,
        confidence=0.99,
    )

    ner_entity = make_entity(
        text="10 million",
        label="MISC",
        start=1,
        end=11,
        confidence=0.95,
    )

    extractor = make_extractor(
        rule_entities=[rule_entity],
        ner_entities=[ner_entity],
    )

    entities = extractor.extract(
        text="$10 million",
        context=make_context(),
    )

    assert entities == [rule_entity]


def test_non_priority_ner_entity_replaces_overlap():

    rule_entity = make_entity(
        text="Microsoft",
        label="ORGANIZATION",
        start=0,
        end=9,
    )

    ner_entity = make_entity(
        text="Microsoft CEO",
        label="PERSON",
        start=0,
        end=13,
    )

    extractor = make_extractor(
        rule_entities=[rule_entity],
        ner_entities=[ner_entity],
    )

    entities = extractor.extract(
        text="Microsoft CEO",
        context=make_context(),
    )

    assert entities == [ner_entity]