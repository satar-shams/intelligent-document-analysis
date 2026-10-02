# Intelligent Document Analysis (IDA)

# Phase 2 — Annotation and Entity Extraction

## Final Technical Report

---

# 1. Phase Overview

Phase 2 establishes the annotation and entity-extraction foundation for structured information extraction from processed document chunks.

The objective was to build a reproducible and maintainable baseline rather than a production-level NER system.

The Phase 2 workflow is:

```text
Processed Document Chunks
        ↓
Deterministic Sampling
        ↓
Weak Annotation
        ↓
Validation & Analysis
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

The extraction architecture combines deterministic rule-based annotation with a pretrained NER model. Both sources are converted into a common `ExtractedEntity` representation and merged using explicit duplicate and overlap-resolution rules.

Phase 2 therefore provides the data preparation, extraction, evaluation, and diagnostic infrastructure required for further development.

---

# 2. Phase 2 Objectives

The main objectives were:

1. Define a structured entity representation and label schema.
2. Establish reproducible annotation rules.
3. Sample document chunks from ChromaDB.
4. Generate weak annotations using deterministic rules and dictionaries.
5. Validate and analyze the annotation dataset.
6. Create deterministic train/validation/test splits.
7. Implement reusable entity-level evaluation.
8. Establish and compare pretrained NER baselines.
9. Integrate NER with deterministic extraction.
10. Implement duplicate and overlap handling.
11. Generate structured entity predictions.
12. Evaluate rule-based, NER, and Hybrid extraction.
13. Perform diagnostic error analysis.

The phase was intentionally designed as a baseline extraction and evaluation stage rather than an attempt to fully optimize a final NER model.

---

# 3. Entity Schema

The project uses a common `ExtractedEntity` structure:

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

This representation preserves the entity text, label, character offsets, confidence, and source-document context.

## 3.1 Implemented Entity Labels

The deterministic annotation layer generates:

```text
DATE
MONEY
PERCENTAGE
ORGANIZATION
PRODUCT
```

The NER component maps supported model labels as follows:

```text
PER → PERSON
ORG → ORGANIZATION
LOC → LOCATION
```

The resulting Hybrid extraction system therefore supports:

```text
PERSON
ORGANIZATION
LOCATION
DATE
MONEY
PERCENTAGE
PRODUCT
```

The schema remains extensible for future domain-specific entity types.

---

# 4. Annotation Guidelines

The Phase 2 annotation conventions are documented separately:

[`docs/annotation_guidelines.md`](../docs/annotation_guidelines.md)

The guidelines define entity interpretation, span boundaries, labeling conventions, and ambiguity handling.

The current guidelines support the deterministic weak-annotation layer and provide a basis for future independently human-annotated evaluation data.

---

# 5. Dataset Sampling

The source ChromaDB collection contains:

```text
13,368 chunks
```

A deterministic sample of 500 chunks was created using:

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

The sampling implementation is located in:

* [`src/annotation/sampler.py`](../src/annotation/sampler.py)
* [`src/annotation/sample_chunks.py`](../src/annotation/sample_chunks.py)

The fixed seed makes the sample reproducible.

---

# 6. Weak Annotation

The weak annotation system is implemented in:

* [`src/annotation/annotator.py`](../src/annotation/annotator.py)
* [`src/annotation/rules.py`](../src/annotation/rules.py)

`AutomaticAnnotator` combines regular-expression rules with predefined entity dictionaries.

## 6.1 Regex Extraction

Regular expressions identify structured entity types:

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

## 6.2 Dictionary Extraction

Predefined dictionaries identify known organizations and products.

Example organization entries include:

```text
Microsoft
Microsoft Corporation
OpenAI
SEC
```

Example product entries include:

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

The deterministic annotator assigns rule-system confidence values:

| Entity Type  | Confidence |
| ------------ | ---------: |
| DATE         |       0.99 |
| MONEY        |       0.99 |
| PERCENTAGE   |       0.99 |
| ORGANIZATION |       0.90 |
| PRODUCT      |       0.95 |

These values are rule-system assignments, not statistically calibrated probabilities.

---

# 7. Dataset Statistics

The resulting weakly annotated dataset contains:

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

These statistics describe the deterministic annotation output and should not be interpreted as the true entity distribution of the complete document collection.

---

# 8. Dataset Validation

Dataset validation is implemented in:

[`src/annotation/validate_dataset.py`](../src/annotation/validate_dataset.py)

The validator checks:

* required chunk and entity fields;
* valid entity labels;
* character offsets;
* correspondence between entity text and source text;
* chunk and document metadata;
* overlapping entity spans.

Entity offsets must satisfy:

```text
0 <= start < end <= len(chunk_text)
```

and:

```python
chunk_text[start:end] == entity["text"]
```

The final validation result was:

```text
Total chunks:       500
Total entities:     771
Validation errors:    0
```

This demonstrates structural validity according to the implemented validation rules.

It does not establish semantic annotation accuracy.

---

# 9. Dataset Split and Annotation Pipeline

The annotation workflow is orchestrated by:

[`src/annotation/annotation_pipeline.py`](../src/annotation/annotation_pipeline.py)

The pipeline consists of:

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
python -m pipelines.annotation
```

