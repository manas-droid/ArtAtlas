"""
Artwork-to-concept affinity pipeline (v2-correct).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import math
from typing import Any, Iterable, Sequence

import psycopg

from db.db_pool import get_connection

MIN_CONFIDENCE_SCORE = 0.7


# ----------------------------
# Data models
# ----------------------------

@dataclass(frozen=True)
class ArtworkConceptRecord:
    artwork_id: int
    concept_id: int
    confidence_score: float


@dataclass(frozen=True)
class _ConceptPrototype:
    concept_id: int
    vector: list[float]
    authority: float


@dataclass(frozen=True)
class ArtworkEmbedding:
    artwork_id: int
    vector: list[float]


@dataclass(frozen=True)
class ConceptMatch:
    concept_id: int
    concept_name: str | None
    confidence_score: float
    normalized_score: float
    similarity: float

@dataclass(frozen=True)
class ConceptResponseForSearch(_ConceptPrototype):
    concept_name: str


def get_concept_prototypes(
    db_pool: Any | None = None,
) -> tuple[ConceptResponseForSearch, ...]:
    """Return concept prototypes with their human-readable names for search."""
    with (db_pool.connection() if db_pool else get_connection()) as conn:
        concept_payload = _fetch_concept_vectors_with_names(conn)

    prototypes: list[ConceptResponseForSearch] = []
    for concept_id, payload in concept_payload.items():
        vectors = payload["vectors"]
        if not vectors:
            continue
        centroid = _mean_vector(vectors)
        authority = _authority(len(vectors))
        prototypes.append(
            ConceptResponseForSearch(
                concept_id=concept_id,
                concept_name=payload["name"],
                vector=centroid,
                authority=authority,
            )
        )

    return tuple(prototypes)


def generate_artwork_concept_affinities(
    *,
    db_pool: Any | None = None,
    confidence_threshold: float = MIN_CONFIDENCE_SCORE,
) -> tuple[ArtworkConceptRecord, ...]:
    """
    Offline propagation of concepts from essays to artworks.
    """
    with (db_pool.connection() if db_pool else get_connection()) as conn:
        concept_vectors = _fetch_concept_vectors(conn)
        artworks = _fetch_artwork_embeddings(conn)

    prototypes = _build_concept_prototypes(concept_vectors)

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


# ----------------------------
# Core pipeline logic
# ----------------------------

def load_concept_prototypes(
    *,
    db_pool: Any | None = None,
) -> tuple[_ConceptPrototype, ...]:
    """Utility for fetching concept prototypes for online use."""
    with (db_pool.connection() if db_pool else get_connection()) as conn:
        concept_vectors = _fetch_concept_vectors(conn)
    return _build_concept_prototypes(concept_vectors)


def _fetch_concept_vectors_with_names(conn) -> dict[int, dict[str, Any]]:
    """
    Fetch concept names alongside their essay-derived embeddings.
    """
    sql = """
        SELECT ecc.concept_id, c.name, e.embedding::float4[]
        FROM essay_concept ecc
        JOIN essay e ON e.id = ecc.essay_id
        JOIN concept c ON c.id = ecc.concept_id
        WHERE e.embedding IS NOT NULL
    """

    concept_vectors: dict[int, dict[str, Any]] = {}

    with conn.cursor() as cur:
        cur.execute(sql)
        for concept_id, name, embedding in cur.fetchall():
            vector = _coerce_vector(embedding)
            if not vector:
                continue
            payload = concept_vectors.setdefault(
                int(concept_id), {"name": name, "vectors": []}
            )
            payload["vectors"].append(vector)

    return concept_vectors


def _fetch_concept_vectors(conn) -> dict[int, list[list[float]]]:
    """
    Fetch essay embeddings grouped by concept.
    """
    sql = """
        SELECT ecc.concept_id, e.embedding::float4[]
        FROM essay_concept ecc
        JOIN essay e ON e.id = ecc.essay_id
        WHERE e.embedding IS NOT NULL
    """

    concept_vectors: dict[int, list[list[float]]] = defaultdict(list)

    with conn.cursor() as cur:
        cur.execute(sql)
        for concept_id, embedding in cur.fetchall():
            vector = _coerce_vector(embedding)
            if vector:
                concept_vectors[int(concept_id)].append(vector)

    return concept_vectors


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
            vector = _coerce_vector(embedding)
            if vector:
                artworks.append(
                    ArtworkEmbedding(
                        artwork_id=int(artwork_id),
                        vector=vector,
                    )
                )

    return tuple(artworks)


def _build_concept_prototypes(
    concept_vectors: dict[int, list[list[float]]]
) -> tuple[_ConceptPrototype, ...]:
    prototypes: list[_ConceptPrototype] = []

    for concept_id, vectors in concept_vectors.items():
        if not vectors:
            continue

        centroid = _mean_vector(vectors)
        authority = _authority(len(vectors))

        prototypes.append(
            _ConceptPrototype(
                concept_id=concept_id,
                vector=centroid,
                authority=authority,
            )
        )

    return tuple(prototypes)


def _score_artworks(
    *,
    artworks: Sequence[ArtworkEmbedding],
    prototypes: Sequence[_ConceptPrototype],
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


def score_concepts_for_vector(
    *,
    vector: Sequence[float],
    prototypes: Sequence[_ConceptPrototype],
    confidence_threshold: float = MIN_CONFIDENCE_SCORE,
    max_concepts: int | None = None,
    concept_lookup: dict[int, str] | None = None,
) -> tuple[ConceptMatch, ...]:
    """Rank concept prototypes against a single embedding vector."""
    if not prototypes:
        return ()

    scored: list[tuple[_ConceptPrototype, float]] = []
    for proto in prototypes:
        similarity = _cosine_similarity(vector, proto.vector)
        scored.append((proto, similarity))

    max_similarity = max((s for _, s in scored), default=0.0)
    if max_similarity <= 0:
        return ()

    matches: list[ConceptMatch] = []
    for proto, similarity in scored:
        normalized = similarity / max_similarity if max_similarity else 0.0
        confidence = normalized * proto.authority
        if confidence < confidence_threshold:
            continue
        matches.append(
            ConceptMatch(
                concept_id=proto.concept_id,
                concept_name=(concept_lookup or {}).get(proto.concept_id),
                confidence_score=confidence,
                normalized_score=normalized,
                similarity=similarity,
            )
        )

    matches.sort(key=lambda match: match.confidence_score, reverse=True)
    if max_concepts is not None:
        matches = matches[:max_concepts]

    return tuple(matches)


# ----------------------------
# Math utilities
# ----------------------------

def _mean_vector(vectors: Sequence[Sequence[float]]) -> list[float]:
    dim = len(vectors[0])
    sums = [0.0] * dim

    for vec in vectors:
        if len(vec) != dim:
            raise ValueError("All vectors must have same dimensionality.")
        for i, v in enumerate(vec):
            sums[i] += v

    count = float(len(vectors))
    return [v / count for v in sums]


def _authority(num_embeddings: int) -> float:
    """
    Authority dampening for low-support concepts.
    """
    return min(1.0, math.log(num_embeddings + 1))


def _cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Vectors must have same dimensionality.")

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def _coerce_vector(values: Sequence[float] | None) -> list[float]:
    if values is None:
        return []
    return [float(v) for v in values]


def _chunked(
    payload: Sequence[tuple[int, int, float]],
    batch_size: int,
) -> Iterable[Sequence[tuple[int, int, float]]]:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    for i in range(0, len(payload), batch_size):
        yield payload[i : i + batch_size]
