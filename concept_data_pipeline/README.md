# Concept Data Pipeline Skeleton

This package holds the v2 concept-propagation data tasks.

- `concept/`: home for curated concept seeding (includes the `insert_concepts` implementation and default payload).
- `essay_concept/`: utilities for populating the bridging table between essay chunks and concepts (includes curated mappings + insert function).
- `artwork_concept/`: logic for storing offline artwork-to-concept affinities.
- `pipeline.py`: orchestration helper that runs all concept-related insert functions in order.

Concept and essay-concept seeding are available today; artwork concept inserts remain a template until the offline affinity job is implemented.