The dataset is divided using a deterministic 70/15/15 split:

```text
Total:        500
Train:        350
Validation:    75
Test:          75
```

The split uses random seed `42`.

Generated datasets include:

```text
data/processed/annotation/annotation_dataset.jsonl
data/processed/annotation/annotated_dataset.jsonl
data/processed/extraction/train.jsonl
data/processed/extraction/validation.jsonl
data/processed/extraction/test.jsonl
```

---

# 10. Annotation Tests

The annotation subsystem contains:

```text
tests/annotation/

├── test_annotator.py
├── test_evaluator.py
├── test_sampler.py
├── test_split_dataset.py
└── test_validate_dataset.py
```

The tests cover:

* entity extraction;
* sampling;
* deterministic splitting;
* dataset validation;
* evaluation logic.

The recorded annotation test result is:

```text
23 passed
```

These tests verify the core annotation infrastructure rather than every possible entity pattern or document context.

---

# 11. Entity Evaluation Framework

A reusable entity-level evaluator is implemented in:

[`src/annotation/evaluator.py`](../src/annotation/evaluator.py)

The evaluator calculates:

```text
True Positives
False Positives
False Negatives
Precision
Recall
F1
```

Metrics can also be calculated per entity type.

Entity matching accounts for case-only differences when the remaining matching criteria are equivalent. For example:

```text
Gold:       Microsoft
Predicted:  microsoft
```

can be treated as the same entity when the relevant span and label criteria are satisfied.

The evaluator provides a common quantitative framework for comparing deterministic extraction, NER, and Hybrid predictions.

---

# 12. NER Baseline

The initial NER component is implemented in:

```text
src/extraction/ner_model.py
```

The initial baseline model was:

```text
dslim/bert-base-NER
```

Its primary labels include:

```text
ORG
PER
LOC
MISC
```

The project maps supported labels into the IDA schema:

```text
ORG → ORGANIZATION
PER → PERSON
LOC → LOCATION
```

`MISC` is currently ignored because it does not map directly to a specific IDA entity category.

NER predictions are converted into the same `ExtractedEntity` structure used by deterministic extraction.

Model confidence values are preserved but are not assumed to be calibrated probabilities.

---

# 13. NER Candidate Comparison

Several pretrained NER models were evaluated using the Phase 2 test dataset and the common entity-matching framework:

```text
dslim/bert-base-NER
gamug/sec-bert-finer-ord-ner
Jean-Baptiste/roberta-large-ner-english
ritam-m/bert-base-company-ner
musk1209/finsight-ner
```

Results:

