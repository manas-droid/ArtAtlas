## ArtAtlas v3.0 — Evidence Bundles & Explanation Graph

### Overview

v3.0 introduces **Evidence Bundles** and a **Query-Scoped Explanation Graph** as first-class outputs of the ArtAtlas retrieval pipeline.

While v2 focused on *what* to retrieve (concept-aware ranking with strict determinism), v3.0 focuses on *why* a given set of results together forms a valid, defensible answer.

This version does **not** change retrieval logic. Instead, it structures existing results into explicit, inspectable evidence artifacts.

---

### Motivation

Traditional retrieval systems return ranked lists.
Even explainable systems typically justify results *individually*.

However, art-historical reasoning relies on **structured evidence**, where:

* artworks,
* stylistic or thematic concepts,
* and authoritative textual sources
  work together to support an interpretation.

v3.0 addresses this gap by making **evidence and reasoning structure explicit**, without introducing generative models or speculative inference.

---

### Key Concepts

#### Evidence Bundle

An **Evidence Bundle** is a query-scoped structure that groups:

* one or more artworks
* supporting essay excerpts
* the concepts that connect them
* explicit justification rules
* confidence and provenance metadata

Each bundle answers the question:

> *“Why are these artworks relevant to this query?”*

Bundles are:

* deterministic
* derived strictly from v2 data and rules
* created only when sufficient supporting evidence exists

---

#### Explanation Graph

For each query, v3.0 constructs a **small, explicit Explanation Graph** that captures:

```
Query → Concept → Evidence Bundle → Artworks / Essay Snippets
```

The graph:

* is generated at query time
* contains only verifiable edges
* allows every claim to be traced back to concrete data

No edges are inferred without stored mappings or confidence thresholds.

---

### What v3.0 Adds

Backend:

* Evidence Bundle construction (runtime, query-scoped)
* Explanation Graph generation
* Extended search API response including evidence artifacts

Frontend (Minimal):

* Single-page UI to visualize:

  * Evidence Bundles
  * Explanation Graph
  * Bundle-level details (artworks + essays)
* No interpretation or generation logic in the UI

---

### What v3.0 Does *Not* Do

* No new retrieval or ranking logic
* No LLM usage
* No free-form explanation generation
* No concept-to-concept reasoning
* No persistent storage of explanation artifacts
* No complex graph visualizations (e.g., D3)

These are intentionally deferred to later versions.

---

### API Output (Simplified)

The existing search endpoint is extended to return:

```json
{
  "query": "...",
  "ranked_results": [...],
  "evidence_bundles": [...],
  "explanation_graph": {
    "nodes": [...],
    "edges": [...]
  }
}
```

The frontend renders these artifacts *as-is* and does not derive additional logic.

---

### Design Principles

* **Determinism over generation**
* **Structure before polish**
* **Explainability as data, not prose**
* **API-first, UI-light**
* **Incremental evolution by version**

---

### Status

* v3.0 is focused, stable, and demo-ready
* UI is intentionally minimal and exists only to expose reasoning artifacts
* Future versions will extend this foundation incrementally
