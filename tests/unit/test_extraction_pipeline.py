from pipelines.extraction import run_extraction
from src.schemas import ExtractedEntity

def test_run_extraction_adds_predicted_entities(
    monkeypatch,
):

    fake_entity = ExtractedEntity(
        text="Microsoft",
        label="ORGANIZATION",
        start=0,
        end=9,
        confidence=0.99,
        chunk_id="chunk_1",
        document_id="doc_1",
        page_start=1,
        page_end=1,
    )

    class FakeEntityExtractor:

        def __init__(self):
            pass

        def extract(
            self,
            text,
            context,
        ):
            return [fake_entity]

    monkeypatch.setattr(
        "pipelines.extraction.EntityExtractor",
        FakeEntityExtractor,
    )

    records = [
        {
            "chunk_id": "chunk_1",
            "document_id": "doc_1",
            "text": "Microsoft announced new products.",
            "page_start": 1,
            "page_end": 1,
            "section_title": None,
            "entities": [],
        }
    ]

    results = run_extraction(records)

    assert len(results) == 1

    assert results[0]["entities"] == []

    assert len(
        results[0]["predicted_entities"]
    ) == 1

    assert (
        results[0]["predicted_entities"][0]["text"]
        == "Microsoft"
    )

    assert (
        results[0]["predicted_entities"][0]["label"]
        == "ORGANIZATION"
    )


def test_run_extraction_preserves_original_records(
    monkeypatch,
):

    class FakeEntityExtractor:

        def __init__(self):
            pass

        def extract(
            self,
            text,
            context,
        ):
            return []

    monkeypatch.setattr(
        "pipelines.extraction.EntityExtractor",
        FakeEntityExtractor,
    )

    records = [
        {
            "chunk_id": "chunk_1",
            "document_id": "doc_1",
            "text": "Seasonality",
            "page_start": 292,
            "page_end": 292,
            "section_title": None,
            "entities": [],
        }
    ]

    results = run_extraction(records)

    assert results[0]["chunk_id"] == "chunk_1"
    assert results[0]["document_id"] == "doc_1"
    assert results[0]["text"] == "Seasonality"
    assert results[0]["page_start"] == 292
    assert results[0]["page_end"] == 292
    assert results[0]["section_title"] is None
    assert results[0]["entities"] == []
    assert results[0]["predicted_entities"] == []


def test_run_extraction_handles_multiple_chunks(
    monkeypatch,
):

    class FakeEntityExtractor:

        def __init__(self):
            pass

        def extract(
            self,
            text,
            context,
        ):
            if "Microsoft" in text:
                return [
                    ExtractedEntity(
                        text="Microsoft",
                        label="ORGANIZATION",
                        start=0,
                        end=9,
                        confidence=0.99,
                        chunk_id=context.chunk_id,
                        document_id=context.document_id,
                        page_start=context.page_start,
                        page_end=context.page_end,
                    )
                ]

            return []

    monkeypatch.setattr(
        "pipelines.extraction.EntityExtractor",
        FakeEntityExtractor,
    )

    records = [
        {
            "chunk_id": "chunk_1",
            "document_id": "doc_1",
            "text": "Microsoft announced results.",
            "page_start": 1,
            "page_end": 1,
            "section_title": None,
            "entities": [],
        },
        {
            "chunk_id": "chunk_2",
            "document_id": "doc_1",
            "text": "Seasonality",
            "page_start": 2,
            "page_end": 2,
            "section_title": None,
            "entities": [],
        },
    ]

    results = run_extraction(records)

    assert len(results) == 2

    assert len(
        results[0]["predicted_entities"]
    ) == 1

    assert (
        results[0]["predicted_entities"][0]["text"]
        == "Microsoft"
    )

    assert results[1]["predicted_entities"] == []