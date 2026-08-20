from pathlib import Path

from src.config import INGESTION_INPUT_DIRECTORY
from src.ingestion.extractor_manager import ExtractorManager
from src.preprocessing.preprocessing_manager import PreprocessorManager


def run_phase1():
    """
    Run the document extraction and preprocessing pipeline.

    The pipeline:
    1. Extracts supported documents into Document objects.
    2. Cleans the extracted page text.
    3. Creates overlapping Chunk objects.

    Returns:
        A list of Chunk objects ready for the embedding phase.
    """
    extractor_manager = ExtractorManager()
    preprocessor_manager = PreprocessorManager()

    documents = extractor_manager.extract_directory(
        Path(INGESTION_INPUT_DIRECTORY)
    )

    chunks = preprocessor_manager.preprocess(
        documents
    )

    return chunks


if __name__ == "__main__":
    chunks = run_phase1()

    print(f"Created {len(chunks)} chunks.")

    if chunks:
        print("\nFirst chunk:")
        print(chunks[0])