"""
Reporting utilities for NER error analysis.

This module contains presentation logic only.

It does not perform mathematical evaluation and does not modify
evaluation results.
"""

from __future__ import annotations

from collections import Counter

from src.extraction.analysis.diagnostics import (
    find_boundary_cases,
    find_wrong_label_cases,
    get_context,
)
from src.extraction.analysis.models import (
    ChunkAnalysis,
    Entity,
)


def print_entity(
    entity: Entity,
) -> None:
    """Print one entity."""

    print(
        f"    {entity.text!r:<40}"
        f"{entity.label:<18}"
        f"[{entity.start}, {entity.end}]"
    )


def print_entity_list(
    entities: list[Entity],
) -> None:
    """Print a list of entities."""

    if not entities:
        print("    None")
        return

    for entity in entities:
        print_entity(entity)


def print_pair(
    expected: Entity,
    predicted: Entity,
) -> None:
    """Print a gold/prediction pair."""

    print(
        f"    GOLD      : "
        f"{expected.text!r} "
        f"[{expected.label}]"
    )

    print(
        f"    PREDICTED : "
        f"{predicted.text!r} "
        f"[{predicted.label}]"
    )


def print_summary(
    chunks: list[ChunkAnalysis],
    model_config: dict,
) -> None:
    """Print the compact mathematical and diagnostic summary."""

    gold_count = sum(
        len(chunk.gold)
        for chunk in chunks
    )

    predicted_count = sum(
        len(chunk.predicted)
        for chunk in chunks
    )

    exact_count = sum(
        len(chunk.exact_matches)
        for chunk in chunks
    )

    fp_count = sum(
        len(chunk.false_positives)
        for chunk in chunks
    )

    fn_count = sum(
        len(chunk.false_negatives)
        for chunk in chunks
    )

    boundary_count = sum(
        len(
            find_boundary_cases(
                chunk.gold,
                chunk.predicted,
            )
        )
        for chunk in chunks
    )

    wrong_label_count = sum(
        len(
            find_wrong_label_cases(
                chunk.gold,
                chunk.predicted,
            )
        )
        for chunk in chunks
    )

    empty_prediction_chunks = sum(
        not chunk.predicted
        for chunk in chunks
    )

    empty_with_gold = sum(
        (
            not chunk.predicted
            and bool(chunk.gold)
        )
        for chunk in chunks
    )

    print()
    print("=" * 80)
    print("NER ERROR ANALYSIS")
    print("=" * 80)

    print(
        f"Selected model       : "
        f"{model_config['name']}"
    )

    print(
        f"Test chunks          : "
        f"{len(chunks)}"
    )

    print(
        f"Gold entities        : "
        f"{gold_count}"
    )

    print(
        f"Predicted entities   : "
        f"{predicted_count}"
    )

    print()
    print("STRICT MATHEMATICAL RESULTS")
    print("-" * 80)

    print(
        f"True positives       : "
        f"{exact_count}"
    )

    print(
        f"False positives      : "
        f"{fp_count}"
    )

    print(
        f"False negatives      : "
        f"{fn_count}"
    )

    print()
    print("DIAGNOSTIC CANDIDATES")
    print("-" * 80)

    print(
        f"Boundary candidates  : "
        f"{boundary_count}"
    )

    print(
        f"Wrong-label candidates: "
        f"{wrong_label_count}"
    )

    print(
        f"Zero-prediction chunks: "
        f"{empty_prediction_chunks}"
    )

    print(
        f"Zero-prediction chunks "
        f"with gold entities   : "
        f"{empty_with_gold}"
    )

    print()
    print(
        "NOTE: Diagnostic candidates are still mathematical errors."
    )

    print(
        "They are reported separately only to support manual semantic"
    )

    print(
        "analysis. They are NOT converted into true positives."
    )


def print_full_data(
    chunks: list[ChunkAnalysis],
) -> None:
    """Print every chunk with gold and predicted entities."""

    print()
    print("=" * 80)
    print("FULL GOLD VS PREDICTED DATA")
    print("=" * 80)

    for chunk in chunks:

        print()
        print(
            f"CHUNK #{chunk.chunk_index}"
        )

        print("-" * 80)

        print(
            f"Gold entities      : "
            f"{len(chunk.gold)}"
        )

        print(
            f"Predicted entities : "
            f"{len(chunk.predicted)}"
        )

        print()
        print("TEXT:")
        print(chunk.text)

        print()
        print("GOLD / REAL ENTITIES:")

        print_entity_list(
            chunk.gold
        )

        print()
        print("MODEL PREDICTIONS:")

        print_entity_list(
            chunk.predicted
        )


