from __future__ import annotations

from typing import Literal, Sequence

from concept_data_pipeline.artwork_concept.affinity import ArtworkConceptRecord
from utils.config import (
    ARTWORK_LEXICAL_FIELD_WEIGHTS,
    ESSAY_LEXICAL_FIELD_WEIGHTS,
    FIELD_AWARE_LEXICAL,
    HYBRID_SEARCH,
)
from search.hybrid_retriever import HybridRetriever
from db.db_pool import get_connection


def compute_retrieval_trace(
    matched_lexemes: list[str],
    matched_fields: list[str],
    lexical_source: Literal["essay_text", "aggregated_metadata"],
    semantic_score: float,
    embedding_source: Literal["essay_chunk", "artwork_embedding"],
):
    
    if matched_lexemes and len(matched_lexemes) > 0:
        return {
            "lexical_match": {
                "source" : lexical_source,
                "matched_lexemes": matched_lexemes,
                "matched_fields": matched_fields,
            },
            "semantic_match": {
                "similarity": semantic_score,
                "source" : embedding_source
            }
        }
    return {
        "semantic_match" : {
            "similarity" : semantic_score,
            "source" : embedding_source
        }
    }


class ArtworkRetriever(HybridRetriever):
    def __init__(self) -> None:
        columns = "id, title, artist, image_url"
        super().__init__(
            table_name="artwork",
            select_columns=columns,
            limit_lexical=HYBRID_SEARCH.artwork_lexical_limit,
            limit_vector=HYBRID_SEARCH.artwork_vector_limit,
            lexical_fields={
                "title": "title",
                "artist": "artist",
                "medium": "medium",
                "culture": "culture",
                "department": "department",
            },
            lexical_field_weights=ARTWORK_LEXICAL_FIELD_WEIGHTS if FIELD_AWARE_LEXICAL else None,
        )


    def _build_payload(self, fields: Sequence,
                       semantic_score: float,
                       lexical_score: float,
                       final_score: float,
                       matched_terms=None,
                       matched_fields=None) -> dict:
        artwork_id, title, artist, image_url = fields

        retrieval_trace:dict = compute_retrieval_trace(
            matched_terms or [],
            matched_fields or [],
            'aggregated_metadata',
            semantic_score,
            'artwork_embedding',
        )

        return {
            "result_type": "artwork",
            "id": artwork_id,
            "title": title,
            "artist": artist,
            "image_url": image_url,
            "score": {
                "lexical_score": lexical_score,
                "semantic_score": semantic_score,
                "final_score": final_score,
            },
            "retrieval_trace" : retrieval_trace
        }

    def _format_to_artwork_concept_record(self, artwork_concepts_row:Sequence):
        artwork_id, concept_id, confidence_score = artwork_concepts_row
        return ArtworkConceptRecord(artwork_id, concept_id, confidence_score)
    
    def get_concept_score(self, artwork_id: int, concept_ids: list[int] = ()) -> list[ArtworkConceptRecord]:
        if not concept_ids:
            return []
        placeholders = ", ".join(["%s"] * len(concept_ids))
        sql = f"""
            SELECT artwork_id, concept_id, confidence_score
            FROM artwork_concept
            WHERE artwork_id = %s
              AND concept_id IN ({placeholders})
        """

        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (artwork_id, *concept_ids))
            rows = cur.fetchall()

        return [self._format_to_artwork_concept_record(row) for row in rows]


class EssayRetriever(HybridRetriever):
    def __init__(self) -> None:
        columns = "id, essay_title, chunk_text, chunk_index, source"
        super().__init__(
            table_name="essay",
            select_columns=columns,
            limit_lexical=HYBRID_SEARCH.essay_lexical_limit,
            limit_vector=HYBRID_SEARCH.essay_vector_limit,
            lexical_fields={
                "title": "essay_title",
                "text": "chunk_text",
            },
            lexical_field_weights=ESSAY_LEXICAL_FIELD_WEIGHTS if FIELD_AWARE_LEXICAL else None,
        )

    def _build_payload(self, fields: Sequence,
                       semantic_score: float,
                       lexical_score: float,
                       final_score: float,
                       matched_terms=None,
                       matched_fields=None) -> dict:
        essay_id, essay_title, chunk_text, chunk_index, source = fields

        retrieval_trace:dict = compute_retrieval_trace(
            matched_terms or [],
            matched_fields or [],
            'essay_text',
            semantic_score,
            'essay_chunk',
        )

        return {
            "result_type": "essay",
            "id": essay_id,
            "title": essay_title,
            "text": chunk_text,
            "chunk_index": chunk_index,
            "source": source,
            "score": {
                "lexical_score": lexical_score,
                "semantic_score": semantic_score,
                "final_score": final_score,
            },
            "retrieval_trace" : retrieval_trace
        }

    def check_if_essay_concept_exists(self, essay_id:int, essay_concept_ids:list[int]):
        if not essay_concept_ids:
            return []

        placeholders = ", ".join(["%s"] * len(essay_concept_ids))

        sql = f"""
                SELECT 1
                FROM essay_concept
                WHERE essay_id = %s
                AND concept_id IN ({placeholders})
                LIMIT 1;        
                """
        result:bool = False

        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (essay_id, *essay_concept_ids))
            temp = cur.fetchone()
            if temp:
                result = True if temp[0] == 1 else False

        return result
        
