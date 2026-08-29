import json
import re
from collections import Counter
from dataclasses import dataclass

from transformers import pipeline


TEST_FILE = "data/processed/extraction/test.jsonl"


# ---------------------------------------------------------------------------
# Candidate NER models
# ---------------------------------------------------------------------------

MODELS = [
    {
        "name": "dslim/bert-base-NER",
        "labels": ["PER", "ORG", "LOC", "MISC"],
        "label_mapping": {
            "PER": "PERSON",
            "ORG": "ORGANIZATION",
            "LOC": "LOCATION",
        },
    },
    {
        "name": "gamug/sec-bert-finer-ord-ner",
        "labels": ["PER", "ORG", "LOC"],
        "label_mapping": {
            "PER": "PERSON",
            "ORG": "ORGANIZATION",
            "LOC": "LOCATION",
        },
    },
    {
        "name": "Jean-Baptiste/roberta-large-ner-english",
        "labels": ["PER", "ORG", "LOC", "MISC"],
        "label_mapping": {
            "PER": "PERSON",
            "ORG": "ORGANIZATION",
            "LOC": "LOCATION",
        },
    },
    {
        "name": "ritam-m/bert-base-company-ner",
        "labels": ["COMPANY"],
        "label_mapping": {
            "COMPANY": "ORGANIZATION",
        },
    },
    {
        "name": "musk1209/finsight-ner",
        "labels": ["PER", "ORG", "LOC"],
        "label_mapping": {
            "PER": "PERSON",
            "ORG": "ORGANIZATION",
            "LOC": "LOCATION",
        },
    },
]


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Metrics:
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1: float


@dataclass
class ModelResult:
    name: str
    metrics: Metrics


# ---------------------------------------------------------------------------
# Text normalization
# ---------------------------------------------------------------------------

def normalize_entity_text(text: str) -> str:
    """
    Normalize entity text for official evaluation.

    Evaluation ignores:
        - capitalization
        - surrounding whitespace
        - repeated whitespace

    Evaluation does not ignore:
        - entity label
        - entity text differences
    """

    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)

    return text


# ---------------------------------------------------------------------------
# Dataset loading
# ---------------------------------------------------------------------------

def load_test_records() -> list[dict]:
    """Load test records from JSONL."""

    records = []

    with open(TEST_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records


# ---------------------------------------------------------------------------
# Expected entities
# ---------------------------------------------------------------------------

def build_expected_entities(
    records: list[dict],
    evaluated_labels: set[str],
) -> list[tuple[str, str]]:
    """
    Build expected entities for the labels supported by the model.

    Labels that cannot be represented by the candidate model are excluded
    from that model's official evaluation.
    """

    expected = []

    for record in records:
        for entity in record.get("entities", []):
            label = entity["label"]

            if label not in evaluated_labels:
                continue

            expected.append(
                (
                    normalize_entity_text(entity["text"]),
                    label,
                )
            )

    return expected


# ---------------------------------------------------------------------------
# Model prediction
# ---------------------------------------------------------------------------

def predict_entities(
    ner,
    records: list[dict],
    label_mapping: dict[str, str],
) -> list[tuple[str, str]]:
    """Run NER model and return normalized mapped predictions."""

    predicted = []

    for record in records:
        text = record.get("text", "")

        if not text.strip():
            continue

        predictions = ner(text)

        for prediction in predictions:
            native_label = prediction.get("entity_group")

            if native_label not in label_mapping:
                continue

            ida_label = label_mapping[native_label]

            entity_text = normalize_entity_text(
                prediction["word"]
            )

            if not entity_text:
                continue

            predicted.append(
                (
                    entity_text,
                    ida_label,
                )
            )

    return predicted


# ---------------------------------------------------------------------------
# Metric calculation
# ---------------------------------------------------------------------------

def calculate_metrics(
    expected: list[tuple[str, str]],
    predicted: list[tuple[str, str]],
) -> Metrics:
    """
    Calculate official NER metrics.

    Matching rule:
        normalized entity text + entity label

    Duplicate occurrences are preserved.
    """

    expected_counter = Counter(expected)
    predicted_counter = Counter(predicted)

    true_positives = sum(
        (expected_counter & predicted_counter).values()
    )

    false_positives = sum(
        (predicted_counter - expected_counter).values()
    )

    false_negatives = sum(
        (expected_counter - predicted_counter).values()
    )

    precision_denominator = (
        true_positives + false_positives
    )

    recall_denominator = (
        true_positives + false_negatives
    )

    precision = (
        true_positives / precision_denominator
        if precision_denominator
        else 0.0
    )

    recall = (
        true_positives / recall_denominator
        if recall_denominator
        else 0.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return Metrics(
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
        precision=precision,
        recall=recall,
        f1=f1,
    )


# ---------------------------------------------------------------------------
# Model evaluation
# ---------------------------------------------------------------------------

def evaluate_model(
    model_config: dict,
    records: list[dict],
) -> ModelResult:
    """Evaluate one candidate NER model."""

    ner = pipeline(
        "ner",
        model=model_config["name"],
        aggregation_strategy="simple",
    )

    evaluated_labels = set(
        model_config["label_mapping"].values()
    )

    expected = build_expected_entities(
        records=records,
        evaluated_labels=evaluated_labels,
    )

    predicted = predict_entities(
        ner=ner,
        records=records,
        label_mapping=model_config["label_mapping"],
    )

    metrics = calculate_metrics(
        expected=expected,
        predicted=predicted,
    )

    return ModelResult(
        name=model_config["name"],
        metrics=metrics,
    )


# ---------------------------------------------------------------------------
# Best model
# ---------------------------------------------------------------------------

def select_best_model(
    results: list[ModelResult],
) -> ModelResult:
    """Select the model with the highest official F1 score."""

    return max(
        results,
        key=lambda result: result.metrics.f1,
    )


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

def print_results(
    results: list[ModelResult],
    best_model: ModelResult,
) -> None:
    """Print concise model comparison."""

    print()
    print("=" * 100)
    print("NER MODEL COMPARISON")
    print("=" * 100)

    print(
        f"{'MODEL':45}"
        f"{'TP':>7}"
        f"{'FP':>7}"
        f"{'FN':>7}"
        f"{'PRECISION':>12}"
        f"{'RECALL':>10}"
        f"{'F1':>10}"
    )

    print("-" * 100)

    for result in sorted(
        results,
        key=lambda result: result.metrics.f1,
        reverse=True,
    ):
        metrics = result.metrics

        print(
            f"{result.name:45}"
            f"{metrics.true_positives:7d}"
            f"{metrics.false_positives:7d}"
            f"{metrics.false_negatives:7d}"
            f"{metrics.precision:12.4f}"
            f"{metrics.recall:10.4f}"
            f"{metrics.f1:10.4f}"
        )

    print()
    print(f"Best model: {best_model.name}")
    print(f"Best F1:    {best_model.metrics.f1:.4f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> ModelResult:
    """Evaluate candidate models and return the best model."""

    records = load_test_records()

    results = []

    for model_config in MODELS:
        result = evaluate_model(
            model_config=model_config,
            records=records,
        )

        results.append(result)

    best_model = select_best_model(results)

    print_results(
        results=results,
        best_model=best_model,
    )

    return best_model


if __name__ == "__main__":
    main()