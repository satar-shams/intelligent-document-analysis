# Phase 3 — RAG Generation, Orchestration, and Evaluation

## 1. Purpose

Phase 3 extends the IDA system from **document retrieval and information extraction** to a complete **Retrieval-Augmented Generation (RAG)** pipeline.

The objective is to allow a user to submit a natural-language question and receive an answer generated from the indexed annual-report documents.

The complete process is:

```text
User Question
      ↓
Question Processing
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
      ↓
Persisted Result
```

For evaluation, the same pipeline can process multiple predefined questions.

---

# 2. Phase 3 Architecture

The main RAG components are:

```text
src/rag/
├── retriever.py
├── context_builder.py
├── prompt_templates.py
├── llm_client.py
├── rag_chain.py
├── rag_pipeline.py
└── evaluation_summary.py
```

The responsibilities are:

| Component            | Responsibility                                |
| -------------------- | --------------------------------------------- |
| `Retriever`          | Retrieves relevant chunks from ChromaDB       |
| `ContextBuilder`     | Converts retrieval results into LLM context   |
| `PromptBuilder`      | Creates the final prompt                      |
| `LLMClient`          | Communicates with the external language model |
| `RAGChain`           | Orchestrates a single question                |
| `RAGPipeline`        | Processes multiple questions sequentially     |
| `evaluation_summary` | Summarizes manually evaluated results         |

---

# 3. Single-Question RAG Flow

For a single question, the pipeline is:

```text
Query
  ↓
Retriever
  ↓
Search Results
  ↓
ContextBuilder
  ↓
Context
  ↓
PromptBuilder
  ↓
Prompt
  ↓
LLMClient
  ↓
Answer
```

For example, the input query may be:

```text
What was the revenue allocated to remaining performance obligations as of June 30, 2025?
```

---

# 4. Retriever

## 4.1 Input

The retriever receives:

```python
search_results = retriever.retrieve(
    query=query,
    top_k=10,
)
```

Example:

```text
query = "What was the revenue allocated to remaining performance obligations as of June 30, 2025?"
top_k = 10
```

## 4.2 Output

The retriever returns a collection of search results.

A result contains information such as:

```text
chunk_id
document_id
page_start
page_end
distance
text
```

Example:

```text
chunk_id: 12353
document_id: 2025_AnnualReport
page_start: 718
page_end: 718
distance: 0.3542
text:
Revenue allocated to remaining performance obligations,
which includes unearned revenue and amounts that will be
invoiced and recognized as revenue in future periods,
was $375 billion as of June 30, 2025...
```

The retrieved chunks are then passed to `ContextBuilder`.

---

# 5. ContextBuilder

## 5.1 Purpose

The retriever returns structured search-result objects.

The LLM needs a text representation.

`ContextBuilder` converts the search results into a single context string.

## 5.2 Input

```python
context = context_builder.build(
    search_results=search_results,
)
```

Input example:

```text
[
    SearchResult(
        chunk_id="12353",
        document_id="2025_AnnualReport",
        page_start=718,
        page_end=718,
        text="Revenue allocated..."
    ),
    ...
]
```

## 5.3 Output

Example generated context:

```text
chunk_id: 12353
document_id: 2025_AnnualReport
page_start: 718
page_end: 718
text: Revenue allocated to remaining performance obligations,
which includes unearned revenue and amounts that will be invoiced
and recognized as revenue in future periods, was $375 billion as
of June 30, 2025, of which $368 billion is related to the
commercial portion of revenue. ...

chunk_id: 11476
document_id: 2024_Annual_Report
page_start: 875
page_end: 875
text: Revenue allocated to remaining performance obligations ...
```

The important point is that the context preserves both:

```text
document information
+
textual evidence
```

---

# 6. PromptBuilder

## 6.1 Purpose

The `PromptBuilder` combines:

1. Instruction
2. Retrieved context
3. User question

The current instruction is:

```text
Answer the question using only the provided context.
Do not add or invent information that is not supported by
the context. If the context does not contain enough information
to answer the question, say that the available context does
not provide enough information.
```

## 6.2 Input

Example:

