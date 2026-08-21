# Annotation Guidelines

## 1. Purpose

This document defines the annotation rules for the initial
Named Entity Recognition (NER) dataset used in Task 2 of the
Intelligent Document Analysis project.

The goal is to identify important entities in business and
financial documents while keeping the annotation scheme
small, consistent, and suitable for transformer-based NER.

---

## 2. Entity Labels

The initial annotation schema contains seven entity types:

- PERSON
- ORG
- LOCATION
- DATE
- MONEY
- PERCENT
- PRODUCT

---

## 3. General Annotation Rules

### 3.1 Annotate only entities from the defined schema

Do not create new labels during annotation.

If a piece of text does not belong to one of the seven defined
categories, leave it unannotated.

### 3.2 Annotate the complete entity span

When an entity contains multiple words, annotate the complete
meaningful span.

Example:

"Satya Nadella"

Annotate:

PERSON = "Satya Nadella"

Not:

PERSON = "Satya"

### 3.3 Preserve the original text

Entity text must be copied exactly from the source text.

Do not normalize spelling, capitalization, punctuation, or
whitespace inside an entity.

### 3.4 Do not annotate surrounding context

Only the entity itself should be annotated.

Example:

"Microsoft announced new products"

Annotate:

ORG = "Microsoft"

Do not annotate:

"Microsoft announced"
"new products"

### 3.5 Nested entities

Do not create overlapping or nested entities in the initial
dataset.

Choose the single entity span that best matches the schema.

---

# 4. Entity Definitions

## 4.1 PERSON

### Definition

A PERSON is the name of an individual human being.

### Examples

"Satya Nadella"
"Bill Gates"
"Amy Hood"

### Annotate

"Satya Nadella" → PERSON

### Do not annotate

"customers"
"employees"
"investors"
"management"

These refer to groups or roles rather than named individuals.

---

## 4.2 ORG

### Definition

ORG represents companies, corporations, institutions,
government organizations, agencies, or other formally named
organizations.

### Examples

"Microsoft"
"Microsoft Corporation"
"U.S. Securities and Exchange Commission"

### Annotate

"Microsoft" → ORG

### Do not annotate

"company"
"customers"
"management"
"employees"

These are generic descriptions rather than named organizations.

---

## 4.3 LOCATION

### Definition

LOCATION represents named geographic locations.

This includes:

- countries
- cities
- states/provinces
- regions
- continents
- other named geographic areas

### Examples

"Ukraine"
"United States"
"Seattle"
"Europe"

### Annotate

"United States" → LOCATION

### Do not annotate

"market"
"region"
"country"

when they are used generically rather than as a specific
geographic name.

---

## 4.4 DATE

### Definition

DATE represents explicit temporal expressions referring to a
specific date, year, month, period, or date range.

### Examples

"June 30, 2021"
"2020"
"fiscal year 2021"
"the first quarter of 2022"

### Annotate

"June 30, 2021" → DATE

"2020" → DATE

### General rule

If the expression clearly identifies a time period relevant
to the document, annotate it as DATE.

---

## 4.5 MONEY

### Definition

MONEY represents monetary amounts and their associated currency
or monetary unit.

### Examples

"$339 million"
"$50 billion"
"€5 million"
"USD 10 million"

### Annotate the complete monetary expression

"$339 million" → MONEY

"$50 billion" → MONEY

### Do not annotate

"revenue"
"profit"
"cost"
"financial results"

unless the expression itself contains a monetary value.

---

## 4.6 PERCENT

### Definition

PERCENT represents percentages or explicit percentage values.

### Examples

"36 percent"
"10%"
"5.5%"

### Annotate

"36 percent" → PERCENT

"10%" → PERCENT

### Do not annotate

"36"
"five percent growth"

if the percentage expression is not clearly represented as a
percentage value.

When a percentage is explicitly expressed, annotate the complete
percentage expression.

---

## 4.7 PRODUCT

### Definition

PRODUCT represents named commercial products, software products,
services, platforms, or product families.

### Examples

"Microsoft 365"
"Windows"
"Azure"
"Xbox"

### Annotate

"Microsoft 365" → PRODUCT

"Windows" → PRODUCT

### Do not annotate

"software"
"cloud services"
"operating system"

when they are generic descriptions rather than named products.

---

# 5. Ambiguous Cases

When an entity could belong to multiple categories, use the
following rules.

## Product vs Organization

"Microsoft" → ORG

"Microsoft 365" → PRODUCT

"Azure" → PRODUCT

If the expression refers to the company itself, use ORG.
If it refers to a named commercial product or service, use PRODUCT.

---

## Location vs Organization

"United States" → LOCATION

"U.S. Securities and Exchange Commission" → ORG

A geographic name is LOCATION unless it is part of a larger
organization name.

---

## Date vs Number

"2021" → DATE when it represents a year.

"2021 employees" → DATE for "2021" only if it clearly refers
to a year; otherwise do not annotate it.

---

## Money vs Number

"$500 million" → MONEY

"500 million users" → no MONEY annotation.

Only monetary quantities are MONEY.

---

# 6. Annotation Boundaries

Entity boundaries must be precise.

Example:

"The company generated $143 billion in revenue."

Correct:

MONEY = "$143 billion"

Incorrect:

MONEY = "$143 billion in revenue"

The entity should not include surrounding descriptive words.

---

# 7. Punctuation

Include punctuation only when it is part of the entity expression.

Examples:

"$339 million" → include "$"

"36%" → include "%"

"June 30, 2021" → include the complete date expression

Do not include surrounding sentence punctuation.

Example:

"Microsoft."

Correct:

ORG = "Microsoft"

The period is not part of the entity.

---

# 8. Missing or Uncertain Entities

If an annotation is genuinely uncertain, do not invent a label.

For the initial dataset, consistency is more important than
aggressive annotation.

Uncertain examples should be recorded separately for later review.

---

# 9. Quality Rules

Every annotation should satisfy:

1. The entity belongs to one of the seven defined labels.
2. The character offsets match the original text.
3. The entity text exactly matches the selected span.
4. Entity boundaries are precise.
5. No overlapping entities exist.
6. No unsupported labels are introduced.

---

# 10. Initial Entity Schema

The initial schema is:

PERSON
ORG
LOCATION
DATE
MONEY
PERCENT
PRODUCT

This schema may be expanded in later iterations based on
error analysis and project requirements.