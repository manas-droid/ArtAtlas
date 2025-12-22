# Art-Based Retrieval System (v1)

## Overview

This project implements a hybrid search engine for art exploration that combines Metropolitan Museum of Art metadata with curated Dutch Golden Age essays. Users can issue free-text queries (e.g., "dramatic lighting", "Dutch still life") and receive artwork hits alongside explanatory essay excerpts. The emphasis for v1 is a local-first, explainable, non-LLM system that demonstrates robust retrieval and concept grounding.

## Goals of v1

- Support natural-language, free-text art queries
- Combine lexical and semantic retrieval for resilient performance
- Provide explanatory context alongside visual search results
- Avoid brittle rule-based parsing or LLM-based generation
- Keep the entire stack runnable on a local Ubuntu machine

## What v1 Is (and Is Not)

**v1 IS**

- A hybrid retrieval engine leveraging PostgreSQL full-text search and pgvector
- An art exploration and explanation system centered on the Dutch Golden Age
- Designed for clarity, debuggability, and demo readiness

**v1 IS NOT**

- A question-answering or LLM-driven assistant
- A visual-analysis pipeline or comprehensive art encyclopedia
- A fully annotated concept graph or biography database

## Data Sources

**Artwork Data**

- Metropolitan Museum of Art Open Access API (European Paintings; Drawings & Prints)
- Stored in PostgreSQL with structured metadata, tsvector columns, and MiniLM embeddings via pgvector

**Essay Data**

- Curated essays from museum and art-history publications (e.g., The Art Story)
- Focused on Dutch Golden Age movements, genres, and techniques (still life, landscape, chiaroscuro, tenebrism, material depiction)
- Essays are chunked into 200–350 word segments that each receive their own embedding

## Search Architecture

**High-Level Flow**

1. **Lexical Search**: PostgreSQL full-text search (tsvector) for precise keyword matches.
2. **Semantic Search**: Sentence embeddings (MiniLM) scored with cosine similarity via pgvector.
3. **Hybrid Logic**:
   - If lexical results exist, perform semantic reranking over that candidate set.
   - If lexical results are empty, fall back to vector-only search.

This ensures high precision when keywords hit, robust recall for abstract queries, and no empty-result scenarios.

## Essay Handling in v1

- Essay chunks are treated as conceptual retrieval units rather than standalone articles.
- Chunks may assume context from their parent essays; v1 does not attempt to reconstruct full narratives.
- Chunks are surfaced to explain stylistic or historical concepts and are not meant as exhaustive reading material.

## API Response Structure

- Search responses can mix result types: `artwork` (visual evidence) and `essay` (conceptual explanation).
- Each result carries explicit `result_type`, lexical score, semantic score, and final blended score.
- Metadata is intentionally minimal but sufficient for UI rendering so clients can distinguish visual examples from explanatory text.

## Example Query Behavior

**Query**: "17<sup>th</sup> Century Dutch Painting"

- Technique-focused essay chunks (e.g., still life explanations) appear first to provide context.
- Relevant artworks follow to visually ground the explanation.
- This ordering reflects the principle: artworks show *what*; essays explain *why*.

```
{
  "message": "Search Successful",
  "metadata": {
    "artworks_results": 3,
    "essay_results": 1,
    "path_taken": "lexical+vector"
  },
  "query": "17th Century Dutch Painting",
  "results": [
    {
      "chunk_index": 2,
      "id": 37,
      "result_type": "essay",
      "score": {
        "final_score": 0.546709026890261,
        "lexical_score": 0.4545987,
        "semantic_score": 0.608115911483769
      },
      "source": "Fiveable.me",
      "text": "\nDutch still life painters used a variety of materials and methods to create their highly detailed and realistic images\nWooden panels and canvas were the most common supports for still life paintings, with canvas becoming increasingly popular throughout the 17th century\nOil paint was the primary medium used by Dutch still life painters, allowing for a wide range of colors, tones, and textures\n\nPigments were often mixed with linseed oil, which acted as a binder and allowed for the creation of transparent glazes and opaque layers\n\n\nArtists used a variety of brushes, ranging from fine sable brushes for detailed work to larger hog bristle brushes for broader strokes and backgrounds\nThe use of a palette allowed artists to mix and blend colors, creating subtle variations in tone and hue\nArtists often used a mahl stick, a long, thin rod with a soft pad at one end, to steady their hand while working on detailed areas of the painting\nThe use of a camera obscura, an optical device that projects an image onto a surface, may have been used by some artists to aid in the creation of highly accurate and detailed compositions\n.",
      "title": "Art in the Dutch Golden Age - Unit 7"
    },
    {
      "artist": "Jan van Goyen",
      "id": 10514,
      "image_url": "https://images.metmuseum.org/CRDImages/ep/web-large/DP147601.jpg",
      "result_type": "artwork",
      "score": {
        "final_score": 0.289679275789347,
        "lexical_score": 0,
        "semantic_score": 0.689712561403208
      },
      "title": "A View of The Hague from the Northwest"
    },
    {
      "artist": "Willem van de Velde II",
      "id": 10347,
      "image_url": "https://images.metmuseum.org/CRDImages/ep/web-large/DP146449.jpg",
      "result_type": "artwork",
      "score": {
        "final_score": 0.287068110493777,
        "lexical_score": 0,
        "semantic_score": 0.68349550117566
      },
      "title": "Entrance to a Dutch Port"
    },
    {
      "artist": "Willem Drost",
      "id": 10921,
      "image_url": "https://images.metmuseum.org/CRDImages/ep/web-large/DP145401.jpg",
      "result_type": "artwork",
      "score": {
        "final_score": 0.281283106727415,
        "lexical_score": 0,
        "semantic_score": 0.669721682684322
      },
      "title": "The Sibyl"
    }
  ]
}
```

## Technology Stack

- **Backend**: Python
- **Database**: PostgreSQL with pgvector (IVFFLAT index)
- **Search**: PostgreSQL full-text search plus MiniLM sentence embeddings
- **Environment**: Ubuntu (local development)

## Known Limitations (Intentional in v1)

- No artwork-level concept annotations (e.g., "this painting uses chiaroscuro")
- No feedback loop linking essay insights back to artworks
- No artist biographies or historical event modeling
- No LLM-based generation, reasoning, or narrative reconstruction

These constraints are documented and deferred to future versions.
