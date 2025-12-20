# Concept Data Pipeline Skeleton

This package holds the v2 concept-propagation data tasks.

- `concept/`: home for curated concept seeding (includes the `insert_concepts` implementation and default payload).
- `essay_concept/`: utilities for populating the bridging table between essay chunks and concepts (includes curated mappings + insert function).
- `artwork_concept/`: logic for storing offline artwork-to-concept affinities (includes cosine-scoring pipeline + insert helper).
- `pipeline.py`: orchestration helper that runs all concept-related insert functions in order.

Concept, essay-concept, and artwork-concept seeding are available today. Running

```bash
python -c "from concept_data_pipeline.pipeline import seed_concept_mappings; seed_concept_mappings()"
```

will upsert the curated concepts, essay mappings, and then compute artwork affinities by:

1. **Prototype construction** (`insert_artwork_concept_data.py`):
   - Fetch every essay chunk linked to a concept and average their embeddings to produce a concept prototype vector.
   - Compute an authority scalar for the concept via `min(1.0, log(n_chunks + 1))`.
2. **Artwork scoring**:
   - Pull all artwork embeddings and, for each artwork, compute cosine similarity to *every* concept prototype.
   - Normalize similarities per artwork by dividing by that artwork’s best-matching concept.
   - Multiply the normalized score by the concept authority to obtain the final confidence.
3. **Filtering + insert**:
   - Keep only confidences ≥ 0.7 (after authority) and upsert them into `artwork_concept` in batches of 500 rows, so a corpus of ~5k artworks can be processed safely.

The resulting `ArtworkConceptRecord`s are inserted into `artwork_concept` with upserts so the pipeline is idempotent.
