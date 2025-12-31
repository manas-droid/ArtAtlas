"""Concept table seed utilities."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Sequence

import psycopg

from db.db_pool import get_connection


class ConceptType(str, Enum):
    """Supported curated concept buckets."""

    MOVEMENT = "movement"
    TECHNIQUE = "technique"
    GENRE = "genre"
    THEME = "theme"


@dataclass(frozen=True)
class ConceptRecord:
    """Represents a single row destined for the `concept` table."""

    name: str
    concept_type: ConceptType | str  # 'technique' | 'genre' | 'movement'


def insert_concepts(
    concepts: Iterable[ConceptRecord], *, db_pool: Any | None = None
) -> int:
    """Insert curated concept records into Postgres."""

    payload = _serialize_concepts(concepts)
    if not payload:
        return 0

    insert_sql = """
        INSERT INTO concept (name, type)
        VALUES (%s, %s)
        ON CONFLICT (name) DO UPDATE
        SET type = EXCLUDED.type
    """

    connection_factory = db_pool.connection if db_pool else get_connection

    with connection_factory() as conn:
        try:
            with conn.cursor() as cur:
                cur.executemany(insert_sql, payload)
            conn.commit()
        except psycopg.Error:
            conn.rollback()
            raise

    return len(payload)


def _serialize_concepts(concepts: Iterable[ConceptRecord]) -> Sequence[tuple[str, str]]:
    serialized: list[tuple[str, str]] = []
    for concept in concepts:
        name = concept.name.strip()
        if not name:
            raise ValueError("Concept name cannot be empty.")

        ctype = (
            concept.concept_type.value
            if isinstance(concept.concept_type, ConceptType)
            else str(concept.concept_type)
        ).strip()
        if not ctype:
            raise ValueError(f"Concept type missing for concept '{name}'.")

        serialized.append((name, ctype))
    return tuple(serialized)


CURATED_CONCEPTS: tuple[ConceptRecord, ...] = (
    ConceptRecord(name="Dutch Golden Age", concept_type=ConceptType.MOVEMENT), #1
    ConceptRecord(name="Vanitas", concept_type=ConceptType.GENRE), #2
    ConceptRecord(name="Still life", concept_type=ConceptType.GENRE), #3
    ConceptRecord(name="Landscape", concept_type=ConceptType.GENRE), #4
    ConceptRecord(name="Genre Painting", concept_type=ConceptType.GENRE), #5
    ConceptRecord(name="Chiaroscuro", concept_type=ConceptType.TECHNIQUE), #6
    ConceptRecord(name="Tenebrism", concept_type=ConceptType.TECHNIQUE), #7
    ConceptRecord(name="Realism", concept_type=ConceptType.THEME), #8
    ConceptRecord(name="Spatial Realism", concept_type=ConceptType.THEME), #9
    ConceptRecord(name="Symbolism", concept_type=ConceptType.THEME), #10
    ConceptRecord(name="Baroque", concept_type=ConceptType.MOVEMENT), #31
    ConceptRecord(name="Impressionism", concept_type=ConceptType.MOVEMENT), #32
    ConceptRecord(name="Cubism", concept_type=ConceptType.MOVEMENT), #33
    ConceptRecord(name="Religious Narrative", concept_type=ConceptType.GENRE) #34

)
