# ArtAtlas

**ArtAtlas** is a local-first, explainable art retrieval system designed to answer *why* specific artworks support art-historical ideas — not just *what* matches a query.

The system prioritizes:

* deterministic retrieval
* traceable evidence
* scoped, versioned evolution
* no black-box reasoning or LLM-generated explanations

ArtAtlas runs fully locally on Ubuntu using PostgreSQL + pgvector.

## Full Result Tab:

![Full Result Tab](/media/full-results-tab.png "Full Result Tab")




## Explanation Tab:
![Explanation Tab](/media/explanation-tab.png "Explanation Tab")


---

## Design Philosophy

ArtAtlas is built incrementally.
Each version introduces **one flagship capability**, is **explicitly frozen**, and serves as a stable foundation for the next.

> If a system cannot explain *why* it retrieved something, it should not pretend it understands it.

---

## Version Overview

### v2 — Concept-Aware Retrieval (Frozen)

**Goal:**
Introduce a semantic layer that helps guide retrieval without sacrificing determinism.

**What v2 introduced:**

* Hybrid retrieval:

  * lexical (Postgres FTS)
  * semantic (vector embeddings)
* A **human-curated concept layer**
  Examples:

  * Dutch Golden Age
  * Still Life
  * Vanitas
  * Chiaroscuro
* Concepts detected at query time with confidence
* Concepts used to:

  * guard query expansion
  * re-rank results lightly
* Essays treated as **knowledge sources**, not evidence

**What v2 did *not* do:**

* No UI
* No explanation of *why* artworks support concepts
* No opaque reasoning

v2 answers:

> *“What should I retrieve?”*

---

### v3.0 — Evidence Bundles & Explanation Graph (Frozen)

**Goal:**
Explain *why* specific artworks support specific concepts for a query.

**Key ideas introduced:**

#### Evidence Bundles

* One bundle per concept per query
* Each bundle contains:

  * artworks
  * artwork–concept confidence
  * aggregate bundle confidence
* Mapping computed at runtime via embedding similarity

#### Explanation Graph

* Runtime-only, validated graph
* Nodes:

  * query
  * concept
  * evidence bundle
  * artwork
* Edges:

  * query → concept
  * concept → bundle
  * bundle → artwork
* Strict validation:

  * no orphan nodes
  * no cycles
  * confidence consistency enforced

**UI principles introduced:**

* Users never see graphs
* Users see **concept-first explanations**
* Only artworks that appear in the explanation graph are shown
* Essays provide context, not evidence

v3.0 answers:

> *“Why does this artwork support this idea?”*

---

### v3.1 — Retrieval Transparency Layer (Frozen)

**Goal:**
Make retrieval *inspectable* without changing retrieval logic or explanation semantics.

**What v3.1 introduced:**

* A **retrieval trace** per result
* Clear separation of signals:

  * lexical match
  * semantic similarity
* No interpretation, only observation
* Retrieval trace is:

  * runtime-only
  * optional
  * does not affect ranking
* UI shows:

  * which signals contributed
  * where they came from
  * how strong they were (without claims of meaning)

**What v3.1 explicitly avoided:**

* No concept semantics in retrieval trace
* No token-level semantic explanations
* No inferred ranking logic
* No metadata boosts

v3.1 answers:

> *“How was this result retrieved?”*

---

### v3.2 — Dataset Expansion & Field-Aware Ingestion (Frozen)

**Goal:**
Improve retrieval quality by improving **data quality**, not algorithms.

**What v3.2 introduced:**

* Dataset expansion across:

  * Dutch Golden Age
  * Baroque
  * Impressionism
  * Cubism (constrained modern contrast)
* New movement- and technique-focused essays
* Field-aware `searchable_text` ingestion:

  * title
  * artist
  * medium
  * culture
  * department
  * (optional) tags
* No schema changes
* No ranking changes
* No UI changes

**Important design decision:**

* Art movements are modeled as **concepts**, not metadata fields
* Artwork–movement relationships are:

  * inferred
  * confidence-weighted
  * derived from essay ↔ artwork similarity
* Dates and artist names are contextual signals, not hard rules

**What v3.2 improved:**

* Stronger essay anchors
* Higher likelihood of artworks attaching to movement concepts
* Richer lexical provenance
* More convincing explanation bundles

v3.2 answers:

> *“Is the dataset rich and structured enough to support good retrieval?”*

---



###  v3.3 - Field-Aware Lexical Ordering (Frozen)

v3.3 refines result ordering using field-aware lexical signals introduced in v3.2, without changing retrieval candidates, explanation logic, or data semantics.
This version focuses strictly on ranking quality, improving how results are ordered once they have already been retrieved.

By leveraging structured searchable_text fields (e.g. title, artist, medium, tags), v3.3 applies conservative, explicit weighting to lexical matches based on where they occur. Matches in semantically strong fields such as artist and title are gently favored over weaker, generic fields like department or culture. Semantic similarity scores remain untouched, and no new retrieval signals are introduced.

Importantly, v3.3 guarantees that candidate sets are identical to v3.2 - only ordering changes. Explanation Graphs, Evidence Bundles, and retrieval transparency remain byte-for-byte consistent. This ensures that results feel more intuitive to users while preserving ArtAtlas’s core contract of honesty, explainability, and version discipline.

v3.3 answers:

> *"Are the best results ordered intuitively without changing meaning?"*

---

## What ArtAtlas Is *Not*

* ❌ Not an LLM-reasoning system
* ❌ Not an ontology or knowledge graph
* ❌ Not a rule-based art historian
* ❌ Not a black-box recommender

ArtAtlas does not guess.
If evidence is weak, results stay sparse — by design.

---

## Current State

| Version | Status |
| ------- | ------ |
| v2      | Frozen |
| v3.0    | Frozen |
| v3.1    | Frozen |
| v3.2    | Frozen |
| v3.3    | Frozen |

---

## Looking Ahead

Future versions may explore:
* query normalization (v3.4)
* multi-institution ingestion (v4.x)
* richer UI affordances

But each will remain:

* scoped
* explainable
* backward-compatible

---

## Core Principle (Final)

> **ArtAtlas prefers being honest over being impressive.**
> If something cannot be justified, it is not shown.
