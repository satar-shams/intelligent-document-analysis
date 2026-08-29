from dataclasses import dataclass

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