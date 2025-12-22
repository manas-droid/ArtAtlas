## Expanded problem statement

### Context

Museum collection APIs (e.g., The Met), Wikidata, and high-quality essays/blog posts contain complementary information about artworks and art movements. Today, it’s hard for a learner (or a museum visitor) to ask a natural question like:

* “Show me paintings from Dutch Golden Age that use chiaroscuro—give examples and explain why.”
* “Find artworks related to ‘Bacchus and Ariadne’ and summarize the movement + iconography.”

…and get a **visually grounded** answer with **traceable sources**.

### Problem

Build a **local-first, multi-source, multi-modal retrieval and visualization system** that:

1. Ingests and normalizes data from:

   * The Met Museum public API (object metadata + image URLs)
   * Wikidata (movement/artist/style relationships)
   * Curated blog/essay text sources (movement explainers, critiques)
2. Indexes both **text** and **images** (via image captions/metadata + optional image embeddings).
3. Lets users query and **see the retrieval**:

   * ranked results with **image thumbnails**
   * highlighted text snippets + provenance
   * filters (movement, period, medium, artist, museum department)
4. Produces a clean, demo-able UI that makes the retrieval explainable and video-friendly.

### Goal

Create a portfolio-grade system that demonstrates:

* data ingestion + entity resolution
* vector search + hybrid retrieval (BM25 + embeddings)
* multi-modal UX (images + text)
* “why this result?” explainability

### Non-goals (for v1)

* No paid APIs / cloud dependency (everything runs locally on Ubuntu)
* Not trying to be a perfect art-historian model (focus on retrieval quality + UX)
* Not building full annotation tools or crowdsourcing workflows

---

## Software Design Document (SDD)

### 1) Overview

**Project name:** ArtAtlas (working name)
**One-liner:** Local-first multi-source art retrieval engine with multi-modal result visualization.

**Primary user:** Student/enthusiast who wants to explore artworks + movements with evidence.
**Secondary user:** Creator showcasing a visually engaging technical demo video.

---

### 2) User stories

**U1 — Search & explore**

* As a user, I can type a query (“Impressionism city scenes at dusk”) and get ranked results with thumbnails and snippets.

**U2 — Filter & refine**

* As a user, I can filter results by movement, time range, medium, artist, or source.

**U3 — Evidence & provenance**

* As a user, I can click a result and see where it came from (Met object page, Wikidata entity, essay URL + extracted snippet).

**U4 — Movement drill-down**

* As a user, I can open a movement page (e.g., “Baroque”) and see:

  * definition summary (from curated essays)
  * key artists/works (from Wikidata + Met objects)
  * representative images in a grid

**U5 — Visualize retrieval**

* As a user, I can switch to a “retrieval view” that shows:

  * top-k ranked items
  * score breakdown (BM25 vs vector vs metadata boost)
  * embedding neighborhood (optional scatter plot / cluster view)

---

### 3) Functional requirements

#### Data ingestion

* **FR1:** Import Met objects (metadata + image URLs) by department/criteria.
* **FR2:** Query Wikidata via SPARQL for:

  * movements, artists, influences, locations, time periods
  * mappings between artist ↔ movement, artwork ↔ artist (where possible)
* **FR3:** Ingest essays/blog posts:

  * raw HTML/text → cleaned text
  * chunking into passages
  * store source URL + title + author/date if available

#### Normalization & linking

* **FR4:** Normalize entities (Artist, Artwork, Movement) into canonical tables.
* **FR5:** Link Met objects to Wikidata entities when possible:

  * via artist name + birth/death + known IDs (when available)
  * fallback: fuzzy match with confidence score + manual override support

#### Indexing & retrieval

* **FR6:** Build a hybrid search index:

  * BM25 (lexical) over text fields + essay chunks
  * Vector search over embeddings for semantic retrieval
* **FR7:** Support query parsing:

  * detect filters from query (“oil on canvas”, “1890–1910”, “Monet”)
  * allow explicit filter chips in UI
