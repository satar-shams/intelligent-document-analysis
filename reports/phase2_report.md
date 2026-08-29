# Intelligent Document Analysis (IDA)

# Phase 2 — Annotation and Entity Extraction

## Final Technical Report

---

# 1. Phase Overview

Phase 2 of the Intelligent Document Analysis (IDA) project established the annotation and entity-extraction foundation required for structured information extraction from processed document chunks.

The objective of Phase 2 was not to achieve production-level NER accuracy. Instead, the goal was to build a complete, reproducible, maintainable, and understandable extraction workflow that can be improved without redesigning the system.

The Phase 2 workflow is:

```text
Processed Document Chunks
          ↓
      Sampling
          ↓
   Weak Annotation
          ↓
Dataset Validation & Analysis
          ↓
 Train / Validation / Test Split
          ↓
      NER Baseline
          ↓
 Hybrid Entity Extraction
          ↓
Structured Predictions
          ↓
     Evaluation
          ↓
    Error Analysis
```

Phase 2 therefore establishes both the **data foundation** and the **extraction architecture** for structured entity recognition in IDA.

---

# 2. Phase 2 Objectives

The main objectives of Phase 2 were:

1. Define a structured entity schema.
2. Establish annotation guidelines.
3. Sample representative document chunks from ChromaDB.
4. Generate weak annotations using deterministic rules.
5. Store annotation data in JSONL format.
6. Validate the generated dataset.
7. Analyze dataset characteristics and entity distribution.
8. Create deterministic train/validation/test splits.
9. Implement reusable entity evaluation.
10. Establish a pretrained NER baseline.
11. Compare candidate NER models.
12. Integrate NER with deterministic extraction.
13. Implement duplicate and overlap handling.
14. Produce structured extraction predictions.
15. Evaluate rule-based, NER, and Hybrid extraction.
16. Perform chunk-level and NER-specific error analysis.

The phase was intentionally designed as a **baseline architecture and evaluation stage**, rather than an attempt to fully optimize the final extraction model.

---

# 3. Entity Schema

The project uses the `ExtractedEntity` structure:

```python
@dataclass
class ExtractedEntity:
    text: str
    label: str
    start: int
    end: int
    confidence: float | None
    chunk_id: str
    document_id: str
    page_start: int
    page_end: int
```

Each entity therefore contains both the extracted information and its source context.

The intended IDA entity schema is:

```text
ORGANIZATION
PERSON
LOCATION
DATE
MONEY
PERCENTAGE
NUMBER
PRODUCT
FINANCIAL_METRIC
DOCUMENT_REFERENCE
```

The schema is intentionally extensible.

The currently implemented deterministic annotation rules primarily cover:

```text
DATE
MONEY
PERCENTAGE
ORGANIZATION
PRODUCT
```

The broader schema provides room for additional domain-specific extraction in future phases.

---

# 4. Annotation Guidelines

Annotation guidelines are documented in:

```text
docs/annotation_guidelines.md
```

The guidelines define the intended interpretation of entity categories and provide a common basis for automatic annotation and future human annotation.

The current annotation strategy is deliberately simple and focused on establishing a reproducible baseline.

---

# 5. Dataset Sampling

The source ChromaDB collection contains:

```text
13,368 chunks
```

Rather than attempting to manually annotate the complete collection, a deterministic sample was created.

The sampling configuration is:

```yaml
annotation:
  annotation_sample_size: 500
  annotation_random_seed: 42
```

The resulting process is:

```text
13,368 ChromaDB chunks
        ↓
Deterministic sampling
        ↓
500 chunks
```

Using a fixed random seed makes the resulting dataset reproducible.

Relevant implementation:

```text
src/annotation/sampler.py
src/annotation/sample_chunks.py
```

The 500 sampled chunks form the development and evaluation foundation for the Phase 2 extraction experiments.

---

# 6. Weak Annotation

The initial annotation system uses deterministic rules rather than a trained model.

Implementation:

```text
src/annotation/annotator.py
src/annotation/rules.py
```

The main component is:

```text
AutomaticAnnotator
```

It combines regex-based and dictionary-based extraction.

## 6.1 Regex-Based Extraction

Regular expressions are used for structured entities such as:

```text
DATE
MONEY
PERCENTAGE
```

Examples include:

