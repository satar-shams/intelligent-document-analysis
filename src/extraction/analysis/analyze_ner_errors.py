"""
NER Error Analysis.

Purpose:
    Perform detailed manual analysis of the best NER model selected by
    compare_ner_models.py.

The mathematical evaluation remains strict and unchanged.

Workflow:

    compare_ner_models.py
            |
            v
       select_best_model()
            |
            v
    analyze_ner_errors.py
            |
            +--> load selected model
            |
            +--> run predictions
            |
            +--> strict mathematical matching
            |
            +--> diagnostic analysis
            |
            +--> detailed report

Usage:

    python -m src.extraction.analyze_ner_errors
"""

from __future__ import annotations

from pathlib import Path

from transformers import pipeline

from src.extraction.analysis.dataset import (
    extract_gold_entities,
    extract_text,
    load_test_dataset,
)
from src.extraction.analysis.matching import match_entities
from src.extraction.analysis.models import (
    ChunkAnalysis,
    Entity,
)
from src.extraction.analysis.reporting import print_report
from src.extraction.compare_ner_models import (
    MODELS,
    evaluate_model,
    select_best_model,
)


TEST_FILE = Path(
    "data/processed/extraction/test.jsonl"
)


def load_model(
    model_config: dict,
):
    """Load the selected NER model."""

    return pipeline(
        "ner",
        model=model_config["name"],
        aggregation_strategy="simple",
    )


def predict_entities(
    ner,
    text: str,
    label_mapping: dict[str, str],
) -> list[Entity]:
    """
    Run the selected NER model on one chunk.

    Only labels represented in the selected model's mapping are retained.
    """

    predictions = ner(text)

    entities: list[Entity] = []

    for prediction in predictions:

        native_label = prediction.get(
            "entity_group"
        )

        if native_label not in label_mapping:
            continue

        ida_label = label_mapping[
            native_label
        ]

        entity_text = str(
            prediction["word"]
        ).strip()

        if not entity_text:
            continue

        entities.append(
            Entity(
                text=entity_text,
                label=ida_label,
                start=int(
                    prediction["start"]
                ),
                end=int(
                    prediction["end"]
                ),
            )
        )

    return entities


def analyze_chunk(
    chunk_index: int,
    record: dict,
    ner,
    label_mapping: dict[str, str],
) -> ChunkAnalysis:
    """Run complete analysis for one chunk."""

    text = extract_text(record)

    gold = extract_gold_entities(
        record
    )

    predicted = predict_entities(
        ner=ner,
        text=text,
        label_mapping=label_mapping,
    )

    (
        exact_matches,
        false_negatives,
        false_positives,
    ) = match_entities(
        gold=gold,
        predicted=predicted,
    )

    return ChunkAnalysis(
        chunk_index=chunk_index,
        text=text,
        gold=gold,
        predicted=predicted,
        exact_matches=exact_matches,
        false_positives=false_positives,
        false_negatives=false_negatives,
    )


def select_best_model_config(
    dataset: list[dict],
) -> dict:
    """
    Run the official model comparison and return the selected
    model configuration.
    """

    results = []

    for model_config in MODELS:

        result = evaluate_model(
            model_config=model_config,
            records=dataset,
        )

        results.append(result)

    best_model = select_best_model(
        results
    )

    return next(
        config
        for config in MODELS
        if config["name"] == best_model.name
    )


def analyze_dataset(
    dataset: list[dict],
    model_config: dict,
) -> list[ChunkAnalysis]:
    """Run detailed analysis over the complete test dataset."""

    ner = load_model(
        model_config
    )

    chunks: list[ChunkAnalysis] = []

    for index, record in enumerate(
        dataset,
        start=1,
    ):

        chunks.append(
            analyze_chunk(
                chunk_index=index,
                record=record,
                ner=ner,
                label_mapping=model_config[
                    "label_mapping"
                ],
            )
        )

    return chunks


def main() -> None:
    """Run the complete NER error-analysis workflow."""

    dataset = load_test_dataset(
        TEST_FILE
    )

    model_config = select_best_model_config(
        dataset
    )

    chunks = analyze_dataset(
        dataset=dataset,
        model_config=model_config,
    )

    print_report(
        chunks=chunks,
        model_config=model_config,
    )


if __name__ == "__main__":
    main()