# Intelligent Document Analysis — Phase 1 Technical Report

## 1. Overview

Phase 1 establishes the document-processing and semantic-retrieval foundation of the Intelligent Document Analysis system.

The pipeline processes PDF and DOCX documents, extracts and normalizes their text, divides the content into overlapping chunks, generates semantic embeddings, stores the resulting vectors and metadata in ChromaDB, and performs semantic similarity search.

The main workflow is:

```text
Raw Documents
      │
      ▼
Document Extraction
      │
      ├── PDF
      ├── DOCX
      └── Scanned PDF → OCR
      │
      ▼
Text Preprocessing
      │
      ▼
Chunking
      │
      ▼
Semantic Embeddings
      │
      ▼
ChromaDB
      │
      ▼
Semantic Search
```

The executable entry point is:

```text
pipelines/phase1.py
```

It can be run with:

```bash
python -m pipelines.phase1
```

The pipeline recreates the configured ChromaDB collection before storing the newly processed documents. This keeps repeated development runs deterministic and prevents stale or duplicate data from accumulating.

---

## 2. Document Ingestion

Phase 1 supports:

* PDF documents
* DOCX documents
* OCR fallback for scanned or image-based PDF pages

The ingestion layer uses PyMuPDF for standard PDF text extraction. When a PDF page does not contain usable extractable text, OCR can be used as a fallback.

DOCX documents are processed paragraph by paragraph and represented as page-like units for downstream processing.

The extraction flow is:

```text
PDF
 │
 ├── Usable text
 │       ↓
 │   PDF extraction
 │
 └── No usable text
         ↓
        OCR
```

Unsupported file types are skipped and reported through the application logger rather than causing the complete pipeline to fail.

---

## 3. Text Preprocessing

Extracted text is normalized before chunking and embedding.

The preprocessing layer handles operations such as:

* text normalization
* whitespace normalization
* line-ending normalization
* removal of excessive blank lines
* preservation of document and page metadata

Preprocessing is separated from document extraction so that the individual stages can be tested and modified independently.

---

## 4. Chunking

Documents are divided into overlapping chunks before embedding.

The current configuration uses:

```yaml
chunking:
  chunk_size: 1000
  chunk_overlap: 200
  max_length_preview: 200
```

The chunk size and overlap are configurable through the project configuration.

The `max_length_preview` parameter controls only how much retrieved text is displayed in the Phase 1 demonstration output. It does not modify the stored chunk.

Each chunk preserves metadata such as:

```text
chunk_id
document_id
page_start
page_end
section_title
```

This metadata is retained throughout the retrieval process so that search results can be traced back to their source documents and pages.

---

## 5. Embedding Generation

Each processed chunk is converted into a dense semantic vector using Sentence Transformers.

The embedding model is configurable through:

```text
configs/config.yaml
```

The embedding pipeline provides:

* configurable embedding model
* batch embedding
* input validation
* ChromaDB-compatible vector output

The resulting vectors remain associated with their original chunks and metadata.

---

## 6. ChromaDB Vector Storage

ChromaDB is used as the persistent local vector database.

The vector-store layer is responsible for:

* creating or opening the configured collection
* storing embeddings
* storing document and chunk metadata
* performing semantic similarity search
* counting stored chunks
* deleting and recreating the collection when required

The main vector-store location is:

```text
data/vectorstore/
```

The configured collection is:

```text
documents
```

Stored metadata includes:

```text
chunk_id
document_id
text
page_start
page_end
section_title
```

This metadata allows retrieved chunks to retain their document and page context.

---

## 7. Semantic Search

Phase 1 provides semantic retrieval over the stored document chunks.

A query is first converted into an embedding using the same embedding model used for document chunks:

```python
query = "When he came to the war he was barely eighteen"

query_embedding = embedding_pipeline.embed_texts(
    [query]
)[0]
```

The resulting vector is passed to ChromaDB:

```python
results = chroma_store.search(
    query_embedding=query_embedding,
    top_k=3,
)
```

Search results contain the most semantically similar chunks together with their document and page metadata.

A result is represented by information such as:

```text
SearchResultData(
    chunk_id="59",
    document_id="sample-text-pdf",
    text="When he came to the war he was barely eighteen...",
    page_start=19,
    page_end=19,
    distance=0.8499,
    section_title=None,
)
```

The retrieval distance is a vector-search distance and should not be interpreted as a correctness or confidence percentage.

The complete chunk remains available to the retrieval system; only the demonstration output may be shortened using `max_length_preview`.

---

## 8. Phase 1 Pipeline

The complete Phase 1 workflow is implemented in:

```text
pipelines/phase1.py
```

The pipeline performs:

```text
1. Extract documents
2. Preprocess extracted text
3. Create chunks
4. Generate embeddings
5. Recreate the ChromaDB collection
6. Store chunks and embeddings
7. Run an example semantic search
8. Display retrieved results
```

The pipeline uses the same reusable components that are independently tested under `src/`.

---

## 9. Project Structure

The Phase 1 implementation is organized into reusable components:

