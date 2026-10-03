# Annotation Guidelines

## 1. Purpose

This document defines the annotation rules for the initial Named Entity Recognition (NER) dataset used in the Intelligent Document Analysis project.

The goal is to identify important entities in business and financial documents using a small, consistent schema suitable for NER model development and evaluation.

The guidelines are designed to support reproducible annotation and future human verification of the automatically generated weak annotations.

---

## 2. Entity Schema

The target annotation schema contains seven entity types:

* PERSON
* ORGANIZATION
* LOCATION
* DATE
* MONEY
* PERCENTAGE
* PRODUCT

The initial automated weak-annotation implementation covers five categories:

* ORGANIZATION
* PRODUCT
* DATE
* MONEY
* PERCENTAGE

PERSON and LOCATION are included in the target schema for NER and future annotation/model development.

---

## 3. General Annotation Rules

### 3.1 Use only defined labels

Do not create new labels during annotation.

If a piece of text does not belong to one of the defined categories, leave it unannotated.

### 3.2 Annotate the complete entity span

When an entity contains multiple words, annotate the complete meaningful span.

Example:

```text
Satya Nadella
```

Correct:

```text
PERSON = "Satya Nadella"
```

Not:

```text
PERSON = "Satya"
```

### 3.3 Preserve the original text

Entity text must be copied exactly from the source.

Do not normalize spelling, capitalization, punctuation, or whitespace inside an entity.

### 3.4 Exclude surrounding context

Annotate only the entity itself.

Example:

```text
Microsoft announced new products
```

Correct:

```text
ORGANIZATION = "Microsoft"
```

Do not annotate surrounding phrases such as:

```text
"Microsoft announced"
"new products"
```

### 3.5 Avoid overlapping or nested entities

The initial annotation scheme does not use overlapping or nested entities.

When multiple interpretations are possible, select the single span that best matches the defined schema.

---

# 4. Entity Definitions

## 4.1 PERSON

### Definition

A PERSON is the name of an individual human being.

### Examples

```text
Satya Nadella
Bill Gates
Amy Hood
```

Annotate:

```text
"Satya Nadella" → PERSON
```

Do not annotate generic groups or roles such as:

```text
customers
employees
investors
management
```

---

## 4.2 ORGANIZATION

### Definition

ORGANIZATION represents companies, corporations, institutions, government organizations, agencies, and other formally named organizations.

### Examples

```text
Microsoft
Microsoft Corporation
U.S. Securities and Exchange Commission
```

Annotate:

```text
"Microsoft" → ORGANIZATION
```

Do not annotate generic descriptions such as:

```text
company
customers
management
employees
```

---

## 4.3 LOCATION

### Definition

LOCATION represents named geographic locations, including:

* countries
* cities
* states or provinces
* regions
* continents
* other named geographic areas

### Examples

```text
Ukraine
United States
Seattle
Europe
```

Annotate:

```text
"United States" → LOCATION
```

Do not annotate generic terms such as:

```text
market
region
country
```

unless they refer to a specific named geographic entity.

---

## 4.4 DATE

### Definition

DATE represents explicit temporal expressions referring to a specific date, year, month, period, or date range.

### Examples

```text
June 30, 2021
2020
fiscal year 2021
the first quarter of 2022
```

Annotate:

```text
"June 30, 2021" → DATE
"2020" → DATE
```

If an expression clearly identifies a relevant time period, annotate the complete temporal expression.

---

## 4.5 MONEY

### Definition

MONEY represents monetary amounts together with their associated currency or monetary unit.

### Examples

```text
$339 million
$50 billion
€5 million
USD 10 million
```

Annotate the complete monetary expression:

```text
"$339 million" → MONEY
"$50 billion" → MONEY
```

Do not annotate generic financial concepts such as:

```text
revenue
profit
cost
financial results
```

unless the expression itself contains a monetary value.

---

## 4.6 PERCENTAGE

### Definition

PERCENTAGE represents explicit percentage values.

### Examples

```text
36 percent
10%
5.5%
```

Annotate the complete percentage expression:

```text
"36 percent" → PERCENTAGE
"10%" → PERCENTAGE
```

A number by itself is not a percentage:

```text
36
500
10 million
```

Annotate a percentage only when the expression clearly represents a percentage value.

---

## 4.7 PRODUCT

### Definition

PRODUCT represents named commercial products, software products, services, platforms, or product families.

### Examples

```text
Microsoft 365
Windows
Azure
Xbox
```

Annotate:

```text
"Microsoft 365" → PRODUCT
"Windows" → PRODUCT
```

Do not annotate generic descriptions such as:

```text
software
cloud services
operating system
```

unless they are part of a named product expression.

---

# 5. Ambiguous Cases

## 5.1 Product vs Organization

```text
Microsoft       → ORGANIZATION
Microsoft 365   → PRODUCT
Azure           → PRODUCT
```

If the expression refers to the company itself, use ORGANIZATION.

If it refers to a named commercial product or service, use PRODUCT.

---

## 5.2 Location vs Organization

```text
United States
→ LOCATION

U.S. Securities and Exchange Commission
→ ORGANIZATION
```

A geographic name is LOCATION unless it is part of a larger organization name.

---

## 5.3 Date vs Number

```text
2021
```

Annotate as DATE when it represents a year.

If the number is used as a quantity rather than a year, it should not automatically be labeled DATE.

For example:

```text
2021 employees
```

should not be labeled DATE merely because the number resembles a year.

---

## 5.4 Money vs Number

```text
$500 million → MONEY
500 million users → no MONEY annotation
```

Only monetary quantities are MONEY.

---

# 6. Annotation Boundaries

Entity boundaries must be precise.

Example:

```text
The company generated $143 billion in revenue.
```

Correct:

```text
MONEY = "$143 billion"
```

Incorrect:

```text
MONEY = "$143 billion in revenue"
```

The entity should not include surrounding descriptive words.

---

# 7. Punctuation

Include punctuation when it is part of the entity expression.

Examples:

```text
"$339 million" → include "$"
"36%" → include "%"
"June 30, 2021" → include the complete date expression
```

Do not include surrounding sentence punctuation.

Example:

```text
Microsoft.
```

Correct:

```text
ORGANIZATION = "Microsoft"
```

The final period is not part of the entity.

---

# 8. Missing or Uncertain Entities

If an annotation is genuinely uncertain, do not invent a label.

For the initial dataset, consistency is more important than aggressive annotation.

Uncertain cases should be recorded separately when possible so they can be reviewed during later annotation or dataset refinement.

---

# 9. Quality Rules

Every annotation should satisfy the following:

1. The entity belongs to one of the defined labels.
2. Character offsets match the original source text.
3. Entity text exactly matches the selected span.
4. Entity boundaries are precise.
5. No overlapping entities are created.
6. No unsupported labels are introduced.

These rules provide the structural requirements later checked by dataset validation.

---

# 10. Initial Target Schema

The initial target schema is:

```text
PERSON
ORGANIZATION
LOCATION
DATE
MONEY
PERCENTAGE
PRODUCT
```

The schema may be expanded or refined in later iterations based on project requirements, annotation review, and model error analysis.

The schema defines the entity types that the project can represent; individual annotations determine which entity occurrences actually appear in a given document or dataset.