| Model                                     |   TP |   FP |   FN | Precision | Recall |         F1 |
| ----------------------------------------- | ---: | ---: | ---: | --------: | -----: | ---------: |
| `musk1209/finsight-ner`                   |   11 |   47 |    4 |    0.1897 | 0.7333 | **0.3014** |
| `gamug/sec-bert-finer-ord-ner`            |   11 |   49 |    4 |    0.1833 | 0.7333 |     0.2933 |
| `Jean-Baptiste/roberta-large-ner-english` |    8 |   53 |    7 |    0.1311 | 0.5333 |     0.2105 |
| `ritam-m/bert-base-company-ner`           |    2 |    6 |   13 |    0.2500 | 0.1333 |     0.1739 |
| `dslim/bert-base-NER`                     |    8 |   70 |    7 |    0.1026 | 0.5333 |     0.1720 |

Under this benchmark configuration, `musk1209/finsight-ner` achieved the highest F1 among the evaluated candidates:

```text
Precision: 0.1897
Recall:    0.7333
F1:        0.3014
```

It was therefore selected as the NER component for the current Hybrid implementation.

This selection is specific to the evaluated candidates and the current weakly annotated benchmark. It does not establish that the model is globally optimal for IDA or financial-document NER.

---

# 14. Hybrid Extraction

The experiments showed that deterministic extraction and standalone NER provide complementary capabilities.

Deterministic extraction handles structured patterns and configured vocabulary:

```text
DATE
MONEY
PERCENTAGE
PRODUCT
known ORGANIZATION names
```

NER provides contextual recognition for:

```text
PERSON
ORGANIZATION
LOCATION
```

The resulting architecture is:

```text
Rules
   +
Dictionaries
   +
NER
   =
Broader entity coverage
```

The main Hybrid abstraction is implemented in:

[`src/extraction/entity_extractor.py`](../src/extraction/entity_extractor.py)

`EntityExtractor` combines:

```text
AutomaticAnnotator
        +
NERModel
        ↓
ExtractedEntity
```

The rest of the application can use a unified interface:

```python
entities = extractor.extract(
    text=text,
    context=context,
)
```

This keeps the extraction interface independent from the underlying extraction mechanisms.

---

# 15. Entity Merging and Conflict Resolution

The Hybrid extractor applies explicit rules when combining deterministic and NER predictions.

### Exact duplicates

If both systems produce the same span and label, only one entity is retained.

```text
Microsoft → ORGANIZATION
```

### Non-overlapping entities

Different non-overlapping entities can both be retained:

```text
Azure      → PRODUCT
Microsoft  → ORGANIZATION
```

### Overlapping entities

The current rule-priority labels are:

```text
DATE
MONEY
PERCENTAGE
PRODUCT
```

When an NER entity overlaps one of these priority rule-based entities, the rule-based entity is preserved.

For overlaps involving a non-priority rule-based entity, the NER entity can replace the existing overlapping entity.

The final entity list is sorted by character position.

This provides deterministic behavior when the two extraction mechanisms produce conflicting spans.

---

# 16. Extraction Pipeline and Output

The end-to-end extraction pipeline is implemented in:

[`src/extraction/extraction_pipeline.py`](../src/extraction/extraction_pipeline.py)

Input:

```text
data/processed/extraction/test.jsonl
```

Output:

```text
data/processed/extraction/predictions.jsonl
```

The latest pipeline execution processed:

```text
Chunks processed:          75
Chunks with entities:      37
Total predicted entities:  118
```

Each prediction preserves:

```text
text
label
character offsets
confidence
chunk metadata
document metadata
page information
```

The predictions provide the input for the final evaluation and error-analysis stages.

---

# 17. Evaluation Methodology

The final evaluation compares:

```text
1. Rule-based
2. NER
3. Hybrid
```

The selected NER model is:

```text
musk1209/finsight-ner
```

