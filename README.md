# Intelligent Document Analysis

A modular document intelligence pipeline for processing documents, building semantic search infrastructure, extracting structured entities, and answering questions with Retrieval-Augmented Generation (RAG).

The project brings together three connected stages:

* **Document processing and semantic retrieval** — ingestion, text extraction, preprocessing, chunking, embeddings, and vector search.
* **Entity annotation and extraction** — weak annotation, pretrained NER, hybrid extraction, and evaluation.
* **Retrieval-Augmented Generation** — retrieval, context construction, prompt generation, and LLM-based answer generation.

The main executable pipelines are:

```text
pipelines/
├── phase1.py       # Document processing and semantic retrieval
├── annotation.py   # Annotation dataset generation and validation
├── extraction.py   # Hybrid entity extraction
└── rag.py          # Batch RAG question answering
```

The repository also includes automated tests, evaluation data, and technical reports documenting the implementation and evaluation of the project.

## Project Workflow

Phase 1 establishes the shared document-processing foundation used by the downstream workflows.

```text
                          ┌──────────────────────┐
                          │      Documents       │
                          └──────────┬───────────┘
                                     │
                                     ▼
                 ┌──────────────────────────────────┐
                 │              Phase 1             │
                 │ Ingestion · Preprocessing        │
                 │ Chunking · Embeddings · ChromaDB │
                 │ Semantic Retrieval               │
                 └───────────────┬──────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
        ┌──────────────────────┐   ┌──────────────────────┐
        │       Phase 2        │   │       Phase 3        │
        │ Annotation           │   │ RAG                  │
        │ Entity Extraction    │   │ Retrieval            │
        │ Evaluation           │   │ Context & Prompt     │
        └──────────────────────┘   │ LLM Generation       │
                                   └──────────────────────┘
```

# Quick Start

Clone the repository, create a virtual environment, and install the project dependencies:

```bash
git clone https://github.com/satar-shams/intelligent-document-analysis.git
cd intelligent-document-analysis

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt
```

The main experimental document collection consists primarily of Microsoft annual reports and is not included in the repository. Input documents can be placed under:

```text
data/raw/
```

The repository includes a small set of ingestion fixtures under `data/phase1/` for testing PDF text extraction, OCR fallback, and DOCX ingestion.

The main configuration file is:

```text
configs/config.yaml
```

## Running the Pipelines

```bash
python -m pipelines.phase1
python -m pipelines.annotation
python -m pipelines.extraction
python -m pipelines.rag
```

Live RAG answer generation requires an `OPENAI_API_KEY` with available API credits. The RAG test suite uses a mock LLM and does not require external API access.

## Tests

Run the complete test suite with:

```bash
python -m pytest
```

# Phase 1 — Document Processing and Semantic Retrieval

Phase 1 establishes the document processing and semantic retrieval foundation for the project.

The pipeline consists of seven main stages:

1. Document ingestion
2. Text extraction
3. Preprocessing
4. Chunking
5. Embedding generation
6. Vector storage
7. Semantic retrieval

## Document Ingestion

The ingestion layer supports:

* PDF documents
* DOCX documents
* OCR fallback for scanned or image-based PDF pages

PDF text is extracted with PyMuPDF when usable text is available. When standard extraction does not produce usable text, OCR can be used as a fallback.

DOCX documents are processed paragraph by paragraph and represented as page-like units for downstream processing.

## Preprocessing

Extracted text is normalized before chunking and embedding.

## Chunking

Documents are divided into overlapping chunks.

The current configuration uses:

```text
Chunk size: 1000 characters
Overlap:     200 characters
```

This provides manageable units for semantic embedding and retrieval while preserving contextual continuity between adjacent chunks.

## Embeddings

The project uses:

```text
all-MiniLM-L6-v2
```

for semantic embeddings.

## Vector Store

ChromaDB is used as the persistent vector store.

The Phase 1 pipeline builds the configured collection from the processed documents.

```text
data/vectorstore/
```

The configured collection is:

```text
documents
```

## Semantic Retrieval

Queries are embedded using the same embedding model and searched against the ChromaDB collection.

Retrieved chunks provide the semantic search layer used by downstream workflows, including entity extraction and Retrieval-Augmented Generation.

# Phase 2 — Annotation and Entity Extraction

Phase 2 introduces the annotation and entity-extraction workflow used to build and evaluate the project's entity extraction system.

The annotation pipeline performs:

1. Dataset creation
2. Weak annotation generation
3. Annotation validation
4. Annotation analysis
5. Dataset splitting

## Weak Annotation

The current annotation system generates deterministic weak labels using rules for:

* `DATE`
* `MONEY`
* `PERCENTAGE`
* `ORGANIZATION`
* `PRODUCT`

These annotations are automatically generated and are **not treated as human ground truth**. They provide a reproducible reference for developing and testing the extraction pipeline.

