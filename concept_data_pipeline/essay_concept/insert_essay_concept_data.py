"""Essay-to-concept mapping insert utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence

import psycopg

from db.db_pool import get_connection


@dataclass(frozen=True)
class EssayConceptRecord:
    """Represents the link between an essay chunk and a concept."""

    essay_chunk_id: int
    concept_id: int

def insert_essay_concepts(
    mappings: Iterable[EssayConceptRecord], *, db_pool: Any | None = None
) -> int:
    """Insert essay chunk to concept associations."""
    payload = _serialize_mappings(mappings)
    if not payload:
        return 0

    insert_sql = """
        INSERT INTO essay_concept (essay_id, concept_id)
        VALUES (%s, %s)
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


def _serialize_mappings(
    mappings: Iterable[EssayConceptRecord],
) -> Sequence[tuple[int, int, str | None]]:
    serialized: list[tuple[int, int, str | None]] = []
    for mapping in mappings:
        essay_chunk_id = int(mapping.essay_chunk_id)
        concept_id = int(mapping.concept_id)

        if essay_chunk_id <= 0:
            raise ValueError("essay_chunk_id must be positive.")
        if concept_id <= 0:
            raise ValueError("concept_id must be positive.")

        serialized.append((essay_chunk_id, concept_id))
    return tuple(serialized)


ESSAY_CONCEPT_MAPPINGS: tuple[EssayConceptRecord, ...] = (
    EssayConceptRecord(essay_chunk_id=5, concept_id=2),
    EssayConceptRecord(essay_chunk_id=6, concept_id=3),
    EssayConceptRecord(essay_chunk_id=7, concept_id=3),
    EssayConceptRecord(essay_chunk_id=8, concept_id=3),
    EssayConceptRecord(essay_chunk_id=9, concept_id=4),
    EssayConceptRecord(essay_chunk_id=10, concept_id=4),
    EssayConceptRecord(essay_chunk_id=11, concept_id=4),
    EssayConceptRecord(essay_chunk_id=12, concept_id=5),
    EssayConceptRecord(essay_chunk_id=13, concept_id=5),
    EssayConceptRecord(essay_chunk_id=14, concept_id=6),
    EssayConceptRecord(essay_chunk_id=15, concept_id=6),
    EssayConceptRecord(essay_chunk_id=15, concept_id=7),
    EssayConceptRecord(essay_chunk_id=19, concept_id=6),
    EssayConceptRecord(essay_chunk_id=21, concept_id=6),
    EssayConceptRecord(essay_chunk_id=21, concept_id=7),
    EssayConceptRecord(essay_chunk_id=22, concept_id=6),
    EssayConceptRecord(essay_chunk_id=23, concept_id=6),
    EssayConceptRecord(essay_chunk_id=24, concept_id=6),
    EssayConceptRecord(essay_chunk_id=27, concept_id=6),
    EssayConceptRecord(essay_chunk_id=29, concept_id=6),
    EssayConceptRecord(essay_chunk_id=30, concept_id=6),
    EssayConceptRecord(essay_chunk_id=31, concept_id=6),
    EssayConceptRecord(essay_chunk_id=32, concept_id=7),
    EssayConceptRecord(essay_chunk_id=34, concept_id=8),
    EssayConceptRecord(essay_chunk_id=34, concept_id=6),
    EssayConceptRecord(essay_chunk_id=34, concept_id=9),
    EssayConceptRecord(essay_chunk_id=35, concept_id=3),
    EssayConceptRecord(essay_chunk_id=35, concept_id=6),
    EssayConceptRecord(essay_chunk_id=35, concept_id=8),
    EssayConceptRecord(essay_chunk_id=36, concept_id=3),
    EssayConceptRecord(essay_chunk_id=36, concept_id=10),
    EssayConceptRecord(essay_chunk_id=36, concept_id=2),
    EssayConceptRecord(essay_chunk_id=38, concept_id=1),
    EssayConceptRecord(essay_chunk_id=39, concept_id=1),
)


"""
Essay Concept mapping:
Essay Id            Concept Id
5                     2
6                     3
7                     3
8                     3
9                     4
10                    4
11                    4
12                    5      
13                    5      
14                    6
15                    6
15                    7
19                    6
21                    6
21                    7
22                    6
23                    6
24                    6
27                    6
29                    6
30                    6
31                    6
32                    7
34                    8
34                    6
34                    9
35                    3
35                    6
35                    8
36                    3
36                    10
36                    2
38                    1
39                    1



"""
