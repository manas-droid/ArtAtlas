# Art-Based Retrieval System — v2 Design Document

## 1. Purpose of v2

### Problem Statement

In v1, the system successfully retrieves:

* artworks (visual examples)
* essay chunks (conceptual explanations)

However, for **abstract stylistic queries** (e.g. *“dramatic lighting”*), artwork relevance is limited because:

* artwork metadata rarely encodes visual techniques explicitly
* concepts such as *chiaroscuro* live only in essays, not in artwork records

### v2 Objective

> **Use essays as structured knowledge to improve artwork retrieval quality, while preserving explainability and avoiding LLM dependence.**

v2 introduces **concept propagation** from essays to artworks.

---

## 2. Design Goals

### Functional Goals

* Improve artwork relevance for abstract, stylistic queries
* Preserve hybrid search behavior (lexical + semantic)
* Maintain deterministic, explainable ranking

### Non-Goals (Explicitly Out of Scope)

* No LLM-generated text
* No image-based feature extraction
* No artist biographies
* No full historical or ontological reasoning
* No automatic concept discovery

---

## 3. High-Level Architecture

### v1 Architecture (Baseline)

```
Query
 ├─ Lexical Search (FTS)
 ├─ Semantic Search (Embeddings)
 └─ Fallback Logic
      └─ Results: Artworks + Essays
```

### v2 Architecture (Extended)

```
Query
 ├─ Lexical Search (FTS)
 ├─ Semantic Search (Embeddings)
 ├─ Concept Matching
 │    ├─ Essay → Concept
 │    └─ Artwork → Concept
 └─ Concept-Aware Ranking
      └─ Results: Better Artworks + Essays
```

v2 **extends** v1 — it does not replace it.

---

## 4. Core v2 Concept Model

### 4.1 Concept Definition

A **concept** represents a reusable art-historical idea, such as:

* a technique
* a genre
* a stylistic pattern

Examples:

* chiaroscuro
* tenebrism
* vanitas
* still life
* dramatic lighting

Concepts are:

* human-curated
* limited in number
* explainable

---

### 4.2 Concept Table

```sql
CREATE TABLE concept (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    concept_type TEXT NOT NULL  -- 'technique' | 'genre' | 'movement'
);
```

Initial size:

* 10–20 concepts total (v2 scope)

---

## 5. Essay → Concept Mapping

### Purpose

Essays already encode authoritative explanations of concepts.
v2 makes this explicit.

### Table: `essay_chunk_concept`

```sql
CREATE TABLE essay_chunk_concept (
    essay_chunk_id INT REFERENCES essay_chunk(id),
    concept_id INT REFERENCES concept(id),
    PRIMARY KEY (essay_chunk_id, concept_id)
);
```

### Population Strategy (v2)

* Manual or semi-manual tagging
* Each essay chunk:

  * 1–3 associated concepts max
* No automatic NLP extraction in v2

### Rationale

* Keeps noise low
* Preserves explainability
* Avoids overfitting or hallucinated concepts

---

## 6. Artwork → Concept Affinity

### Motivation

Artwork–concept affinity is computed using enriched textual surrogates for artworks (metadata + available curatorial descriptions). Direct visual inference is not attempted.

Artwork–concept affinity in v2 relies on relative embedding alignment, not absolute semantic understanding. Concept scores are used strictly as weak, bounded ranking signals.
---

### 6.1 Offline Affinity Computation

For each artwork:

1. Compute similarity to essay chunks linked to a concept
2. Aggregate similarity (e.g. max or mean)
3. Assign concept if similarity exceeds threshold

This is an **offline batch process**.

---

### 6.2 Artwork Concept Table

```sql
CREATE TABLE artwork_concept (
    artwork_id INT REFERENCES artwork(id),
    concept_id INT REFERENCES concept(id),
    confidence_score FLOAT NOT NULL,
    PRIMARY KEY (artwork_id, concept_id)
);
```

Constraints:

* Only high-confidence associations stored
* Confidence is numeric and inspectable

---

### 6.3 Why Offline?

* No runtime cost
* Stable, reproducible results
* Easy to debug and re-run
* Avoids query-time complexity

---

## 7. Query Processing in v2

### 7.1 Concept Detection from Query

At query time:

1. Match query embedding against **concept-linked essay chunks**
2. Identify top matching concepts
3. Use concepts only as *ranking signals*, not filters

No hard concept filtering is performed.

---

### 7.2 Concept-Aware Ranking

Final ranking score:

```
final_score =
    w1 * lexical_score
  + w2 * semantic_score
  + w3 * concept_support_score
```

Where:

* `concept_support_score` reflects how strongly an artwork aligns with concepts relevant to the query

Weights are tuned conservatively:

* semantic remains dominant
* concept provides *boost*, not replacement

---

## 8. Explainability Guarantees

v2 maintains explainability by:

* Explicit concept tables
* Numeric confidence scores
* Deterministic ranking logic

Example explanation:

> “This artwork ranked higher because it aligns strongly with the ‘chiaroscuro’ concept explained in retrieved essays.”

No black-box reasoning.

---

## 9. API Impact

### v2 API Additions (Non-Breaking)

Optional fields added to artwork results:

```json
"concepts": [
  {
    "name": "chiaroscuro",
    "confidence": 0.81
  }
]
```

Essays remain unchanged.

Clients can ignore this field safely.

---

## 10. Data Scope in v2

### Essays

* Still limited to **Dutch Golden Age**
* No expansion to new movements yet

### Artworks

* Same Met Museum dataset as v1
* Enriched via concept propagation

This ensures:

* controlled evaluation
* clean comparison vs v1

---

## 11. Evaluation Criteria

v2 is considered successful when:

* Queries like **“dramatic lighting”** return:

  * essays explaining the technique
  * artworks that visually demonstrate it
* Ranking improvements are observable
* Behavior remains explainable
* No regression in v1 query performance

---

## 12. Known Limitations (Accepted)

* Concepts are curated, not discovered
* No image-level visual analysis
* Some false positives expected at low confidence
* No automatic concept taxonomy

These are intentional tradeoffs.

---

## 13. Roadmap Beyond v2 (Preview)

### v3 Possibilities (Not Implemented)

* Automatic concept discovery
* Visual feature extraction
* Artist-level concept aggregation
* LLM-assisted explanations

v2 does not assume or require these.

---

## 14. Summary

v2 extends v1 by:

* Treating essays as structured knowledge
* Propagating conceptual understanding to artworks
* Improving retrieval for abstract stylistic queries
* Preserving explainability and system clarity

The system remains:

* local-first
* deterministic
* non-LLM-dependent

---

### One-Sentence Summary

> **v2 transforms essays from passive explanations into active knowledge sources that improve artwork retrieval through explicit, explainable concept propagation.**

---

Next in line:

* create **ER diagrams** for v2
* write the **offline concept-assignment pipeline**
* choose **similarity thresholds**
* plan **v2 evaluation experiments**
