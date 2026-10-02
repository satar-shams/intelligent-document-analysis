# Intelligent Document Analysis (IDA)

# Phase 3 — RAG Generation, Orchestration, and Evaluation

## Final Technical Report

---

# 1. Phase Overview

Phase 3 extends IDA from document retrieval and structured information extraction to a Retrieval-Augmented Generation (RAG) system.

The objective is to accept a natural-language question, retrieve relevant document chunks, construct a grounded prompt, and generate an answer using an external language model.

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

For evaluation, the same pipeline can process a predefined set of questions.

Phase 3 therefore establishes the generation, orchestration, persistence, testing, and evaluation layers on top of the retrieval infrastructure developed in earlier phases.

---

# 2. Phase 3 Architecture

The main RAG components are located in:

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

Their responsibilities are:

| Component            | Responsibility                              |
| -------------------- | ------------------------------------------- |
| `Retriever`          | Retrieves relevant chunks from ChromaDB     |
| `ContextBuilder`     | Converts retrieval results into LLM context |
| `PromptBuilder`      | Constructs the final prompt                 |
| `LLMClient`          | Provides the external LLM interface         |
| `RAGChain`           | Orchestrates a single question              |
| `RAGPipeline`        | Processes multiple questions                |
| `evaluation_summary` | Summarizes manual evaluation results        |

The architecture uses dependency injection so individual components can be tested and replaced independently.

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

A question is executed through:

```python
answer = rag_chain.run(
    query=query,
    top_k=10,
)
```

The chain itself does not create its dependencies, which keeps orchestration separate from implementation details.

---

# 4. Retrieval

The `Retriever` uses the existing ChromaDB vector store and embedding infrastructure to identify relevant document chunks.

Example:

```python
search_results = retriever.retrieve(
    query=query,
    top_k=10,
)
```

A retrieval result contains information such as:

```text
chunk_id
document_id
page_start
page_end
distance
text
```

This preserves both the retrieved evidence and its document context.

The retrieved results are passed directly to `ContextBuilder`.

---

# 5. Context Construction

`ContextBuilder` converts structured retrieval results into the textual context supplied to the LLM.

The context preserves:

```text
chunk identification
document identification
page information
source text
```

Conceptually:

```text
Search Results
      ↓
ContextBuilder
      ↓
Document-aware textual context
```

Keeping document metadata alongside the source text allows the RAG system to retain the provenance of retrieved evidence throughout the generation process.

---

# 6. Prompt Construction

`PromptBuilder` combines three inputs:

1. System instruction
2. Retrieved context
3. User question

The current instruction is intentionally restrictive:

```text
Answer the question using only the provided context.
Do not add or invent information that is not supported by the context.
If the context does not contain enough information to answer the question,
say that the available context does not provide enough information.
```

The resulting prompt therefore follows:

```text
Instruction
    +
Retrieved Context
    +
Question
    ↓
Final Prompt
```

This instruction establishes the intended grounding behavior of the RAG system.

---

# 7. LLM Client

`LLMClient` provides a small abstraction around the external language-model API.

The RAG system only needs:

```python
answer = llm_client.generate(
    prompt=prompt,
)
```

The current implementation uses the OpenAI Responses API.

The API credential is loaded from the environment rather than stored in source code:

```text
OPENAI_API_KEY=...
```

The intended execution is:

```text
Prompt
  ↓
OpenAI Responses API
  ↓
response.output_text
  ↓
Answer
```

Live API execution is currently unavailable because the configured OpenAI account has no remaining API credits.

The API integration itself remains implemented in the codebase.

---

# 8. Batch RAG Pipeline

`RAGPipeline` extends the single-question chain to multiple questions.

The batch workflow is:

```text
Evaluation Questions
        ↓
Question Preprocessing
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

Questions are processed independently, making the pipeline suitable for:

* evaluation;
* batch experiments;
* offline testing;
* future automated benchmarking.

The evaluation input is:

```text
data/evaluation/questions.jsonl
```

Each JSONL record represents one question.

---

# 9. Evaluation Preparation

The evaluation questions are validated before RAG processing.

The pipeline checks that:

```text
id exists
query exists
query is a string
query is not empty
```

Surrounding whitespace is removed from questions.

The processed questions are stored in:

```text
data/evaluation/preprocessed_questions.jsonl
```

Generated prompts are stored in:

```text
data/evaluation/prompts.jsonl
```

A prompt record also preserves retrieval metadata such as:

```text
rank
chunk_id
document_id
page_start
page_end
distance
```

This provides a reproducible record of the evidence and prompt prepared for each question.

---

# 10. Result Persistence

When live LLM execution is available, generated answers can be stored in:

```text
data/evaluation/llm_results.jsonl
```

The result record contains the generated answer together with the relevant question and retrieval information.

The distinction between generated output and evaluation is intentional:

```text
LLM Result
    ↓
System Output

Evaluation
    ↓
