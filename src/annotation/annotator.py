from dataclasses import dataclass

from src.annotation.rules import (
    ENTITY_DICTIONARIES,
    ENTITY_RULES,
)
from src.schemas import ExtractedEntity


@dataclass
class AnnotationContext:
    chunk_id: str
    document_id: str
    page_start: int
    page_end: int


class AutomaticAnnotator:
    """Generate weak annotations using deterministic rules."""

    CONFIDENCE = {
        "DATE": 0.99,
        "MONEY": 0.99,
        "PERCENTAGE": 0.99,
        "ORGANIZATION": 0.90,
        "PRODUCT": 0.95,
    }

    def annotate(
        self,
        text: str,
        context: AnnotationContext,
    ) -> list[ExtractedEntity]:

        entities: list[ExtractedEntity] = []

        entities.extend(
            self._annotate_regex(
                text=text,
                context=context,
            )
        )

        entities.extend(
            self._annotate_dictionary(
                text=text,
                context=context,
            )
        )

        return self._remove_overlaps(entities)

    def _annotate_regex(
        self,
        text: str,
        context: AnnotationContext,
    ) -> list[ExtractedEntity]:

        entities: list[ExtractedEntity] = []

        for label, patterns in ENTITY_RULES.items():

            for pattern in patterns:

                for match in pattern.finditer(text):

                    entities.append(
                        self._create_entity(
                            text=text,
                            start=match.start(),
                            end=match.end(),
                            label=label,
                            context=context,
                        )
                    )

        return entities

    def _annotate_dictionary(
        self,
        text: str,
        context: AnnotationContext,
    ) -> list[ExtractedEntity]:

        entities: list[ExtractedEntity] = []

        for label, terms in ENTITY_DICTIONARIES.items():

            for term in terms:

                start = 0

                while True:

                    position = text.find(
                        term,
                        start,
                    )

                    if position == -1:
                        break

                    end = position + len(term)

                    entities.append(
                        self._create_entity(
                            text=text,
                            start=position,
                            end=end,
                            label=label,
                            context=context,
                        )
                    )

                    start = end

        return entities

    def _create_entity(
        self,
        text: str,
        start: int,
        end: int,
        label: str,
        context: AnnotationContext,
    ) -> ExtractedEntity:

        return ExtractedEntity(
            text=text[start:end],
            label=label,
            start=start,
            end=end,
            confidence=self.CONFIDENCE[label],
            chunk_id=context.chunk_id,
            document_id=context.document_id,
            page_start=context.page_start,
            page_end=context.page_end,
        )

    @staticmethod
    def _remove_overlaps(
        entities: list[ExtractedEntity],
    ) -> list[ExtractedEntity]:

        entities = sorted(
            entities,
            key=lambda entity: (
                entity.start,
                -(entity.end - entity.start),
            ),
        )

        selected: list[ExtractedEntity] = []

        for entity in entities:

            overlaps = any(
                entity.start < existing.end
                and entity.end > existing.start
                for existing in selected
            )

            if not overlaps:
                selected.append(entity)

        return selected