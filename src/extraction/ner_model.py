from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    pipeline,
)

from src.annotation.annotator import AnnotationContext
from src.schemas import ExtractedEntity


MODEL_NAME = "dslim/bert-base-NER"


LABEL_MAPPING = {
    "ORG": "ORGANIZATION",
    "PER": "PERSON",
    "LOC": "LOCATION",
}


class NERModel:
    """Run pretrained NER inference."""

    def __init__(
        self,
        model_name: str = MODEL_NAME,
    ) -> None:

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name
        )

        self.model = (
            AutoModelForTokenClassification.from_pretrained(
                model_name
            )
        )

        self.pipeline = pipeline(
            "ner",
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple",
        )

    def predict(
        self,
        text: str,
        context: AnnotationContext,
    ) -> list[ExtractedEntity]:

        if not text.strip():
            return []

        predictions = self.pipeline(text)

        entities: list[ExtractedEntity] = []

        for prediction in predictions:

            entity_group = prediction[
                "entity_group"
            ]

            label = LABEL_MAPPING.get(
                entity_group
            )

            if label is None:
                continue

            entities.append(
                ExtractedEntity(
                    text=prediction["word"],
                    label=label,
                    start=prediction["start"],
                    end=prediction["end"],
                    confidence=float(
                        prediction["score"]
                    ),
                    chunk_id=context.chunk_id,
                    document_id=context.document_id,
                    page_start=context.page_start,
                    page_end=context.page_end,
                )
            )

        return entities


def main() -> None:

    model = NERModel()

    context = AnnotationContext(
        chunk_id="test_chunk_001",
        document_id="test_document_001",
        page_start=1,
        page_end=1,
    )

    test_texts = [
        (
            "Simple NER test",
            "Microsoft CEO Satya Nadella "
            "lives in New York.",
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

        entities = model.predict(
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