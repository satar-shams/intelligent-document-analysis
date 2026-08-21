# Intelligent Document Analysis — Phase 2

Phase 2 extends the Phase 1 semantic retrieval foundation into a simple RAG-oriented retrieval and context-building layer.

> **Status:** **Phase 2 complete.** Query retrieval, context construction, RAG orchestration, unit tests, and a real-data end-to-end integration test have been implemented and verified.

---

# Overview

Phase 1 established the document processing and semantic retrieval foundation:

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

Phase 2 builds on that existing retrieval layer.

The main goal is to transform a user query into relevant document chunks and then transform those chunks into a structured text context suitable for a later generation step.

The Phase 2 flow is:

```text
User Query
    ↓
Retriever
    ↓
Semantic Search
    ↓
Search Results
    ↓
ContextBuilder
    ↓
Context
    ↓
RAGChain
```

The current Phase 2 implementation does **not** require an LLM. It establishes the retrieval and context layer that can later provide grounded information to an LLM.

---

# Phase 2 Components

Phase 2 introduces three main components:

```text
src/rag/
├── context_builder.py
├── __init__.py
├── prompt_templates.py
├── rag_chain.py
└── retriever.py
```

---

# Retriever

The `Retriever` connects a natural-language query to the existing Phase 1 embedding and vector-store components.

```text
src/rag/retriever.py
```

Its responsibilities are:

* Receive a natural-language query
* Generate an embedding for the query
* Search ChromaDB using that embedding
* Return the top-k semantic search results

The implementation uses dependency injection:

```python
Retriever(
    embedding_pipeline=embedding_pipeline,
    chroma_store=chroma_store,
)
```

The main method is:

```python
retrieve(
    query: str,
    top_k: int = 5,
) -> list[SearchResultData]
```

The retrieval process is:

```text
Query
  ↓
EmbeddingPipeline
  ↓
Query Embedding
  ↓
ChromaStore.search()
  ↓
list[SearchResultData]
```

The Retriever does not implement embedding generation or vector search itself. It delegates those responsibilities to the existing Phase 1 components.

---

# Context Builder

The `ContextBuilder` converts retrieved `SearchResultData` objects into a single text context.

```text
src/rag/context_builder.py
```

It receives:

```python
list[SearchResultData]
```

and produces:

```python
str
```

Each result is represented with its document and page metadata:

```text
chunk_id: ...
document_id: ...
page_start: ...
page_end: ...
text: ...
```

Multiple chunks are separated by blank lines.

Example:

```text
chunk_id: 1
document_id: doc-1
page_start: 1
page_end: 1
text: Some text 1

chunk_id: 2
document_id: doc-1
page_start: 2
page_end: 2
text: Some text 2
```

The original retrieved chunk text is preserved.

The ContextBuilder therefore acts as the bridge between structured retrieval results and a text-based context that can later be inserted into an LLM prompt.

---

# RAG Chain

The `RAGChain` provides the orchestration layer for the Phase 2 flow.

```text
src/rag/rag_chain.py
```

It receives:

```python
RAGChain(
    retriever=retriever,
    context_builder=context_builder,
)
```

The main method is:

```python
run(
    query: str,
    top_k: int = 5,
) -> str
```

The method performs two operations:

```python
search_result = self.retriever.retrieve(
    query=query,
    top_k=top_k,
)

context_result = self.context_builder.build(
    search_results=search_result,
)

return context_result
```

Therefore:

```text
Query
  ↓
Retriever
  ↓
Top-K Search Results
  ↓
ContextBuilder
  ↓
Formatted Context
  ↓
Returned by RAGChain
```

The RAG chain intentionally remains simple at this stage.

It does not contain embedding logic, vector-store logic, or context-formatting logic. Those responsibilities remain inside their respective components.

---

# Relationship to Phase 1

Phase 2 does not duplicate the functionality developed in Phase 1.

Instead, it reuses the existing components:

