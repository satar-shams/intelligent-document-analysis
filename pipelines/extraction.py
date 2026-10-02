import json
from pathlib import Path

from src.annotation.annotator import AnnotationContext
from src.config import EXTRACTION_DATA_PATH
from src.extraction.entity_extractor import EntityExtractor


INPUT_FILE = (
    Path(EXTRACTION_DATA_PATH)
    / "test.jsonl"
)

OUTPUT_FILE = (
    Path(EXTRACTION_DATA_PATH)
    / "predictions.jsonl"
)


def load_dataset(
    input_file: Path,
) -> list[dict]:

    records: list[dict] = []

    with input_file.open(
        mode="r",
        encoding="utf-8",
    ) as file:

        for line in file:

            if not line.strip():
                continue

            records.append(
                json.loads(line)
            )

    return records


def write_dataset(
    records: list[dict],
    output_file: Path,
) -> None:

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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


def run_extraction(
    records: list[dict],
) -> list[dict]:

    entity_extractor = EntityExtractor()

    results: list[dict] = []

    for record in records:

        context = AnnotationContext(
            chunk_id=record["chunk_id"],
            document_id=record["document_id"],
            page_start=record["page_start"],
            page_end=record["page_end"],
        )

        entities = entity_extractor.extract(
            text=record["text"],
            context=context,
        )

        result = record.copy()

        result["predicted_entities"] = [
            {
                "text": entity.text,
                "label": entity.label,
                "start": entity.start,
                "end": entity.end,
                "confidence": entity.confidence,
                "chunk_id": entity.chunk_id,
                "document_id": entity.document_id,
                "page_start": entity.page_start,
                "page_end": entity.page_end,
            }
            for entity in entities
        ]

        results.append(result)

    return results


def main() -> None:

    print("=" * 60)
    print("ENTITY EXTRACTION PIPELINE")
    print("=" * 60)

    records = load_dataset(
        INPUT_FILE
    )

    print(
        f"\nInput chunks: {len(records)}"
    )

    results = run_extraction(
        records
    )

    write_dataset(
        results,
        OUTPUT_FILE,
    )

    total_entities = sum(
        len(record["predicted_entities"])
        for record in results
    )

    chunks_with_entities = sum(
        bool(record["predicted_entities"])
        for record in results
    )

    print(
        f"Chunks processed: {len(results)}"
    )

    print(
        f"Chunks with entities: "
        f"{chunks_with_entities}"
    )

    print(
        f"Total predicted entities: "
        f"{total_entities}"
    )

    print(
        f"\nOutput written to: "
        f"{OUTPUT_FILE}"
    )

    print("\n" + "=" * 60)
    print("ENTITY EXTRACTION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()