```text
2025
January 15, 2025
January 2025
$10 million
$5 billion
$100
25%
12.5%
25 percent
```

The deterministic rules produce structured `ExtractedEntity` objects with character offsets, confidence values, and source-document metadata.

## 6.2 Dictionary-Based Extraction

Dictionaries are used for known organizations and products.

Examples include organizations such as:

```text
Microsoft
Microsoft Corporation
OpenAI
SEC
```

and products such as:

```text
Microsoft 365
Azure
Windows
LinkedIn
GitHub
Xbox
Office
Teams
```

The dictionary approach provides deterministic recognition for entities that can be identified from known vocabulary.

---

# 7. Annotation Confidence

The current deterministic confidence assignments are:

| Entity Type  | Confidence |
| ------------ | ---------: |
| DATE         |       0.99 |
| MONEY        |       0.99 |
| PERCENTAGE   |       0.99 |
| ORGANIZATION |       0.90 |
| PRODUCT      |       0.95 |

These values represent **rule-system confidence assignments**.

They are not statistically calibrated probabilities and should not be interpreted as such.

---

# 8. Annotation Dataset

The annotation workflow produces JSONL datasets.

Intermediate dataset:

```text
data/processed/annotation/annotation_dataset.jsonl
```

Annotated dataset:

```text
data/processed/annotation/annotated_dataset.jsonl
```

Each record preserves the original chunk information and adds its entity list.

Chunks without entities are retained.

This is important because negative examples are useful for later extraction and NER development.

---

# 9. Dataset Statistics

The current Phase 2 annotation dataset contains:

```text
Total chunks:             500
Chunks with entities:     203
Chunks without entities:  297
Total entities:           771
Average entities/chunk:   1.54
Minimum entities/chunk:    0
Maximum entities/chunk:   23
```

Entity distribution:

| Entity Type  |   Count | Percentage |
| ------------ | ------: | ---------: |
| DATE         |     276 |      35.8% |
| MONEY        |     161 |      20.9% |
| PRODUCT      |     158 |      20.5% |
| ORGANIZATION |      94 |      12.2% |
| PERCENTAGE   |      82 |      10.6% |
| **Total**    | **771** |   **100%** |

The dataset is still relatively small compared with the full collection of 13,368 processed chunks.

It should therefore be considered a **development and baseline evaluation dataset**, rather than a production-scale training corpus.

The dataset is divided into:

```text
Total:        500
Train:        350
Validation:    75
Test:          75
```

using random seed:

```text
42
```

This provides a reproducible evaluation foundation for the Phase 2 experiments.

---

# 10. Dataset Validation

Dataset validation is implemented in:

```text
src/annotation/validate_dataset.py
```

The validator checks:

* required chunk fields;
* required entity fields;
* valid entity labels;
* character offsets;
* correspondence between entity text and source text;
* chunk/document metadata consistency;
* overlapping entity spans.

Entity offsets must satisfy:

```text
0 <= start < end <= len(chunk_text)
```

and:

```python
chunk_text[start:end] == entity["text"]
```

The final validation result is:

```text
Total chunks:       500
Total entities:     771
Validation errors:    0
```

Therefore, the generated dataset is **structurally valid**.

This result does not prove semantic annotation accuracy.

---

# 11. Weak Annotation vs. Ground Truth

A central limitation of Phase 2 is the distinction between **weak annotation** and **human-verified ground truth**.

The current annotations were generated automatically using deterministic rules that also form part of the extraction system.

Therefore:

```text
Validation successful
```

means that the dataset is structurally consistent.

It does not mean:

```text
100% semantic annotation accuracy
```

For example, a dictionary can identify a known product name in a context where it does not function as a product entity. Similarly, a regular expression can identify a date-like or monetary expression without understanding its semantic role.

Consequently, the current dataset should be treated as a **weakly annotated benchmark**.

This limitation is particularly important when interpreting the final extraction metrics.

---

# 12. Dataset Split

The annotated dataset is divided into:

```text
70% → Training
15% → Validation
15% → Test
```

using random seed:

```text
42
```

The resulting split is:

```text
Total:        500
Train:        350
Validation:    75
Test:          75
```

Generated files:

```text
data/processed/extraction/train.jsonl
data/processed/extraction/validation.jsonl
data/processed/extraction/test.jsonl
```