```python
prompt = prompt_builder.build(
    instruction=instruction,
    context=context,
    query=query,
)
```

The inputs are:

```text
Instruction:
Answer the question using only the provided context...

Context:
chunk_id: 12353
document_id: 2025_AnnualReport
...

Question:
What was the revenue allocated to remaining performance obligations
as of June 30, 2025?
```

## 6.3 Output

The final prompt becomes one string:

```text
Instruction:
Answer the question using only the provided context. Do not add
or invent information that is not supported by the context. If
the context does not contain enough information to answer the
question, say that the available context does not provide enough
information.

Context:
chunk_id: 12353
document_id: 2025_AnnualReport
page_start: 718
page_end: 718
text: Revenue allocated to remaining performance obligations...
was $375 billion as of June 30, 2025...

Question:
What was the revenue allocated to remaining performance obligations
as of June 30, 2025?
```

This exact prompt is what is eventually sent to the LLM.

---

# 7. LLMClient

## 7.1 Purpose

`LLMClient` provides a small abstraction around the external LLM API.

The RAG system does not need to know the implementation details of the API.

It only needs:

```python
answer = llm_client.generate(
    prompt=prompt,
)
```

## 7.2 Input

The LLM receives the complete prompt created by `PromptBuilder`.

Example:

```text
Instruction:
...

Context:
...

Question:
What was the revenue allocated to remaining performance obligations
as of June 30, 2025?
```

## 7.3 Output

The expected output is a string.

Example:

```text
The revenue allocated to remaining performance obligations
as of June 30, 2025 was $375 billion.
```

## 7.4 OpenAI implementation

The current implementation uses the OpenAI Responses API.

The API key is loaded from the environment:

```text
OPENAI_API_KEY=...
```

The key is not stored in the source code.

The client conceptually performs:

```text
prompt
   ↓
OpenAI Responses API
   ↓
response.output_text
   ↓
answer
```

At the moment, live API execution is unavailable because the API account has no remaining credits.

---

# 8. RAGChain

## 8.1 Purpose

`RAGChain` coordinates the individual components for one question.

The class receives its dependencies through dependency injection:

```python
RAGChain(
    retriever=retriever,
    context_builder=context_builder,
    prompt_builder=prompt_builder,
    llm_client=llm_client,
)
```

This means `RAGChain` does not create these objects itself.

## 8.2 Input

```python
query = "What was the revenue allocated to remaining performance obligations as of June 30, 2025?"
```

and:

```python
top_k = 10
```

## 8.3 Internal processing

```text
query
  ↓
retriever.retrieve()
  ↓
search_results
  ↓
context_builder.build()
  ↓
context
  ↓
prompt_builder.build()
  ↓
prompt
  ↓
llm_client.generate()
  ↓
answer
```

## 8.4 Output

```python
answer = rag_chain.run(
    query=query,
    top_k=10,
)
```

Example:

```text
The revenue allocated to remaining performance obligations
as of June 30, 2025 was $375 billion.
```

---

# 9. Batch RAG Pipeline

`RAGPipeline` extends the single-question workflow to multiple questions.

This is useful for:

* evaluation
* batch experiments
* offline testing
* future automated benchmarking

The input is a JSONL file.

---

# 10. Evaluation Input

The evaluation questions are stored in:

```text
data/evaluation/questions.jsonl
```

Each line represents one independent question.

Example:

```json
{"id":1,"query":"What was the total revenue in fiscal year 2025?"}
{"id":2,"query":"What was the total revenue in fiscal year 2024?"}
{"id":3,"query":"How did revenue in fiscal year 2025 compare with fiscal year 2024?"}
```

JSONL is used because each question is an independent record.

---

# 11. Question Preprocessing

The pipeline reads the file line by line.

For each record, it checks:

```text
id exists
query exists
query is a string
query is not empty
```

The query is also stripped of surrounding whitespace.

Example input:

```json
{"id":1,"query":"  What was the total revenue in fiscal year 2025?  "}
```

becomes:

```json
{"id":1,"query":"What was the total revenue in fiscal year 2025?"}
```

The processed questions are stored in:

