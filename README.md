# intelligent-document-analysis

A modular document processing pipeline for extracting, preprocessing, and structuring content from heterogeneous documents for downstream NLP, semantic search, knowledge extraction, and retrieval-augmented generation (RAG) workflows.

> **Status:** Document ingestion and OCR pipeline implemented. PDF text extraction, DOCX parsing, scanned-PDF OCR, structured OCR output, and ingestion tests are currently available.

---

## Overview

Documents frequently exist in different formats and may contain either directly accessible text or scanned images requiring OCR before further processing.

This project provides a modular ingestion layer designed to handle these different document types and prepare their contents for subsequent processing stages.

The current pipeline supports:

* PDF text extraction
* DOCX text extraction
* OCR-based extraction from scanned PDFs
* Page-level and paragraph-level structured output
* JSON serialization of OCR results
* Automated ingestion tests
* Local processing with no external AI API dependency

The project is being developed incrementally, with document ingestion serving as the foundation for later preprocessing, embedding generation, vector storage, information extraction, and RAG components.

---

## Processing Pipeline

```text
                    Document Sources
                          │
              ┌───────────┼───────────┐
              │           │           │
             PDF         DOCX       Scanned PDF
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
                    Preprocessing
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

The current implementation covers the document ingestion layer and the beginning of the OCR workflow.

---

## Project Structure

```text
intelligent-document-analysis/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── docker/
│   └── Dockerfile
│
├── data/
│   ├── raw/
│   │   ├── docx/
│   │   ├── images/
│   │   └── pdf/
│   ├── processed/
│   └── samples/
│
├── src/
│   ├── __init__.py
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   └── ocr_engine.py
│   │
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   ├── cleaner.py
│   │   └── chunker.py
│   │
│   ├── embeddings/
│   │   ├── __init__.py
│   │   └── embedding_pipeline.py
│   │
│   ├── vectorstore/
│   │   ├── __init__.py
│   │   └── chroma_store.py
│   │
│   ├── extraction/
│   │   ├── __init__.py
│   │   ├── ner_model.py
│   │   └── classifier.py
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── rag_chain.py
│   │   └── prompt_templates.py
│   │
│   └── monitoring/
│       ├── __init__.py
│       └── metrics.py
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_preprocessing_experiments.ipynb
│   ├── 03_embedding_evaluation.ipynb
│   └── 04_rag_evaluation.ipynb
│
├── tests/
│   ├── test_ingestion.py
│   ├── test_preprocessing.py
│   ├── test_embeddings.py
│   └── test_vectorstore.py
│
├── mlflow/
│   └── mlruns/
│
├── configs/
│   └── config.yaml
│
└── reports/
    ├── task1_report.md
    ├── task2_report.md
    ├── task3_report.md
    └── task4_report.md
```

---

## Tech Stack

| Layer               | Tools                        |
| ------------------- | ---------------------------- |
| Language            | Python 3.12                  |
| PDF processing      | PyMuPDF                      |
| DOCX processing     | python-docx                  |
| Image processing    | Pillow                       |
| OCR                 | Tesseract OCR + pytesseract  |
| Testing             | pytest                       |
| Configuration       | YAML / environment variables |
| Experiment tracking | MLflow                       |
| Vector database     | ChromaDB                     |
| Containerisation    | Docker                       |

> The current implementation only requires the dependencies needed for document ingestion and OCR. Additional components will be introduced as their corresponding pipeline stages are implemented.

---

## Environment Setup

### 1. Create the virtual environment

From the project root:

```bash
python3 -m venv .venv
```

Activate the environment:

```bash
source .venv/bin/activate
```

Verify the active Python interpreter:

```bash
which python
python --version
pip --version
```

The Python interpreter should point to the project's virtual environment:

```text
/home/satar/ida/.venv/bin/python
```

---

### 2. Install Python dependencies

Install the dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Current dependencies include:

```text
PyMuPDF==1.28.0
python-docx==1.2.0
pillow==12.3.0
pytesseract==0.3.13
```

---

### 3. Install Tesseract OCR

Tesseract is a system-level dependency and is therefore not installed through `requirements.txt`.

On Ubuntu:

```bash
sudo apt install tesseract-ocr
```

Verify the installation:

```bash
tesseract --version
```

The Python package `pytesseract` acts as a Python interface to the Tesseract executable. The actual OCR engine is provided by the system-level Tesseract installation.

---

## Document Ingestion

The ingestion layer provides separate parsers for different document types.

```text
src/ingestion/
├── pdf_parser.py
├── docx_parser.py
└── ocr_engine.py
```

Each component exposes reusable functions and receives input paths externally rather than relying on hardcoded document locations.

---

## PDF Text Extraction

Digital PDFs containing an accessible text layer can be processed using the PDF parser.

```python
from src.ingestion.pdf_parser import extract_pdf_text