def print_exact_matches(
    chunks: list[ChunkAnalysis],
) -> None:
    """Print strict mathematical matches."""

    matches: list[
        tuple[Entity, Entity]
    ] = []

    for chunk in chunks:
        matches.extend(
            chunk.exact_matches
        )

    print()
    print("=" * 80)
    print("EXACT MATHEMATICAL MATCHES")
    print("=" * 80)

    print(
        f"Total exact matches: "
        f"{len(matches)}"
    )

    for index, (
        expected,
        predicted,
    ) in enumerate(
        matches,
        start=1,
    ):

        print(
            f"{index:4d}. "
            f"{expected.text!r:<40}"
            f"{expected.label}"
        )


def print_false_positives(
    chunks: list[ChunkAnalysis],
) -> None:
    """Print every mathematical false positive."""

    print()
    print("=" * 80)
    print("APPARENT FALSE POSITIVES")
    print("=" * 80)

    index = 1

    for chunk in chunks:

        for prediction in chunk.false_positives:

            print()
            print(
                f"FP #{index} "
                f"(chunk {chunk.chunk_index})"
            )

            print(
                f"Prediction : "
                f"{prediction.text!r}"
            )

            print(
                f"Label      : "
                f"{prediction.label}"
            )

            print(
                f"Offsets    : "
                f"[{prediction.start}, "
                f"{prediction.end}]"
            )

            print()
            print("Context:")

            print(
                get_context(
                    chunk.text,
                    prediction.start,
                    prediction.end,
                )
            )

            print()
            print("Gold entities in chunk:")

            print_entity_list(
                chunk.gold
            )

            print()
            print("Manual classification:")

            print("    [ ] GENUINE_ERROR")
            print("    [ ] SEMANTICALLY_VALID")
            print("    [ ] BOUNDARY_ERROR")
            print("    [ ] WRONG_LABEL")
            print("    [ ] ANNOTATION_PROBLEM")
            print("    [ ] TOKENIZATION_ERROR")
            print("    [ ] OTHER")

            index += 1


def print_false_negatives(
    chunks: list[ChunkAnalysis],
) -> None:
    """Print every mathematically missed gold entity."""

    print()
    print("=" * 80)
    print("APPARENT FALSE NEGATIVES")
    print("=" * 80)

    index = 1

    for chunk in chunks:

        for expected in chunk.false_negatives:

            print()
            print(
                f"FN #{index} "
                f"(chunk {chunk.chunk_index})"
            )

            print(
                f"Expected : "
                f"{expected.text!r}"
            )

            print(
                f"Label    : "
                f"{expected.label}"
            )

            print(
                f"Offsets  : "
                f"[{expected.start}, "
                f"{expected.end}]"
            )

            print()
            print("Context:")

            print(
                get_context(
                    chunk.text,
                    expected.start,
                    expected.end,
                )
            )

            print()
            print("Predictions in chunk:")

            print_entity_list(
                chunk.predicted
            )

            print()
            print("Manual classification:")

            print("    [ ] GENUINE_MISSED_ENTITY")
            print("    [ ] BOUNDARY_ERROR")
            print("    [ ] WRONG_LABEL")
            print("    [ ] ANNOTATION_PROBLEM")
            print("    [ ] TOKENIZATION_ERROR")
            print("    [ ] OTHER")

            index += 1


def print_boundary_cases(
    chunks: list[ChunkAnalysis],
) -> None:
    """Print overlapping gold/prediction pairs."""

    print()
    print("=" * 80)
    print("POSSIBLE BOUNDARY / PARTIAL MATCHES")
    print("=" * 80)

    total = 0

    for chunk in chunks:

        cases = find_boundary_cases(
            gold=chunk.gold,
            predicted=chunk.predicted,
        )

        for expected, predicted in cases:

            total += 1

            print()
            print(
                f"Boundary case #{total} "
                f"(chunk {chunk.chunk_index})"
            )

            print_pair(
                expected,
                predicted,
            )

            print()
            print("Context:")

            print(
                get_context(
                    chunk.text,
                    predicted.start,
                    predicted.end,
                )
            )

            print()
            print("Manual classification:")

            print("    [ ] SEMANTICALLY_VALID")
            print("    [ ] GENUINE_BOUNDARY_ERROR")
            print("    [ ] ANNOTATION_PROBLEM")
            print("    [ ] OTHER")

    if total == 0:
        print(
            "No overlapping boundary candidates found."
        )