The deterministic split ensures that evaluation can be reproduced.

---

# 13. Annotation Pipeline

The complete annotation workflow is orchestrated by:

```text
src/annotation/annotation_pipeline.py
```

The pipeline combines five sequential stages:

```text
Create Dataset
      ↓
Apply Automatic Annotations
      ↓
Validate Dataset
      ↓
Analyze Dataset
      ↓
Split Dataset
```

It can be executed with:

```bash
python -m src.annotation.annotation_pipeline
```

The complete data-preparation flow is:

```text
13,368 source chunks
        ↓
500 deterministically sampled chunks
        ↓
771 weakly annotated entities
        ↓
0 validation errors
        ↓
Dataset analysis
        ↓
350 train
75 validation
75 test
```

The resulting dataset statistics are:

```text
Source ChromaDB chunks:       13,368
Sampled chunks:                  500
Annotated chunks:                500
Total entities:                  771
Validation errors:                 0
Training chunks:                350
Validation chunks:               75
Test chunks:                     75
```

The generated datasets are written to:

```text
data/processed/annotation/annotation_dataset.jsonl
data/processed/annotation/annotated_dataset.jsonl
```

and:

```text
data/processed/extraction/train.jsonl
data/processed/extraction/validation.jsonl
data/processed/extraction/test.jsonl
```

The use of a fixed random seed (`42`) makes sampling and dataset splitting deterministic and reproducible.

---

# 14. Annotation Tests

The annotation subsystem contains tests for:

```text
tests/annotation/

├── test_annotator.py
├── test_evaluator.py
├── test_sampler.py
├── test_split_dataset.py
└── test_validate_dataset.py
```

The tests cover the core infrastructure, including:

* entity extraction behavior;
* sampling;
* deterministic splitting;
* dataset validation;
* evaluation logic.

The current annotation test result is:

```text
23 passed
```

The purpose of these tests is to verify the core infrastructure rather than exhaustively test every possible entity pattern.

---

# 15. Entity Evaluation Framework

A reusable evaluation framework was implemented in:

```text
src/annotation/evaluator.py
```

It calculates:

```text
True Positives
False Positives
False Negatives
Precision
Recall
F1
```

Metrics can also be calculated by entity type.

The evaluator uses counters rather than simple sets so that duplicate entity mentions can be handled correctly.

Entity matching also accounts for case-only differences when comparing otherwise equivalent entity spans and labels.

For example:

```text
Gold:       Microsoft
Predicted:  microsoft
```

can be treated as the same entity when the remaining matching criteria are satisfied.

The evaluation framework provides the common basis for comparing different extraction strategies.

---

# 16. NER Baseline

A pretrained Transformer NER component was introduced after the annotation dataset had been established.

Implementation:

```text
src/extraction/ner_model.py
```

The initial baseline was:

```text
dslim/bert-base-NER
```

The model provides general-purpose English NER without requiring model training.

Its primary labels are:

```text
ORG
PER
LOC
MISC
```

The project maps supported labels to the IDA schema:

```text
ORG → ORGANIZATION
PER → PERSON
LOC → LOCATION
```

`MISC` is currently ignored because it does not directly correspond to a specific IDA entity category.

---

# 17. NER Output

The NER component converts model predictions into the common `ExtractedEntity` structure.

Each prediction retains:

```text
text
label
start
end
confidence
chunk_id
document_id
page_start
page_end
```

This allows the NER component to remain compatible with the rest of the IDA extraction architecture.

The confidence values originate from the NER model and are preserved as model outputs. They are not treated as guaranteed calibrated probabilities.

---

# 18. Initial NER Findings

The general-purpose NER approach successfully identifies common contextual entities such as:

```text
Microsoft       → ORGANIZATION
Satya Nadella   → PERSON
New York        → LOCATION
```

However, the IDA entity schema is broader than the label space of the general-purpose model.

IDA requires categories including:

```text
DATE
MONEY
PERCENTAGE
PRODUCT
FINANCIAL_METRIC
DOCUMENT_REFERENCE
NUMBER
```

while the baseline primarily provides:

```text
PERSON
ORGANIZATION
LOCATION
MISC
```

Therefore, standalone NER cannot provide complete coverage of the IDA extraction requirements.