Pretrained NER models use labels such as `PER`, `ORG`, and `LOC`, which are mapped to the project's schema:

```text
PER → PERSON
ORG → ORGANIZATION
LOC → LOCATION
```

The project's combined entity schema contains seven labels:

```text
PERSON
ORGANIZATION
LOCATION
DATE
MONEY
PERCENTAGE
PRODUCT
```

## Entity Extraction

The extraction pipeline combines deterministic rule-based extraction with pretrained NER:

```text
Document Chunks
      │
      ├───────────────┐
      ▼               ▼
Rule-Based        Pretrained
Extraction             NER
      │               │
      └───────┬───────┘
              ▼
      Hybrid Extraction
              │
              ▼
      Extracted Entities
```

The extraction entry point is:

```text
pipelines/extraction.py
```

The hybrid extractor combines rule-based and NER predictions, maps them to the project schema, and handles duplicate entities.

Each extracted entity contains information such as:

* entity text
* entity label
* start position
* end position

Predictions are stored under:

```text
data/processed/extraction/
```

## Current NER Baseline

The current baseline uses:

```text
musk1209/finsight-ner
```

as the selected pretrained NER model under the current weak-annotation benchmark. Several pretrained NER models were compared during Phase 2.

The current benchmark measures consistency with the project's automatically generated weak annotations. It should therefore **not be interpreted as an independent measurement of true semantic extraction quality**.

## Phase 2 Evaluation

The current evaluation is a **baseline against weak annotations**. This is useful for checking extraction behavior and pipeline consistency, but the reference annotations are generated automatically rather than manually verified.

The intended future evaluation is based on a **human-verified entity annotation dataset**. The existing dataset structure provides the basis for this workflow:

```text
350 training
75 validation
75 test
```

**The planned evaluation process is:**

* **Training set:** project-specific NER fine-tuning
* **Validation set:** model selection and tuning
* **Test set:** held out until final evaluation
* **Reference:** human-verified entity annotations
* **Metrics:** Precision, Recall, and F1 against the verified reference

The evaluation should maintain a clear separation between the target entity schema, reference annotations, extraction system, and evaluation process. This prevents automatically generated extraction rules from becoming the definition of correctness.

The hybrid rule-based + NER system can then be evaluated against the same human-verified reference, including cases where the two extraction methods produce different predictions.

This human-verified evaluation and project-specific NER fine-tuning are future improvements, not part of the current baseline.

# Phase 3 — Retrieval-Augmented Generation

The RAG pipeline extends semantic retrieval into question answering by combining vector search, context construction, prompt generation, and LLM-based answer generation.

The workflow is:

```text
Question
   │
   ▼
Retriever
   │
   ▼
ContextBuilder
   │
   ▼
PromptBuilder
   │
   ▼
LLMClient
   │
   ▼
Answer
```

The executable entry point is:

```text
pipelines/rag.py
```

The pipeline is built from independent components under `src/rag/`:

```text
src/rag/
├── retriever.py
│   └── Retrieves relevant document chunks from ChromaDB
├── context_builder.py
│   └── Builds the context supplied to the language model
├── prompt_templates.py
│   └── Builds the question-answering prompt
├── llm_client.py
│   └── Sends prompts to the OpenAI Responses API
├── rag_chain.py
│   └── Provides reusable RAG orchestration
└── evaluation_summary.py
    └── Summarizes manual RAG evaluation results
```

The batch pipeline loads evaluation questions, retrieves relevant chunks, builds the context and prompt, and stores the generated outputs for evaluation., and stores the outputs for evaluation.

## Retriever

`retriever.py` converts a question into an embedding and searches ChromaDB for semantically relevant document chunks.

Each result includes information such as the chunk ID, document ID, page information, retrieved text, and retrieval distance.

## ContextBuilder

`context_builder.py` formats retrieved results into the context supplied to the LLM while preserving document and page metadata.

## PromptBuilder

`prompt_templates.py` validates the instruction, question, and retrieved context and builds the final question-answering prompt.

The prompt instructs the model to answer only from the supplied context and avoid unsupported information.

## **LLMClient**

`llm_client.py` provides the LLM interface designed for the OpenAI Responses API.

The configured model is:

```text
gpt-5-mini
```

API-based execution was implemented but could not be used for the current evaluation because API access and credits were not available.

For the current RAG evaluation, prompts were therefore generated from the same retrieval and context-building pipeline and evaluated through **manual prompting**. This allowed the retrieval and prompt-construction workflow to be examined without presenting the manually generated results as API-generated outputs.

The automated RAG tests use a mock LLM and do not require API access.

## RAGChain

`rag_chain.py` provides reusable single-question RAG orchestration across the retrieval, context, prompt, and generation components.

## RAGPipeline