def print_wrong_label_cases(
    chunks: list[ChunkAnalysis],
) -> None:
    """Print same-text predictions with a different label."""

    print()
    print("=" * 80)
    print("POSSIBLE WRONG-LABEL CASES")
    print("=" * 80)

    total = 0

    for chunk in chunks:

        cases = find_wrong_label_cases(
            gold=chunk.gold,
            predicted=chunk.predicted,
        )

        for expected, predicted in cases:

            total += 1

            print()
            print(
                f"Wrong-label case #{total} "
                f"(chunk {chunk.chunk_index})"
            )

            print_pair(
                expected,
                predicted,
            )

            print()
            print("Context:")

            print(
                get_context(
                    chunk.text,
                    predicted.start,
                    predicted.end,
                )
            )

            print()
            print("Manual classification:")

            print("    [ ] GENUINE_WRONG_LABEL")
            print("    [ ] SEMANTICALLY_VALID")
            print("    [ ] ANNOTATION_PROBLEM")
            print("    [ ] OTHER")

    if total == 0:
        print(
            "No same-text wrong-label candidates found."
        )


def print_empty_predictions(
    chunks: list[ChunkAnalysis],
) -> None:
    """Print chunks where the model predicted nothing."""

    empty_chunks = [
        chunk
        for chunk in chunks
        if not chunk.predicted
    ]

    empty_with_gold = [
        chunk
        for chunk in empty_chunks
        if chunk.gold
    ]

    empty_without_gold = [
        chunk
        for chunk in empty_chunks
        if not chunk.gold
    ]

    print()
    print("=" * 80)
    print("ZERO-PREDICTION CHUNKS")
    print("=" * 80)

    print(
        f"Total zero-prediction chunks : "
        f"{len(empty_chunks)}"
    )

    print(
        f"With gold entities            : "
        f"{len(empty_with_gold)}"
    )

    print(
        f"Without gold entities         : "
        f"{len(empty_without_gold)}"
    )

    if not empty_chunks:
        return

    print()

    for chunk in empty_chunks:

        print("-" * 80)

        print(
            f"CHUNK #{chunk.chunk_index}"
        )

        print(
            f"Gold entities: "
            f"{len(chunk.gold)}"
        )

        print()
        print("Gold entities:")

        print_entity_list(
            chunk.gold
        )

        print()
        print("Text:")

        print(chunk.text)

        if chunk.gold:
            print()
            print(
                "Status: MATHEMATICAL MISS "
                "because gold entities exist."
            )
        else:
            print()
            print(
                "Status: No gold entities; "
                "zero prediction is not automatically an error."
            )


def print_prediction_distribution(
    chunks: list[ChunkAnalysis],
) -> None:
    """Print predicted entity distribution by label."""

    distribution = Counter(
        entity.label
        for chunk in chunks
        for entity in chunk.predicted
    )

    print()
    print("=" * 80)
    print("PREDICTION DISTRIBUTION")
    print("=" * 80)

    if not distribution:
        print("No predictions.")
        return

    for label, count in sorted(
        distribution.items()
    ):
        print(
            f"{label:<20}"
            f"{count}"
        )


def print_manual_analysis_header() -> None:
    """Print instructions for manual semantic analysis."""

    print()
    print("=" * 80)
    print("MANUAL SEMANTIC ANALYSIS")
    print("=" * 80)

    print(
        "The mathematical TP/FP/FN values above must remain unchanged."
    )

    print(
        "Use the detailed evidence above to classify apparent errors."
    )

    print(
        "Only after manual classification should a semantic acceptance"
    )

    print(
        "rate be calculated."
    )

    print()
    print("Example final report:")

    print(
        "  Mathematical FP             : 20"
    )

    print(
        "  Semantically acceptable FP  : 17"
    )

    print(
        "  Genuine FP                  : 3"
    )

    print(
        "  Semantic acceptance rate    : 85%"
    )

    print()
    print(
        "This semantic analysis does NOT change the official F1 score."
    )


def print_report(
    chunks: list[ChunkAnalysis],
    model_config: dict,
) -> None:
    """
    Print the complete NER error-analysis report.
    """

    print_summary(
        chunks=chunks,
        model_config=model_config,
    )

    print_prediction_distribution(
        chunks
    )

    print_full_data(
        chunks
    )

    print_exact_matches(
        chunks
    )

    print_false_positives(
        chunks
    )

    print_false_negatives(
        chunks
    )

    print_boundary_cases(
        chunks
    )

    print_wrong_label_cases(
        chunks
    )

    print_empty_predictions(
        chunks
    )

    print_manual_analysis_header()