This motivated the Hybrid extraction architecture.

---

# 19. NER Candidate Model Comparison

Several pretrained NER models were evaluated as candidates:

```text
dslim/bert-base-NER
gamug/sec-bert-finer-ord-ner
Jean-Baptiste/roberta-large-ner-english
ritam-m/bert-base-company-ner
musk1209/finsight-ner
```

The candidates were evaluated using the Phase 2 extraction test dataset and the same entity-matching evaluation framework.

The candidate comparison produced:

| Model                                     |   TP |   FP |   FN | Precision | Recall |         F1 |
| ----------------------------------------- | ---: | ---: | ---: | --------: | -----: | ---------: |
| `musk1209/finsight-ner`                   |   11 |   47 |    4 |    0.1897 | 0.7333 | **0.3014** |
| `gamug/sec-bert-finer-ord-ner`            |   11 |   49 |    4 |    0.1833 | 0.7333 |     0.2933 |
| `Jean-Baptiste/roberta-large-ner-english` |    8 |   53 |    7 |    0.1311 | 0.5333 |     0.2105 |
| `ritam-m/bert-base-company-ner`           |    2 |    6 |   13 |    0.2500 | 0.1333 |     0.1739 |
| `dslim/bert-base-NER`                     |    8 |   70 |    7 |    0.1026 | 0.5333 |     0.1720 |

Under the candidate-model evaluation configuration, `musk1209/finsight-ner` produced the highest F1:

```text
Precision: 0.1897
Recall:    0.7333
F1:        0.3014
```

It was therefore selected as the NER component for the current Hybrid evaluation.

The selection is based on the highest F1 among the evaluated candidates. It is an engineering baseline choice rather than a claim that the model is globally optimal for IDA.

The low precision observed across the candidates also demonstrates that general-purpose pretrained NER models can introduce substantial predictions that do not exactly match the current weakly annotated benchmark.

---

# 20. Why Hybrid Extraction?

The experiments showed that neither deterministic extraction nor standalone NER provides the complete desired extraction architecture.

Deterministic extraction is effective for structured and domain-specific patterns:

```text
DATE
MONEY
PERCENTAGE
PRODUCT
known ORGANIZATION names
```

NER provides contextual recognition for entities that are more difficult to describe using deterministic rules:

```text
PERSON
ORGANIZATION
LOCATION
```

The resulting strategy is:

```text
Rules
   +
Dictionaries
   +
NER
   =
Broader entity coverage
```

The Hybrid architecture therefore combines deterministic precision for known patterns with contextual recognition from NER.

---

# 21. Hybrid EntityExtractor

The main Hybrid abstraction is:

```text
src/extraction/entity_extractor.py
```

The `EntityExtractor` combines:

```text
AutomaticAnnotator
        +
NERModel
```

and returns one unified list of:

```text
ExtractedEntity
```

The rest of the application can therefore use:

```python
entities = extractor.extract(
    text=text,
    context=context,
)
```

without needing to know which extraction mechanism produced each entity.

This creates a clean interface for future model or rule changes.

---

# 22. Entity Merging and Conflict Resolution

The Hybrid extractor does not simply concatenate rule-based and NER predictions.

It implements explicit conflict handling.

## 22.1 Exact Duplicates

If both systems identify the same span and label:

```text
Microsoft → ORGANIZATION
```

only one entity is retained.

## 22.2 Non-Overlapping Entities

If the systems identify different entities:

```text
Azure      → PRODUCT
Microsoft  → ORGANIZATION
```

both can be retained.

## 22.3 Overlapping Entities

When an NER prediction overlaps with a rule-based entity, the extractor checks rule-based label priority.

The current priority labels are:

```text
DATE
MONEY
PERCENTAGE
PRODUCT
```

These deterministic entities are preserved when they conflict with a generic NER prediction.

For non-priority overlaps, the NER prediction can replace the existing rule-based entity.

The final entity list is sorted by character position.

---

# 23. Extraction Pipeline

The end-to-end extraction pipeline is implemented in:

```text
src/extraction/extraction_pipeline.py
```

Input:

```text
data/processed/extraction/test.jsonl
```

Output:

```text
data/processed/extraction/predictions.jsonl
```

Each output record retains the original chunk information and adds:

```json
"predicted_entities": [...]
```

