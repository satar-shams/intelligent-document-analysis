from src.annotation.evaluator import EntityEvaluator
from src.schemas import ExtractedEntity


def make_entity(
    text: str,
    label: str,
    start: int,
    end: int,
) -> ExtractedEntity:
    return ExtractedEntity(
        text=text,
        label=label,
        start=start,
        end=end,
        confidence=1.0,
        chunk_id="1",
        document_id="doc",
        page_start=1,
        page_end=1,
    )


def test_perfect_match():
    entity = make_entity(
        "Microsoft",
        "ORGANIZATION",
        0,
        9,
    )

    evaluator = EntityEvaluator()

    metrics = evaluator.evaluate(
        expected=[entity],
        predicted=[entity],
    )

    assert metrics.true_positives == 1
    assert metrics.false_positives == 0
    assert metrics.false_negatives == 0
    assert metrics.precision == 1.0
    assert metrics.recall == 1.0
    assert metrics.f1 == 1.0


def test_false_positive():
    predicted = make_entity(
        "Microsoft",
        "ORGANIZATION",
        0,
        9,
    )

    evaluator = EntityEvaluator()

    metrics = evaluator.evaluate(
        expected=[],
        predicted=[predicted],
    )

    assert metrics.true_positives == 0
    assert metrics.false_positives == 1
    assert metrics.false_negatives == 0
    assert metrics.precision == 0.0
    assert metrics.recall == 0.0
    assert metrics.f1 == 0.0


def test_false_negative():
    expected = make_entity(
        "Microsoft",
        "ORGANIZATION",
        0,
        9,
    )

    evaluator = EntityEvaluator()

    metrics = evaluator.evaluate(
        expected=[expected],
        predicted=[],
    )

    assert metrics.true_positives == 0
    assert metrics.false_positives == 0
    assert metrics.false_negatives == 1
    assert metrics.precision == 0.0
    assert metrics.recall == 0.0
    assert metrics.f1 == 0.0


def test_wrong_label_is_not_a_match():
    expected = make_entity(
        "Microsoft",
        "ORGANIZATION",
        0,
        9,
    )

    predicted = make_entity(
        "Microsoft",
        "PRODUCT",
        0,
        9,
    )

    evaluator = EntityEvaluator()

    metrics = evaluator.evaluate(
        expected=[expected],
        predicted=[predicted],
    )

    assert metrics.true_positives == 0
    assert metrics.false_positives == 1
    assert metrics.false_negatives == 1


def test_metrics_by_label():
    organization = make_entity(
        "Microsoft",
        "ORGANIZATION",
        0,
        9,
    )

    date = make_entity(
        "2020",
        "DATE",
        10,
        14,
    )

    evaluator = EntityEvaluator()

    results = evaluator.evaluate_by_label(
        expected=[organization, date],
        predicted=[organization],
    )

    assert results["ORGANIZATION"].f1 == 1.0
    assert results["DATE"].recall == 0.0