```text
src/
├── config.py
├── schemas.py
├── types.py
│
├── embeddings/
│   └── embedding_pipeline.py
│
├── ingestion/
│   ├── docx_parser.py
│   ├── extractor_manager.py
│   ├── extractors.py
│   ├── ocr_engine.py
│   └── pdf_parser.py
│
├── preprocessing/
│   ├── chunker.py
│   ├── cleaner.py
│   └── preprocessing_manager.py
│
└── vectorstore/
    └── chroma_store.py
```

The main executable workflow is separated from these reusable components:

```text
pipelines/
└── phase1.py
```

This separation allows individual processing stages to be tested independently while still supporting an end-to-end pipeline.

---

## 10. Technology Stack

| Component        | Technology                      |
| ---------------- | ------------------------------- |
| Language         | Python 3.12                     |
| PDF Processing   | PyMuPDF                         |
| DOCX Processing  | python-docx                     |
| OCR              | Tesseract OCR + pytesseract     |
| Image Processing | Pillow                          |
| Text Processing  | Python / Regex                  |
| Embeddings       | Sentence Transformers + PyTorch |
| Vector Database  | ChromaDB                        |
| Testing          | pytest                          |
| Configuration    | YAML                            |

---

## 11. Environment Setup

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install project dependencies:

```bash
pip install -r requirements.txt
```

Install development and testing dependencies:

```bash
pip install -r requirements-dev.txt
```

For OCR support on Ubuntu:

```bash
sudo apt install tesseract-ocr
```

Verify the OCR installation:

```bash
tesseract --version
```

---

## 12. Configuration

The main project configuration is stored in:

```text
configs/config.yaml
```

Relevant Phase 1 settings include:

* input directories
* embedding model
* chunk size
* chunk overlap
* retrieval-result preview length
* ChromaDB database path
* ChromaDB collection name

Current chunking configuration:

```yaml
chunking:
  chunk_size: 1000
  chunk_overlap: 200
  max_length_preview: 200
```

Keeping these parameters in configuration allows the processing pipeline to be changed without modifying the implementation code.

---

## 13. Testing

Phase 1 components are covered by both unit tests and real-data integration tests.

### Unit Tests

Unit tests cover the main Phase 1 components, including:

* document ingestion
* text preprocessing
* embedding generation
* ChromaDB storage and retrieval

Examples include:

```text
tests/unit/test_ingestion.py
tests/unit/test_preprocessing.py
tests/unit/test_embeddings.py
tests/unit/test_vectorstore.py
```

The complete repository test suite can be run with:

```bash
python -m pytest
```

At the current project state, the full suite contains:

```text
98 tests
98 passed
```

### Real-Data Integration Testing

Phase 1 also includes integration tests using actual project documents rather than only synthetic test data.

Relevant tests include:

```text
tests/integration/test_ingestion_real_data.py
tests/integration/test_vectorstore_real_data.py
```

These tests verify the interaction between the major components, including:

```text
Real Documents
      ↓
Extraction
      ↓
Preprocessing
      ↓
Chunking
      ↓
Embedding
      ↓
ChromaDB
      ↓
Semantic Search
      ↓
Retrieved Chunks
```

This provides verification beyond isolated unit tests and confirms that the processing and retrieval components work together on real document data.

---

## 14. Experimental Verification

The final Phase 1 pipeline was executed against the project's document collection.

The run successfully:

* extracted supported documents;
* used OCR fallback where required;
* skipped unsupported `.doc` files;
* skipped an unsupported `.txt` input;
* generated 13,368 chunks;
* populated the configured ChromaDB collection;
* executed semantic retrieval successfully.

The unsupported `.doc` files were:

```text
data/raw/docx/2011 Annual Report.doc
data/raw/docx/2019_Annual_Report.doc
```

The unsupported text file was:

```text
data/raw/unsupported.txt
```

These files were reported as skipped rather than treated as pipeline failures.

The successful end-to-end run confirms that the Phase 1 processing, embedding, vector-storage, and retrieval stages operate together on the available project data.

---

## 15. Engineering Principles

The Phase 1 implementation follows several engineering principles:

* **Modularity** — individual processing stages have dedicated components.
* **Separation of concerns** — extraction, preprocessing, embedding, storage, and retrieval remain distinct.
* **Testability** — components are tested independently and through integration tests.
* **Configurability** — important processing parameters are maintained in YAML configuration.
* **Incremental development** — functionality is implemented and verified step by step.
* **Controlled complexity** — more advanced functionality is introduced as separate stages rather than tightly coupling it to the document-processing foundation.

---

## 16. Phase 1 Summary

Phase 1 establishes the document-processing and semantic-retrieval foundation used by the rest of the project:

```text
Documents
   ↓
Extraction
   ↓
Preprocessing
   ↓
Chunking
   ↓
Embeddings
   ↓
ChromaDB
   ↓
Semantic Search
```

The implementation supports PDF and DOCX ingestion, OCR fallback, configurable preprocessing and chunking, semantic embeddings, persistent vector storage, and semantic retrieval.

The pipeline has been verified through unit tests, real-data integration tests, and an end-to-end execution against the project document collection.

Later stages of the project build on this foundation for entity extraction and Retrieval-Augmented Generation.

---

## 17. License

This project is developed for educational and portfolio purposes.
