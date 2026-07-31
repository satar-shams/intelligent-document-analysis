from typing import TypedDict


class PageData(TypedDict):
    page: int
    text: str


class ChunkData(TypedDict):
    chunk_id: int
    page: int
    text: str


class SearchResultData(TypedDict):
    chunk_id: int
    page: int
    text: str
    distance: float