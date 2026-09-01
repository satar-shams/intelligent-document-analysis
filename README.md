# Intelligent Document Analysis

A modular document processing pipeline for extracting, preprocessing, embedding, and storing heterogeneous documents for semantic retrieval and Retrieval-Augmented Generation (RAG).

> **Status:** **Phase 3 complete.** The project now provides an end-to-end document processing, semantic retrieval, RAG generation, batch orchestration, and initial evaluation pipeline.

---

# Project Documentation

The project is being developed incrementally in multiple phases. Each phase has its own detailed report.

### Phase 1 — Document Processing and Semantic Retrieval

Phase 1 covers the document processing and semantic retrieval foundation.

📄 **[Read the Phase 1 Report](reports/phase1_report.md)**

### Phase 2 — Annotation, Entity Extraction, and RAG Retrieval

Phase 2 extends the project with annotation, entity extraction, hybrid extraction, evaluation, semantic error analysis, and the RAG retrieval-to-context layer.

📄 **[Read the Phase 2 Report](reports/phase2_report.md)**

### Phase 3 — RAG Generation, Orchestration, and Evaluation

Phase 3 extends the RAG system from retrieval and context construction to complete answer generation.

It includes:

* Prompt construction
* OpenAI LLM client integration
* Dependency injection
* Single-question RAG chain
* Batch RAG orchestration
* Prompt and result persistence
* Manual evaluation
* Evaluation summary
* Initial retrieval-quality analysis

📄 [**Read the Phase 3 Report**](reports/phase3_report.md)

### Upcoming Phases

Future work will focus on improving the existing baseline rather than changing the core architecture.

Possible improvements include:

* Retrieval quality optimization
* Better table extraction and retrieval
* Larger evaluation datasets
* Automated evaluation
* Source attribution
* Production error handling
* Live LLM benchmarking

---

# Current Architecture

The current system follows:

```text
Documents
    ↓
Document Processing
    ↓
Chunking
    ↓
Embeddings
    ↓
ChromaDB
    ↓
Semantic Retrieval
    ↓
Context Construction
    ↓
Prompt Construction
    ↓
LLM
    ↓
Generated Answer
```

For batch processing:

```text
questions.jsonl
    ↓
RAG Pipeline
    ↓
retrieval
    ↓
context
    ↓
prompt
    ↓
LLM
    ↓
results
```

---

# Current Status

```text
Phase 1  ✅ Complete
Phase 2  ✅ Complete
Phase 3  ✅ Complete
Phase 4  ⏳ Not started
```

The OpenAI integration is implemented, but live API execution is currently limited by API-credit availability. The system can still be developed and evaluated locally using mocked LLM behavior and manually evaluated prompts.
