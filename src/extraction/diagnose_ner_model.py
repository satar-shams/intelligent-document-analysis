import json
from pathlib import Path

from transformers import AutoConfig, pipeline

from src.annotation.annotator import AnnotationContext
from src.extraction.ner_model import LABEL_MAPPING
from src.schemas import ExtractedEntity


MODEL_NAME = "musk1209/finsight-ner"

TEST_FILE = Path(
    "data/processed/extraction/test.jsonl"
)


def load_test_dataset() -> list[dict]:
    records = []

    with TEST_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            if line.strip():
                records.append(
                    json.loads(line)
                )

    return records


def print_model_configuration() -> None:

    config = AutoConfig.from_pretrained(
        MODEL_NAME
    )

    print("=" * 70)
    print("MODEL CONFIGURATION")
    print("=" * 70)

    print(f"\nModel: {MODEL_NAME}")

    print("\nNative labels:")

    for label_id, label in config.id2label.items():
        print(f"  {label_id}: {label}")

    print("\nIDA label mapping:")

    for native, ida in LABEL_MAPPING.items():
        print(f"  {native:10} -> {ida}")


def print_expected_entities(
    record: dict,
) -> None:

    print("\nEXPECTED ENTITIES:")

    if not record["entities"]:
        print("  None")
        return

    for entity in record["entities"]:

        print(
            f"  {entity['text']!r:<35}"
            f"{entity['label']:<15}"
            f"[{entity['start']}, {entity['end']}]"
        )


def print_raw_predictions(
    predictions: list[dict],
) -> None:

    print("\nRAW MODEL PREDICTIONS:")

    if not predictions:
        print("  None")
        return

    for prediction in predictions:

        print(
            f"  {prediction['word']!r:<35}"
            f"{prediction['entity_group']:<10}"
            f"score={float(prediction['score']):.4f} "
            f"[{prediction['start']}, "
            f"{prediction['end']}]"
        )


def print_mapped_predictions(
    predictions: list[dict],
) -> None:

    print("\nMAPPED PREDICTIONS:")

    mapped = []

    for prediction in predictions:

        native_label = prediction[
            "entity_group"
        ]

        ida_label = LABEL_MAPPING.get(
            native_label
        )

        if ida_label is None:
            continue

        mapped.append(
            {
                "text": prediction["word"],
                "label": ida_label,
                "start": prediction["start"],
                "end": prediction["end"],
                "score": float(
                    prediction["score"]
                ),
            }
        )

    if not mapped:
        print("  None")
        return

    for entity in mapped:

        print(
            f"  {entity['text']!r:<35}"
            f"{entity['label']:<15}"
            f"score={entity['score']:.4f} "
            f"[{entity['start']}, "
            f"{entity['end']}]"
        )


def print_text_spans(
    record: dict,
) -> None:

    text = record["text"]

    print("\nTEXT SPANS:")

    for entity in record["entities"]:

        start = entity["start"]
        end = entity["end"]

        print(
            f"  [{start}:{end}] "
            f"{text[start:end]!r} "
            f"-> expected={entity['text']!r}"
        )


def main() -> None:

    records = load_test_dataset()

    print_model_configuration()

    print("\n")
    print("=" * 70)
    print("LOADING MODEL")
    print("=" * 70)

    ner = pipeline(
        "ner",
        model=MODEL_NAME,
        aggregation_strategy="simple",
    )

    print("\nModel loaded successfully.")

    print("\n")
    print("=" * 70)
    print("TEST DATASET")
    print("=" * 70)

    print(f"\nTest file: {TEST_FILE}")
    print(f"Test chunks: {len(records)}")

    shown = 0

    for record in records:

        # Start with chunks that actually contain
        # annotations so the comparison is useful.
        if not record["entities"]:
            continue

        shown += 1

        print("\n")
        print("=" * 70)
        print(
            f"CHUNK {shown}"
            f" | chunk_id={record['chunk_id']}"
        )
        print("=" * 70)

        print("\nTEXT:")
        print(record["text"])

        print_text_spans(record)

        print_expected_entities(record)

        predictions = ner(
            record["text"]
        )

        print_raw_predictions(
            predictions
        )

        print_mapped_predictions(
            predictions
        )

        if shown >= 10:
            break

    print("\n")
    print("=" * 70)
    print("DIAGNOSTIC COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()