```text
data/evaluation/preprocessed_questions.jsonl
```

---

# 12. Batch Prompt Generation

For every question, the batch pipeline performs the normal RAG process.

Example:

```text
Question 1
    ↓
Retriever
    ↓
Context
    ↓
PromptBuilder
    ↓
Prompt 1
```

Then:

```text
Question 2
    ↓
Retriever
    ↓
Context
    ↓
PromptBuilder
    ↓
Prompt 2
```

and so on.

The questions are processed independently.

---

# 13. Prompt Storage

Generated prompts are stored in:

```text
data/evaluation/prompts.jsonl
```

Example record:

```json
{
  "id": 4,
  "query": "What was the revenue allocated to remaining performance obligations as of June 30, 2025?",
  "top_k": 10,
  "prompt": "Instruction:\n...\nContext:\n...\nQuestion:\n...",
  "retrieved_results": [
    {
      "rank": 1,
      "chunk_id": "12353",
      "document_id": "2025_AnnualReport",
      "page_start": 718,
      "page_end": 718,
      "distance": 0.3542
    }
  ]
}
```

This file provides a record of **what the RAG system actually prepared for the LLM**.

---

# 14. LLM Execution

When the API is available, the same generated prompt is passed to:

```python
llm_client.generate(
    prompt=prompt,
)
```

The process becomes:

```text
prompts.jsonl
      ↓
read one prompt
      ↓
LLMClient
      ↓
OpenAI
      ↓
answer
```

Each question is handled independently.

Example:

```text
Prompt 1
   ↓
LLM
   ↓
Answer 1

Prompt 2
   ↓
LLM
   ↓
Answer 2
```

---

# 15. Result Storage

The live RAG pipeline stores future LLM outputs separately from the manual evaluation baseline.

Recommended output:

```text
data/evaluation/llm_results.jsonl
```

Example:

```json
{
  "id": 4,
  "query": "What was the revenue allocated to remaining performance obligations as of June 30, 2025?",
  "answer": "The revenue allocated to remaining performance obligations as of June 30, 2025 was $375 billion.",
  "retrieved_results": [
    {
      "rank": 1,
      "chunk_id": "12353",
      "document_id": "2025_AnnualReport",
      "page_start": 718,
      "page_end": 718,
      "distance": 0.3542
    }
  ]
}
```

The live result file contains system output.

It does not determine whether the answer is correct.

---

# 16. Manual Evaluation

Because the external LLM API is currently unavailable, a manual evaluation was performed using ChatGPT.

The generated prompts were copied into independent ChatGPT conversations.

The resulting answers were manually reviewed against the retrieved context.

The manual evaluation file is:

```text
data/evaluation/manually_evaluated_results.jsonl
```

It contains fields such as:

```text
id
query
answer
evaluation.answerable_from_context
evaluation.correct
evaluation.grounded
evaluation.notes
```

Example:

```json
{
  "id": 4,
  "query": "What was the revenue allocated to remaining performance obligations as of June 30, 2025?",
  "answer": "The revenue allocated to remaining performance obligations as of June 30, 2025 was $375 billion.",
  "evaluation": {
    "answerable_from_context": true,
    "correct": true,
    "grounded": true,
    "notes": ""
  }
}
```

---

# 17. Meaning of Evaluation Fields

## `answerable_from_context`

This asks:

> Does the retrieved context contain enough information to answer the question?

Example:

```text
Question:
What was the total revenue in fiscal year 2025?

Context:
Only contains fiscal-year comparison headings.
No 2025 revenue value.
```

Result:

```json
"answerable_from_context": false
```

---

## `correct`

This asks:

> Did the generated answer correctly answer the question?

This was manually judged against the available context.

A strict interpretation was used.

For example, the context says:

```text
over $245 billion
```

while the answer says:

```text
$245 billion
```

The answer loses the qualification "over", so it was considered not fully precise.

---

## `grounded`

This asks:

> Is the answer supported by the provided context rather than unsupported external information?

For the current baseline, all 15 manually reviewed answers were judged grounded.

---

# 18. Current Manual Evaluation Dataset

The initial evaluation set contains 15 questions covering:

```text
Direct factual questions
Numeric questions
Historical questions
Comparison questions
Percentage calculations
Questions involving remaining performance obligations
Questions where the necessary information is absent
```

Examples include:

```text
What was the total revenue in fiscal year 2025?

What was the total revenue in fiscal year 2024?

How did revenue in fiscal year 2025 compare with fiscal year 2024?

What was the revenue allocated to remaining performance obligations
as of June 30, 2025?

What was the revenue allocated to remaining performance obligations
as of June 30, 2023?

What percentage of the 2022 revenue allocated to remaining
performance obligations was related to the commercial portion
of revenue?
```

---

# 19. Initial Evaluation Results

The manual evaluation produced:

```text
Total cases             : 15
Answerable from context : 11
Not answerable          : 4
Correct answers         : 14
Incorrect answers       : 1
Grounded answers        : 15
Not grounded            : 0
```

As percentages:

```text
Answerable from context : 73.3%
Not answerable          : 26.7%

Correct answers         : 93.3%
Incorrect answers       : 6.7%

Grounded answers        : 100.0%
Not grounded            : 0.0%
```

These numbers are a **manual baseline**, not a formal scientific benchmark.

---

# 20. Example of a Successful Case

### Query

```text
What was the revenue allocated to remaining performance obligations
as of June 30, 2025?
```

### Retrieved context

```text
Revenue allocated to remaining performance obligations,
which includes unearned revenue and amounts that will be
invoiced and recognized as revenue in future periods,
was $375 billion as of June 30, 2025...
```

### Prompt

```text
Instruction:
Answer the question using only the provided context...

Context:
...
$375 billion as of June 30, 2025...

Question:
What was the revenue allocated to remaining performance obligations
as of June 30, 2025?
```

### Answer

```text
The revenue allocated to remaining performance obligations
as of June 30, 2025 was $375 billion.
```

### Evaluation

```text
answerable_from_context = true
correct                 = true
grounded                = true
```

---

# 21. Example of an Unanswerable Case

### Query

```text
What was the total revenue in fiscal year 2025?
```

### Retrieved context

Several retrieved chunks contain:

```text
Fiscal Year 2025 Compared with Fiscal Year 2024
```

but do not contain the actual 2025 revenue figure.

### LLM Answer

```text
The available context does not provide enough information
to determine the total revenue in fiscal year 2025.
```

### Evaluation

```text
answerable_from_context = false
correct                 = true
grounded                = true
```

This is an important RAG behavior because the model follows the instruction not to invent information.

---

# 22. Example of a Calculation Case

### Query

```text
How did the revenue allocated to remaining performance obligations
change from 2021 to 2022?
```

### Retrieved evidence

```text
2021: $146 billion

2022: $193 billion
```

### Answer

```text
The revenue allocated to remaining performance obligations increased
from $146 billion in 2021 to $193 billion in 2022, an increase of
$47 billion, or approximately 32.2%.
```

The percentage is:

```text
(193 - 146) / 146 × 100
≈ 32.2%
```

The answer is therefore evaluated as correct and grounded.

---

# 23. Retrieval Limitation Observed

The current system sometimes retrieves semantically related information without retrieving the exact evidence required.

For example, a query about:

```text
total fiscal-year-2025 revenue
```

may retrieve multiple chunks containing:

```text
Fiscal Year 2025 Compared with Fiscal Year 2024
```

but not the specific revenue figure.

This means:

```text
Retrieval failure
      ↓
Insufficient context
      ↓
LLM cannot reliably answer
```

This is currently treated as a known limitation.

Improving retrieval quality is intentionally deferred to a later iteration.

---

# 24. Testing

Phase 3 contains lightweight tests around the implemented components.

Current test structure:

```text
tests/
├── unit/
│   └── rag/
│       ├── test_prompt_templates.py
│       └── test_mock_llm.py
│
└── integration/
    └── test_rag_chain.py
```

The integration test uses the real retrieval stack:

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

The real LLM API is intentionally not required for the current integration test.

---

# 25. Environment Configuration

The OpenAI API key is not stored in source code.

The local `.env` file contains:

```text
OPENAI_API_KEY=your_api_key
```

and `.env` is excluded from Git.

The expected flow is:

```text
.env
 ↓
environment variable
 ↓
LLMClient
 ↓
OpenAI client
```

The previously exposed API credential should not be reused and should be revoked.

---

# 26. Current File Structure

A simplified project structure for Phase 3 is:

```text
ida/
│
├── data/
│   └── evaluation/
│       ├── questions.jsonl
│       ├── preprocessed_questions.jsonl
│       ├── prompts.jsonl
│       ├── manually_evaluated_results.jsonl
│       ├── llm_results.jsonl
│       └── retrieval_review.txt
│
├── src/
│   └── rag/
│       ├── context_builder.py
│       ├── evaluation_summary.py
│       ├── llm_client.py
│       ├── prompt_templates.py
│       ├── rag_chain.py
│       ├── rag_pipeline.py
│       └── retriever.py
│
└── tests/
    ├── unit/
    │   └── rag/
    │       ├── test_mock_llm.py
    │       └── test_prompt_templates.py
    │
    └── integration/
        └── test_rag_chain.py
```

---

# 27. Execution Examples

## Single-question chain

```bash
python -m src.rag.rag_chain
```

For the current development setup, a mock LLM is used.

Example output:

```text
RAG CHAIN TEST

Query: 2025 revenue
Top K: 10

GENERATED ANSWER
----------------
FAKE ANSWER
```

---

## Generate evaluation prompts

```bash
python -m src.evaluation.prepare_prompts
```

Example output:

```text
RAG EVALUATION PROMPT PREPARATION

Input questions       : data/evaluation/questions.jsonl
Processed questions   : data/evaluation/preprocessed_questions.jsonl
Generated prompts     : data/evaluation/prompts.jsonl
Number of questions   : 15
Top K                 : 10
```

---

## Run evaluation summary

```bash
python -m src.rag.evaluation_summary
```

Example output:

```text
RAG EVALUATION SUMMARY
================================================================================
Total cases             : 15
Answerable from context : 11 (73.3%)
Not answerable          : 4 (26.7%)
Correct answers         : 14 (93.3%)
Incorrect answers       : 1 (6.7%)
Grounded answers        : 15 (100.0%)
Not grounded            : 0 (0.0%)
```

---

# 28. API Availability

The complete API integration is implemented in the codebase, but live execution is currently unavailable because the OpenAI account has exhausted its available API credits.

The intended future execution is:

```text
questions.jsonl
      ↓
RAGPipeline
      ↓
Retriever
      ↓
ContextBuilder
      ↓
PromptBuilder
      ↓
LLMClient
      ↓
OpenAI API
      ↓
Answer
      ↓
llm_results.jsonl
```

When API access becomes available, the same pipeline can be executed without redesigning the RAG architecture.

---

# 29. Future Improvements

The following work is intentionally deferred:

### Retrieval

Improve ranking and retrieval quality for broad factual questions.

### Tables

Improve extraction and retrieval of table contents from annual reports.

### Evaluation

Increase the number of evaluation questions and automate more of the evaluation process.

### LLM Evaluation

Compare different models and measure answer quality systematically.

### Source Attribution

Expose document and page references with generated answers.

### Production Reliability

Improve handling of:

* API failures
* rate limits
* timeouts
* empty results
* malformed responses

---

# 30. Phase 3 Completion Status

```text
✅ RAG retrieval integration
✅ Context construction
✅ Prompt construction
✅ OpenAI client
✅ Dependency injection
✅ Single-question RAGChain
✅ Batch RAGPipeline
✅ Prompt persistence
✅ Result persistence
✅ Manual evaluation
✅ Evaluation summary
✅ Integration testing
✅ Environment-based API configuration

⚠️ Live API execution
   Blocked by API credit availability

🔜 Retrieval optimization
   Deferred

🔜 Larger-scale evaluation
   Deferred
```

Phase 3 establishes a complete RAG generation pipeline on top of the existing IDA retrieval infrastructure. The current implementation is sufficient as a working baseline, while retrieval optimization and large-scale automated evaluation remain future improvements.