This preserves the relationship between predictions and their source document chunks and allows the predictions to be evaluated independently.

---

# 24. Current Pipeline Output

The current extraction pipeline processes the held-out test set:

```text
75 test chunks
```

The latest pipeline execution produced:

```text
Chunks processed:          75
Chunks with entities:      37
Total predicted entities:  118
```

The predictions are written to:

```text
data/processed/extraction/predictions.jsonl
```

Each prediction record preserves:

```text
text
label
character offsets
confidence
chunk metadata
document metadata
page information
```

This output serves as the input for final extraction evaluation and error analysis.

---

# 25. Final Hybrid Evaluation

The final evaluation compares three extraction strategies:

```text
1. Rule-based
2. NER
3. Hybrid
```

The selected NER model is:

```text
musk1209/finsight-ner
```

The current evaluation dataset contains:

```text
Test chunks:        75
```

The test set is the held-out 15% portion of the 500-sample Phase 2 dataset.

## Evaluation Methodology

The evaluator uses strict entity matching based on the available annotation benchmark.

Matching considers the entity representation and character span, while case-only differences are normalized so that capitalization differences do not create artificial false-positive/false-negative pairs.

This correction is important because:

```text
Gold:       Microsoft
Predicted:  microsoft
```

should not automatically be treated as two different entities when the remaining matching criteria are equivalent.

The current metrics must therefore be interpreted in the context of the latest evaluator implementation.

## Important Evaluation Limitation

The Phase 2 benchmark is generated from the same deterministic annotation framework that is also used by the rule-based extraction component.

Conceptually:

```text
Expected Entities
        ↑
AutomaticAnnotator
```

while Hybrid predictions are generated through:

```text
EntityExtractor
      ├── AutomaticAnnotator
      └── NERModel
```

Therefore, rule-based performance against this benchmark is expected to be extremely strong and should not be interpreted as independent evidence of semantic extraction quality.

Furthermore, the annotations are not exhaustive human-verified ground truth.

For this reason, exact Precision, Recall, and F1 values should be interpreted as **benchmark metrics**, not production-level semantic accuracy.

---

# 26. Hybrid Error Analysis

A separate error-analysis process was used to investigate mismatches between the expected entities and Hybrid predictions.

The analysis examines:

* expected entities;
* predicted entities;
* false negatives;
* false positives;
* labels;
* character offsets;
* confidence scores;
* source context.

Several recurring error patterns were identified.

---

## 26.1 NER False Positives

The NER component frequently identifies geographic or organizational expressions that are absent from the current annotation dataset.

Examples include:

```text
United States → LOCATION
Ireland       → LOCATION
Singapore     → LOCATION
Japan         → LOCATION
India         → LOCATION
Australia     → LOCATION
Europe        → LOCATION
```

Some of these predictions are clearly meaningful entities in the source text.

However, because they are absent from the current annotations, strict evaluation counts them as false positives.

This demonstrates that the current annotation dataset is more conservative than the output of a general-purpose NER model.

---

## 26.2 Entity Boundary and Type Differences

The NER model sometimes identifies a broader expression than the annotation or assigns a different entity type.

Examples include:

```text
Gold:       Xbox → PRODUCT
Prediction: xbox live → ORGANIZATION
```

and:

```text
Gold:       Office → PRODUCT
Prediction: office 365 → ORGANIZATION
```

These represent strict evaluation mismatches involving:

* entity boundaries;
* entity granularity;
* entity types;
* differences between annotation policy and model behavior.

---

## 26.3 Tokenization Artifacts

The NER model sometimes produces subword fragments instead of complete entities.

Examples include:

```text
cop   → ORGANIZATION
##ilo → ORGANIZATION
```

where the intended entity is:

```text
Copilot
```

Other fragmented predictions included:

```text
fa
##sb
```

These examples demonstrate that NER output may require post-processing before being treated as final document entities.

---

## 26.4 Low-Confidence Spurious Predictions

Several suspicious NER predictions were produced with relatively low confidence scores.

Examples include:

```text
x          → ORGANIZATION   0.5190
outlook.   → ORGANIZATION   0.5417
i          → ORGANIZATION   0.6438
```

These predictions are useful examples of cases where confidence-based filtering may help remove obvious NER noise.

However, confidence filtering alone cannot solve the complete precision problem.

