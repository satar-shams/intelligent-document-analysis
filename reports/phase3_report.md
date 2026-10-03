# Intelligent Document Analysis (IDA)

# Phase 3 — RAG Generation, Orchestration, and Evaluation

## Final Technical Report

---

# 1. Phase Overview

Phase 3 extends IDA from document retrieval and structured information extraction to a Retrieval-Augmented Generation (RAG) system.

The objective is to accept a natural-language question, retrieve relevant document chunks, construct grounded context and a prompt, and generate an answer through an external language model.

The complete workflow is:

```text
User Question
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

The same architecture supports both single-question execution and batch processing of predefined evaluation questions.

Phase 3 therefore establishes the generation and orchestration layer on top of the retrieval infrastructure developed in earlier phases.

---

# 2. Architecture

The main RAG components are located in:

```text
src/rag/

├── context_builder.py
├── evaluation_summary.py
├── llm_client.py
├── prompt_templates.py
├── rag_chain.py
└── retriever.py
```

Batch execution is implemented through:

```text
pipelines/rag.py
```

| Component               | Responsibility                              |
| ----------------------- | ------------------------------------------- |
| `Retriever`             | Retrieves relevant chunks from ChromaDB     |
| `ContextBuilder`        | Converts retrieval results into LLM context |
| `PromptBuilder`         | Constructs the final prompt                 |
| `LLMClient`             | Provides the external LLM interface         |
| `RAGChain`              | Orchestrates a single question              |
| `pipelines/rag.py`      | Processes multiple evaluation questions     |
| `evaluation_summary.py` | Summarizes manual evaluation results        |

The components use dependency injection so retrieval, context construction, prompting, and LLM communication can be tested independently.

---

# 3. RAG Chain

The single-question RAG flow is:

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

`RAGChain` receives its dependencies explicitly:

```python
RAGChain(
    retriever=retriever,
    context_builder=context_builder,
    prompt_builder=prompt_builder,
    llm_client=llm_client,
)
```

A question can then be executed through:

```python
answer = rag_chain.run(
    query=query,
    top_k=10,
)
```

This keeps orchestration separate from the individual retrieval, context, prompt, and LLM implementations.

---

# 4. Retrieval and Context Construction

The `Retriever` uses the existing embedding and ChromaDB infrastructure to identify relevant document chunks.

```python
search_results = retriever.retrieve(
    query=query,
    top_k=10,
)
```

Each retrieval result preserves information such as:

```text
chunk_id
document_id
page_start
page_end
distance
text
```

`ContextBuilder` converts these structured results into textual context while preserving document and page metadata.

The resulting context contains:

```text
chunk identification
document identification
page information
source text
```

This context is then passed to the prompt construction stage.

---

# 5. Prompt Construction

`PromptBuilder` combines:

1. the system instruction;
2. retrieved context;
3. the user question.

The current instruction establishes the intended grounding behavior:

```text
Answer the question using only the provided context.

Do not add or invent information that is not supported by the context.

If the context does not contain enough information to answer the question,
say that the available context does not provide enough information.
```

The prompt therefore explicitly instructs the model not to infer unsupported information when the retrieved evidence is insufficient.

---

# 6. LLM Client

`LLMClient` provides a small abstraction around the external language-model API.

The generation interface is:

```python
answer = llm_client.generate(
    prompt=prompt,
)
```

The current implementation uses the OpenAI Responses API.

The API credential is supplied through the environment:

```text
OPENAI_API_KEY=...
```

The intended execution flow is:

```text
Prompt
  ↓
OpenAI Responses API
  ↓
response.output_text
  ↓
Answer
```

The API integration is implemented in the codebase, but live API execution was not available during the final evaluation because API credit access was unavailable.

---

# 7. Batch RAG Pipeline

The batch RAG execution is implemented in:

```text
pipelines/rag.py
```

It processes predefined questions independently:

```text
Evaluation Questions
        ↓
Retrieval
        ↓
Context Construction
        ↓
Prompt Construction
        ↓
LLM
        ↓
Results
```

The evaluation questions are stored in:

```text
data/evaluation/questions.jsonl
```

For each question, the pipeline can preserve the query, generated prompt, answer, and retrieved-result metadata.

---

# 8. Evaluation Methodology

Because live OpenAI execution was unavailable, Phase 3 evaluation was performed manually using the prepared questions, retrieved context, and available generated/manual answers.

The manually reviewed results are stored in:

```text
data/evaluation/manually_evaluated_results.jsonl
```

The evaluation records include:

```text
id
query
answer
evaluation.answerable_from_context
evaluation.correct
evaluation.grounded
evaluation.notes
```

Three aspects were evaluated:

### Answerability

Whether the retrieved context contains enough information to answer the question.

### Correctness

Whether the answer correctly addresses the question based on the available evidence.

### Grounding

Whether the answer is supported by the retrieved context rather than unsupported external information.

---

# 9. Evaluation Dataset and Results

The initial evaluation set contains:

```text
15 questions
```

The questions cover:

```text
Direct factual questions
Numeric questions
Historical questions
Comparison questions
Percentage calculations
Remaining-performance-obligation questions
Questions where the retrieved context is insufficient
```

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

Equivalent percentages:

```text
Answerable from context : 73.3%
Not answerable          : 26.7%

