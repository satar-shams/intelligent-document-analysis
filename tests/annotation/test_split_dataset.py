from src.annotation.split_dataset import split_dataset


def make_records(count: int) -> list[dict]:
    return [
        {
            "chunk_id": str(index),
            "document_id": f"doc-{index}",
            "text": f"chunk {index}",
            "entities": [],
        }
        for index in range(count)
    ]


def test_split_sizes():

    records = make_records(200)

    train, validation, test = split_dataset(
        records
    )

    assert len(train) == 140
    assert len(validation) == 30
    assert len(test) == 30


def test_all_records_are_preserved():

    records = make_records(200)

    train, validation, test = split_dataset(
        records
    )

    combined = train + validation + test

    assert len(combined) == len(records)

    assert {
        record["chunk_id"]
        for record in combined
    } == {
        record["chunk_id"]
        for record in records
    }


def test_no_records_are_shared_between_splits():

    records = make_records(200)

    train, validation, test = split_dataset(
        records
    )

    train_ids = {
        record["chunk_id"]
        for record in train
    }

    validation_ids = {
        record["chunk_id"]
        for record in validation
    }

    test_ids = {
        record["chunk_id"]
        for record in test
    }

    assert train_ids.isdisjoint(validation_ids)
    assert train_ids.isdisjoint(test_ids)
    assert validation_ids.isdisjoint(test_ids)


def test_split_is_deterministic():

    records = make_records(200)

    first_split = split_dataset(records)
    second_split = split_dataset(records)

    assert first_split == second_split


def test_empty_dataset_is_rejected():

    try:
        split_dataset([])
    except ValueError as exc:
        assert "empty dataset" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_too_small_dataset_is_rejected():

    records = make_records(2)

    try:
        split_dataset(records)
    except ValueError as exc:
        assert "at least 3 records" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )