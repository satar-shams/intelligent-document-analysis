"""
Mathematical entity matching utilities.

This module contains the strict matching logic used by NER error analysis.

IMPORTANT:
    Mathematical matching must remain unchanged.

An entity matches when:

    normalized text == normalized text
    AND
    label == label

Character offsets are deliberately ignored.
"""

from __future__ import annotations

import re

from src.extraction.analysis.models import Entity


def normalize_text(text: str) -> str:
    """
    Normalize entity text for mathematical comparison.

    Rules:
        - strip surrounding whitespace
        - collapse repeated whitespace
        - ignore case
    """

    text = text.strip().lower()
    return re.sub(r"\s+", " ", text)


def entity_key(entity: Entity) -> tuple[str, str]:
    """
    Return the mathematical comparison key for an entity.

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
    Perform strict mathematical entity matching.

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
            gold_entity = gold_by_key[key].pop(0)

            exact_matches.append(
                (
                    gold_entity,
                    prediction,
                )
            )
        else:
            false_positives.append(prediction)

    false_negatives: list[Entity] = []

    for remaining in gold_by_key.values():
        false_negatives.extend(remaining)

    return (
        exact_matches,
        false_negatives,
        false_positives,
    )