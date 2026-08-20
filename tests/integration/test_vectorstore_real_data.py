from pathlib import Path

from src.config import INGESTION_INPUT_DIRECTORY
from src.embeddings.embedding_pipeline import EmbeddingPipeline
from src.ingestion.extractor_manager import ExtractorManager
from src.preprocessing.preprocessing_manager import PreprocessorManager
from src.schemas import SearchResultData
from src.vectorstore.chroma_store import ChromaStore


def test_vectorstore_with_real_data():
    extractor_manager = ExtractorManager()
    preprocessor_manager = PreprocessorManager()
    embedding_pipeline = EmbeddingPipeline()
    store = ChromaStore()

    store.delete_collection()

    documents = extractor_manager.extract_directory(
        Path(INGESTION_INPUT_DIRECTORY)
    )

    chunks = preprocessor_manager.preprocess(
        documents
    )

    embeddings = embedding_pipeline.embed_chunks(
        chunks
    )

    store.add(
        chunks,
        embeddings,
    )

    assert len(documents) == 4
    assert len(chunks) > 0
    assert len(embeddings) == len(chunks)
    assert store.count() == len(chunks)

    query_embedding = embedding_pipeline.embed_texts(
        ["Python programming"]
    )[0]

    results = store.search(
        query_embedding=query_embedding,
        top_k=3,
    )

    assert len(results) == 3

    print("\nTop search results:")

    for index, result in enumerate(results, start=1):
        print(f"\nResult {index}:")
        print(f"Chunk ID: {result.chunk_id}")
        print(f"Document ID: {result.document_id}")
        print(f"Pages: {result.page_start}-{result.page_end}")
        print(f"Section: {result.section_title}")
        print(f"Distance: {result.distance}")
        print(f"Text: {result.text[:500]}")

    for result in results:
        assert isinstance(result, SearchResultData)
        assert result.chunk_id
        assert result.document_id
        assert result.text
        assert isinstance(result.page_start, int)
        assert isinstance(result.page_end, int)
        assert isinstance(result.distance, float)