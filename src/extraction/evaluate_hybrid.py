import json
from pathlib import Path

from src.annotation.annotator import (
    AnnotationContext,
    AutomaticAnnotator,
)
from src.annotation.evaluator import EntityEvaluator
from src.config import EXTRACTION_DATA_PATH
from src.extraction.compare_ner_models import (
    MODELS,
    evaluate_model,
    select_best_model,
)
from src.extraction.entity_extractor import EntityExtractor
from src.extraction.ner_model import NERModel
from src.schemas import ExtractedEntity


DATASET_PATH = (
    Path(EXTRACTION_DATA_PATH)
    / "test.jsonl"
)


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

def load_test_dataset(
    input_file: Path,
) -> list[dict]:
    """Load the extraction test dataset."""

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


# ---------------------------------------------------------------------------
# Entity conversion
# ---------------------------------------------------------------------------

def convert_entities(
    entities: list[dict],
) -> list[ExtractedEntity]:
    """Convert dataset entities to ExtractedEntity objects."""

    return [
        ExtractedEntity(
            text=entity["text"],
            label=entity["label"],
            start=entity["start"],
            end=entity["end"],
            confidence=entity.get("confidence"),
            chunk_id=entity["chunk_id"],
            document_id=entity["document_id"],
            page_start=entity["page_start"],
            page_end=entity["page_end"],
        )
        for entity in entities
    ]


# ---------------------------------------------------------------------------
# Model selection
# ---------------------------------------------------------------------------