* **FR8:** Return results with:

  * thumbnail
  * title/artist/date/movement
  * snippet (for essay results) or description (for museum objects)
  * provenance and confidence/linking info

#### Visualization

* **FR9:** Grid/list view for results with lazy-loaded thumbnails.
* **FR10:** Detail panel for selected item:

  * images, metadata, related entities, sources
* **FR11:** Retrieval explanation view:

  * show score components and match highlights
* **FR12 (optional):** Embedding “map” view (2D projection) for top results.

---

### 4) Non-functional requirements

* **NFR1:** Local-first: runs on Ubuntu, no cloud requirement.
* **NFR2:** Reproducible: `docker compose up` (recommended) or `make run`.
* **NFR3:** Reasonable performance:

  * Search response < 500ms for typical queries on a few hundred thousand chunks (after warmup)
* **NFR4:** Respect external sources:

  * rate limiting + caching for API calls
  * store source URLs and attribution
* **NFR5:** Maintainability:

  * clear module boundaries (ingestion, indexing, API, UI)
  * schema migrations
* **NFR6:** Observability:

  * structured logs + ingestion progress metrics

---

### 5) System architecture

**High-level components**

1. **Ingestion workers**

   * Met API importer
   * Wikidata importer (SPARQL)
   * Essay ingestion (crawler + cleaner)
2. **Processing pipeline**

   * cleaning, chunking, normalization
   * entity linking
   * embedding generation
3. **Storage**

   * PostgreSQL for canonical entities + metadata
   * pgvector for embeddings (or Qdrant locally if you prefer)
   * Local object store for cached images/thumbnails
4. **Search API**

   * hybrid retrieval orchestration
   * scoring + result formatting
5. **Web UI**

   * search box, filters, gallery grid, detail drawer
   * retrieval explanation panel

**Recommended local stack (Ubuntu-friendly)**

* Backend: Node.js (Express + TypeScript) or Python (FastAPI).
  (Given your comfort: Node/TS is a great fit.)
* DB: PostgreSQL + pgvector
* Optional lexical index:

  * Postgres full-text search (simpler) **or**
  * Meilisearch/OpenSearch locally (more powerful)
* Embeddings:

  * Text: sentence-transformers model locally
  * Image (optional): CLIP model locally
* Frontend: React + Tailwind

---

### 6) Data model (proposed)

**Core tables**

* `artwork`

  * `id`, `source` (met|wikidata|essay), `source_id`, `title`, `artist_id`, `year_start`, `year_end`, `medium`, `department`, `culture`, `image_url`, `local_image_path`, `description`
* `artist`

  * `id`, `name`, `birth_year`, `death_year`, `wikidata_qid`, `met_artist_id?`
* `movement`

  * `id`, `name`, `wikidata_qid`, `summary`
* `essay_source`

  * `id`, `url`, `title`, `author`, `published_date`, `license_note`, `raw_text_hash`
* `text_chunk`

  * `id`, `source_type` (essay|artwork_description|wikidata), `source_ref_id`, `chunk_index`, `text`, `char_start`, `char_end`
* `entity_link`

  * `id`, `left_type`, `left_id`, `right_type`, `right_id`, `link_type` (same_as|related_to), `confidence`, `method`
* `embedding`

  * `id`, `object_type` (text_chunk|artwork|artist|movement), `object_id`, `model`, `vector` (pgvector), `created_at`

**Search logging (for demos + evaluation)**

* `search_query_log`

  * query text, filters, top results, latency, clicked item (optional)

---

### 7) Retrieval approach

**Hybrid ranking**

* Candidate generation:

  1. lexical match on `text_chunk.text`, `artwork.title`, `artist.name`, `movement.name`
  2. vector similarity on chunk/artwork embeddings
* Scoring:

  * `score = w1*bm25 + w2*vector + w3*metadata_boost + w4*link_confidence`
