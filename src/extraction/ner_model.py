from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    pipeline,
)

from src.annotation.annotator import AnnotationContext
from src.schemas import ExtractedEntity

from src.config import NER_MODEL_NAME


LABEL_MAPPING = {
    "ORG": "ORGANIZATION",
    "PER": "PERSON",
    "LOC": "LOCATION",
}


class NERModel:
    """Run pretrained NER inference."""

    def __init__(
        self,
        model_name: str = NER_MODEL_NAME,
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

