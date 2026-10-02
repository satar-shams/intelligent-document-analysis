# Intelligent Document Analysis

A modular document intelligence pipeline for processing documents, building semantic search infrastructure, extracting structured entities, and answering questions using Retrieval-Augmented Generation (RAG).

The project is organized into four main pipelines:

```text
                    ┌─────────────────────────┐
                    │      Source Documents   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  1. Phase 1 Pipeline    │
                    │  Ingestion → ChromaDB   │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
          ┌──────────────────┐     ┌────────────────────┐
          │ 2. Annotation    │     │ 3. Entity          │
          │ Pipeline         │     │ Extraction Pipeline│
          └──────────────────┘     └────────────────────┘
                    ┌─────────────────────────┐
                    │ 4. RAG Pipeline         │
                    │ Retrieval → LLM → Answer│
                    └─────────────────────────┘
```

> **Status:** Phase 1, Phase 2, and Phase 3 are complete. The repository currently provides the implemented document-processing, retrieval, entity-extraction, and RAG workflows.

---

# Quick Start

## 1. Clone the repository

```bash
git clone https://github.com/satar-shams/intelligent-document-analysis.git

cd intelligent-document-analysis
```

## 2. Create a virtual environment

### Linux / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

### Windows

```powershell
python -m venv .venv

.venv\Scripts\activate
```

## 3. Install dependencies

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Install development and testing dependencies:

```bash
pip install -r requirements-dev.txt
```

---

## 4. Prepare the Microsoft Data

This project uses **Microsoft annual reports** as its primary document corpus.

The annual reports are not included in this repository. Download the required reports from Microsoft's official Investor Relations website.

