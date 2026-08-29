import json
from pathlib import Path

from src.extraction.analysis.models import Entity

def load_test_dataset(
    path: Path,
) -> list[dict]:
    """Load the test JSONL dataset."""

    if not path.exists():
        raise FileNotFoundError(
            f"Test file not found: {path}"
        )

    records = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line_number, line in enumerate(
            file,
            start=1,
        ):

            line = line.strip()

            if not line:
                continue

            try:
                records.append(
                    json.loads(line)
                )
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line "
                    f"{line_number}: {path}"
                ) from exc

    return records


# ============================================================================
# ENTITY EXTRACTION
# ============================================================================


def extract_text(
    record: dict,
) -> str:
    """Extract text from one dataset record."""

    text = record.get("text")

    if text is None:
        raise KeyError(
            "Dataset record does not contain `text`."
        )

    return str(text)


def extract_gold_entities(
    record: dict,
) -> list[Entity]:
    """
    Extract gold entities from the dataset.

    The current IDA dataset uses `entities`.
    Common alternatives are supported for robustness.
    """

    candidates = (
        record.get("entities")
        or record.get("text_spans")
        or record.get("spans")
        or []
    )

    entities: list[Entity] = []

    for item in candidates:

        if not isinstance(item, dict):
            continue

        text = (
            item.get("text")
            or item.get("entity")
            or item.get("value")
        )

        label = (
            item.get("label")
            or item.get("type")
            or item.get("entity_type")
        )

        if text is None or label is None:
            continue

        start = item.get("start", -1)
        end = item.get("end", -1)

        entities.append(
            Entity(
                text=str(text),
                label=str(label).upper(),
                start=int(start),
                end=int(end),
            )
        )

    return entities