The evaluation uses the 75-chunk held-out test set.

The evaluator performs strict entity matching while normalizing case-only differences.

The metrics are:

```text
Precision
Recall
F1
```

The benchmark is useful for measuring consistency against the available annotations, but it has an important limitation: the reference annotations were generated automatically using the same deterministic annotation framework that forms part of the rule-based extraction system.

Therefore:

```text
AutomaticAnnotator
       ↓
Expected Entities

AutomaticAnnotator + NER
       ↓
Hybrid Predictions
```

Rule-based performance against this benchmark is therefore expected to be very strong.

The benchmark should not be interpreted as independent human-verified semantic ground truth.

---

# 18. Hybrid Evaluation Results

The current benchmark provides a quantitative basis for comparing the three extraction strategies.

The rule-based system can reproduce the deterministic annotations very closely because the annotations themselves were generated using the same rule system.

Consequently, a result such as:

```text
Precision = 100%
Recall    = 100%
F1        = 100%
```

for rule-based extraction should be interpreted as evidence of deterministic consistency rather than proof of perfect real-world semantic extraction.

The NER candidate comparison established:

```text
musk1209/finsight-ner

Precision: 0.1897
Recall:    0.7333
F1:        0.3014
```

under the current benchmark configuration.

The Hybrid system provides a broader prediction space by combining deterministic and contextual extraction, but its strict metrics are affected by the limited coverage of the weak annotations.

---

# 19. Error Analysis

A dedicated error-analysis process investigates mismatches between expected and predicted entities.

The analysis considers:

* expected entities;
* predicted entities;
* false positives;
* false negatives;
* entity labels;
* character offsets;
* confidence;
* source context.

Several recurring patterns were identified.

### NER overprediction

NER frequently identifies geographic or organizational expressions absent from the annotation dataset:

```text
United States → LOCATION
Ireland       → LOCATION
Singapore     → LOCATION
Japan         → LOCATION
India         → LOCATION
Australia     → LOCATION
Europe        → LOCATION
```

Some of these predictions are supported by the source text even though they are absent from the weak annotations.

### Boundary and label differences

Examples include:

```text
Gold:       Xbox
Prediction: xbox live → ORGANIZATION
```

and:

```text
Gold:       Office
Prediction: office 365 → ORGANIZATION
```

These mismatches involve entity boundaries, granularity, or labels.

### Tokenization artifacts

The NER model can produce subword fragments:

```text
cop   → ORGANIZATION
##ilo → ORGANIZATION
```

where the intended entity is:

```text
Copilot
```

Such outputs may require post-processing before being treated as final entities.

### Low-confidence predictions

Examples include:

```text
x          → ORGANIZATION   0.5190
outlook.   → ORGANIZATION   0.5417
i          → ORGANIZATION   0.6438
```

Confidence filtering may help remove some obvious noise, but confidence alone cannot resolve the broader annotation-coverage problem.

---

# 20. Evaluation Limitations

The most important limitation of Phase 2 is that the benchmark is based on weak, automatically generated annotations rather than exhaustive human-verified ground truth.

This creates two important consequences.

First, rule-based performance is inherently related to the annotation process because the same deterministic rules generate both the reference annotations and the rule-based predictions.

Second, a valid entity that is absent from the annotations is counted as a false positive under strict matching.

For example, one analyzed chunk contained explicit geographic references including:

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

The Hybrid extractor identified several of these as `LOCATION`, while the available annotation contained none.

Under strict evaluation:

```text
Prediction absent from annotation
            ↓
        False Positive
```

But:

```text
Prediction supported by source text
            ↓
May still be semantically valid
```

Therefore:

```text
Strict-evaluation False Positive
            ≠
Automatically confirmed semantic error
```

This limitation affects the interpretation of Precision, Recall, and F1 throughout Phase 2.

The current benchmark should therefore be understood as a **weakly annotated development and evaluation benchmark**, not exhaustive semantic ground truth.