```text
Phase 1
────────────────────────────
EmbeddingPipeline
ChromaStore
SearchResultData
────────────────────────────
             ↓
             ↓
Phase 2
────────────────────────────
Retriever
ContextBuilder
RAGChain
────────────────────────────
```

This separation keeps the architecture modular.

The Retriever uses the Phase 1 embedding and vector-store infrastructure rather than implementing another retrieval mechanism.

---

# Top-K Retrieval

The RAG chain does not send the complete document collection to a future LLM.

For the current dataset, there are approximately 1,000 chunks.

If:

```python
top_k = 5
```

the flow is:

```text
~1,000 stored chunks
        ↓
   semantic search
        ↓
    top 5 chunks
        ↓
  ContextBuilder
        ↓
  context for LLM
```

Only the retrieved chunks are intended to become the context supplied to a later generation component.

This keeps the generation step focused on the most relevant document content instead of sending the complete document collection.

---

# Data Contract

Phase 2 uses the existing `SearchResultData` schema:

```python
@dataclass
class SearchResultData:
    chunk_id: str
    document_id: str
    text: str
    page_start: int
    page_end: int
    distance: float
    section_title: str | None = None
```

This provides the information required to construct grounded context while preserving source information such as document and page location.

---

# Testing

Phase 2 was tested at both the **unit** and **integration** levels.

## Retriever Unit Tests

The Retriever is tested independently using mocked dependencies.

The embedding pipeline and ChromaDB store are mocked so that the tests focus only on Retriever behavior.

The tests verify that:

* A query is passed to the embedding pipeline correctly
* The query is wrapped in the expected list format
* The generated embedding is passed to ChromaDB
* The configured `top_k` value is passed correctly
* Search results from ChromaDB are returned by the Retriever

Run:

```bash
python -m pytest tests/unit/test_retriever.py -v
```

---

## Context Builder Unit Tests

The ContextBuilder is tested independently using controlled `SearchResultData` objects.

The tests verify that:

* The result is a string
* Retrieved chunks are formatted correctly
* Metadata is included
* Multiple chunks are separated correctly
* The final context matches the expected structure

Run:

```bash
python -m pytest tests/unit/test_context_builder.py -v
```

---

## RAG Chain Unit Tests

The RAGChain orchestration is tested using mocked Retriever and ContextBuilder objects.

The tests verify that:

1. The query and `top_k` are passed to the Retriever.
2. The Retriever's returned value is passed to ContextBuilder.
3. The value returned by ContextBuilder is returned by `RAGChain.run()`.

The internal behavior of Retriever and ContextBuilder is intentionally not retested here because those components have their own unit tests.

---

## Real-Data Integration Test

A real-data integration test verifies the complete Phase 2 flow using the actual ChromaDB data and real implementations.

The test constructs:

```text
EmbeddingPipeline
      ↓
ChromaStore
      ↓
Retriever
      ↓
ContextBuilder
      ↓
RAGChain
```

and executes a real query:

```text
"When he came to the war he was barely eighteen"
```

The test verifies that the complete flow produces a non-empty string context.

Run:

```bash
python -m pytest tests/integration/test_rag_chain_real_data.py -v -s
```

The `-s` option allows output printed by the integration test to be displayed directly in the terminal when needed for inspection.

---

# Phase 2 Test Coverage

The Phase 2 test structure is:

```text
Unit Tests
│
├── Retriever
│   ├── Query embedding
│   ├── ChromaDB search
│   └── Result propagation
│
├── ContextBuilder
│   ├── String output
│   └── Context formatting
│
└── RAGChain
    ├── Retriever orchestration
    ├── ContextBuilder orchestration
    └── Final result propagation

Integration Test
│
└── Complete real-data RAG flow
```

---

# Current Phase 2 Status