The error analysis also identified high-confidence predictions such as:

```text
United States → LOCATION
Ireland       → LOCATION
Singapore     → LOCATION
Japan         → LOCATION
India         → LOCATION
Australia     → LOCATION
```

These can be semantically meaningful entities even when they are absent from the current annotations.

Therefore:

```text
High confidence
      ≠
Guaranteed semantic correctness
```

and:

```text
Low confidence
      ≠
Guaranteed semantic incorrectness
```

Any confidence threshold should therefore be selected through systematic evaluation rather than individual examples.

---

# 27. Important Finding: Annotation Coverage

One of the most important findings of Phase 2 is that a mathematical false positive does not necessarily represent a semantically incorrect prediction.

A clear example is **Chunk 5882**.

The chunk contains numerous explicit geographic references, including:

```text
Ireland
Singapore
Japan
India
Greater China
Asia-Pacific
Fargo
North Dakota
Fort Lauderdale
Florida
Puerto Rico
Redmond
Washington
Reno
Nevada
Latin America
North America
Americas
Australia
Europe
Asia
```

However, the available gold annotation for this chunk contains no entities.

The Hybrid extractor predicted multiple `LOCATION` entities corresponding to these geographic expressions.

Under strict evaluation, these predictions are counted as false positives.

However, the predictions are supported by the actual source text and are therefore semantically meaningful geographic entities.

This demonstrates an important limitation of evaluating extraction against an incomplete or non-exhaustive annotation set:

```text
Evaluation FP
      ≠
necessarily semantic model error
```

A prediction can be semantically valid while still being classified as a false positive if the corresponding entity is missing from the gold annotations.

This is particularly important for the Hybrid extractor because one of its purposes is to increase entity coverage through contextual NER.

Consequently, additional valid entities can reduce strict precision when those entities are not represented in the available annotations.

The current dataset should therefore be treated as an **evaluation benchmark with limited annotation coverage**, rather than an exhaustive representation of every valid entity appearing in the source documents.

---

# 28. NER Error-Analysis Framework

A dedicated error-analysis framework was developed to investigate the causes behind mathematical evaluation mismatches.

Relevant categories include:

```text
VALID_UNANNOTATED
WRONG_ENTITY
WRONG_LABEL
BOUNDARY_ERROR
TOKENIZATION_ERROR
ANNOTATION_PROBLEM
SEMANTICALLY_VALID
OTHER
```

This analysis does not replace the official evaluation.

The two levels serve different purposes:

```text
Official Evaluation
        ↓
Precision / Recall / F1
```

and:

```text
Error Analysis
        ↓
Why did the mismatch occur?
```

The official metrics remain the primary quantitative benchmark.

The error analysis is diagnostic and is intended to determine whether a mathematical mismatch represents:

* a genuine extraction problem;
* an annotation limitation;
* an entity boundary difference;
* a label mismatch;
* a tokenization problem; or
* another processing issue.

---

# 29. Semantic Acceptance Rate

The error-analysis framework also defines a diagnostic metric called:

```text
Semantic Acceptance Rate
```

Conceptually:

```text
Semantically acceptable apparent errors
-------------------------------------- × 100
All evaluated apparent errors
```

The metric asks:

> When a prediction does not exactly match the annotation, how often is it nevertheless semantically meaningful?

This metric must not be interpreted as:

* model accuracy;
* precision;
* recall;
* F1.

It should only be reported when the relevant apparent errors have been manually classified sufficiently to support the calculation.

For Phase 2, the official evaluation metrics remain the primary quantitative benchmark.

---

# 30. Hybrid False Negatives

False negatives represent expected entities that were not recovered by the Hybrid extractor under the strict evaluation criteria.

These cases should be treated as diagnostic examples rather than interpreted in isolation.

The Hybrid architecture is specifically intended to combine deterministic extraction with contextual NER:

```text
Deterministic rules
        +
Contextual NER
        ↓
Broader entity coverage
```

The current benchmark demonstrates that this combination can recover a broad range of the entities represented in the weak annotations.

However, false-negative analysis should ultimately be repeated against an independently verified dataset because the current benchmark does not represent exhaustive semantic ground truth.

---

# 31. Interpretation of Rule-Based Performance