* Metadata boosts:

  * exact artist match
  * movement match
  * medium match
  * time range overlap

**Multi-modal angle (practical v1)**

* Use **images as UI outputs** + retrieval context.
* Treat image understanding via:

  * metadata (title, medium, tags)
  * optional CLIP embeddings for “semantic image” queries later

---

### 8) API design (example)

**Search**

* `GET /api/search?q=...&movement=...&artist=...&year_min=...&year_max=...&source=...`
* Response:

  * `results[]` with `{type, id, title, thumbnailUrl, snippet, score, provenance, highlights, facets}`

**Artwork detail**

* `GET /api/artworks/:id`
* includes linked movement/artist + related essay chunks

**Movement page**

* `GET /api/movements/:id`
* includes representative works + key essay snippets

**Ingestion control (dev-only)**

* `POST /api/admin/ingest/met?departmentId=...`
* `POST /api/admin/ingest/wikidata?movement=...`
* `POST /api/admin/ingest/essay` body: `{url}`

---

### 9) UI spec (video-friendly)

**Pages**

1. **Search / Explore**

   * left: search + filters
   * center: thumbnail grid
   * right: detail drawer on click
2. **Retrieval Debug View**

   * score breakdown bars
   * highlights in text
   * “why shown?” bullets
3. **Movement Explorer**

   * movement overview
   * key artists + representative thumbnails

**Nice demo moments**

* type query → thumbnails update instantly
* click artwork → linked movement + “supporting essay snippets”
* toggle “Explain ranking” → show score components

---

### 10) Ingestion plan

**Met API**

* Pull object IDs by department/search endpoint
* Fetch objects in batches
* Store metadata + image URLs
* Download and cache thumbnails locally (respect rate limits)

**Wikidata**

* SPARQL queries per movement/artist
* Store QIDs + relationships
* Link artists/movements to Met data via normalized names + confidence

**Essays**

* Start with a curated list (10–30 URLs) for clean demo
* Clean HTML (strip nav/footer)
* Chunk into passages (e.g., 300–500 tokens)
* Store attribution + URL

---

### 11) Deployment & local dev

**Local dev modes**

* **Docker Compose (recommended)**:

  * postgres + pgvector
  * optional meilisearch
* Backend runs locally (`npm run dev`)
* Frontend runs locally (`pnpm dev` / `npm run dev`)

**Config**

* `.env`:

  * DB connection
  * embedding model name
  * cache paths
  * rate limit settings

---

### 12) Evaluation

**Offline**

* Build a small “golden queries” set (20–50 queries)
* Measure:

  * Precision@k (manual)
  * Diversity (artist/movement variety)
  * Link accuracy (Met ↔ Wikidata match confidence)

**Online (during demo)**

* Log latency and top results
* Track clicked results for iterative tuning

---

### 13) Risks & mitigations

* **R1: Entity linking errors**

  * Mitigation: confidence scoring + “unlinked” state + manual override file
* **R2: Blog content licensing**

  * Mitigation: store only excerpts/snippets + attribution; start with permissive sources or your own notes
* **R3: Scale/performance locally**

  * Mitigation: batch embeddings; incremental indexing; cache; start small (few thousand objects + few hundred essays) for v1

---

### 14) Milestones (practical build plan)

1. **Week 1:** DB schema + Met ingestion + basic UI grid
2. **Week 2:** Essay ingestion + chunking + lexical search
3. **Week 3:** Embeddings + vector search + hybrid ranker
4. **Week 4:** Wikidata linking + movement explorer page
5. **Week 5:** Retrieval explanation view + polish for demo video

---

If you want, I can also generate:

* a concrete **SPARQL query set** for Wikidata movements/artists,
* the initial **DB migrations** (Postgres + pgvector),
* and a **repo folder structure** (backend/frontend/ingestion/shared types) tailored to Node.js + TypeScript on Ubuntu.
