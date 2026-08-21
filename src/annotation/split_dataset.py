import json
import random
from pathlib import Path

from src.config import (
    ANNOTATION_RANDOM_SEED,
    PROCESSED_DATA_PATH,
)


ANNOTATION_DIRECTORY = (
    Path(PROCESSED_DATA_PATH)
    / "annotation"
)

INPUT_FILE = (
    ANNOTATION_DIRECTORY
    / "annotated_dataset.jsonl"
)

TRAIN_FILE = (
    ANNOTATION_DIRECTORY
    / "train.jsonl"
)

VALIDATION_FILE = (
    ANNOTATION_DIRECTORY
    / "validation.jsonl"
)

TEST_FILE = (
    ANNOTATION_DIRECTORY
    / "test.jsonl"
)

TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.15
TEST_RATIO = 0.15


def load_dataset(
    input_file: Path,
) -> list[dict]:

    records: list[dict] = []

    with input_file.open(
        mode="r",
        encoding="utf-8",
    ) as file:

        for line in file:
            line = line.strip()

            if line:
                records.append(
                    json.loads(line)
                )

    return records


def write_dataset(
    records: list[dict],
    output_file: Path,
) -> None:

    with output_file.open(
        mode="w",
        encoding="utf-8",
    ) as file:

        for record in records:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )


def split_dataset(
    records: list[dict],
) -> tuple[list[dict], list[dict], list[dict]]:

    if not records:
        raise ValueError(
            "Cannot split an empty dataset."
        )

    total = len(records)

    if total < 3:
        raise ValueError(
            "Dataset must contain at least 3 records."
        )

    shuffled = records.copy()

    random.Random(
        ANNOTATION_RANDOM_SEED
    ).shuffle(shuffled)

    train_end = int(
        total * TRAIN_RATIO
    )

    validation_end = (
        train_end
        + int(total * VALIDATION_RATIO)
    )

    train = shuffled[:train_end]

    validation = shuffled[
        train_end:validation_end
    ]

    test = shuffled[
        validation_end:
    ]

    return train, validation, test


def main() -> None:

    print("=" * 60)
    print("ANNOTATION DATASET SPLIT")
    print("=" * 60)

    records = load_dataset(
        INPUT_FILE
    )

    train, validation, test = split_dataset(
        records
    )

    write_dataset(
        train,
        TRAIN_FILE,
    )

    write_dataset(
        validation,
        VALIDATION_FILE,
    )

    write_dataset(
        test,
        TEST_FILE,
    )

    print(
        f"\nTotal records: {len(records)}"
    )

    print(
        f"Train:        {len(train)}"
    )

    print(
        f"Validation:   {len(validation)}"
    )

    print(
        f"Test:         {len(test)}"
    )

    print(
        f"\nRandom seed: {ANNOTATION_RANDOM_SEED}"
    )

    print("\nFiles written:")

    print(f"  {TRAIN_FILE}")
    print(f"  {VALIDATION_FILE}")
    print(f"  {TEST_FILE}")


if __name__ == "__main__":
    main()