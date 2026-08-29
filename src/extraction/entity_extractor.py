from src.annotation.annotator import (
    AnnotationContext,
    AutomaticAnnotator,
)
from src.schemas import ExtractedEntity
from src.extraction.ner_model import NERModel


RULE_BASED_PRIORITY_LABELS = {
    "DATE",
    "MONEY",
    "PERCENTAGE",
    "PRODUCT",
}


class EntityExtractor:
    """Combine deterministic rules and NER predictions."""

    def __init__(
        self,
        ner_model_name: str | None = None,
    ) -> None:

        self.rule_based_extractor = AutomaticAnnotator()

        if ner_model_name is None:
            self.ner_model = NERModel()
        else:
            self.ner_model = NERModel(
                model_name=ner_model_name
            )

    def extract(
        self,
        text: str,
        context: AnnotationContext,
    ) -> list[ExtractedEntity]:

        rule_entities = (
            self.rule_based_extractor.annotate(
                text=text,
                context=context,
            )
        )

        ner_entities = self.ner_model.predict(
            text=text,
            context=context,
        )

        return self._merge_entities(
            rule_entities=rule_entities,
            ner_entities=ner_entities,
        )

    @staticmethod
    def _merge_entities(
        rule_entities: list[ExtractedEntity],
        ner_entities: list[ExtractedEntity],
    ) -> list[ExtractedEntity]:

        selected = list(rule_entities)

        for ner_entity in ner_entities:

            duplicate = any(
                EntityExtractor._same_entity(
                    ner_entity,
                    existing,
                )
                for existing in selected
            )

            if duplicate:
                continue

            overlap = [
                existing
                for existing in selected
                if EntityExtractor._overlaps(
                    ner_entity,
                    existing,
                )
            ]

            if not overlap:
                selected.append(ner_entity)
                continue

            rule_priority_overlap = any(
                existing.label
                in RULE_BASED_PRIORITY_LABELS
                for existing in overlap
            )

            if not rule_priority_overlap:
                selected = [
                    existing
                    for existing in selected
                    if existing not in overlap
                ]

                selected.append(ner_entity)

        return sorted(
            selected,
            key=lambda entity: (
                entity.start,
                entity.end,
            ),
        )

    @staticmethod
    def _same_entity(
        first: ExtractedEntity,
        second: ExtractedEntity,
    ) -> bool:

        return (
            first.start == second.start
            and first.end == second.end
            and first.label == second.label
        )

    @staticmethod
    def _overlaps(
        first: ExtractedEntity,
        second: ExtractedEntity,
    ) -> bool:

        return (
            first.start < second.end
            and first.end > second.start
        )


def main() -> None:

    extractor = EntityExtractor()

    context = AnnotationContext(
        chunk_id="test_chunk_001",
        document_id="test_document_001",
        page_start=1,
        page_end=1,
    )

    test_texts = [
        (
            "Simple entity test",
            "Microsoft CEO Satya Nadella lives in New York.",
        ),
        (
            "IDA-style entity test",
            "Microsoft announced on January 15, 2025 "
            "that Azure revenue increased by 25% "
            "to $10 million in New York.",
        ),
    ]

    for title, text in test_texts:

        print("=" * 60)
        print(title)
        print("=" * 60)

        print(f"\nText:\n{text}")

        entities = extractor.extract(
            text=text,
            context=context,
        )

        print("\nExtracted entities:")

        if not entities:
            print("No entities found.")

        else:
            for entity in entities:
                print(
                    f"{entity.text:<20}"
                    f"→ {entity.label:<15}"
                    f"→ {entity.confidence:.4f}"
                )

        print()


if __name__ == "__main__":
    main()