def select_best_ner_model(
    records: list[dict],
) -> dict:
    """
    Select the best NER model using the official comparison logic.

    The full comparison is intentionally not printed here. Only the
    selected model is returned and reported.
    """

    results = []

    for model_config in MODELS:

        result = evaluate_model(
            model_config=model_config,
            records=records,
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


# ---------------------------------------------------------------------------
# Prediction helpers
# ---------------------------------------------------------------------------

def predict_rule_based(
    extractor: AutomaticAnnotator,
    text: str,
    context: AnnotationContext,
) -> list[ExtractedEntity]:

    return extractor.annotate(
        text=text,
        context=context,
    )


def predict_ner(
    model: NERModel,
    text: str,
    context: AnnotationContext,
) -> list[ExtractedEntity]:

    return model.predict(
        text=text,
        context=context,
    )


def predict_hybrid(
    extractor: EntityExtractor,
    text: str,
    context: AnnotationContext,
) -> list[ExtractedEntity]:

    return extractor.extract(
        text=text,
        context=context,
    )


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_strategy(
    strategy_name: str,
    records: list[dict],
    evaluator: EntityEvaluator,
    ner_model_name: str | None = None,
) -> tuple[
    str,
    object,
    dict[str, object],
    list[dict],
]:
    """
    Evaluate one extraction strategy.

    Returns:
        strategy name
        overall metrics
        metrics by label
        detailed chunk-level predictions
    """

    if strategy_name == "Rule-based":

        extractor = AutomaticAnnotator()

    elif strategy_name == "NER":

        if ner_model_name is None:
            raise ValueError(
                "NER model name is required."
            )

        extractor = NERModel(
            model_name=ner_model_name
        )

    elif strategy_name == "Hybrid":

        if ner_model_name is None:
            raise ValueError(
                "NER model name is required."
            )

        extractor = EntityExtractor(
            ner_model_name=ner_model_name
        )

    else:

        raise ValueError(
            f"Unknown strategy: {strategy_name}"
        )

    all_expected: list[ExtractedEntity] = []
    all_predicted: list[ExtractedEntity] = []

    detailed_results: list[dict] = []

    for record in records:

        expected = convert_entities(
            record.get("entities", [])
        )

        context = AnnotationContext(
            chunk_id=record["chunk_id"],
            document_id=record["document_id"],
            page_start=record["page_start"],
            page_end=record["page_end"],
        )

        if strategy_name == "Rule-based":

            predicted = predict_rule_based(
                extractor=extractor,
                text=record["text"],
                context=context,
            )

        elif strategy_name == "NER":

            predicted = predict_ner(
                model=extractor,
                text=record["text"],
                context=context,
            )

        else:

            predicted = predict_hybrid(
                extractor=extractor,
                text=record["text"],
                context=context,
            )

        all_expected.extend(expected)
        all_predicted.extend(predicted)

        detailed_results.append(
            {
                "chunk_id": record["chunk_id"],
                "text": record["text"],
                "expected": expected,
                "predicted": predicted,
            }
        )

    metrics = evaluator.evaluate(
        expected=all_expected,
        predicted=all_predicted,
    )

    by_label = evaluator.evaluate_by_label(
        expected=all_expected,
        predicted=all_predicted,
    )

    return (
        strategy_name,
        metrics,
        by_label,
        detailed_results,
    )


# ---------------------------------------------------------------------------
# Entity formatting
# ---------------------------------------------------------------------------

def format_entity(
    entity: ExtractedEntity,
) -> str:
    """Format one entity for detailed reporting."""

    confidence = (
        f"{entity.confidence:.4f}"
        if entity.confidence is not None
        else "N/A"
    )

    return (
        f"'{entity.text}'"
        f" [{entity.label}]"
        f" [{entity.start}, {entity.end}]"
        f" conf={confidence}"
    )


def entity_key(
    entity: ExtractedEntity,
) -> tuple[str, str, int, int]:

    return (
        entity.text,
        entity.label,
        entity.start,
        entity.end,
    )


# ---------------------------------------------------------------------------
# Detailed comparison
# ---------------------------------------------------------------------------

def compare_chunk_entities(
    expected: list[ExtractedEntity],
    predicted: list[ExtractedEntity],
) -> tuple[
    list[ExtractedEntity],
    list[ExtractedEntity],
]:
    """
    Return exact false negatives and false positives for one chunk.

    The same exact matching definition used by EntityEvaluator is used here.
    """

    expected_counts = {}

    for entity in expected:

        key = entity_key(entity)

        expected_counts[key] = (
            expected_counts.get(key, 0) + 1
        )

    predicted_counts = {}

    for entity in predicted:

        key = entity_key(entity)

        predicted_counts[key] = (
            predicted_counts.get(key, 0) + 1
        )

    false_negatives: list[ExtractedEntity] = []
    false_positives: list[ExtractedEntity] = []

    for entity in expected:

        key = entity_key(entity)

        if expected_counts.get(key, 0) > 0:

            if predicted_counts.get(key, 0) > 0:

                expected_counts[key] -= 1
                predicted_counts[key] -= 1

            else:

                false_negatives.append(entity)
                expected_counts[key] -= 1

    for entity in predicted:

        key = entity_key(entity)

        if predicted_counts.get(key, 0) > 0:

            false_positives.append(entity)
            predicted_counts[key] -= 1

    return (
        false_negatives,
        false_positives,
    )


def print_detailed_analysis(
    strategy_name: str,
    detailed_results: list[dict],
) -> None:
    """
    Print gold/predicted entities and detailed errors.

    Only chunks containing an error are shown in the detailed section.
    """

    print()
    print("=" * 100)
    print(f"DETAILED {strategy_name.upper()} ANALYSIS")
    print("=" * 100)

    error_chunks = []

    for result in detailed_results:

        false_negatives, false_positives = (
            compare_chunk_entities(
                expected=result["expected"],
                predicted=result["predicted"],
            )
        )

        if false_negatives or false_positives:

            error_chunks.append(
                (
                    result,
                    false_negatives,
                    false_positives,
                )
            )

    if not error_chunks:

        print(
            f"\nNo exact mathematical errors found for "
            f"{strategy_name}."
        )

        return

    print(
        f"\nChunks with mathematical errors: "
        f"{len(error_chunks)}"
    )

    for (
        result,
        false_negatives,
        false_positives,
    ) in error_chunks:

        print()
        print("-" * 100)

        print(
            f"CHUNK: {result['chunk_id']}"
        )

        print(
            f"\nText:\n{result['text']}"
        )

        print("\nGOLD / EXPECTED:")

        if result["expected"]:

            for entity in result["expected"]:

                print(
                    f"    {format_entity(entity)}"
                )

        else:

            print("    None")

        print("\nPREDICTED:")

        if result["predicted"]:

            for entity in result["predicted"]:

                print(
                    f"    {format_entity(entity)}"
                )

        else:

            print("    None")

        print("\nFALSE NEGATIVES:")

        if false_negatives:

            for entity in false_negatives:

                print(
                    f"    {format_entity(entity)}"
                )

        else:

            print("    None")

        print("\nFALSE POSITIVES:")

        if false_positives:

            for entity in false_positives:

                print(
                    f"    {format_entity(entity)}"
                )

        else:

            print("    None")


# ---------------------------------------------------------------------------
# Overall results
# ---------------------------------------------------------------------------

def print_overall_results(
    results: list[
        tuple[
            str,
            object,
            dict[str, object],
            list[dict],
        ]
    ],
) -> None:
    """Print overall extraction comparison."""

    print()
    print("=" * 100)
    print("EXTRACTION STRATEGY COMPARISON")
    print("=" * 100)

    print(
        f"{'STRATEGY':20}"
        f"{'TP':>8}"
        f"{'FP':>8}"
        f"{'FN':>8}"
        f"{'PRECISION':>14}"
        f"{'RECALL':>12}"
        f"{'F1':>10}"
    )

    print("-" * 100)

    for (
        strategy_name,
        metrics,
        _,
        _,
    ) in results:

        print(
            f"{strategy_name:20}"
            f"{metrics.true_positives:8d}"
            f"{metrics.false_positives:8d}"
            f"{metrics.false_negatives:8d}"
            f"{metrics.precision:14.4f}"
            f"{metrics.recall:12.4f}"
            f"{metrics.f1:10.4f}"
        )


# ---------------------------------------------------------------------------
# Label results
# ---------------------------------------------------------------------------

def print_label_results(
    results: list[
        tuple[
            str,
            object,
            dict[str, object],
            list[dict],
        ]
    ],
) -> None:
    """Print metrics for every entity type."""

    labels = sorted(
        {
            label
            for _, _, by_label, _ in results
            for label in by_label
        }
    )

    print()
    print("=" * 90)
    print("METRICS BY ENTITY TYPE")
    print("=" * 90)

    for label in labels:

        print()
        print(f"{label}")
        print("-" * 70)

        print(
            f"{'STRATEGY':20}"
            f"{'TP':>8}"
            f"{'FP':>8}"
            f"{'FN':>8}"
            f"{'PRECISION':>14}"
            f"{'RECALL':>12}"
            f"{'F1':>10}"
        )

        print("-" * 70)

        for (
            strategy_name,
            _,
            by_label,
            _,
        ) in results:

            metrics = by_label.get(label)

            if metrics is None:

                print(
                    f"{strategy_name:20}"
                    f"{'-':>8}"
                    f"{'-':>8}"
                    f"{'-':>8}"
                    f"{'-':>14}"
                    f"{'-':>12}"
                    f"{'-':>10}"
                )

                continue

            print(
                f"{strategy_name:20}"
                f"{metrics.true_positives:8d}"
                f"{metrics.false_positives:8d}"
                f"{metrics.false_negatives:8d}"
                f"{metrics.precision:14.4f}"
                f"{metrics.recall:12.4f}"
                f"{metrics.f1:10.4f}"
            )
                        
# ---------------------------------------------------------------------------
# Best strategy
# ---------------------------------------------------------------------------

def print_best_strategy(
    results: list[
        tuple[
            str,
            object,
            dict[str, object],
            list[dict],
        ]
    ],
) -> None:
    """Print the strategy with the highest F1."""

    best_strategy, best_metrics, _, _ = max(
        results,
        key=lambda result: result[1].f1,
    )

    print()
    print("=" * 100)
    print("BEST EXTRACTION STRATEGY")
    print("=" * 100)

    print(
        f"Best strategy: {best_strategy}"
    )

    print(
        f"Best F1:      {best_metrics.f1:.4f}"
    )

    print(
        f"Precision:    {best_metrics.precision:.4f}"
    )

    print(
        f"Recall:       {best_metrics.recall:.4f}"
    )


# ---------------------------------------------------------------------------
# Selected model
# ---------------------------------------------------------------------------

def print_selected_model(
    model_config: dict,
) -> None:
    """Print the selected NER model."""

    print()
    print("=" * 100)
    print("SELECTED NER MODEL")
    print("=" * 100)

    print(
        f"Model: {model_config['name']}"
    )

    print(
        "This model is used for both standalone NER "
        "and Hybrid evaluation."
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Evaluate rule-based, selected NER, and hybrid extraction."""

    print("=" * 100)
    print("HYBRID EXTRACTION EVALUATION")
    print("=" * 100)

    records = load_test_dataset(
        DATASET_PATH
    )

    total_expected = sum(
        len(record.get("entities", []))
        for record in records
    )

    print(
        f"\nTest chunks:        {len(records)}"
    )

    print(
        f"Expected entities:  {total_expected}"
    )

    # ------------------------------------------------------------------
    # Select best NER model using official comparison logic.
    # ------------------------------------------------------------------

    print(
        "\nSelecting best NER model..."
    )

    model_config = select_best_ner_model(
        records
    )

    print_selected_model(
        model_config
    )

    best_ner_model_name = model_config["name"]

    evaluator = EntityEvaluator()

    # ------------------------------------------------------------------
    # Evaluate all extraction strategies.
    # ------------------------------------------------------------------

    strategies = [
        "Rule-based",
        "NER",
        "Hybrid",
    ]

    results = []

    for strategy_name in strategies:

        print(
            f"\nEvaluating {strategy_name}..."
        )

        result = evaluate_strategy(
            strategy_name=strategy_name,
            records=records,
            evaluator=evaluator,
            ner_model_name=best_ner_model_name,
        )

        results.append(result)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    print_overall_results(
        results
    )

    print_label_results(
        results
    )

    print_best_strategy(
        results
    )

    # ------------------------------------------------------------------
    # Detailed NER analysis.
    # ------------------------------------------------------------------

    ner_result = next(
        result
        for result in results
        if result[0] == "NER"
    )

    print_detailed_analysis(
        strategy_name="NER",
        detailed_results=ner_result[3],
    )

    # ------------------------------------------------------------------
    # Detailed Hybrid analysis.
    # ------------------------------------------------------------------

    hybrid_result = next(
        result
        for result in results
        if result[0] == "Hybrid"
    )

    print_detailed_analysis(
        strategy_name="Hybrid",
        detailed_results=hybrid_result[3],
    )

    # ------------------------------------------------------------------
    # Final information.
    # ------------------------------------------------------------------

    print()
    print("=" * 100)
    print("HYBRID EVALUATION COMPLETED")
    print("=" * 100)

    print(
        f"Selected NER model: {best_ner_model_name}"
    )

    print(
        "The same selected NER model was used for "
        "both NER and Hybrid evaluation."
    )


if __name__ == "__main__":
    main()
