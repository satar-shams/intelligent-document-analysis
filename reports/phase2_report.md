# Intelligent Document Analysis (IDA)

# Phase 2 — Annotation and Entity Extraction

## Final Technical Report

---

# 1. Phase Overview

Phase 2 of the Intelligent Document Analysis (IDA) project established the annotation and entity-extraction foundation required for structured information extraction from processed document chunks.

The objective of Phase 2 was not to achieve production-level NER accuracy. Instead, the goal was to build a complete, reproducible, and understandable extraction workflow that could later be improved without redesigning the system.

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
16. Analyze the main extraction errors and limitations.

The phase was intentionally designed as a **baseline architecture and evaluation stage**, rather than an attempt to fully optimize the final extraction model.

---

# 3. Entity Schema

The project uses the existing `ExtractedEntity` structure:

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

The broader schema provides room for additional domain-specific extraction in future work.

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

The source ChromaDB collection contained:

```text
5,837 chunks
```

Rather than attempting to manually annotate the complete collection, a deterministic sample was created.

The sampling configuration is:

```yaml
annotation:
  annotation_sample_size: 200
  annotation_random_seed: 42
```

The resulting process is:

```text
5,837 ChromaDB chunks
        ↓
Deterministic sampling
        ↓
200 chunks
```

Using a fixed random seed makes the resulting dataset reproducible.

Relevant implementation:

```text
src/annotation/sampler.py
src/annotation/sample_chunks.py
```

The sampled dataset is used as the development and evaluation foundation for the Phase 2 extraction experiments.

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

The final sampled annotation dataset contains:

```text
Total chunks:             200
Chunks with entities:      69
Chunks without entities:  131
Total entities:            205
Average entities/chunk:   1.02
Maximum entities/chunk:    19
```

Entity distribution:

```text
DATE             68
PRODUCT          62
MONEY            28
ORGANIZATION     25
PERCENTAGE       22
```

The dataset is therefore relatively small.

It should be considered a **development and baseline evaluation dataset**, not a production-scale training corpus.

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
Total chunks:       200
Total entities:     205
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
Total:        200
Train:        140
Validation:    30
Test:          30
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

The pipeline combines:

```text
Create Dataset
      ↓
Apply Annotations
      ↓
Validate
      ↓
Analyze
      ↓
Split
```

It can be executed with:

```bash
python -m src.annotation.annotation_pipeline
```

The complete data-preparation flow is:

```text
5,837 source chunks
        ↓
200 sampled chunks
        ↓
205 weakly annotated entities
        ↓
0 validation errors
        ↓
140 train
30 validation
30 test
```

This establishes a reproducible annotation and dataset-preparation pipeline.

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

The evaluation framework provides the common basis for comparing the different extraction strategies.

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

The project maps the supported labels to the IDA schema:

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

Several pretrained models were evaluated as candidates:

```text
dslim/bert-base-NER
gamug/sec-bert-finer-ord-ner
Jean-Baptiste/roberta-large-ner-english
ritam-m/bert-base-company-ner
musk1209/finsight-ner
```

Under the candidate-model evaluation configuration, `musk1209/finsight-ner` produced the highest F1 among the evaluated candidates:

```text
Precision: 0.1897
Recall:    0.7333
F1:        0.3014
```

It was therefore selected as the NER component for the current Hybrid evaluation.

This selection is an engineering baseline choice rather than a claim that the model is globally optimal for IDA.

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

When an NER prediction overlaps with a rule-based entity, the extractor checks the rule-based label priority.

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

This preserves the relationship between predictions and their source document chunks and allows the predictions to be evaluated later.

---

# 24. Current Pipeline Output

The current extraction pipeline processes:

```text
30 test chunks
```

and produces:

```text
Chunks processed:          30
Chunks with entities:      14
Total predicted entities:  47
```

The prediction records preserve entity metadata including:

```text
text
label
character offsets
confidence
chunk metadata
document metadata
page information
```

---

# 25. Final Hybrid Evaluation

The final evaluation compares three strategies:

```text
1. Rule-based
2. NER
3. Hybrid
```

The selected NER model is:

```text
musk1209/finsight-ner
```

The latest evaluation dataset contains:

```text
Test chunks:        30
Expected entities: 118
```

The final results are:

| Strategy   |   TP |   FP |   FN | Precision | Recall |     F1 |
| ---------- | ---: | ---: | ---: | --------: | -----: | -----: |
| Rule-based |  118 |    0 |    0 |    1.0000 | 1.0000 | 1.0000 |
| NER        |    0 |   58 |  118 |    0.0000 | 0.0000 | 0.0000 |
| Hybrid     |  116 |   44 |    2 |    0.7250 | 0.9831 | 0.8345 |

The Hybrid extractor therefore achieved:

```text
TP:        116
FP:         44
FN:          2

Precision:  72.50%
Recall:     98.31%
F1:         83.45%
```

The Hybrid system recovered:

```text
116 / 118
```

expected entities.

The most significant quantitative characteristic is the very high recall.

The main weakness is the increase in false positives caused primarily by the NER component.