Judgment of System Output
```

The presence of an answer in `llm_results.jsonl` does not imply that the answer is correct or sufficiently grounded.

---

# 11. Manual Evaluation

Because live OpenAI execution is currently unavailable, an initial manual evaluation was performed using the generated prompts and ChatGPT.

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

Three main questions are evaluated:

### Answerability

Does the retrieved context contain enough information to answer the question?

### Correctness

Does the generated answer correctly answer the question based on the available evidence?

### Grounding

Is the answer supported by the retrieved context rather than unsupported external information?

This separates retrieval quality from generation quality.

---

# 12. Evaluation Dataset

The initial evaluation set contains:

```text
15 questions
```

The questions cover several types of RAG behavior:

```text
Direct factual questions
Numeric questions
Historical questions
Comparison questions
Percentage calculations
Remaining-performance-obligation questions
Questions where the retrieved context is insufficient
```

This provides a small functional evaluation set rather than a large statistical benchmark.

---

# 13. Initial Evaluation Results

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

These results should be interpreted as a **manual baseline**, not as a statistically representative evaluation of RAG quality.

The dataset contains only 15 questions, and the judgments were manually performed.

---

# 14. Grounded Answer Behavior

One important behavior observed during evaluation is that the prompt instruction can cause the system to explicitly refuse unsupported answers rather than inventing information.

For example, when retrieval identifies references to:

```text
Fiscal Year 2025 Compared with Fiscal Year 2024
```

but does not retrieve the actual 2025 revenue value, the appropriate response is:

```text
The available context does not provide enough information
to determine the total revenue in fiscal year 2025.
```

This behavior is important for the current RAG design because the system is explicitly instructed to rely only on retrieved context.

---

# 15. Calculation and Evidence Handling

The evaluation also includes questions requiring simple calculations from retrieved evidence.

For example:

```text
2021: $146 billion
2022: $193 billion
```

The change is:

```text
$193 billion - $146 billion = $47 billion
```

and the relative increase is:

```text
(193 - 146) / 146 × 100 ≈ 32.2%
```

Such cases test whether the generation stage can use numerical evidence contained in the retrieved context rather than merely repeating a retrieved sentence.

---

# 16. Retrieval Limitation

The main limitation observed during Phase 3 evaluation is retrieval quality.

A question may be semantically related to retrieved chunks without the chunks containing the exact evidence required for the answer.

For example:

```text
Question:
total fiscal-year-2025 revenue

Retrieved context:
Fiscal Year 2025 Compared with Fiscal Year 2024
```

The context is related to the question but may not contain the required revenue figure.

The resulting dependency is:

```text
Insufficient Retrieval
        ↓
Insufficient Context
        ↓
Limited Generation
```

Therefore, some RAG failures originate before the LLM generation stage.

Retrieval optimization is intentionally deferred to future work rather than being treated as a Phase 3 requirement.

---

# 17. Testing

Phase 3 includes unit and integration tests for the RAG components.

Current test structure:

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

The external LLM API is intentionally not required for the integration test.

The current RAG integration test passed successfully.

The separate RAG unit tests also passed, providing coverage for prompt construction and mock LLM behavior.

---

# 18. Environment Configuration

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

API credentials must never be committed to the repository.

Any previously exposed credential should be revoked rather than reused.

---

# 19. Phase 3 File Structure

The main Phase 3 structure is:

```text
ida/

├── data/
│   └── evaluation/
│       ├── questions.jsonl
│       ├── preprocessed_questions.jsonl
│       ├── prompts.jsonl
│       ├── manually_evaluated_results.jsonl
│       └── llm_results.jsonl
│
├── src/
│   ├── evaluation/
│   │   └── prepare_prompts.py
│   │
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

Generated evaluation artifacts are not treated as permanent source code.

---

# 20. Execution

The single-question RAG chain can be exercised with:

```bash
python -m src.rag.rag_chain
```

The current development configuration uses a mock LLM where live API access is unavailable.

Evaluation prompts can be generated with:

```bash
python -m src.evaluation.prepare_prompts
```

The evaluation summary can be generated with:

```bash
python -m src.rag.evaluation_summary
```

The prompt-preparation stage reports:

```text
Input questions       : data/evaluation/questions.jsonl
Processed questions   : data/evaluation/preprocessed_questions.jsonl
Generated prompts     : data/evaluation/prompts.jsonl
Number of questions   : 15
Top K                 : 10
```

---

# 21. Implementation Status

The following Phase 3 components are implemented:

```text
✓ RAG retrieval integration
✓ Context construction
✓ Prompt construction
✓ OpenAI client
✓ Dependency injection
✓ Single-question RAGChain
✓ Batch RAGPipeline
✓ Question preprocessing
✓ Prompt persistence
✓ Result persistence
✓ Manual evaluation dataset
✓ Evaluation summary
✓ RAG unit tests
✓ RAG integration test
✓ Environment-based API configuration
```

The following items remain externally constrained or intentionally deferred:

```text
⚠ Live LLM execution
  Blocked by API credit availability

🔜 Retrieval optimization
  Deferred to future iteration

🔜 Larger-scale automated evaluation
  Deferred to future iteration

🔜 Systematic LLM/model comparison
  Deferred to future iteration
```

---

# 22. Future Work

The main future improvements are:

### Retrieval

Improve retrieval and ranking for questions where semantically related chunks do not contain the required evidence.

### Tables

Improve extraction and retrieval of tabular information from annual reports.

### Evaluation

Expand the question set and automate more of the evaluation process.

### LLM Evaluation

Evaluate multiple language models under the same retrieval and prompt conditions.

### Source Attribution

Expose document and page references alongside generated answers.

### Reliability

Add stronger handling for:

```text
API failures
rate limits
timeouts
empty retrieval results
malformed responses
```

These are improvements to the existing baseline rather than prerequisites for the current Phase 3 architecture.

---

# 23. Phase 3 Conclusion

Phase 3 establishes a complete baseline RAG architecture on top of the IDA retrieval infrastructure.

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

These results demonstrate the functionality of the current baseline but should not be interpreted as a formal benchmark because of the small manually evaluated dataset and the current retrieval limitations.

The most important limitation identified in Phase 3 is retrieval quality: if the required evidence is not retrieved, the generation layer cannot reliably answer the question.

Live OpenAI execution is also currently unavailable because of API credit limitations, but the LLM integration is implemented and the RAG architecture can use the same pipeline when API access becomes available.

**Phase 3 is considered complete as a baseline RAG generation, orchestration, persistence, testing, and manual-evaluation implementation.**
