import json

from src.annotation.validate_dataset import (
    validate_dataset,
    validate_entity,
    validate_overlaps,
)


def test_valid_entity():

    chunk = {
        "chunk_id": "1",
        "document_id": "doc1",
        "text": "Microsoft reported revenue.",
    }

    entity = {
        "text": "Microsoft",
        "label": "ORGANIZATION",
        "start": 0,
        "end": 9,
        "confidence": 0.9,
        "chunk_id": "1",
        "document_id": "doc1",
        "page_start": 1,
        "page_end": 1,
    }

    errors = validate_entity(
        entity=entity,
        chunk=chunk,
    )

    assert errors == []


def test_invalid_offsets():

    chunk = {
        "chunk_id": "1",
        "document_id": "doc1",
        "text": "Microsoft reported revenue.",
    }

    entity = {
        "text": "Microsoft",
        "label": "ORGANIZATION",
        "start": 0,
        "end": 10,
        "confidence": 0.9,
        "chunk_id": "1",
        "document_id": "doc1",
        "page_start": 1,
        "page_end": 1,
    }

    errors = validate_entity(
        entity=entity,
        chunk=chunk,
    )

    assert any(
        "offset mismatch" in error
        for error in errors
    )


def test_invalid_label():

    chunk = {
        "chunk_id": "1",
        "document_id": "doc1",
        "text": "Microsoft reported revenue.",
    }

    entity = {
        "text": "Microsoft",
        "label": "UNKNOWN",
        "start": 0,
        "end": 9,
        "confidence": 0.9,
        "chunk_id": "1",
        "document_id": "doc1",
        "page_start": 1,
        "page_end": 1,
    }

    errors = validate_entity(
        entity=entity,
        chunk=chunk,
    )

    assert any(
        "invalid label" in error
        for error in errors
    )


def test_overlapping_entities():

    entities = [
        {
            "text": "Microsoft",
            "start": 0,
            "end": 9,
        },
        {
            "text": "Microsoft Corporation",
            "start": 0,
            "end": 21,
        },
    ]

    errors = validate_overlaps(entities)

    assert len(errors) == 1


def test_dataset_validation(tmp_path):

    dataset = tmp_path / "dataset.jsonl"

    records = [
        {
            "chunk_id": "1",
            "document_id": "doc1",
            "text": "Microsoft reported revenue.",
            "page_start": 1,
            "page_end": 1,
            "entities": [
                {
                    "text": "Microsoft",
                    "label": "ORGANIZATION",
                    "start": 0,
                    "end": 9,
                    "confidence": 0.9,
                    "chunk_id": "1",
                    "document_id": "doc1",
                    "page_start": 1,
                    "page_end": 1,
                }
            ],
        }
    ]

    with dataset.open(
        mode="w",
        encoding="utf-8",
    ) as file:

        for record in records:
            file.write(
                json.dumps(record)
                + "\n"
            )

    chunks, entities, errors = validate_dataset(
        annotation_file=dataset
    )

    assert chunks == 1
    assert entities == 1
    assert errors == []