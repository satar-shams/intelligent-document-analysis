# Intelligent Document Analysis

A modular document processing pipeline for extracting, preprocessing, embedding, and storing heterogeneous documents for semantic retrieval and Retrieval-Augmented Generation (RAG).

> **Status:** **Phase 2 complete.** The project currently provides an end-to-end document processing, semantic retrieval, and retrieval-to-context RAG pipeline, verified with unit tests, real-data integration tests, and end-to-end pipeline runs.

---

# Project Documentation

The project is being developed incrementally in multiple phases. Each completed phase has its own detailed report describing the implementation, design decisions, testing, and results.

### Phase 1 — Document Processing and Semantic Retrieval

Phase 1 covers:

* PDF and DOCX extraction
* OCR fallback for scanned PDFs
* Text preprocessing and chunking
* Semantic embedding generation
* ChromaDB vector storage
* Semantic similarity search
* Unit and real-data integration testing
* End-to-end Phase 1 pipeline

📄 **[Read the Phase 1 Report](reports/phase1_report.md)**

### Phase 2 — RAG Retrieval and Context Construction

Phase 2 builds on the Phase 1 retrieval foundation and covers:

* Query retrieval through the existing embedding and vector-store layers
* `Retriever` component
* `ContextBuilder` component
* `RAGChain` orchestration
* Top-k semantic retrieval
* Retrieval-to-context transformation
* Unit testing with mocked dependencies
* Real-data integration testing
* Grounded context generation for a future LLM generation stage

📄 **[Read the Phase 2 Report](reports/phase2_report.md)**

### Upcoming Phases

Additional phases will be documented here as they are implemented and completed.

* Phase 3 — Not started
* Phase 4 — Not started
