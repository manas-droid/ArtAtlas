# Art-Based Retrieval System (v2)

## Overview

**Art-Based Retrieval System v2** improves upon v1 by introducing **concept-aware retrieval** while preserving:

* explainability
* determinism
* local-first execution
* no LLM dependency

v2 treats **art-historical essays as structured knowledge** and uses them to subtly improve artwork retrieval for **abstract stylistic and thematic queries**.

The system runs locally on **Ubuntu + PostgreSQL** and builds on a hybrid **lexical + semantic** retrieval pipeline.

---

## Motivation

### Problem in v1

In v1:

* Abstract queries (e.g. *“symbolism in still life”*, *“dramatic lighting”*) retrieved strong essays
* Artwork results were often weak or loosely related because:

  * museum metadata does not encode techniques or themes explicitly
  * concepts like *vanitas* or *chiaroscuro* live only in essays

### v2 Objective

> **Use essays as structured knowledge to improve artwork retrieval quality — without modifying metadata or using LLMs.**

---

## Core Idea: Concept-Aware Retrieval

v2 introduces a **concept layer** that sits between essays and artworks.

Concepts are:

* human-curated
* limited in number
* explicit and explainable

They are used to:

* propagate knowledge from essays to artworks (offline)
* influence ranking and recall safely (online)

---

## Concept Model

### Concept Types

Concepts fall into three categories:

* **genre** (e.g. Still Life, Vanitas)
* **technique** (e.g. Chiaroscuro, Tenebrism)
* **theme** (e.g. Symbolism, Realism)

### Concept Table

```sql
concept(id, name, type)
```

---

## Essay → Concept Mapping

Essays already *define* concepts.

Each essay (or essay chunk) is manually or semi-manually mapped to **1–3 concepts**.

```sql
essay_concept(essay_id, concept_id)
```

Design choices:

* No automatic NLP extraction
* No ontology inference
* Low noise, high authority

---

## Artwork → Concept Mapping (Offline)

Artworks do not explicitly encode concepts.

v2 infers **artwork–concept affinity** offline using embeddings.

### Offline Pipeline

For each concept:

1. Aggregate embeddings of essays mapped to the concept
2. Build a **concept prototype embedding**
3. Compare each artwork embedding to the prototype
4. Store only high-confidence matches

```sql
artwork_concept(artwork_id, concept_id, confidence_score)
```

Key properties:

* Offline only
* Deterministic
* Thresholded (confidence ≥ 0.7)
* Rebuildable

Concepts are **annotations**, not metadata.

---

## Primary vs Secondary Concepts

Not all concepts are allowed to drive retrieval.

### Primary Concepts

Used for **query expansion** (artwork recall).

Current primary set:

* Vanitas
* Still Life
* Landscape
* Genre Painting

These answer:

> *“What kind of artwork is the user looking for?”*

### Secondary Concepts

Used only for **re-ranking and explanation**.

Examples:

* Chiaroscuro
* Tenebrism
* Symbolism
* Realism
* Spatial Realism
* Dutch Golden Age

These explain *how* or *why*, not *what*.

---

## Query Flow in v2

### Step 1 — Base Retrieval (v1 behavior)

* Lexical search (Postgres FTS)
* Semantic search (pgvector)
* Retrieve artworks and essays independently

### Step 2 — Concept Detection (Query Side)

* Detect concepts from query via essay embeddings
* Assign confidence scores

### Step 3 — Concept-Aware Artwork Expansion (Guarded)

Artwork query expansion occurs **only if all conditions are met**:

* concept confidence ≥ threshold
* concept is **primary**
* concept has **artwork mappings**

Expansion is:

* query-time only
* limited (top 1–2 concepts)
* never applied to essays

### Step 4 — Concept-Aware Re-ranking

Final score:

```
final_score =
  w1 * lexical_score +
  w2 * semantic_score +
  w3 * concept_score
```

Essays:

* receive a small fixed boost if mapped to query concepts

Artworks:

* receive a confidence-weighted boost based on concept overlap

---

## Explainability Guarantees

Every result can be explained using:

* matched concepts
* stored confidence scores
* deterministic ranking logic

Example explanation:

> “This artwork ranked higher because it has a strong association with the ‘Vanitas’ concept detected in the query.”

No hidden inference.

---

## Observed Improvements vs v1

* Better coherence for genre + theme queries
* Vanitas artworks surface for symbolic still-life queries
* Reduced noise from lighting-only concepts
* No regression on concrete or control queries

Improvements are **subtle but consistent**, by design.

---

## Explicit Non-Goals (Still Out of Scope)

* LLM-generated text
* Image feature extraction
* Curatorial text scraping
* Automatic concept discovery
* Ontologies or graphs

---

## Status

v2 is **complete and frozen**

No further tuning is planned without introducing **new data sources**.

---

## One-Sentence Summary

> **v2 enhances artwork retrieval by using essays as structured, explainable knowledge while preserving metadata integrity and system determinism.**

---

---
