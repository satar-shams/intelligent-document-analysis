# intelligent-document-analysis

A modular document processing pipeline for extracting, preprocessing, embedding, and storing heterogeneous documents for semantic retrieval and future Retrieval-Augmented Generation (RAG) workflows.

> **Status:** **Task 1 Complete.** Document ingestion, OCR, text preprocessing, semantic embedding generation, ChromaDB vector database integration, semantic search, retrieval pipeline, and automated unit testing have been implemented.

---

# Overview

This project provides a modular pipeline for processing documents in multiple formats and preparing them for semantic search and retrieval applications.

Current capabilities include:

- PDF text extraction
- DOCX text extraction
- OCR for scanned PDFs
- Text cleaning and normalization
- Configurable text chunking
- Metadata preservation
- Semantic embedding generation
- ChromaDB vector storage
- Semantic similarity search
- Document retrieval pipeline
- Automated unit testing

Future improvements may introduce advanced information extraction and full Retrieval-Augmented Generation (RAG) workflows with LLM integration.

---

# Processing Pipeline

```text
                    Document Sources
                          │
              ┌───────────┼───────────┐
              │           │           │
             PDF         DOCX     Scanned PDF
              │           │           │
              ▼           ▼           ▼
         PDF Parser   DOCX Parser   OCR Engine
              │           │           │
              └───────────┼───────────┘
                          │
                          ▼
                 Structured Text
                          │
                          ▼
                 Text Cleaning
                          │
                          ▼
                     Chunking
                          │
                          ▼
                    Embeddings
                          │
                          ▼
                    ChromaDB
                          │
                          ▼
                  Semantic Search
                          │
                          ▼
                Retrieval Pipeline
                          │
                          ▼
               Context Preparation
```

---

# Project Structure

```text
intelligent-document-analysis/
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
│
├── configs/
│   └── config.yaml
│
├── src/
│   ├── ingestion/
│   ├── preprocessing/
│   ├── embeddings/
│   │   └── embedding_pipeline.py
│   ├── vectorstore/
│   │   └── chroma_store.py
│   ├── rag/
│   │   ├── rag_chain.py
│   │   └── prompt_templates.py
│   ├── extraction/
│   └── monitoring/
│
├── tests/
├── notebooks/
└── reports/
```

---

# Tech Stack

| Layer | Tools |
|-------|-------|
| Language | Python 3.12 |
| PDF Processing | PyMuPDF |
| DOCX Processing | python-docx |
| OCR | Tesseract OCR + pytesseract |
| Image Processing | Pillow |
| Text Processing | Regex |
| Embeddings | Sentence Transformers + PyTorch |
| Vector Database | ChromaDB |
| Testing | pytest |
| Configuration | YAML |
| Containerization | Docker |

---

# Environment Setup

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install Tesseract (Ubuntu):

```bash
sudo apt install tesseract-ocr
```

Verify:

```bash
tesseract --version
```

---

# Document Ingestion

Supported document formats:

- PDF
- DOCX
- Scanned PDF using OCR

Example:

```python
from src.ingestion.pdf_parser import extract_pdf_text

pages = extract_pdf_text(
    "data/raw/pdf/document.pdf"
)
```

OCR example:

```python
from src.ingestion.ocr_engine import extract_ocr_text

pages = extract_ocr_text(
    "data/raw/pdf/scanned.pdf",
    max_pages=3,
)
```

---

# Text Preprocessing

Current preprocessing features:

- Normalize whitespace
- Normalize line endings
- Remove excessive blank lines
- Page-wise cleaning
- Configurable chunk size
- Configurable overlap
- Metadata preservation

Example chunk:

```python
{
    "chunk_id": 1,
    "page": 2,
    "text": "Chunk content..."
}
```

---

# Embedding Generation

Document chunks are converted into dense semantic vectors using Sentence Transformers.

Current model:

- `all-MiniLM-L6-v2`

Features:

- Configurable embedding model
- Dependency injection for testing
- Input validation
- ChromaDB-compatible vector output

