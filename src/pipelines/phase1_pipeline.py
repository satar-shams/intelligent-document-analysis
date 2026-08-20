from pathlib import Path

from src.config import INGESTION_INPUT_DIRECTORY
from src.ingestion.extractor_manager import ExtractorManager
from src.preprocessing.preprocessing_manager import PreprocessorManager
from src.embeddings.embedding_pipeline import EmbeddingPipeline
from src.vectorstore.chroma_store import ChromaStore

def run_phase1():
    """
    Run the Phase 1 document processing pipeline.

    The pipeline:
    1. Extracts supported documents into Document objects.
    2. Cleans the extracted page text.
    3. Creates overlapping Chunk objects.
    4. Generates embeddings for the chunks.
    5. Clears the existing vector collection.
    6. Stores the chunks and embeddings in ChromaDB.

    Returns:
        A tuple containing the processed chunks and embeddings.
    """
    extractor_manager = ExtractorManager()
    preprocessor_manager = PreprocessorManager()
    embedding_pipeline = EmbeddingPipeline()
    chroma_store = ChromaStore()

    documents = extractor_manager.extract_directory(
        Path(INGESTION_INPUT_DIRECTORY)
    )

    chunks = preprocessor_manager.preprocess(
        documents
    )
    embedded = embedding_pipeline.embed_chunks(chunks)

    chroma_store.delete_collection()
    chroma_store.add(chunks=chunks, embeddings=embedded)

    return chunks, embedded


if __name__ == "__main__":
    chunks, embedded = run_phase1()

    print(f"Created {len(chunks)} chunks.")

    if chunks:
        print("\nFirst chunk:")
        print(chunks[0])

    if embedded:
        print("\nFirst chunk:")
        print(embedded[0])

    chroma_store = ChromaStore()
    embedding_pipeline = EmbeddingPipeline()

    query = "When he came to the war he was barely eighteen"

    query_embedding = embedding_pipeline.embed_texts(
        [query]
    )[0]

    results = chroma_store.search(
        query_embedding=query_embedding,
        top_k=3,
    )

    from src.config import MAX_TEXT_PREVIEW_LENGTH

    print("\nSearch results:")

    for rank, result in enumerate(results, start=1):
        print(f"\nResult {rank}")
        print(f"Document: {result.document_id}")
        print(f"Pages: {result.page_start}-{result.page_end}")
        print(f"Distance: {result.distance:.4f}")

        if len(result.text) > MAX_TEXT_PREVIEW_LENGTH:
            print(
                f"Text: {result.text[:MAX_TEXT_PREVIEW_LENGTH]}..."
            )
        else:
            print(f"Text: {result.text}")