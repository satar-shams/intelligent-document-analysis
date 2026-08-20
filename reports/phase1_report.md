# Intelligent Document Analysis

A modular document processing pipeline for extracting, preprocessing, embedding, and storing heterogeneous documents for semantic retrieval.

> **Status:** **Phase 1 complete.** Document extraction, OCR fallback, text preprocessing, chunking, semantic embedding generation, ChromaDB storage, and semantic similarity search have been implemented and verified with unit and real-data integration tests.

---

# Overview

This project implements the first stage of an intelligent document analysis system.

The current implementation focuses on building a reliable document-to-vector pipeline:

* Extract text from PDF and DOCX documents
* Use OCR as a fallback for scanned PDFs
* Clean and normalize extracted text
* Split documents into overlapping chunks
* Preserve document and page metadata
* Generate semantic embeddings using Sentence Transformers
* Store embeddings and metadata in ChromaDB
* Perform semantic similarity search
* Run the complete Phase 1 pipeline end-to-end

The project is intentionally being developed incrementally. More advanced retrieval, document management, and RAG functionality will be considered after the core pipeline is complete.

---

# Phase 1 Pipeline

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
Extracted Documents
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

The complete pipeline is implemented in:

```text
src/pipelines/phase1_pipeline.py
```

Run it with:

```bash
python -m src.pipelines.phase1_pipeline
```

The pipeline currently clears and recreates the configured ChromaDB collection before storing the newly processed documents. This keeps repeated development runs deterministic and avoids accumulating duplicate data during the current development stage.

---

# Project Structure

```text
intelligent-document-analysis/
├── README.md
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
│
├── configs/
│   └── config.yaml
│
├── data/
│   └── raw/
│
├── src/
│   ├── config.py
│   ├── schemas.py
│   │
│   ├── ingestion/
│   │   ├── extractor_manager.py
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   └── ocr_engine.py
│   │
│   ├── preprocessing/
│   │   └── preprocessing_manager.py
│   │
│   ├── embeddings/
│   │   └── embedding_pipeline.py
│   │
│   ├── vectorstore/
│   │   └── chroma_store.py
│   │
│   └── pipelines/
│       └── phase1_pipeline.py
│
└── tests/
    ├── unit/
    └── integration/
```

---

# Tech Stack

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

# Environment Setup

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install project dependencies:

```bash
pip install -r requirements.txt
```

Install development/test dependencies:

```bash
pip install -r requirements-dev.txt
```

For OCR support on Ubuntu:

```bash
sudo apt install tesseract-ocr
```

Verify the installation:

```bash
tesseract --version
```

---

# Document Ingestion

Phase 1 currently supports:

* PDF documents
* DOCX documents
* Scanned PDFs through OCR fallback

The extraction manager processes all supported files from the configured input directory.

For PDFs, the system first attempts normal text extraction. If no extractable text is found, it automatically falls back to OCR.

Example processing flow:

```text
PDF
 │
 ├── Text available
 │       ↓
 │   PDF extraction
 │
 └── No text
         ↓
       OCR
```

Unsupported file types are skipped and reported through the application logger.

---

# Text Preprocessing and Chunking

Extracted documents are cleaned before being divided into chunks.

Current preprocessing includes:

* Text normalization
* Whitespace normalization
* Line-ending normalization
* Removal of excessive blank lines
* Page-level text processing
* Configurable chunk size
* Configurable chunk overlap
* Metadata preservation

Current configuration:

```yaml
chunking:
  chunk_size: 500
  chunk_overlap: 50
  max_length_preview: 200
```

The `max_length_preview` value only controls how much retrieved text is displayed in the Phase 1 demonstration output. It does **not** change the stored chunk.

Each chunk is represented by:

```python
Chunk(
    chunk_id="153",
    document_id="sample-ocr",
    text="Invoice #12345. Total: $1,250.00",
    page_start=1,
    page_end=1,
    section_title=None,
)
```

---

# Embedding Generation

Each chunk is converted into a dense semantic vector using Sentence Transformers.

The embedding model is configurable through the project configuration.

The resulting embeddings are passed directly to the vector database together with their corresponding chunks and metadata.

The embedding pipeline provides:

* Configurable embedding model
* Batch embedding
* Input validation
* ChromaDB-compatible vector output

---

# ChromaDB Vector Storage

Phase 1 uses ChromaDB as a persistent local vector database.

The `ChromaStore` is responsible for:

* Creating or opening the configured collection
* Storing chunk embeddings
* Storing document metadata
* Performing semantic similarity search
* Counting stored chunks
* Deleting and recreating the collection

Stored metadata includes:

```text
chunk_id
document_id
text
page_start
page_end
section_title
```

Search results are represented as:

```python
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

---

# Semantic Search

The Phase 1 pipeline also demonstrates semantic retrieval.

A query is converted into an embedding:

```python
query = "When he came to the war he was barely eighteen"

query_embedding = embedding_pipeline.embed_texts(
    [query]
)[0]
```

The embedding is then passed to ChromaDB:

```python
results = chroma_store.search(
    query_embedding=query_embedding,
    top_k=3,
)
```

The results contain the most semantically similar chunks together with their document and page metadata.

Example:

```text
Search results:

Result 1
Document: sample-text-pdf
Pages: 19-19
Distance: 0.8499
Text: mouth. When he came to the war he was barely eighteen...

