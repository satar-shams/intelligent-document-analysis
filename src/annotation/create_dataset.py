from src.annotation.dataset_writer import AnnotationDatasetWriter
from src.annotation.sampler import AnnotationSampler
from src.config import (
    ANNOTATION_RANDOM_SEED,
    ANNOTATION_SAMPLE_SIZE,
)
from src.vectorstore.chroma_store import ChromaStore


OUTPUT_PATH = (
    "data/processed/annotation/annotation_dataset.jsonl"
)


def main() -> None:
    chroma_store = ChromaStore()

    chunks = chroma_store.get_chunks()

    print(
        f"Total chunks in ChromaDB: {len(chunks)}"
    )

    sampler = AnnotationSampler(
        sample_size=ANNOTATION_SAMPLE_SIZE,
        random_seed=ANNOTATION_RANDOM_SEED,
    )

    sampled_chunks = sampler.sample(chunks)

    print(
        f"Sampled chunks: {len(sampled_chunks)}"
    )

    writer = AnnotationDatasetWriter()

    writer.write(
        chunks=sampled_chunks,
        output_path=OUTPUT_PATH,
    )

    print(
        f"Annotation dataset written to: "
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()