---

# 21. Phase 2 Architecture

The final Phase 2 architecture is:

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
* quantitative evaluation;
* diagnostic error analysis.

Individual components can therefore be improved or replaced without redesigning the entire extraction pipeline.

---

# 22. Implementation Status

The following Phase 2 components are implemented and operational:

```text
✓ Entity schema
✓ Annotation guidelines
✓ ChromaDB sampling
✓ Deterministic sampling
✓ Weak annotation rules
✓ Regex extraction
✓ Dictionary extraction
✓ Automatic annotation
✓ Dataset generation
✓ Dataset validation
✓ Dataset analysis
✓ Train / validation / test splitting
✓ Entity evaluator
✓ Precision / Recall / F1
✓ Per-label evaluation
✓ Case-normalized matching
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
✓ Rule-based / NER / Hybrid evaluation
✓ Hybrid error analysis
✓ NER error analysis
```

The resulting implementation provides a complete Phase 2 baseline workflow from sampling and annotation through extraction, evaluation, and diagnostic analysis.

---

# 23. Limitations / Not Finished

The following areas are not considered production-quality completed components.

### Human-verified gold dataset

The current annotations are weak annotations. A smaller independently verified dataset is required for reliable measurement of semantic extraction quality.

### Final NER model

`musk1209/finsight-ner` is the current NER baseline selected under the Phase 2 benchmark configuration. It is not claimed to be the final or globally optimal model for IDA.

### Expanded domain entity coverage

The current implemented schema is:

```text
PERSON
ORGANIZATION
LOCATION
DATE
MONEY
PERCENTAGE
PRODUCT
```

Additional domain-specific categories can be introduced if concrete project requirements justify them and suitable annotation and evaluation data are available.

### Production-level accuracy benchmark

The current benchmark cannot provide a final measurement of real-world semantic extraction accuracy because the annotations are automatically generated and not exhaustive.

---

# 24. Future Work

The most useful future improvements are:

1. Create a small independently verified gold-standard dataset.
2. Re-evaluate the NER candidates against that dataset.
3. Add targeted post-processing for clearly identified NER artifacts.
4. Evaluate confidence filtering through systematic experiments.
5. Expand deterministic rules when concrete extraction requirements emerge.
6. Fine-tune a domain-specific NER model only if later requirements justify it.
7. Revisit semantic error analysis using higher-quality annotations.

Phase 2 does not need to become an open-ended NER research project. The current infrastructure is sufficient to support the next stage of IDA development.

---

# 25. Conclusion

Phase 2 established a maintainable annotation and hybrid entity-extraction foundation for IDA.

The resulting benchmark contains:

```text
Source ChromaDB chunks:        13,368
Sampled chunks:                   500
Annotated chunks:                 500
Weakly annotated entities:        771
Train:                             350
Validation:                         75
Test:                               75
Validation errors:                  0
```

The current extraction architecture combines:

```text
Deterministic Rules
        +
Dictionaries
        +
Contextual NER
        ↓
Unified ExtractedEntity
        ↓
Evaluation
        ↓
Error Analysis
```

Among the evaluated NER candidates, `musk1209/finsight-ner` achieved the highest F1 under the Phase 2 benchmark configuration and was selected as the current NER baseline.

The most important result of Phase 2 is not a single evaluation score, but the establishment of a reproducible extraction workflow covering:

```text
Sampling
    ↓
Weak Annotation
    ↓
Validation
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

The evaluation also established the limitations of the current benchmark. Because the annotations are automatically generated and not exhaustive, strict false positives cannot always be interpreted as genuine semantic extraction errors.

The next major improvement is therefore an independently verified gold-standard dataset. Until such data are available, the current implementation should be considered a **baseline extraction system**, rather than a final semantic NER solution.

**Phase 2 is considered complete as a baseline annotation, hybrid entity-extraction, evaluation, and error-analysis implementation.**
