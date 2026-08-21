import json
from collections import Counter
from pathlib import Path


INPUT_FILE = Path(
    "data/processed/annotation/annotated_dataset.jsonl"
)


def analyze_dataset() -> None:
    entity_counts = Counter()
    entity_counts_per_chunk = []

    total_chunks = 0
    chunks_with_entities = 0

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            if not line.strip():
                continue

            record = json.loads(line)

            total_chunks += 1

            entities = record.get(
                "entities",
                [],
            )

            if entities:
                chunks_with_entities += 1

            entity_counts_per_chunk.append(
                len(entities)
            )

            for entity in entities:
                entity_counts[
                    entity["label"]
                ] += 1

    chunks_without_entities = (
        total_chunks - chunks_with_entities
    )

    total_entities = sum(
        entity_counts.values()
    )

    average_entities = (
        total_entities / total_chunks
        if total_chunks
        else 0
    )

    maximum_entities = (
        max(entity_counts_per_chunk)
        if entity_counts_per_chunk
        else 0
    )

    minimum_entities = (
        min(entity_counts_per_chunk)
        if entity_counts_per_chunk
        else 0
    )

    print("=" * 60)
    print("ANNOTATION DATASET ANALYSIS")
    print("=" * 60)

    print(
        f"\nTotal chunks: {total_chunks}"
    )

    print(
        f"Chunks with entities: "
        f"{chunks_with_entities}"
    )

    print(
        f"Chunks without entities: "
        f"{chunks_without_entities}"
    )

    print(
        f"\nTotal entities: {total_entities}"
    )

    print(
        f"Average entities per chunk: "
        f"{average_entities:.2f}"
    )

    print(
        f"Minimum entities per chunk: "
        f"{minimum_entities}"
    )

    print(
        f"Maximum entities per chunk: "
        f"{maximum_entities}"
    )

    print("\nEntity distribution:")
    print("-" * 40)

    if not entity_counts:
        print("No entities found.")

    else:
        for label, count in sorted(
            entity_counts.items(),
            key=lambda item: item[1],
            reverse=True,
        ):
            percentage = (
                count / total_entities * 100
                if total_entities
                else 0
            )

            print(
                f"{label:<20}"
                f"{count:>6}"
                f"  ({percentage:>5.1f}%)"
            )


if __name__ == "__main__":
    analyze_dataset()