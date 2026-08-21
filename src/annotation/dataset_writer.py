import json
from pathlib import Path

from src.schemas import Chunk


class AnnotationDatasetWriter:
    """Write sampled chunks to a JSONL annotation dataset."""

    def write(
        self,
        chunks: list[Chunk],
        output_path: str | Path,
    ) -> None:
        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output_path.open(
            mode="w",
            encoding="utf-8",
        ) as file:

            for chunk in chunks:
                record = {
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "text": chunk.text,
                    "page_start": chunk.page_start,
                    "page_end": chunk.page_end,
                    "section_title": chunk.section_title,
                    "entities": [],
                }

                file.write(
                    json.dumps(
                        record,
                        ensure_ascii=False,
                    )
                    + "\n"
                )