"""Artwork-to-concept affinity generation and persistence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence

import psycopg

from db.db_pool import get_connection
from concept_data_pipeline.artwork_concept.prototypes import (
    ConceptPrototype,
    coerce_vector,
    load_concept_prototypes,
    score_concepts_for_vector,
)

MIN_CONFIDENCE_SCORE = 0.7


@dataclass(frozen=True)
class ArtworkEmbedding:
    artwork_id: int
    vector: list[float]


@dataclass(frozen=True)
class ArtworkConceptRecord:
    artwork_id: int
    concept_id: int
    confidence_score: float


def generate_artwork_concept_affinities(
    *,
    db_pool: Any | None = None,
    confidence_threshold: float = MIN_CONFIDENCE_SCORE,
) -> tuple[ArtworkConceptRecord, ...]:
    """
    Offline propagation of concepts from essays to artworks.
    """
    with (db_pool.connection() if db_pool else get_connection()) as conn:
        artworks = _fetch_artwork_embeddings(conn)

    prototypes = load_concept_prototypes(db_pool=db_pool)

    if not prototypes or not artworks:
        return ()

    return _score_artworks(
        artworks=artworks,
        prototypes=prototypes,
        confidence_threshold=confidence_threshold,
    )


def insert_artwork_concepts(
    affinities: Iterable[ArtworkConceptRecord],
    *,
    db_pool: Any | None = None,
    batch_size: int = 500,
) -> int:
    payload = tuple(
        (rec.artwork_id, rec.concept_id, rec.confidence_score)
        for rec in affinities
    )

    if not payload:
        return 0

    sql = """
        INSERT INTO artwork_concept (artwork_id, concept_id, confidence_score)
        VALUES (%s, %s, %s)
        ON CONFLICT (artwork_id, concept_id)
        DO UPDATE SET confidence_score = EXCLUDED.confidence_score
    """

    connection_factory = db_pool.connection if db_pool else get_connection

    with connection_factory() as conn:
        try:
            with conn.cursor() as cur:
                for chunk in _chunked(payload, batch_size):
                    cur.executemany(sql, chunk)
            conn.commit()
        except psycopg.Error:
            conn.rollback()
            raise

    return len(payload)


def _fetch_artwork_embeddings(conn) -> tuple[ArtworkEmbedding, ...]:
    sql = """
        SELECT id, embedding::float4[]
        FROM artwork
        WHERE embedding IS NOT NULL
    """

    artworks: list[ArtworkEmbedding] = []

    with conn.cursor() as cur:
        cur.execute(sql)
        for artwork_id, embedding in cur.fetchall():
            vector = coerce_vector(embedding)
            if vector:
                artworks.append(
                    ArtworkEmbedding(
                        artwork_id=int(artwork_id),
                        vector=vector,
                    )
                )

    return tuple(artworks)


def _score_artworks(
    *,
    artworks: Sequence[ArtworkEmbedding],
    prototypes: Sequence[ConceptPrototype],
    confidence_threshold: float,
    max_concepts_per_artwork: int = 2,
) -> tuple[ArtworkConceptRecord, ...]:
    results: list[ArtworkConceptRecord] = []

    for art in artworks:
        matches = score_concepts_for_vector(
            vector=art.vector,
            prototypes=prototypes,
            confidence_threshold=confidence_threshold,
            max_concepts=max_concepts_per_artwork,
        )

        for match in matches:
            results.append(
                ArtworkConceptRecord(
                    artwork_id=art.artwork_id,
                    concept_id=match.concept_id,
                    confidence_score=match.confidence_score,
                )
            )

    return tuple(results)


def _chunked(
    payload: Sequence[tuple[int, int, float]],
    batch_size: int,
) -> Iterable[Sequence[tuple[int, int, float]]]:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    for start in range(0, len(payload), batch_size):
        yield payload[start : start + batch_size]