Example:

```python
from src.embeddings.embedding_pipeline import EmbeddingPipeline

pipeline = EmbeddingPipeline(
    model_name="all-MiniLM-L6-v2",
)

embeddings = pipeline.embed(
    [
        "Machine learning",
        "Artificial intelligence",
    ]
)
```

---

# Vector Database

Embeddings are stored locally using ChromaDB.

Features:

- Persistent vector database
- Collection management
- Metadata storage
- Vector insertion
- Semantic similarity search

Example:

```python
from src.vectorstore.chroma_store import ChromaStore

store = ChromaStore()

store.add(
    chunks=chunks,
    embeddings=embeddings,
)

results = store.search(
    query_embedding,
    top_k=5,
)
```

---

# Retrieval Pipeline

The retrieval layer connects user queries with the vector database.

Flow:

```text
User Query
     │
     ▼
Query Embedding
     │
     ▼
ChromaDB Similarity Search
     │
     ▼
Relevant Document Chunks
     │
     ▼
Context Building
```

Implemented features:

- Query embedding generation
- Similarity-based retrieval
- Top-k result selection
- Context preparation for future LLM integration

---

# Testing

Run all tests:

```bash
python -m pytest
```

Run specific suites:

```bash
python -m pytest tests/test_ingestion.py
python -m pytest tests/test_preprocessing.py
python -m pytest tests/test_embeddings.py
python -m pytest tests/test_vectorstore.py
python -m pytest tests/test_rag_chain.py
```

Current status:

- ✅ 38 tests passing
- ✅ Ingestion tests
- ✅ Preprocessing tests
- ✅ Embedding tests
- ✅ Vector database tests
- ✅ Retrieval pipeline tests

---

# Configuration

Project configuration is stored in:

```text
configs/
└── config.yaml
```

Configuration includes:

- Project metadata
- Data paths
- Embedding model
- Chunk size
- Chunk overlap
- ChromaDB path
- Collection name

---

# Development Principles

The project follows these engineering principles:

- **Modularity** — independent pipeline components
- **Reusability** — configurable processing modules
- **Testability** — automated validation
- **Separation of Concerns** — ingestion, preprocessing, embeddings, storage, and retrieval remain independent
- **Local-first Development** — models run locally after download
- **Incremental Development** — components are introduced step-by-step

---

# Current Implementation Status

| Component | Status |
|------------------------|:------:|
| Project Structure | ✅ |
| PDF Parser | ✅ |
| DOCX Parser | ✅ |
| OCR Engine | ✅ |
| OCR JSON Export | ✅ |
| Text Cleaning | ✅ |
| Text Chunking | ✅ |
| Metadata Handling | ✅ |
| Embedding Pipeline | ✅ |
| Vector Database | ✅ |
| Semantic Search | ✅ |
| Retrieval Pipeline | ✅ |
| Unit Tests | ✅ |
| Information Extraction | 🚧 |
| Full RAG Pipeline | 🚧 |
| Monitoring | 🚧 |

---

# Roadmap

## ✅ Phase 1 — Document Ingestion

- PDF parsing
- DOCX parsing
- OCR extraction

## ✅ Phase 2 — Text Preprocessing

- Text cleaning
- Normalization
- Chunking
- Unit tests

## ✅ Phase 3 — Semantic Embeddings

- Sentence Transformer integration
- Embedding pipeline
- Embedding validation

## ✅ Phase 4 — Vector Database

- ChromaDB integration
- Embedding storage
- Metadata storage
- Semantic similarity search

## ✅ Phase 5 — Information Retrieval

- Query embedding
- Retriever pipeline
- Context builder
- Retrieval tests

---

# Future Improvements

Possible future enhancements:

- Advanced OCR denoising
- Header/footer removal
- Improved metadata schema
- Semantic chunking
- Document hierarchy preservation
- Full RAG pipeline with LLM integration
- Monitoring and evaluation metrics

---

# License

This project is available for educational and portfolio purposes.