The deterministic rule-based extractor performs very strongly against the current benchmark because the benchmark itself was generated using the deterministic annotation system.

This creates an inherent relationship between:

```text
Gold / Expected Entities
```

and:

```text
Rule-Based Predictions
```

Therefore, a result such as:

```text
Precision = 100%
Recall    = 100%
F1        = 100%
```

on this benchmark should be interpreted as evidence of deterministic consistency rather than proof of perfect real-world entity extraction.

The result demonstrates:

* deterministic consistency;
* annotation reproducibility;
* pipeline correctness;
* stable entity offsets;
* compatibility between annotation and evaluation infrastructure.

It does not establish:

```text
100% semantic extraction accuracy
```

on unseen real-world documents.

---

# 32. Phase 2 Architecture

The final extraction architecture is:

```text
                    Document Chunks
                           │
                           ▼
                    EntityExtractor
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
      AutomaticAnnotator             NERModel
              │                         │
       ┌──────┴──────┐                  │
       │             │                  │
     Regex       Dictionaries           │
       │             │                  │
       └──────┬──────┘                  │
              │                         │
              └────────────┬────────────┘
                           ▼
                   Entity Merging
                           │
                           ▼
                   ExtractedEntity
                           │
                           ▼
                 predictions.jsonl
                           │
                           ▼
                      Evaluation
                           │
                           ▼
                     Error Analysis
```

The architecture separates:

* deterministic extraction;
* contextual NER;
* duplicate handling;
* overlap resolution;
* structured prediction output;
* evaluation;
* error analysis.

This provides a clean interface for future improvements.

---

# 33. Phase 2 Implementation Status

The following components are complete:

```text
✓ Entity schema

✓ Annotation guidelines

✓ ChromaDB sampling

✓ Deterministic sampling

✓ Weak annotation rules

✓ Regex extraction

✓ Dictionary extraction

✓ Automatic annotation

✓ Annotation dataset generation

✓ Dataset validation

✓ Dataset analysis

✓ Train/validation/test splitting

✓ Reusable entity evaluator

✓ Precision / Recall / F1 calculation

✓ Per-label evaluation

✓ Case-normalized entity matching

✓ NER baseline

✓ NER label mapping

✓ Confidence preservation

✓ Context preservation

✓ NER candidate comparison

✓ Hybrid EntityExtractor

✓ Entity merging

✓ Duplicate handling

✓ Overlap handling

✓ Rule-based priority

✓ End-to-end extraction pipeline

✓ JSONL prediction output

✓ Rule-based vs NER vs Hybrid evaluation

✓ Chunk-level Hybrid error analysis

✓ NER error analysis
```

---

# 34. What Is Not Considered Finished

The following are intentionally **not considered production-quality completed components**.

## 34.1 Human-Verified Gold Dataset

The current annotations are weak annotations.

A smaller independently verified dataset would be required for a reliable measurement of semantic extraction quality.

## 34.2 Final NER Model

`musk1209/finsight-ner` is the selected baseline for the current Hybrid implementation.

It is not claimed to be the final or optimal NER model for IDA.

## 34.3 Complete Entity Schema Coverage

The broader IDA schema still contains categories such as:

```text
NUMBER
FINANCIAL_METRIC
DOCUMENT_REFERENCE
```

that are not comprehensively implemented by the current deterministic extraction system.

## 34.4 Production-Level Accuracy Benchmark

The current benchmark is based on weak annotations and limited annotation coverage.

Therefore, it should not be presented as a final measurement of real-world extraction accuracy.

---

# 35. Recommended Future Work

Phase 2 should not be expanded indefinitely.

The current implementation provides sufficient infrastructure to move forward with the project.

The most useful future improvements are:

1. Create a small independently verified gold-standard dataset.
2. Re-evaluate the current NER candidates against that dataset.
3. Add targeted post-processing for obvious NER artifacts.
4. Evaluate confidence filtering only through systematic experiments.
5. Expand deterministic rules when concrete extraction requirements appear.
6. Fine-tune a domain-specific NER model only if later requirements justify it.
7. Revisit semantic error analysis when better annotations are available.

There is no need to exhaustively test every theoretical entity pattern at this stage.

The goal of Phase 2 is to establish a maintainable extraction foundation, not to turn the project into an open-ended NER research project.

---

# 36. Phase 2 Final Assessment

