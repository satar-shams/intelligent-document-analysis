import json
from pathlib import Path

from src.config import PROCESSED_DATA_PATH


ANNOTATION_FILE = (
    Path(PROCESSED_DATA_PATH)
    / "annotation"
    / "annotated_dataset.jsonl"
)

ALLOWED_LABELS = {
    "DATE",
    "PRODUCT",
    "MONEY",
    "ORGANIZATION",
    "PERCENTAGE",
}


def validate_entity(
    entity: dict,
    chunk: dict,
) -> list[str]:

    errors: list[str] = []

    required_fields = {
        "text",
        "label",
        "start",
        "end",
        "confidence",
        "chunk_id",
        "document_id",
        "page_start",
        "page_end",
    }

    missing_fields = required_fields - entity.keys()

    if missing_fields:
        errors.append(
            f"missing fields: {sorted(missing_fields)}"
        )
        return errors

    start = entity["start"]
    end = entity["end"]
    text = entity["text"]
    chunk_text = chunk["text"]

    if not isinstance(start, int):
        errors.append("start must be an integer")

    if not isinstance(end, int):
        errors.append("end must be an integer")

    if isinstance(start, int) and isinstance(end, int):

        if start < 0:
            errors.append("start cannot be negative")

        if end > len(chunk_text):
            errors.append(
                f"end {end} exceeds text length "
                f"{len(chunk_text)}"
            )

        if start >= end:
            errors.append(
                f"invalid span: start={start}, end={end}"
            )

        if (
            0 <= start < end <= len(chunk_text)
            and chunk_text[start:end] != text
        ):
            errors.append(
                f"offset mismatch: "
                f"expected {text!r}, "
                f"found {chunk_text[start:end]!r}"
            )

    label = entity["label"]

    if label not in ALLOWED_LABELS:
        errors.append(
            f"invalid label: {label!r}"
        )

    if entity["chunk_id"] != chunk["chunk_id"]:
        errors.append(
            "chunk_id does not match parent chunk"
        )

    if entity["document_id"] != chunk["document_id"]:
        errors.append(
            "document_id does not match parent chunk"
        )

    return errors


def validate_overlaps(
    entities: list[dict],
) -> list[str]:

    errors: list[str] = []

    valid_entities = [
        entity
        for entity in entities
        if isinstance(entity.get("start"), int)
        and isinstance(entity.get("end"), int)
    ]

    sorted_entities = sorted(
        valid_entities,
        key=lambda entity: (
            entity["start"],
            entity["end"],
        ),
    )

    for previous, current in zip(
        sorted_entities,
        sorted_entities[1:],
    ):
        if current["start"] < previous["end"]:
            errors.append(
                "overlapping entities: "
                f"{previous['text']!r} "
                f"({previous['start']}-{previous['end']}) "
                f"and "
                f"{current['text']!r} "
                f"({current['start']}-{current['end']})"
            )

    return errors


def validate_dataset(
    annotation_file: Path = ANNOTATION_FILE,
) -> tuple[int, int, list[str]]:

    total_chunks = 0
    total_entities = 0
    errors: list[str] = []

    if not annotation_file.exists():
        raise FileNotFoundError(
            f"Annotation dataset not found: {annotation_file}"
        )

    with annotation_file.open(
        mode="r",
        encoding="utf-8",
    ) as file:

        for line_number, line in enumerate(
            file,
            start=1,
        ):
            total_chunks += 1

            try:
                chunk = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(
                    f"Line {line_number}: invalid JSON: {exc}"
                )
                continue

            required_fields = {
                "chunk_id",
                "document_id",
                "text",
                "page_start",
                "page_end",
                "entities",
            }

            missing_fields = (
                required_fields - chunk.keys()
            )

            if missing_fields:
                errors.append(
                    f"Line {line_number}: "
                    f"missing fields: "
                    f"{sorted(missing_fields)}"
                )
                continue

            if not isinstance(chunk["text"], str):
                errors.append(
                    f"Line {line_number}: text must be a string"
                )
                continue

            if not chunk["text"].strip():
                errors.append(
                    f"Line {line_number}: empty text"
                )

            entities = chunk["entities"]

            if not isinstance(entities, list):
                errors.append(
                    f"Line {line_number}: "
                    "entities must be a list"
                )
                continue

            total_entities += len(entities)

            for entity_index, entity in enumerate(
                entities
            ):
                if not isinstance(entity, dict):
                    errors.append(
                        f"Line {line_number}, "
                        f"entity {entity_index}: "
                        "entity must be an object"
                    )
                    continue

                entity_errors = validate_entity(
                    entity=entity,
                    chunk=chunk,
                )

                for error in entity_errors:
                    errors.append(
                        f"Line {line_number}, "
                        f"entity {entity_index}: "
                        f"{error}"
                    )

            overlap_errors = validate_overlaps(
                entities
            )

            for error in overlap_errors:
                errors.append(
                    f"Line {line_number}: {error}"
                )

    return total_chunks, total_entities, errors


def main() -> None:

    print("=" * 60)
    print("ANNOTATION DATASET VALIDATION")
    print("=" * 60)

    total_chunks, total_entities, errors = (
        validate_dataset()
    )

    print(f"\nDataset: {ANNOTATION_FILE}")
    print(f"Total chunks: {total_chunks}")
    print(f"Total entities: {total_entities}")
    print(f"Validation errors: {len(errors)}")

    if errors:
        print("\nERRORS")
        print("-" * 60)

        for error in errors:
            print(f"- {error}")

        raise SystemExit(1)

    print("\nValidation successful.")
    print("All annotation records are structurally valid.")


if __name__ == "__main__":
    main()