from src.annotation.sampler import AnnotationSampler
from src.config import (
    ANNOTATION_RANDOM_SEED,
    ANNOTATION_SAMPLE_SIZE,
)
from src.vectorstore.chroma_store import ChromaStore


def main() -> None:
    chroma_store = ChromaStore()

    chunks = chroma_store.get_chunks()

    print(f"Total chunks in ChromaDB: {len(chunks)}")

    sampler = AnnotationSampler(
        sample_size=ANNOTATION_SAMPLE_SIZE,
        random_seed=ANNOTATION_RANDOM_SEED,
    )

    sampled_chunks = sampler.sample(chunks)

    print(f"Sampled chunks: {len(sampled_chunks)}")

    for rank, chunk in enumerate(
        sampled_chunks[:10],
        start=1,
    ):
        print("\n" + "=" * 80)
        print(f"Sample {rank}")
        print(f"Chunk ID : {chunk.chunk_id}")
        print(f"Document : {chunk.document_id}")
        print(f"Pages    : {chunk.page_start}-{chunk.page_end}")
        print(f"Section  : {chunk.section_title}")
        print(f"Text     : {chunk.text}")


if __name__ == "__main__":
    main()