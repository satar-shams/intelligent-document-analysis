from pathlib import Path
from typing import Protocol

from src.schemas import Document


class TextExtractor(Protocol):

    def can_process(self, document: Path) -> bool:
        ...

    def extract(self, document: Path) -> Document:
        ...