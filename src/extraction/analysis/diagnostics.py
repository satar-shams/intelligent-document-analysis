"""
NER diagnostic utilities.

These functions identify mathematically incorrect predictions that may
deserve manual semantic analysis.

IMPORTANT:
    Diagnostic candidates remain mathematical errors.

They must NOT be converted into mathematical true positives.
"""

from __future__ import annotations

from src.extraction.analysis.matching import (
    entity_key,
    normalize_text,
)
from src.extraction.analysis.models import Entity


CONTEXT_CHARS = 180


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

    Examples:

        GOLD:
            Microsoft Corporation

        PREDICTED:
            Microsoft

    or:

        GOLD:
            New York City

        PREDICTED:
            New York

    These remain mathematical errors.
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
    Find predictions whose normalized text matches a gold entity
    but whose label differs.
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