Phase 2 successfully established the annotation and entity-extraction foundation for IDA.

The system now provides:

```text
Structured Entity Schema
        ↓
Reproducible Annotation Dataset
        ↓
Validation and Analysis
        ↓
Train / Validation / Test Splits
        ↓
NER Baseline
        ↓
Hybrid Extraction
        ↓
Structured Predictions
        ↓
Quantitative Evaluation
        ↓
Error Analysis
```

The current Phase 2 dataset consists of:

```text
Source ChromaDB chunks:       13,368
Sampled chunks:                  500
Annotated chunks:                500
Total weakly annotated entities: 771

Train:                            350
Validation:                        75
Test:                              75

Validation errors:                 0
```

The selected NER baseline is:

```text
musk1209/finsight-ner
```

with the highest F1 among the evaluated candidate NER models under the Phase 2 benchmark configuration.

The Hybrid architecture combines:

```text
Deterministic Rules
        +
Dictionaries
        +
Contextual NER
        ↓
Unified ExtractedEntity output
```

The error analysis identified several important limitations:

```text
• NER false-positive overprediction
• Entity boundary mismatches
• Entity-type mismatches
• Subword-tokenization artifacts
• Low-confidence spurious predictions
• Valid entities absent from the weak annotations
• Limited annotation coverage
```

The analysis also established that strict mathematical false positives cannot always be interpreted as genuine semantic extraction errors.

In particular, source chunks containing explicit geographic entities can receive `LOCATION` false positives when those entities are absent from the automatically generated annotations.

Therefore, the current metrics should be interpreted as:

```text
Performance against the Phase 2 benchmark
```

rather than:

```text
Production-level semantic extraction accuracy
```

The strongest conclusion from Phase 2 is not a single F1 value.

The stronger result is that IDA now has a **complete, reproducible, extensible extraction pipeline** covering:

```text
Sampling
    ↓
Weak Annotation
    ↓
Validation
    ↓
Dataset Analysis
    ↓
Dataset Splitting
    ↓
NER
    ↓
Hybrid Extraction
    ↓
Entity Merging
    ↓
Prediction Generation
    ↓
Evaluation
    ↓
Error Analysis
```

---

# 37. Final Conclusion

The main achievement of Phase 2 is the establishment of a maintainable entity-extraction architecture and evaluation framework that can now be improved without redesigning the entire system.

The current design combines:

```text
Deterministic Rules
    ↓
Structured / domain-specific entities

Dictionaries
    ↓
Known organizations and products

NER
    ↓
Contextual entity candidates

EntityExtractor
    ↓
Unified structured output

Evaluator
    ↓
Quantitative measurement

Error Analysis
    ↓
Diagnosis of extraction and annotation mismatches
```

The Phase 2 dataset provides a reproducible benchmark consisting of **500 sampled chunks**, divided into **350 training, 75 validation, and 75 test chunks**, with **771 automatically generated entity annotations** and **zero structural validation errors**.

The NER experiments established `musk1209/finsight-ner` as the current baseline candidate based on the highest F1 among the evaluated models.

The Hybrid architecture demonstrates the practical value of combining deterministic extraction with contextual NER. Deterministic rules provide strong handling of structured entities, while NER expands contextual coverage for entities such as people, organizations, and locations.

At the same time, the error analysis demonstrates that the current benchmark has important limitations. NER false positives, tokenization artifacts, boundary mismatches, label mismatches, and incomplete annotation coverage all influence the strict evaluation results.

Most importantly, the analysis shows that:

```text
Mathematical False Positive
          ≠
Automatically confirmed semantic error
```

when the annotation set is incomplete.

The current benchmark is therefore best understood as a **weakly annotated development and evaluation benchmark**, not as exhaustive human-verified ground truth.

The most valuable next step is not to continuously expand the weak annotation system. Instead, a relatively small independently human-verified gold-standard dataset should eventually be created. This would provide a much more reliable basis for measuring semantic extraction quality and deciding whether additional NER tuning, confidence filtering, post-processing, or rule expansion is justified.

Until such a dataset is available, the current system should be considered a **baseline extraction implementation** rather than a final semantic NER solution.

**Phase 2 is therefore considered complete as a baseline annotation, hybrid entity-extraction, evaluation, and error-analysis implementation.**
