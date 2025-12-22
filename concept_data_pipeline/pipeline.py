"""Common entry point for running concept-mapping data tasks."""

from __future__ import annotations

from typing import Iterable, Sequence

from concept_data_pipeline.artwork_concept.affinity import (
    ArtworkConceptRecord,
    generate_artwork_concept_affinities,
    insert_artwork_concepts,
)
from concept_data_pipeline.concept.insert_concept_data import (
    CURATED_CONCEPTS,
    ConceptRecord,
    insert_concepts,
)
from concept_data_pipeline.essay_concept.insert_essay_concept_data import (
    ESSAY_CONCEPT_MAPPINGS,
    EssayConceptRecord,
    insert_essay_concepts,
)


def seed_concept_mappings(
    *,
    concepts: Iterable[ConceptRecord] | None = None,
    essay_concepts: Iterable[EssayConceptRecord] | None = None,
    artwork_concepts: Iterable[ArtworkConceptRecord] | None = None,
    db_pool=None,
) -> None:
    """
    Run all concept-related insert tasks in a consistent order.

    Args:
        concepts: Optional override for concept payload; defaults to CURATED_CONCEPTS.
        essay_concepts: Essay-chunk to concept associations (optional).
        artwork_concepts: Artwork to concept confidence mappings (optional).
        db_pool: Optional psycopg_pool.ConnectionPool override.
    """

    concept_payload = _coerce_sequence(concepts, fallback=CURATED_CONCEPTS)
    if concept_payload:
        insert_concepts(concept_payload, db_pool=db_pool)

    essay_payload = _coerce_sequence(essay_concepts, fallback=ESSAY_CONCEPT_MAPPINGS)
    if essay_payload:
        _safe_call(insert_essay_concepts, essay_payload, db_pool=db_pool)

    if artwork_concepts is None:
        artwork_payload = generate_artwork_concept_affinities(db_pool=db_pool)
    else:
        artwork_payload = _coerce_sequence(artwork_concepts)
    if artwork_payload:
        _safe_call(insert_artwork_concepts, artwork_payload, db_pool=db_pool)


def _coerce_sequence(
    records: Iterable[object] | None, *, fallback: Sequence[object] | None = None
) -> Sequence[object]:
    if records is None:
        return fallback or ()
    if isinstance(records, Sequence):
        return records
    return tuple(records)


def _safe_call(func, payload, *, db_pool=None) -> None:
    """Call a mapper while tolerating placeholder functions."""
    try:
        func(payload, db_pool=db_pool)
    except NotImplementedError as exc:
        print(f"Skipping {func.__name__}: {exc}")
