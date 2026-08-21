from dataclasses import dataclass

@dataclass
class Page:
    page_number: int
    raw_text: str
    cleaned_text: str | None = None
    extraction_method: str | None = None


@dataclass
class Document:
    document_id: str
    source_path: str
    file_type: str
    pages: list[Page]
    metadata: dict


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    text: str
    page_start: int
    page_end: int
    section_title: str | None = None
@dataclass
class SearchResultData:

    chunk_id: str
    document_id: str
    text: str
    page_start: int
    page_end: int
    distance: float
    section_title: str | None = None

@dataclass
class ExtractedEntity:
    text: str
    label: str
    start: int
    end: int
    confidence: float | None
    chunk_id: str
    document_id: str
    page_start: int
    page_end: int