---

# 26. Interpretation of the Evaluation

The rule-based system achieved:

```text
Precision = 100%
Recall    = 100%
F1        = 100%
```

on this particular test set.

However, these values must not be interpreted as evidence of perfect real-world entity extraction.

The reason is that the evaluation annotations were generated by the deterministic annotation system itself.

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

Therefore, part of the evaluation target is inherently related to one of the prediction mechanisms.

The results primarily demonstrate:

* deterministic consistency;
* pipeline correctness;
* reproducibility;
* behavior of the Hybrid architecture;
* performance against the current annotation benchmark.

They do not establish production-level semantic extraction accuracy.

---

# 27. Hybrid Error Analysis

The final Hybrid evaluation produced mathematical errors in:

```text
16 chunks
```

The analysis examined:

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

## 27.1 NER False Positives

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

## 27.2 Boundary and Type Differences

The NER model sometimes identifies a broader expression than the annotation or assigns a different entity type.

Examples observed during analysis include:

```text
Gold:       Xbox → PRODUCT
Prediction: xbox live → ORGANIZATION
```

```text
Gold:       Office → PRODUCT
Prediction: office 365 → ORGANIZATION
```

```text
Gold:       Microsoft → ORGANIZATION
Prediction: microsoft news → ORGANIZATION
```

These represent strict evaluation mismatches involving:

* entity boundaries;
* entity granularity;
* entity types;
* differences between annotation policy and model behavior.

---

## 27.3 Tokenization Artifacts

The NER model sometimes produces subword fragments instead of complete entities.

Examples observed include:

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

## 27.4 Low-Confidence Spurious Predictions

Several suspicious predictions had relatively low model confidence.

Examples include:

```text
x                → ORGANIZATION   0.5190
outlook.         → ORGANIZATION   0.5417
i                → ORGANIZATION   0.6438
financial review → ORGANIZATION   0.8056
```

This suggests that confidence filtering could potentially reduce some false positives.

However, no confidence threshold should be selected based only on a few examples. If confidence filtering is introduced later, it should be evaluated systematically on an independently verified dataset.

---

# 28. Hybrid False Negatives

Only:

```text
2 false negatives
```

remained in the final Hybrid result.

These represent cases where the deterministic rules did not recover an expected entity and the NER model also failed to identify it.

Examples include missing structured entities such as:

```text
2010 → DATE
```

The small number of remaining false negatives demonstrates the primary strength of the Hybrid architecture: deterministic extraction preserves coverage for structured entities while NER adds contextual predictions.

---

# 29. Important Finding: Annotation Coverage

One of the most important findings of Phase 2 is that a mathematical false positive does not necessarily represent a semantically incorrect prediction.

A clear example is **CHUNK 5882**.

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

However, the gold annotation for this chunk contains:

```text
GOLD / EXPECTED:

None
```

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

# 30. NER Error-Analysis Framework

A separate error-analysis framework was developed to investigate the causes behind mathematical evaluation mismatches.

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

The error analysis is diagnostic and is intended to reveal whether a mathematical mismatch represents a genuine extraction problem, an annotation limitation, or an output-processing issue.

---

# 31. Semantic Acceptance Rate

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

For the current Phase 2 report, the official Hybrid metrics remain the primary quantitative result.

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

`musk1209/finsight-ner` is the selected baseline for the current Hybrid evaluation.

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

Future improvements should be driven by actual requirements and stronger evaluation data.

The most useful next steps are:

1. Create a small independently verified gold-standard dataset.
2. Re-evaluate the current NER candidates against that dataset.
3. Add targeted post-processing for obvious NER artifacts.
4. Evaluate confidence filtering only if independently justified.
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

The main quantitative result of the current Hybrid system is:

```text
TP:        116
FP:         44
FN:          2

Precision:  72.50%
Recall:     98.31%
F1:         83.45%
```

The result demonstrates that the Hybrid architecture provides very high recall on the current evaluation benchmark.

Its primary weakness is over-extraction from the NER component, which increases the number of strict false positives.

At the same time, the evaluation has two important limitations:

1. The expected entities were generated through deterministic annotation rules.
2. The annotations are not exhaustive human-verified ground truth.

Therefore, the current metrics should be interpreted as **performance against the available Phase 2 benchmark**, rather than production-level semantic extraction accuracy.

---

# 37. Final Conclusion

The main achievement of Phase 2 is not a particular F1 score.

The main achievement is the establishment of a complete and reproducible entity-extraction architecture that can now be improved without redesigning the entire system.

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
Contextual entities

EntityExtractor
    ↓
Unified structured output

Evaluator
    ↓
Quantitative measurement

Error Analysis
    ↓
Diagnosis of evaluation mismatches
```

This provides IDA with a practical extraction baseline and a clear path for future improvements.

Most importantly, Phase 2 has reached the point where further work should be driven by actual requirements and independently verified evaluation data rather than by continuously expanding the test suite or adding unnecessary complexity.

**Phase 2 is therefore considered complete as a baseline annotation and entity-extraction implementation.**