[Microsoft Investor Relations — Annual Reports](https://www.microsoft.com/en-us/investor/annual-reports?utm_source=chatgpt.com)

After downloading the reports, place the document files under:

```text
data/raw/
```

For example:

```text
data/
└── raw/
    ├── Microsoft_Annual_Report_2025.pdf
    ├── Microsoft_Annual_Report_2024.pdf
    ├── Microsoft_Annual_Report_2023.pdf
    └── ...
```

The exact filenames do not need to match the examples above. The important requirement is that the documents are placed inside the configured `data/raw/` directory.

> **Important:** The Microsoft document corpus is intentionally excluded from Git because these are external source documents and can be downloaded directly from Microsoft.

---

## 5. Prepare the Test Files

Before running the integration tests, make sure the Phase 1 test fixtures exist under:

```text
data/phase1/
```

The four files represent different document-ingestion cases:

```text
data/phase1/
├── sample_pdf_text.pdf
├── sample_pdf_text_a4.pdf
├── sample_pdf_ocr.pdf
└── sample_docx.docx
```

| File                     | Purpose                                                                           |
| ------------------------ | --------------------------------------------------------------------------------- |
| `sample_pdf_text.pdf`    | Text-based PDF used to test normal PDF text extraction. OCR is not required.      |
| `sample_pdf_text_a4.pdf` | Text-based A4 PDF used to test standard PDF text extraction. OCR is not required. |
| `sample_pdf_ocr.pdf`     | Scanned/image-based PDF used to test the OCR fallback path.                       |
| `sample_docx.docx`       | DOCX document used to test Word document extraction.                              |

The PDF ingestion logic first attempts normal text extraction. If the PDF does not contain usable text, the pipeline falls back to OCR.

Therefore, `sample_pdf_ocr.pdf` specifically exercises the **OCR branch of the ingestion algorithm**.

The test-file paths are configured in:

```text
configs/config.yaml
```

If the files are stored somewhere else, update the corresponding paths in `configs/config.yaml` before running the affected tests.

Verify the files with:

```bash
ls -lh data/phase1/
```

You should see:

```text
sample_pdf_text.pdf
sample_pdf_text_a4.pdf
sample_pdf_ocr.pdf
sample_docx.docx
```

---

## 6. Run the Pipelines

The project provides four main pipeline entry points:

### Phase 1 — Document Processing & Retrieval

```bash
python -m pipelines.phase1
```

Extracts documents from `data/raw/`, preprocesses and chunks the text, generates embeddings, and stores document vectors in ChromaDB.

### Annotation

```bash
python -m pipelines.annotation
```

Samples processed document chunks, generates the deterministic annotation dataset, validates it, and prepares the train/validation/test splits.

### Entity Extraction

```bash
python -m pipelines.extraction
```

Runs the hybrid entity-extraction workflow using deterministic rules and a pretrained NER model, merges the extracted entities, and produces structured predictions.

### RAG

```bash
python -m pipelines.rag
```

Runs the Retrieval-Augmented Generation workflow by retrieving relevant document chunks, constructing the context and prompt, and generating answers through the configured LLM client.

The RAG pipeline can use a mocked LLM for local development and testing.

Live LLM execution requires:

* a valid `OPENAI_API_KEY`;
* available API credits.

Do not commit API keys or other credentials to the repository.

---

## 7. Run Tests

The project uses `pytest` for automated testing.

Run the complete test suite:

```bash
python -m pytest
```

Run unit tests:

```bash
python -m pytest tests/unit
```

Run integration tests:

```bash
python -m pytest tests/integration
```

Some integration tests require the local Phase 1 test files described above.

The RAG integration tests can use a mocked LLM, so live OpenAI API access is not required for the automated test suite.

---

# Project Workflow

The four pipelines are organized around the main stages of the project.

```text
Source Documents
       │
       ▼
┌──────────────────────────┐
│ Phase 1                  │
│                          │
│ Ingestion                │
│ Preprocessing            │
│ Chunking                 │
│ Embeddings               │
│ ChromaDB                 │
└────────────┬─────────────┘
             │
             ├──────────────────────┐
             │                      │
             ▼                      ▼
┌──────────────────────┐  ┌────────────────────────┐
│ Annotation Pipeline  │  │ Extraction Pipeline    │
│                      │  │                        │
│ Sampling             │  │ Rules                  │
│ Weak Annotation      │  │ NER                    │
│ Validation           │  │ Entity Merging         │
└──────────────────────┘  └────────────────────────┘
             │
             ▼
┌──────────────────────────┐
│ RAG Pipeline             │
│                          │
│ Retrieval                │
│ Context Construction     │
│ Prompt Construction      │
│ LLM                      │
│ Answer                   │
└──────────────────────────┘
```

Phase 1 provides the document-processing and semantic-retrieval foundation.

The annotation and extraction pipelines operate on the processed document chunks.

The RAG pipeline uses the retrieval infrastructure to construct context for question answering.

---

# Configuration

Project configuration is stored in:

```text
configs/config.yaml
```

The configuration defines important project paths, including:

```yaml
paths:
  raw_data: data/raw
  processed_data: data/processed
  samples: data/samples
  annotation_data: data/processed/annotation
  extraction_data: data/processed/extraction
```

The ingestion configuration also defines the local test files:

```yaml
ingestion:
  input_directory: data/raw

  test_files:
    pdf: data/phase1/sample_pdf_text_a4.pdf
    docx: data/phase1/sample_docx.docx
    ocr: data/phase1/sample_pdf_ocr.pdf
```

The additional `sample_pdf_text.pdf` fixture is used by the relevant ingestion tests as a normal text-based PDF case.

If the test documents are located elsewhere, update the corresponding configuration paths before running the affected tests.

---

# Phase 1 — Document Processing and Semantic Retrieval

Phase 1 establishes the document-processing and retrieval foundation.

The pipeline performs:

1. Document ingestion
2. Text extraction
3. Preprocessing
4. Chunking
5. Embedding generation
6. ChromaDB storage
7. Semantic retrieval

The main flow is:

```text
Documents
    ↓
Document Extraction
    ↓
Preprocessing
    ↓
Chunking
    ↓
Embeddings
    ↓
ChromaDB
    ↓
Semantic Retrieval
```

The resulting ChromaDB collection is used by later components of the project.

---

# Annotation Pipeline

The annotation pipeline creates the dataset required for entity-extraction development.

The workflow is:

```text
ChromaDB Chunks
      ↓
Sampling
      ↓
Weak / Deterministic Annotation
      ↓
Annotation Dataset
      ↓
Validation
      ↓
Train / Validation / Test Split
```

The current annotation schema contains seven entity types:

```text
PERSON
ORGANIZATION
LOCATION
DATE
MONEY
PERCENTAGE
PRODUCT
```

The annotation dataset is generated automatically using deterministic rules.

Because the annotations are automatically generated, they should be considered a development benchmark rather than independently verified human ground truth.

---

# Entity Extraction Pipeline

The extraction pipeline combines deterministic rules with a pretrained NER model.

The workflow is:

```text
Document Chunks
      │
      ├───────────────┐
      ▼               ▼
Rule-Based        NER Model
Extraction        Extraction
      │               │
      └───────┬───────┘
              ▼
      Entity Merging
              ↓
      Structured Entities
              ↓
          Evaluation
```

The final entity representation contains:

```python
ExtractedEntity(
    text,
    label,
    start,
    end,
    confidence,
    chunk_id,
    document_id,
    page_start,
    page_end,
)
```

The extraction pipeline produces structured JSONL predictions under:

```text
data/processed/extraction/
```

The NER baseline was selected by comparing several pretrained NER models on the project's development benchmark.

The benchmark is based on automatically generated annotations and therefore measures consistency with the project's annotation rules rather than independently verified semantic accuracy.

---

**# RAG Pipeline**

The RAG pipeline extends semantic retrieval into question answering by combining vector search, context construction, prompt generation, and LLM-based answer generation.

The complete pipeline is:

```text
Question
   ↓
Retriever
   ↓
ContextBuilder
   ↓
PromptBuilder
   ↓
LLMClient
   ↓
Answer
```

The executable entry point is:

```text
pipelines/rag.py
```

Internally, the pipeline is built from independent components under `src/rag/`:

```text
src/rag/

├── retriever.py
│   └── Retrieves relevant document chunks from ChromaDB
│
├── context_builder.py
│   └── Builds the context supplied to the language model
│
├── prompt_templates.py
│   └── Builds the question-answering prompt
│
├── llm_client.py
│   └── Sends the prompt to the OpenAI Responses API
│
├── rag_chain.py
│   └── Connects retrieval, context construction, prompting,
│       and LLM generation into a reusable RAG chain
│
└── evaluation_summary.py
    └── Summarizes the manual RAG evaluation results
```

The batch pipeline loads evaluation questions, retrieves the most relevant chunks from ChromaDB, builds the context and prompt, generates an answer through the LLM client, and stores the resulting outputs for evaluation.

For live answer generation, the pipeline requires an `OPENAI_API_KEY` with available API credits. The API key is loaded from the environment and is not stored in the repository.

The RAG unit and integration tests use a mock LLM, so the RAG chain can be tested without an OpenAI API key or API credits.

## Retriever

Retrieves relevant document chunks from ChromaDB.

## ContextBuilder

Combines retrieved chunks into the context provided to the LLM.

## PromptBuilder

Constructs the question-answering prompt.

## LLMClient

Provides the interface to the external LLM service.

## RAGChain

Connects retrieval, context construction, prompt construction, and LLM execution for a single question.

## RAGPipeline

Provides batch processing for evaluation questions.

---

# OpenAI Configuration

The live RAG pipeline uses the OpenAI Responses API.

Set the API key through an environment variable:

```bash
export OPENAI_API_KEY="your-api-key"
```

Do not commit API keys to the repository.

The `.env` file is ignored by Git.

For local development and automated tests, the RAG architecture can operate with a mocked LLM, so live API access is not required for the test suite.

---

# Testing

The project contains both unit and integration tests.

## Unit Tests

Unit tests cover individual components such as:

* document ingestion;
* preprocessing;
* embeddings;
* vector-store operations;
* entity extraction;
* NER processing;
* retrieval;
* context construction;
* prompt construction;
* RAG chain behavior.

Run them with:

```bash
python -m pytest tests/unit
```

---

## Integration Tests

Integration tests verify how multiple project components work together.

For example, the RAG integration test connects:

```text
EmbeddingPipeline
      ↓
ChromaDB
      ↓
Retriever
      ↓
ContextBuilder
      ↓
PromptBuilder
      ↓
Mock LLM
```

Run integration tests with:

```bash
python -m pytest tests/integration
```

Some integration tests require local sample documents and configured data paths.

---

# Evaluation

The project contains evaluation workflows for both entity extraction and RAG.

## Entity Extraction Evaluation

Phase 2 evaluates:

* Precision
* Recall
* F1 score
* per-label performance
* strict entity matching
* error analysis

The current benchmark uses automatically generated annotations.

Therefore, the results measure consistency against the project's annotation rules and should not be interpreted as independent human-verified semantic accuracy.

---

## RAG Evaluation

Phase 3 includes a manually evaluated set of 15 questions.

The evaluation considers:

* whether the retrieved context is sufficient;
* answer correctness;
* answer grounding.

Initial manual results:

```text
Answerable from context : 11 / 15
Correct answers          : 14 / 15
Grounded answers         : 15 / 15
```

This is a small development baseline rather than a statistically representative benchmark.

---

# Data and Generated Files

The project separates source data, generated data, test fixtures, and evaluation artifacts.

```text
data/
├── raw/             Source documents
├── processed/       Generated processing results
├── samples/         Sample data
├── phase1/          Local Phase 1 test fixtures
└── evaluation/      Evaluation questions and results
```

Tracked evaluation files include:

```text
data/evaluation/questions.jsonl
data/evaluation/manually_evaluated_results.jsonl
```

Generated evaluation artifacts are excluded from version control where appropriate.

Large datasets, vector databases, models, logs, temporary files, and secrets are also excluded from Git.

---

# Project Structure

The main repository structure is:

```text
.
├── configs/
│   └── config.yaml
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── samples/
│   ├── phase1/
│   └── evaluation/
│
├── docs/
│   └── annotation_guidelines.md
│
├── pipelines/
│   ├── phase1.py
│   ├── annotation.py
│   ├── extraction.py
│   └── rag.py
│
├── reports/
│   ├── phase1_report.md
│   ├── phase2_report.md
│   └── phase3_report.md
│
├── src/
│   ├── annotation/
│   ├── embeddings/
│   ├── extraction/
│   ├── ingestion/
│   ├── preprocessing/
│   ├── rag/
│   └── vectorstore/
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

The pipeline entry points are intentionally kept separate from the reusable implementation modules under `src/`.

---

# Documentation

Detailed technical information is available in the phase reports.

* [Phase 1 Report](reports/phase1_report.md) — document processing and semantic retrieval
* [Phase 2 Report](reports/phase2_report.md) — annotation and hybrid entity extraction
* [Phase 3 Report](reports/phase3_report.md) — RAG generation, orchestration, and evaluation
* [Annotation Guidelines](docs/annotation_guidelines.md) — entity schema and annotation rules

The README focuses on **using and running the project**. The reports contain the detailed technical methodology and development history.

---

# Current Status

```text
Phase 1 — Document Processing & Retrieval    Complete
Phase 2 — Annotation & Entity Extraction    Complete
Phase 3 — RAG & Evaluation                   Complete
```

The current implementation provides an end-to-end workflow:

```text
Documents
    ↓
Processing
    ↓
Embeddings
    ↓
ChromaDB
    ↓
Retrieval
    ↓
Context
    ↓
Prompt
    ↓
LLM
    ↓
Answer
```

The entity-extraction workflow operates alongside the retrieval pipeline:

```text
Document Chunks
      ↓
Rule-Based Extraction + NER
      ↓
Entity Merging
      ↓
Structured Entities
```

Live LLM execution depends on external API access. Local testing is supported through the mocked LLM path.

---

# Future Improvements

Future work is focused on improving the existing implementation rather than adding another major project phase.

Possible improvements include:

* retrieval-quality optimization;
* improved table extraction;
* independently verified entity annotations;
* larger RAG evaluation datasets;
* automated evaluation;
* source and page attribution;
* stronger API error handling;
* systematic LLM comparison;
* live LLM benchmarking when API access is available.