Correct answers         : 93.3%
Incorrect answers       :  6.7%

Grounded answers        : 100.0%
Not grounded            :   0.0%
```

These results represent a **manual functional baseline**, not a statistically representative benchmark. The evaluation contains only 15 questions and relies on manual judgment.

---

# 10. Retrieval Limitation and Observed Behavior

The main limitation observed during Phase 3 is retrieval quality.

A question may be semantically related to retrieved chunks without those chunks containing the exact evidence required to answer it.

For example:

```text
Question:

total fiscal-year-2025 revenue

Retrieved context:

Fiscal Year 2025 Compared with Fiscal Year 2024
```

The retrieved context is relevant to the question but may not contain the required revenue figure.

The resulting limitation can be summarized as:

```text
Insufficient Retrieval
        ↓
Insufficient Context
        ↓
Limited Generation
```

The grounding instruction is designed to prevent the generation layer from inventing missing information. When the required evidence is absent, the intended behavior is to indicate that the available context is insufficient.

This demonstrates that some RAG failures originate in retrieval rather than generation.

Retrieval optimization is therefore deferred to future work.

---

# 11. Testing

Phase 3 includes unit and integration tests for the RAG components.

The relevant tests are:

```text
tests/

├── unit/
│   └── rag/
│       ├── test_mock_llm.py
│       └── test_prompt_templates.py
│
└── integration/
    └── test_rag_chain.py
```

The integration test uses the retrieval stack together with a mock LLM:

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

The external LLM API is therefore not required for the integration test.

The RAG unit tests and integration test passed successfully.

---

# 12. Environment and Security

The external API credential is provided through the environment:

```text
OPENAI_API_KEY=your_api_key
```

The `.env` file is excluded from Git.

The intended configuration flow is:

```text
.env
 ↓
Environment Variable
 ↓
LLMClient
 ↓
OpenAI Client
```

API credentials must not be committed to the repository.

Any previously exposed credential should be revoked rather than reused.

---

# 13. Evaluation Artifacts and Execution

The main evaluation data is stored under:

```text
data/evaluation/
```

Important artifacts include:

```text
questions.jsonl
preprocessed_questions.jsonl
prompts.jsonl
results.jsonl
manually_evaluated_results.jsonl
retrieval_review.jsonl
retrieval_review.txt
```

These files preserve the questions, retrieval and prompt outputs, generated results where available, and manual evaluation records used during Phase 3.

The batch pipeline can be executed with:

```bash
python -m pipelines.rag
```

Live generation requires:

```text
OPENAI_API_KEY
```

The single-question RAG chain can also be exercised through:

```bash
python -m src.rag.rag_chain
```

The evaluation summary can be generated with:

```bash
python -m src.rag.evaluation_summary
```

The execution path depends on whether live API access or the local/mock evaluation path is being used.

---

# 14. Implementation Status

The following Phase 3 components are implemented:

```text
✓ RAG retrieval integration
✓ Context construction
✓ Prompt construction
✓ OpenAI client
✓ Dependency injection
✓ Single-question RAGChain
✓ Batch RAG pipeline
✓ Question preprocessing
✓ Prompt persistence
✓ Result persistence
✓ Manual evaluation dataset
✓ Evaluation summary
✓ RAG unit tests
✓ RAG integration test
✓ Environment-based API configuration
```

The following items remain intentionally deferred:

```text
⚠ Live LLM execution
  Requires available API access

🔜 Retrieval optimization
🔜 Larger-scale automated evaluation
🔜 Systematic LLM/model comparison
```

The deferred items are improvements to the baseline rather than missing components of the current architecture.

---

# 15. Future Work

### Retrieval

Improve retrieval and ranking for questions where semantically related chunks do not contain the required evidence.

### Tables

Improve extraction and retrieval of tabular information from annual reports.

### Evaluation

Expand the question set and automate more of the evaluation process.

### LLM Evaluation

Evaluate multiple language models under consistent retrieval and prompt conditions.

### Source Attribution

Expose document and page references alongside generated answers.

### Reliability

Improve handling of API failures, rate limits, timeouts, empty retrieval results, and malformed responses.

---

# 16. Phase 3 Conclusion

Phase 3 establishes a baseline RAG architecture on top of the IDA retrieval infrastructure.

The implemented system provides:

```text
Question
   ↓
Retrieval
   ↓
Context Construction
   ↓
Prompt Construction
   ↓
LLM Interface
   ↓
Generated Answer
```

and supports both single-question execution and batch evaluation.

The initial 15-question manual evaluation produced:

```text
Answerable from context : 11 / 15
Correct answers         : 14 / 15
Grounded answers        : 15 / 15
```

These results document the behavior of the current baseline but should not be interpreted as a formal benchmark because of the small manually evaluated dataset and the observed retrieval limitations.

The main technical limitation identified during Phase 3 is retrieval quality: when the required evidence is not retrieved, the generation layer cannot reliably answer the question.

Live OpenAI execution was unavailable during the final evaluation because of API credit limitations, but the LLM integration itself is implemented and tested through the project abstractions and mock-based integration path.

**Phase 3 is considered complete as a baseline RAG generation, orchestration, persistence, testing, and manual-evaluation implementation.**
