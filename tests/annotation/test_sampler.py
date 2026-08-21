from src.annotation.sampler import AnnotationSampler
from src.schemas import Chunk


def test_sampler_returns_requested_number_of_chunks():
    chunks = [
        Chunk(
            chunk_id=str(i),
            document_id="doc",
            text=f"text {i}",
            page_start=i,
            page_end=i,
        )
        for i in range(100)
    ]

    sampler = AnnotationSampler(
        sample_size=20,
        random_seed=42,
    )

    sampled = sampler.sample(chunks)

    assert len(sampled) == 20


def test_sampler_is_reproducible():
    chunks = [
        Chunk(
            chunk_id=str(i),
            document_id="doc",
            text=f"text {i}",
            page_start=i,
            page_end=i,
        )
        for i in range(100)
    ]

    sampler_1 = AnnotationSampler(
        sample_size=20,
        random_seed=42,
    )

    sampler_2 = AnnotationSampler(
        sample_size=20,
        random_seed=42,
    )

    sampled_1 = sampler_1.sample(chunks)
    sampled_2 = sampler_2.sample(chunks)

    assert [chunk.chunk_id for chunk in sampled_1] == [
        chunk.chunk_id for chunk in sampled_2
    ]


def test_sampler_rejects_too_large_sample():
    chunks = [
        Chunk(
            chunk_id=str(i),
            document_id="doc",
            text=f"text {i}",
            page_start=i,
            page_end=i,
        )
        for i in range(10)
    ]

    sampler = AnnotationSampler(
        sample_size=20,
        random_seed=42,
    )

    try:
        sampler.sample(chunks)
        assert False
    except ValueError:
        pass