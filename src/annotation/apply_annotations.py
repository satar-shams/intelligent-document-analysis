import json
from pathlib import Path

from src.annotation.annotator import (
    AnnotationContext,
    AutomaticAnnotator,
)


INPUT_FILE = Path(
    "data/processed/annotation/annotation_dataset.jsonl"
)

OUTPUT_FILE = Path(
    "data/processed/annotation/annotated_dataset.jsonl"
)


def apply_annotations() -> None:

    annotator = AutomaticAnnotator()

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    total_chunks = 0
    total_entities = 0

    with (
        INPUT_FILE.open(
            "r",
            encoding="utf-8",
        ) as input_file,
        OUTPUT_FILE.open(
            "w",
            encoding="utf-8",
        ) as output_file,
    ):

        for line in input_file:

            if not line.strip():
                continue

            record = json.loads(line)

            context = AnnotationContext(
                chunk_id=record["chunk_id"],
                document_id=record["document_id"],
                page_start=record["page_start"],
                page_end=record["page_end"],
            )

            entities = annotator.annotate(
                text=record["text"],
                context=context,
            )

            record["entities"] = [
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

            output_file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )

            total_chunks += 1
            total_entities += len(entities)

    print(
        f"Annotated chunks: {total_chunks}"
    )

    print(
        f"Total entities: {total_entities}"
    )

    print(
        f"Annotated dataset written to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    apply_annotations()