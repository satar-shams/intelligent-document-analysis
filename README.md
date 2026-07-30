# intelligent-document-analysis

A modular document processing pipeline for extracting, preprocessing, and structuring content from heterogeneous documents for semantic search, information extraction, and Retrieval-Augmented Generation (RAG).

> **Status:** **Phase 3 Complete.** Document ingestion, OCR, text preprocessing, semantic embedding generation, and unit tests have been implemented. The next milestone is vector database integration with ChromaDB.

---

# Overview

This project provides a modular pipeline for processing documents in multiple formats and preparing them for downstream NLP applications.

Current capabilities include:

* PDF text extraction
* DOCX text extraction
* OCR for scanned PDFs
* Text cleaning and normalization
* Configurable text chunking
* Semantic embedding generation
* Automated unit testing

Future stages will introduce vector databases, information extraction, and Retrieval-Augmented Generation (RAG).

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
                    Vector Store
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
├── .env.example
├── .gitignore
│
├── configs/
│   └── config.yaml
│
├── docker/
│   └── Dockerfile
│
├── src/
│   ├── ingestion/
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   └── ocr_engine.py
│   │
│   ├── preprocessing/
│   │   ├── cleaner.py
│   │   └── chunker.py
│   │
│   ├── embeddings/
│   │   └── embedding_pipeline.py
│   │
│   ├── vectorstore/
│   │   └── chroma_store.py
│   │
│   ├── extraction/
│   │   ├── classifier.py
│   │   └── ner_model.py
│   │
│   ├── rag/
│   │   ├── rag_chain.py
│   │   └── prompt_templates.py
│   │
│   └── monitoring/
│       └── metrics.py
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
| Testing | pytest |
| Configuration | YAML |
| Vector Database | ChromaDB *(planned)* |
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

Install Tesseract on Ubuntu:

```bash
sudo apt install tesseract-ocr
```

Verify the installation:

```bash
tesseract --version
```

---

# Document Ingestion

The ingestion layer provides reusable parsers for different document types.

Supported inputs:

* PDF documents
* DOCX documents
* Scanned PDFs using OCR

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

OCR results can optionally be saved as structured JSON for downstream processing.

---

# Text Preprocessing

After extraction, documents are normalized before semantic processing.

Current functionality:

* Normalize line endings
* Normalize whitespace
* Remove excessive blank lines
* Page-wise cleaning
* Configurable chunk size
* Configurable chunk overlap
* Sequential chunk IDs
* Metadata preservation

Chunk structure:

```python
{
    "chunk_id": 1,
    "page": 2,
    "text": "Chunk content..."
}
```

---

# Embedding Generation

Document chunks are converted into dense semantic vectors using **Sentence Transformers**.

Current model:

* `all-MiniLM-L6-v2`

The embedding pipeline provides:

* Input validation
* Dependency injection for testing
* One embedding per text chunk
* Python list output compatible with vector databases

Example:

```python
from src.embeddings.embedding_pipeline import EmbeddingPipeline

pipeline = EmbeddingPipeline(
    model_name="all-MiniLM-L6-v2",
)

embeddings = pipeline.embed(
    [
        "Machine learning is fun.",
        "Artificial intelligence is changing software."
    ]
)
```

---

# Testing

Run all tests:

```bash
python -m pytest
```

Run ingestion tests:

```bash
python -m pytest tests/test_ingestion.py
```

Run preprocessing tests:

```bash
python -m pytest tests/test_preprocessing.py
```

Run embedding tests:

```bash
python -m pytest tests/test_embeddings.py
```

Current status:

* ✅ Ingestion tests passing
* ✅ Preprocessing tests passing
* ✅ Embedding tests passing

---

# Data Organization

```text
data/
├── raw/
│   ├── pdf/
│   ├── docx/
│   └── images/
│
├── processed/
└── samples/
```

Raw documents remain separate from generated outputs throughout the pipeline.

---

# Configuration

Project configuration is stored in:

```text
configs/
└── config.yaml
```

Shared settings such as chunk size, overlap, embedding model, and future vector database configuration are managed from this file.

---

# Development Principles

The project follows several engineering principles:

* **Modularity** — independent pipeline components.
* **Reusability** — configurable processing functions.
* **Testability** — automated unit tests.
* **Separation of Concerns** — parsing, preprocessing, embeddings, storage, and retrieval remain independent.
* **Local-first Development** — pretrained models run locally after the initial download.
* **Incremental Development** — components are added only when needed.

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
| Unit Tests | ✅ |
| Vector Database | 🚧 |
| Information Extraction | 🚧 |
| RAG Pipeline | 🚧 |
| Monitoring | 🚧 |

---

# Roadmap

## ✅ Phase 1 — Document Ingestion

* PDF parsing
* DOCX parsing
* OCR extraction

## ✅ Phase 2 — Text Preprocessing

* Text cleaning
* Chunking
* Unit tests

## ✅ Phase 3 — Semantic Embeddings

* Sentence Transformer integration
* Embedding pipeline
* Embedding unit tests

## 🚧 Phase 4 — Vector Database

* ChromaDB integration
* Similarity search
* Metadata storage

## 🚧 Phase 5 — Information Extraction

* Named Entity Recognition
* Document classification

## 🚧 Phase 6 — Retrieval-Augmented Generation

* Retriever
* Prompt templates
* RAG pipeline

---

# License

This project is available for educational and portfolio purposes.