"""
NER Error Analysis

Purpose:
    Perform detailed manual analysis of the best NER model selected by
    compare_ner_models.py.

The mathematical evaluation remains strict and unchanged.

This analysis is designed to answer two different questions:

1. Mathematical evaluation:
       How many predictions exactly match the gold annotations?

2. Error analysis:
       Of the mathematically incorrect predictions, how many appear to be
       genuine model errors, boundary differences, wrong-label predictions,
       annotation issues, or semantically defensible predictions?

Important:

    A prediction is NOT converted into a mathematical TP just because it
    looks semantically correct.

    Therefore:

        mathematical TP != semantic acceptance

    The official mathematical metrics remain unchanged.

    Manual analysis can later report something such as:

        Mathematical FP:              20
        Semantically acceptable FP:   17
        Genuine FP:                    3
        Semantic acceptance rate:     85%

    This does NOT change the official precision, recall, or F1.

Workflow:

    compare_ner_models.py
            |
            v
       get_best_model()
            |
            v
    analyze_ner_errors.py
            |
            +--> run selected model
            |
            +--> compare gold vs predictions
            |
            +--> print complete evidence
            |
            +--> manual semantic analysis

Usage:

    python -m src.extraction.analyze_ner_errors
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from transformers import pipeline

from src.extraction.compare_ner_models import (
    MODELS,
    evaluate_model,
    select_best_model,
)


# ============================================================================
# CONFIGURATION
# ============================================================================

TEST_FILE = Path(
    "data/processed/extraction/test.jsonl"
)

CONTEXT_CHARS = 180


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass(frozen=True)
class Entity:
    text: str
    label: str
    start: int
    end: int


@dataclass
class ChunkAnalysis:
    chunk_index: int
    text: str
    gold: list[Entity]
    predicted: list[Entity]
    exact_matches: list[tuple[Entity, Entity]]
    false_positives: list[Entity]
    false_negatives: list[Entity]


# ============================================================================
# TEXT NORMALIZATION
# ============================================================================


def normalize_text(text: str) -> str:
    """
    Apply the same normalization used by mathematical evaluation.

    Rules:
        - surrounding whitespace ignored
        - repeated whitespace collapsed
        - case ignored

    Character offsets are NOT used for mathematical matching.
    """

    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)

    return text


# ============================================================================
# DATASET
# ============================================================================


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


# ============================================================================
# MODEL
# ============================================================================


def load_model(
    model_config: dict,
):
    """
    Load the model selected by compare_ner_models.py.
    """

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


# ============================================================================
# MATHEMATICAL MATCHING
# ============================================================================


def entity_key(
    entity: Entity,
) -> tuple[str, str]:
    """
    Mathematical evaluation key:

        normalized entity text + label

    Character offsets are deliberately ignored.
    """

    return (
        normalize_text(entity.text),
        entity.label,
    )


def match_entities(
    gold: list[Entity],
    predicted: list[Entity],
) -> tuple[
    list[tuple[Entity, Entity]],
    list[Entity],
    list[Entity],
]:
    """
    Perform strict mathematical matching.

    Matching requires:

        normalized text == normalized text
        AND
        label == label

    Duplicate occurrences are matched one-to-one.

    Returns:

        exact_matches
        false_negatives
        false_positives
    """

    gold_by_key: dict[
        tuple[str, str],
        list[Entity],
    ] = {}

    for entity in gold:

        gold_by_key.setdefault(
            entity_key(entity),
            [],
        ).append(entity)

    exact_matches: list[
        tuple[Entity, Entity]
    ] = []

    false_positives: list[Entity] = []

    for prediction in predicted:

        key = entity_key(prediction)

        if gold_by_key.get(key):

            gold_entity = (
                gold_by_key[key].pop(0)
            )

            exact_matches.append(
                (
                    gold_entity,
                    prediction,
                )
            )

        else:

            false_positives.append(
                prediction
            )

    false_negatives: list[Entity] = []

    for remaining in gold_by_key.values():
        false_negatives.extend(
            remaining
        )

    return (
        exact_matches,
        false_negatives,
        false_positives,
    )


# ============================================================================
# CONTEXT
# ============================================================================


def get_context(
    text: str,
    start: int,
    end: int,
) -> str:
    """Return readable local context around an entity."""

    if start < 0 or end < 0:
        return text

    left = max(
        0,
        start - CONTEXT_CHARS,
    )

    right = min(
        len(text),
        end + CONTEXT_CHARS,
    )

    before = text[left:start]
    entity = text[start:end]
    after = text[end:right]

    return (
        f"{before}"
        f">>> {entity} <<<"
        f"{after}"
    )


# ============================================================================
# SEMANTIC / BOUNDARY DIAGNOSTICS
# ============================================================================


def overlaps(
    first: Entity,
    second: Entity,
) -> bool:
    """Return True if two entities overlap by character offsets."""

    if (
        first.start < 0
        or first.end < 0
        or second.start < 0
        or second.end < 0
    ):
        return False

    return (
        first.start < second.end
        and second.start < first.end
    )


def find_boundary_cases(
    gold: list[Entity],
    predicted: list[Entity],
) -> list[tuple[Entity, Entity]]:
    """
    Find mathematically incorrect predictions that overlap a gold entity.

    Example:

        GOLD:
            Microsoft Corporation

        PREDICTED:
            Microsoft

    Or:

        GOLD:
            New York City

        PREDICTED:
            New York

    These remain mathematical errors.

    They are only candidates for manual semantic/boundary analysis.
    """

    cases: list[
        tuple[Entity, Entity]
    ] = []

    for prediction in predicted:

        for expected in gold:

            if not overlaps(
                prediction,
                expected,
            ):
                continue

            if (
                entity_key(prediction)
                == entity_key(expected)
            ):
                continue

            cases.append(
                (
                    expected,
                    prediction,
                )
            )

    return cases


def find_wrong_label_cases(
    gold: list[Entity],
    predicted: list[Entity],
) -> list[tuple[Entity, Entity]]:
    """
    Find predictions where entity text matches a gold entity but
    the label is different.

    Example:

        GOLD:
            Microsoft -> ORGANIZATION

        PREDICTED:
            Microsoft -> PERSON
    """

    cases: list[
        tuple[Entity, Entity]
    ] = []

    gold_by_text: dict[
        str,
        list[Entity],
    ] = {}

    for entity in gold:

        gold_by_text.setdefault(
            normalize_text(entity.text),
            [],
        ).append(entity)

    for prediction in predicted:

        text_key = normalize_text(
            prediction.text
        )

        for expected in gold_by_text.get(
            text_key,
            [],
        ):

            if (
                prediction.label
                != expected.label
            ):

                cases.append(
                    (
                        expected,
                        prediction,
                    )
                )

    return cases


# ============================================================================
# CHUNK ANALYSIS
# ============================================================================


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


# ============================================================================
# REPORT HELPERS
# ============================================================================


def print_entity(
    entity: Entity,
) -> None:

    print(
        f"    {entity.text!r:<40}"
        f"{entity.label:<18}"
        f"[{entity.start}, {entity.end}]"
    )


def print_entity_list(
    entities: list[Entity],
) -> None:

    if not entities:
        print("    None")
        return

    for entity in entities:
        print_entity(entity)


def print_pair(
    expected: Entity,
    predicted: Entity,
) -> None:

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


# ============================================================================
# SUMMARY
# ============================================================================


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


# ============================================================================
# FULL GOLD VS PREDICTED DATA
# ============================================================================


def print_full_data(
    chunks: list[ChunkAnalysis],
) -> None:
    """
    Print every chunk with complete gold and predicted entities.

    This is the primary evidence for the final manual report.
    """

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


# ============================================================================
# EXACT MATCHES
# ============================================================================


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


# ============================================================================
# FALSE POSITIVES
# ============================================================================


def print_false_positives(
    chunks: list[ChunkAnalysis],
) -> None:
    """
    Print every mathematical false positive with context.

    Manual classification is intentionally not performed automatically.
    """

    print()
    print("=" * 80)
    print("APPARENT FALSE POSITIVES")
    print("=" * 80)

    index = 1

    for chunk in chunks:

        for prediction in (
            chunk.false_positives
        ):

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

            print(
                "    [ ] GENUINE_ERROR"
            )

            print(
                "    [ ] SEMANTICALLY_VALID"
            )

            print(
                "    [ ] BOUNDARY_ERROR"
            )

            print(
                "    [ ] WRONG_LABEL"
            )

            print(
                "    [ ] ANNOTATION_PROBLEM"
            )

            print(
                "    [ ] TOKENIZATION_ERROR"
            )

            print(
                "    [ ] OTHER"
            )

            index += 1


# ============================================================================
# FALSE NEGATIVES
# ============================================================================


def print_false_negatives(
    chunks: list[ChunkAnalysis],
) -> None:
    """
    Print every mathematically missed gold entity.

    Empty predictions are therefore naturally represented here when a
    chunk contains gold entities.
    """

    print()
    print("=" * 80)
    print("APPARENT FALSE NEGATIVES")
    print("=" * 80)

    index = 1

    for chunk in chunks:

        for expected in (
            chunk.false_negatives
        ):

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

            print(
                "    [ ] GENUINE_MISSED_ENTITY"
            )

            print(
                "    [ ] BOUNDARY_ERROR"
            )

            print(
                "    [ ] WRONG_LABEL"
            )

            print(
                "    [ ] ANNOTATION_PROBLEM"
            )

            print(
                "    [ ] TOKENIZATION_ERROR"
            )

            print(
                "    [ ] OTHER"
            )

            index += 1


# ============================================================================
# BOUNDARY CASES
# ============================================================================


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

            print(
                "    [ ] SEMANTICALLY_VALID"
            )

            print(
                "    [ ] GENUINE_BOUNDARY_ERROR"
            )

            print(
                "    [ ] ANNOTATION_PROBLEM"
            )

            print(
                "    [ ] OTHER"
            )

    if total == 0:
        print(
            "No overlapping boundary candidates found."
        )


# ============================================================================
# WRONG LABEL CASES
# ============================================================================


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

            print(
                "    [ ] GENUINE_WRONG_LABEL"
            )

            print(
                "    [ ] SEMANTICALLY_VALID"
            )

            print(
                "    [ ] ANNOTATION_PROBLEM"
            )

            print(
                "    [ ] OTHER"
            )

    if total == 0:
        print(
            "No same-text wrong-label candidates found."
        )


# ============================================================================
# EMPTY PREDICTIONS
# ============================================================================


def print_empty_predictions(
    chunks: list[ChunkAnalysis],
) -> None:
    """
    Show chunks where the model predicted nothing.

    A zero-prediction chunk with gold entities represents genuine
    mathematical misses for those gold entities.

    A zero-prediction chunk without gold entities is not automatically
    an error.
    """

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


# ============================================================================
# PREDICTION DISTRIBUTION
# ============================================================================


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


# ============================================================================
# MAIN
# ============================================================================


def main() -> None:

    dataset = load_test_dataset(
        TEST_FILE
    )

    # ------------------------------------------------------------------
    # Run the official model comparison.
    # ------------------------------------------------------------------

    results = []

    for model_config in MODELS:

        result = evaluate_model(
            model_config=model_config,
            records=dataset,
        )

        results.append(result)

    # ------------------------------------------------------------------
    # Select the best model using the official F1 score.
    # ------------------------------------------------------------------

    best_model = select_best_model(
        results
    )

    # Recover the full configuration of the selected model.
    model_config = next(
        config
        for config in MODELS
        if config["name"] == best_model.name
    )

    # ------------------------------------------------------------------
    # Load only the selected model for detailed analysis.
    # ------------------------------------------------------------------

    ner = load_model(
        model_config
    )
    # ------------------------------------------------------------------
    # Analyze every test chunk.
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------

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
    print(
        "Example final report:"
    )

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


if __name__ == "__main__":
    main()