pages = extract_pdf_text(
    "data/raw/pdf/document.pdf"
)
```

The extracted content is represented at page level, preserving the relationship between the extracted text and its original PDF page.

Example output:

```python
[
    {
        "page_number": 1,
        "text": "Document content..."
    },
    {
        "page_number": 2,
        "text": "Additional content..."
    }
]
```

---

## DOCX Text Extraction

DOCX documents can be processed using the DOCX parser:

```python
from src.ingestion.docx_parser import extract_docx_text

paragraphs = extract_docx_text(
    "data/raw/docx/document.docx"
)
```

The extracted content is returned as structured paragraph-level records.

This allows the original paragraph boundaries to remain available for subsequent preprocessing.

---

## OCR for Scanned PDFs

Some PDF documents contain scanned pages rather than an accessible text layer. In these cases, OCR is required.

The OCR pipeline uses:

* PyMuPDF to open and render PDF pages
* 300 DPI rendering for OCR input
* Pillow for image handling
* pytesseract as the Python interface
* Tesseract OCR as the underlying OCR engine

The pipeline is:

```text
Scanned PDF
     │
     ▼
PyMuPDF
     │
     ▼
Render page at 300 DPI
     │
     ▼
Pillow Image
     │
     ▼
pytesseract
     │
     ▼
Tesseract OCR
     │
     ▼
Extracted Text
```

Run OCR on a PDF:

```python
from src.ingestion.ocr_engine import extract_ocr_text

pages = extract_ocr_text(
    "data/raw/pdf/scanned-document.pdf"
)
```

The function returns page-level OCR results:

```python
[
    {
        "page_number": 1,
        "text": "Extracted OCR text..."
    },
    {
        "page_number": 2,
        "text": "More extracted text..."
    }
]
```

Pages where OCR does not recognize any text are still represented in the output with an empty string:

```python
{
    "page_number": 2,
    "text": ""
}
```

This preserves the document's page structure without assuming that every page must contain recognizable text.

---

## Development and Limited-Page OCR

OCR can be computationally expensive, particularly for large scanned documents.

The OCR function therefore supports an optional `max_pages` parameter for development and testing:

```python
from src.ingestion.ocr_engine import extract_ocr_text

pages = extract_ocr_text(
    "data/raw/pdf/scanned-document.pdf",
    max_pages=3,
)
```

This processes only the first three pages.

To process the complete document, omit the parameter:

```python
pages = extract_ocr_text(
    "data/raw/pdf/scanned-document.pdf"
)
```

This allows small subsets of large documents to be used during development without repeatedly processing the entire document.

---

## Saving OCR Results

OCR results can be serialized as structured JSON:

```python
from src.ingestion.ocr_engine import (
    extract_ocr_text,
    save_ocr_results,
)

pages = extract_ocr_text(
    "data/raw/pdf/scanned-document.pdf",
    max_pages=3,
)

save_ocr_results(
    pages,
    "data/processed/ocr_output.json",
)
```

The resulting JSON structure is page-based:

```json
[
  {
    "page_number": 1,
    "text": "Extracted text..."
  },
  {
    "page_number": 2,
    "text": "Additional extracted text..."
  }
]
```

The generated output is stored separately from the original source documents:

```text
data/
├── raw/
│   ├── docx/
│   ├── images/
│   └── pdf/
│
└── processed/
    └── ocr_output.json
