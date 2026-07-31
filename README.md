# intelligent-document-analysis

A modular document processing pipeline for extracting, preprocessing, and structuring content from heterogeneous documents for semantic search, information extraction, and Retrieval-Augmented Generation (RAG).

> **Status:** **Phase 4 Complete.** Document ingestion, OCR, text preprocessing, semantic embedding generation, vector database integration, semantic search, and unit tests have been implemented. The next milestone is document retrieval for Retrieval-Augmented Generation (RAG).

---

# Overview

This project provides a modular pipeline for processing documents in multiple formats and preparing them for downstream NLP applications.

Current capabilities include:

- PDF text extraction
- DOCX text extraction
- OCR for scanned PDFs
- Text cleaning and normalization
- Configurable text chunking
- Semantic embedding generation
- ChromaDB vector storage
- Semantic similarity search
- Automated unit testing

Future stages will introduce document retrieval, information extraction, and Retrieval-Augmented Generation (RAG).

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
                 Retrieval / RAG
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
- Scanned PDF (OCR)

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
- Compatible with ChromaDB

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
- Automatic collection creation
- Metadata storage
- Semantic similarity search
- Collection management

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
```

Current status:

- ✅ Ingestion tests
- ✅ Preprocessing tests
- ✅ Embedding tests
- ✅ Vector database tests

---

# Configuration

Project configuration is stored in:

```text
configs/
└── config.yaml
```

Configuration currently includes:

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

- **Modularity**
- **Reusability**
- **Testability**
- **Separation of Concerns**
- **Local-first Development**
- **Incremental Development**

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
| Embedding Pipeline | ✅ |
| Vector Database | ✅ |
| Semantic Search | ✅ |
| Unit Tests | ✅ |
| Information Extraction | 🚧 |
| RAG Pipeline | 🚧 |
| Monitoring | 🚧 |

---
# Roadmap

## ✅ Phase 1 — Document Ingestion

- PDF parsing
- DOCX parsing
- OCR extraction

## ✅ Phase 2 — Text Preprocessing

- Text cleaning
- Chunking
- Unit tests

## ✅ Phase 3 — Semantic Embeddings

- Sentence Transformer integration
- Embedding pipeline
- Embedding unit tests

## ✅ Phase 4 — Vector Database

- ChromaDB integration
- Embedding storage
- Metadata storage
- Semantic similarity search

## 🚧 Phase 5 — Information Retrieval

- Retriever
- Context builder
- Retrieval tests
- Retrieval-ready pipeline

---

# License

This project is available for educational and portfolio purposes.