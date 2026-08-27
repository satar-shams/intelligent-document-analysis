from collections import Counter
from dataclasses import dataclass

from src.schemas import ExtractedEntity


@dataclass
class EntityMetrics:
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1: float


class EntityEvaluator:
    """Evaluate predicted entities against annotated entities."""

    def evaluate(
        self,
        expected: list[ExtractedEntity],
        predicted: list[ExtractedEntity],
    ) -> EntityMetrics:
        expected_counter = Counter(
            self._entity_key(entity)
            for entity in expected
        )

        predicted_counter = Counter(
            self._entity_key(entity)
            for entity in predicted
        )

        true_positives = sum(
            (expected_counter & predicted_counter).values()
        )

        false_positives = sum(
            (predicted_counter - expected_counter).values()
        )

        false_negatives = sum(
            (expected_counter - predicted_counter).values()
        )

        precision = self._precision(
            true_positives,
            false_positives,
        )

        recall = self._recall(
            true_positives,
            false_negatives,
        )

        f1 = self._f1(
            precision,
            recall,
        )

        return EntityMetrics(
            true_positives=true_positives,
            false_positives=false_positives,
            false_negatives=false_negatives,
            precision=precision,
            recall=recall,
            f1=f1,
        )

    def evaluate_by_label(
        self,
        expected: list[ExtractedEntity],
        predicted: list[ExtractedEntity],
    ) -> dict[str, EntityMetrics]:
        labels = sorted(
            {
                entity.label
                for entity in expected
            }
            |
            {
                entity.label
                for entity in predicted
            }
        )

        results: dict[str, EntityMetrics] = {}

        for label in labels:
            expected_label = [
                entity
                for entity in expected
                if entity.label == label
            ]

            predicted_label = [
                entity
                for entity in predicted
                if entity.label == label
            ]

            results[label] = self.evaluate(
                expected=expected_label,
                predicted=predicted_label,
            )

        return results

    @staticmethod
    def _entity_key(
        entity: ExtractedEntity,
    ) -> tuple[str, str, int, int]:
        return (
            entity.text,
            entity.label,
            entity.start,
            entity.end,
        )

    @staticmethod
    def _precision(
        true_positives: int,
        false_positives: int,
    ) -> float:
        denominator = (
            true_positives + false_positives
        )

        if denominator == 0:
            return 0.0

        return true_positives / denominator

    @staticmethod
    def _recall(
        true_positives: int,
        false_negatives: int,
    ) -> float:
        denominator = (
            true_positives + false_negatives
        )

        if denominator == 0:
            return 0.0

        return true_positives / denominator

    @staticmethod
    def _f1(
        precision: float,
        recall: float,
    ) -> float:
        if precision + recall == 0:
            return 0.0

        return (
            2 * precision * recall
            / (precision + recall)
        )