Result 2
Document: sample-text-pdf
Pages: 124-124
Distance: 0.8612
Text: ...he was nervous and high-strung, and only seventeen...

Result 3
Document: sample-text-pdf
Pages: 67-67
Distance: 0.9539
Text: ...I should guess him to be thirty...
```

The complete chunk remains available to the retrieval system; only the demonstration output is shortened using `max_length_preview`.

---

# Running Phase 1

Run the complete Phase 1 pipeline:

```bash
python -m src.pipelines.phase1_pipeline
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
8. Display the retrieved results
```

---

# Testing

Phase 1 has been verified using both **unit tests** and **real-data integration testing**.

## Unit Tests

Unit tests validate individual Phase 1 components independently, including:

* Document ingestion
* Text preprocessing
* Embedding generation
* ChromaDB storage and retrieval

Run the Phase 1 unit tests with the relevant unit-test files:

```bash
python -m pytest tests/unit/test_ingestion.py \
tests/unit/test_preprocessing.py \
tests/unit/test_embeddings.py \
tests/unit/test_vectorstore.py -v
```

The RAG tests are intentionally not included here because RAG is outside the current Phase 1 scope.

## Real-Data Integration Test

The integration test uses the actual documents in `data/raw/` rather than artificial test dictionaries.

Run:

```bash
python -m pytest tests/integration/test_vectorstore_real_data.py -v -s
```

The `-s` option is intentional because the test prints the retrieved results so semantic search can be inspected directly.

The real-data test verifies the complete flow:

```text
Real documents
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
Semantic search
      ↓
Retrieved chunks
```

---

# Configuration

Project configuration is stored in:

```text
configs/config.yaml
```

Relevant configuration includes:

* Input directories
* Embedding model
* Chunk size
* Chunk overlap
* Search-result preview length
* ChromaDB database path
* ChromaDB collection name

Example:

```yaml
chunking:
  chunk_size: 500
  chunk_overlap: 50
  max_length_preview: 200
```

---

# Current Phase 1 Status

| Component                  | Status |
| -------------------------- | :----: |
| Project Structure          |   ✅    |
| PDF Extraction             |   ✅    |
| DOCX Extraction            |   ✅    |
| OCR Fallback               |   ✅    |
| Text Cleaning              |   ✅    |
| Text Chunking              |   ✅    |
| Metadata Preservation      |   ✅    |
| Embedding Pipeline         |   ✅    |
| ChromaDB Storage           |   ✅    |
| Semantic Search            |   ✅    |
| Phase 1 Pipeline           |   ✅    |
| Unit Tests                 |   ✅    |
| Real-Data Integration Test |   ✅    |

---

# Suggested Future Improvements

The following ideas are intentionally **not part of the current Phase 1 implementation**. They are possible improvements identified during development.

### Document Tracking and Reprocessing

Currently, the Phase 1 pipeline recreates the ChromaDB collection before storing the processed data.

Future versions could track which documents have already been processed and:

* Skip documents that have not changed
* Detect when a document has changed
* Reprocess only affected documents
* Replace the previous chunks belonging to a changed document

### Stable Document and Chunk Identification

Future versions could introduce more robust identifiers for documents and chunks.

Possible approaches include:

* File-based identifiers
* Content hashes
* Document fingerprints
* Stable chunk identifiers

This would make incremental processing and document replacement easier.

### Duplicate Detection

A future version could detect duplicate documents or duplicate content before storing them.

Content-based hashing could be considered instead of relying only on filenames or paths.

### Chunking Strategy Improvements

The current implementation uses a fixed chunk size and overlap.

Future improvements could investigate:

* Semantic chunking
* Structure-aware chunking
* Paragraph-aware chunking
* Header/section-aware chunking
* Multiple chunk sizes for different retrieval requirements

### Document Structure and Metadata

Future versions could preserve richer document structure, such as:

* Headers
* Sections
* Tables
* Figures
* Source file metadata
* Document hierarchy

### Advanced Retrieval

Future retrieval improvements could include:

* Metadata filtering
* Hybrid search
* Reranking
* Query expansion
* Retrieval evaluation metrics

### RAG and LLM Integration

A later stage can build on the retrieval layer to introduce:

```text
User Query
    ↓
Query Embedding
    ↓
Vector Search
    ↓
Relevant Chunks
    ↓
Context Construction
    ↓
LLM
    ↓
Generated Answer
```

This is deliberately outside the current Phase 1 scope.

---

# Development Principles

The project follows several engineering principles:

* **Modularity** — each processing stage has a dedicated component.
* **Separation of Concerns** — extraction, preprocessing, embedding, storage, and retrieval remain independent.
* **Testability** — individual components are tested independently and the pipeline is also verified with real documents.
* **Configurability** — important processing parameters are stored in YAML configuration.
* **Incremental Development** — functionality is implemented and verified step-by-step.
* **Avoid Premature Complexity** — advanced document tracking, deduplication, and RAG functionality are deferred until they are actually needed.

---

# Phase 1 Summary

Phase 1 establishes the complete foundation for semantic document retrieval:

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

The pipeline has been implemented, tested against real project documents, and verified end-to-end.

The next development stage can build on this foundation without changing the basic Phase 1 architecture.

---

# License

This project is developed for educational and portfolio purposes.
