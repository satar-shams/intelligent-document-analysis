import random

from src.schemas import Chunk


class AnnotationSampler:
    """Select a reproducible subset of chunks for annotation."""

    def __init__(
        self,
        sample_size: int,
        random_seed: int = 42,
    ) -> None:
        if sample_size <= 0:
            raise ValueError(
                "sample_size must be greater than 0."
            )

        self.sample_size = sample_size
        self.random_seed = random_seed

    def sample(
        self,
        chunks: list[Chunk],
    ) -> list[Chunk]:
        if self.sample_size > len(chunks):
            raise ValueError(
                f"sample_size ({self.sample_size}) cannot be "
                f"greater than the number of chunks ({len(chunks)})."
            )

        rng = random.Random(self.random_seed)

        return rng.sample(
            chunks,
            self.sample_size,
        )