```

---

## Testing

The project uses pytest for automated testing.

Run the complete ingestion test suite:

```bash
python -m pytest -v tests/test_ingestion.py
```

Run only OCR-related tests:

```bash
python -m pytest -v tests/test_ingestion.py -k ocr
```

The OCR tests validate the output structure rather than requiring every page to contain recognized text.

For example, the tests verify that:

* OCR returns a list of page records.
* The expected number of pages is returned.
* Page numbers are sequential.
* Each result contains a `text` key.
* The `text` value is a string.

An empty OCR result is considered valid:

```python
{
    "page_number": 5,
    "text": ""
}
```

This is important because a document may contain blank pages, image-only pages, or pages where OCR cannot successfully recognize the content.

---

## Data Organization

Input documents are stored under:

```text
data/raw/
```

The current raw data layout is:

```text
data/raw/
├── docx/
├── images/
└── pdf/
```

Processed outputs are stored under:

```text
data/processed/
```

Sample files used for development and testing are stored under:

```text
data/samples/
```

Keeping raw inputs and processed outputs separate provides a clear boundary between source documents and generated artifacts.

---

## Configuration

The project contains a dedicated configuration directory:

```text
configs/
└── config.yaml
```

At the current stage, reusable ingestion functions receive paths as arguments rather than embedding specific file paths directly into the implementation.

For example:

```python
def extract_ocr_text(
    pdf_path,
    max_pages=None,
):
    ...
```

This allows the same function to process different documents without modification.

Centralized configuration will be introduced as the pipeline grows and shared parameters become necessary across multiple components.

---

## Development Principles

The project is being developed incrementally around several principles:

* **Modularity** — document formats are handled by separate ingestion components.
* **Reusability** — processing functions accept external paths and parameters.
* **Testability** — ingestion components are covered by automated tests.
* **Separation of concerns** — parsing, preprocessing, embeddings, storage, and retrieval remain separate pipeline stages.
* **Local-first processing** — the current ingestion and OCR pipeline does not depend on external AI APIs.
* **Incremental complexity** — components are introduced when they are required rather than adding unnecessary infrastructure prematurely.

---

## Current Implementation Status

| Component                   | Status      |
| --------------------------- | ----------- |
| Project structure           | Implemented |
| Python virtual environment  | Implemented |
| PDF text extraction         | Implemented |
| DOCX text extraction        | Implemented |
| Tesseract OCR integration   | Implemented |
| Scanned PDF OCR             | Implemented |
| Limited-page OCR processing | Implemented |
| Structured OCR output       | Implemented |
| OCR JSON serialization      | Implemented |
| Ingestion tests             | Implemented |
| Text preprocessing          | Planned     |
| Text chunking               | Planned     |
| Embedding pipeline          | Planned     |
| Vector database integration | Planned     |
| Information extraction      | Planned     |
| RAG pipeline                | Planned     |
| Monitoring                  | Planned     |

---

## Roadmap

### Document Processing

* [ ] Text cleaning and normalization
* [ ] Document chunking
* [ ] Metadata preservation
* [ ] Improved OCR preprocessing

### Semantic Representation

* [ ] Embedding generation
* [ ] Embedding evaluation
* [ ] Vector database integration
* [ ] Document retrieval

### Information Extraction

* [ ] Named Entity Recognition
* [ ] Document classification
* [ ] Structured information extraction

### Retrieval-Augmented Generation

* [ ] RAG pipeline
* [ ] Prompt templates
* [ ] Retrieval evaluation
* [ ] RAG quality evaluation

### Engineering

* [ ] Expanded automated test coverage
* [ ] MLflow experiment tracking
* [ ] Containerized execution
* [ ] Monitoring and evaluation metrics

---

## License

This project is open for educational and portfolio use.
