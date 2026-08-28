import json
from pathlib import Path

from src.annotation.annotator import AnnotationContext
from src.annotation.evaluator import EntityEvaluator
from src.extraction.ner_model import NERModel
from src.schemas import ExtractedEntity


DATASET_PATH = Path(
    "data/processed/extraction/test.jsonl"
)


def load_test_dataset() -> list[dict]:

    records = []

    with DATASET_PATH.open(
        mode="r",
        encoding="utf-8",
    ) as file:

        for line in file:

            if line.strip():
                records.append(
                    json.loads(line)
                )

    return records


def convert_entities(
    entities: list[dict],
) -> list[ExtractedEntity]:

    return [
        ExtractedEntity(
            text=entity["text"],
            label=entity["label"],
            start=entity["start"],
            end=entity["end"],
            confidence=entity.get(
                "confidence"
            ),
            chunk_id=entity["chunk_id"],
            document_id=entity["document_id"],
            page_start=entity["page_start"],
            page_end=entity["page_end"],
        )
        for entity in entities
    ]


def main() -> None:

    records = load_test_dataset()

    model = NERModel()
    evaluator = EntityEvaluator()

    all_expected: list[ExtractedEntity] = []
    all_predicted: list[ExtractedEntity] = []

    for record in records:

        expected = convert_entities(
            record["entities"]
        )

        context = AnnotationContext(
            chunk_id=record["chunk_id"],
            document_id=record["document_id"],
            page_start=record["page_start"],
            page_end=record["page_end"],
        )

        predicted = model.predict(
            text=record["text"],
            context=context,
        )

        all_expected.extend(expected)
        all_predicted.extend(predicted)

    metrics = evaluator.evaluate(
        expected=all_expected,
        predicted=all_predicted,
    )

    print("=" * 60)
    print("NER MODEL EVALUATION")
    print("=" * 60)

    print(
        f"Test chunks:        {len(records)}"
    )

    print(
        f"Expected entities:  {len(all_expected)}"
    )

    print(
        f"Predicted entities: {len(all_predicted)}"
    )

    print("\nOverall metrics:")
    print("-" * 40)

    print(
        f"True positives:   {metrics.true_positives}"
    )

    print(
        f"False positives:  {metrics.false_positives}"
    )

    print(
        f"False negatives:  {metrics.false_negatives}"
    )

    print(
        f"Precision:        {metrics.precision:.4f}"
    )

    print(
        f"Recall:           {metrics.recall:.4f}"
    )

    print(
        f"F1:               {metrics.f1:.4f}"
    )

    print("\nMetrics by entity type:")
    print("-" * 40)

    by_label = evaluator.evaluate_by_label(
        expected=all_expected,
        predicted=all_predicted,
    )

    for label, label_metrics in by_label.items():

        print(
            f"{label:15}"
            f" P={label_metrics.precision:.4f}"
            f" R={label_metrics.recall:.4f}"
            f" F1={label_metrics.f1:.4f}"
        )


if __name__ == "__main__":
    main()