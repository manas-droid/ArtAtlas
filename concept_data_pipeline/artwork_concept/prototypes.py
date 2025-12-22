"""Concept prototype helpers shared between offline and online flows."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import math
from typing import Any, Iterable, Sequence

from db.db_pool import get_connection

MIN_CONFIDENCE_SCORE = 0.7


@dataclass(frozen=True)
class ConceptPrototype:
    concept_id: int
    vector: list[float]
    authority: float


@dataclass(frozen=True)
class ConceptMatch:
    concept_id: int
    concept_name: str | None
    confidence_score: float
    normalized_score: float
    similarity: float


@dataclass(frozen=True)
class ConceptResponseForSearch(ConceptPrototype):
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


def load_concept_prototypes(
    *, db_pool: Any | None = None
) -> tuple[ConceptPrototype, ...]:
    """Fetch concept prototypes without names (offline ingestion)."""
    with (db_pool.connection() if db_pool else get_connection()) as conn:
        concept_vectors = _fetch_concept_vectors(conn)
    return _build_concept_prototypes(concept_vectors)


def score_concepts_for_vector(
    *,
    vector: Sequence[float],
    prototypes: Sequence[ConceptPrototype],
    confidence_threshold: float = MIN_CONFIDENCE_SCORE,
    max_concepts: int | None = None,
    concept_lookup: dict[int, str] | None = None,
) -> tuple[ConceptMatch, ...]:
    """Rank concept prototypes against a single embedding vector."""
    if not prototypes:
        return ()

    scored: list[tuple[ConceptPrototype, float]] = []
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
            vector = coerce_vector(embedding)
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
            vector = coerce_vector(embedding)
            if vector:
                concept_vectors[int(concept_id)].append(vector)

    return concept_vectors


def _build_concept_prototypes(
    concept_vectors: dict[int, list[list[float]]]
) -> tuple[ConceptPrototype, ...]:
    prototypes: list[ConceptPrototype] = []

    for concept_id, vectors in concept_vectors.items():
        if not vectors:
            continue

        centroid = _mean_vector(vectors)
        authority = _authority(len(vectors))

        prototypes.append(
            ConceptPrototype(
                concept_id=concept_id,
                vector=centroid,
                authority=authority,
            )
        )

    return tuple(prototypes)


def _mean_vector(vectors: Sequence[Sequence[float]]) -> list[float]:
    dim = len(vectors[0])
    sums = [0.0] * dim

    for vec in vectors:
        if len(vec) != dim:
            raise ValueError("All vectors must have same dimensionality.")
        for idx, value in enumerate(vec):
            sums[idx] += value

    count = float(len(vectors))
    return [value / count for value in sums]


def _authority(num_embeddings: int) -> float:
    return min(1.0, math.log(num_embeddings + 1))


def _cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    if len(vec_a) != len(vec_b):
        raise ValueError("Vectors must have same dimensionality.")

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def coerce_vector(values: Sequence[float] | None) -> list[float]:
    if values is None:
        return []
    return [float(v) for v in values]