| Component                         | Status |
| --------------------------------- | :----: |
| Retriever                         |   ✅    |
| Context Builder                   |   ✅    |
| RAG Chain                         |   ✅    |
| Retriever Unit Tests              |   ✅    |
| Context Builder Unit Tests        |   ✅    |
| RAG Chain Unit Tests              |   ✅    |
| Real-Data RAG Integration Test    |   ✅    |
| Phase 2 Retrieval-to-Context Flow |   ✅    |

---

# Phase 2 Output

The main output of Phase 2 is a **grounded text context** constructed from the most relevant retrieved chunks.

Conceptually:

```text
User Query
    ↓
Semantic Retrieval
    ↓
Top-K Relevant Chunks
    ↓
Structured Context
```

For example:

```text
chunk_id: 59
document_id: sample-text-pdf
page_start: 19
page_end: 19
text: When he came to the war he was barely eighteen...

chunk_id: ...
document_id: ...
page_start: ...
page_end: ...
text: ...
```

This context is ready to become the evidence supplied to a future answer-generation component.

---

# Suggested Future Work

The following items are **future improvements**, not requirements of the completed Phase 2 implementation.

## Extensible Domain-Specific Metadata

`SearchResultData` currently contains a small set of common metadata fields.

A future version could add an optional flexible metadata dictionary:

```python
metadata: dict[str, Any]
```

This would allow the retrieval layer to preserve domain-specific information without repeatedly changing the core schema.

For example, a financial document could contain:

```python
metadata = {
    "document_type": "payroll_report",
    "employee_id": "EMP-1042",
    "department": "Engineering",
    "position": "ML Engineer",
    "pay_period": "2026-07",
    "salary": 4200.00,
    "currency": "USD",
    "bonus": 500.00,
    "tax": 630.00,
    "net_salary": 4070.00,
    "payment_date": "2026-07-31",
}
```

An invoice could instead contain:

```python
metadata = {
    "document_type": "invoice",
    "invoice_number": "INV-2026-1042",
    "vendor": "Example Corp",
    "invoice_date": "2026-07-15",
    "due_date": "2026-08-15",
    "total": 5500.00,
    "currency": "USD",
}
```

This would allow the core retrieval system to remain generic while supporting richer downstream filtering, context construction, and RAG applications.

## Advanced Retrieval

Future retrieval improvements could include:

* Metadata filtering
* Hybrid search
* Reranking
* Query expansion
* More extensive retrieval evaluation

## Answer Generation

A later stage can connect the generated context to an LLM:

```text
User Query
    ↓
Retriever
    ↓
Top-K Relevant Chunks
    ↓
ContextBuilder
    ↓
Prompt
    ↓
LLM
    ↓
Grounded Answer
```

The LLM generation stage is deliberately outside the completed Phase 2 implementation.

---

# Development Principles

The Phase 2 implementation follows the same engineering principles established in Phase 1:

* **Modularity** — retrieval, context construction, and orchestration remain separate.
* **Separation of Concerns** — each component has a focused responsibility.
* **Dependency Injection** — components receive their dependencies rather than constructing them internally.
* **Testability** — individual components are tested with mocks while the complete flow is tested with real data.
* **Reuse** — Phase 2 builds on the existing Phase 1 retrieval infrastructure.
* **Avoid Premature Complexity** — LLM generation and advanced retrieval features are deferred until they are required.

---

# Phase 2 Summary

Phase 2 adds the RAG retrieval and context layer on top of the Phase 1 foundation.

The completed architecture is:

```text
Documents
   ↓
Phase 1 Processing
   ↓
Embeddings
   ↓
ChromaDB
   ↓
Retriever
   ↓
Top-K Relevant Chunks
   ↓
ContextBuilder
   ↓
RAGChain
   ↓
Grounded Context
```

The Phase 2 components have been tested independently and the complete retrieval-to-context flow has been verified against real project data.

Phase 2 therefore provides a clean foundation for a future answer-generation stage while keeping the current implementation focused and maintainable.

---

# License

This project is developed for educational and portfolio purposes.