The batch pipeline in `pipelines/rag.py` processes the evaluation questions stored in:

```text
data/evaluation/questions.jsonl
```

For each question, it retrieves the relevant chunks, builds the prompt, generates the answer, and stores the retrieval and generation results.

The current batch output is:

```text
data/evaluation/results.jsonl
```

# Evaluation

The project uses evaluation workflows for both entity extraction and RAG.

## Entity Extraction

The extraction evaluator supports:

* Precision, Recall, and F1
* per-label results
* strict entity matching
* error analysis

Strict matching compares entity text, label, and character span.

The current Phase 2 benchmark uses deterministic weak annotations and should therefore be interpreted as a **development baseline for agreement with the weak reference**, rather than as a final measurement of semantic NER quality.

## RAG Evaluation

The current RAG evaluation consists of **15 manually evaluated questions**. It considers:

* whether the question is answerable from the retrieved context;
* whether the generated answer is correct;
* whether the answer is grounded in the supplied context.

The current manual baseline is:

```text
Answerable:      11 / 15
Not answerable:   4 / 15

Correct:         14 / 15
Incorrect:        1 / 15

Grounded:        15 / 15
Not grounded:     0 / 15
```

These results represent a small manual development baseline rather than a statistically comprehensive benchmark.

### Retrieval Limitation

The retrieval review showed that semantic retrieval can identify the correct document or topic without always ranking the exact answer-bearing chunk highly.

This is particularly relevant for questions involving:

* specific reporting years;
* similar financial statements across annual reports;
* entity-specific facts;
* exact numerical values.

Therefore, high semantic similarity does not necessarily mean that the retrieved context contains the exact evidence required to answer a factual question.

Improving retrieval precision and answer-bearing chunk ranking is an important area for future work.

# Testing

The project includes unit and integration tests covering the main document-processing, annotation, extraction, retrieval, and RAG components.

The test suite is organized into:

```text
tests/
├── annotation/       # Annotation pipeline tests
├── unit/             # Component-level tests
│   └── rag/          # Focused RAG unit tests
└── integration/      # End-to-end and real-data integration tests
```

Unit tests cover ingestion, preprocessing, embeddings, vector storage, retrieval, entity extraction, NER, and RAG components. Annotation tests cover dataset sampling, annotation, validation, evaluation, and splitting.

Integration tests exercise components together, including real-data ingestion, vector storage, retrieval, and RAG workflows. RAG integration tests use a mock LLM where external API access is not required.

Run the complete test suite with:

```bash
python -m pytest
```

The current test suite contains **98 tests, all passing**.

# OpenAI Configuration

The live RAG pipeline requires an OpenAI API key provided through the `OPENAI_API_KEY` environment variable:

```bash
export OPENAI_API_KEY="your_api_key"
```

The key should never be committed to the repository.

RAG tests use a mock LLM and therefore do not require API access or API credits.

# Project Structure

The repository is organized around executable pipelines, reusable source modules, data, tests, and technical documentation:

```text
.
├── configs/
│   └── config.yaml
├── pipelines/
│   ├── phase1.py
│   ├── annotation.py
│   ├── extraction.py
│   └── rag.py
├── src/
│   ├── annotation/
│   ├── embeddings/
│   ├── extraction/
│   ├── ingestion/
│   ├── preprocessing/
│   ├── rag/
│   └── vectorstore/
├── data/
│   ├── raw/
│   ├── processed/
│   └── evaluation/
├── tests/
│   ├── annotation/
│   ├── unit/
│   └── integration/
├── docs/
├── reports/
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

The `pipelines/` directory contains the main executable workflows, while reusable implementation components are organized under `src/`. Tests, evaluation data, documentation, and reports are kept separate from the application code.

# Documentation

Detailed technical documentation is available in `reports/` and `docs/`.

* [`reports/phase1_report.md`](reports/phase1_report.md) — Document processing and semantic retrieval
* [`reports/phase2_report.md`](reports/phase2_report.md) — Annotation and entity extraction
* [`reports/phase3_report.md`](reports/phase3_report.md) — RAG architecture and evaluation
* [`docs/annotation_guidelines.md`](docs/annotation_guidelines.md) — Annotation guidance

The README provides the project overview and usage, while the reports contain the detailed technical documentation.


# Future Improvements

Future work focuses on improving the existing implementation and evaluation methodology rather than adding another major project phase.

Potential improvements include:

* retrieval quality optimization and improved answer-bearing chunk ranking;
* improved table extraction;
* human-verified entity annotations;
* project-specific NER fine-tuning with held-out evaluation;
* evaluation methodology that better reflects semantic extraction quality;
* larger RAG evaluation datasets and automated evaluation;
* source and page attribution for generated answers;
* stronger API error handling;
* systematic comparison of LLM configurations;
* live LLM benchmarking when API access is available.