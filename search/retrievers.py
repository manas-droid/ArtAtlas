from __future__ import annotations

from typing import Sequence

from concept_data_pipeline.artwork_concept.affinity import ArtworkConceptRecord
from utils.config import HYBRID_SEARCH
from search.hybrid_retriever import HybridRetriever
from db.db_pool import get_connection


class ArtworkRetriever(HybridRetriever):
    def __init__(self) -> None:
        columns = "id, title, artist, image_url"
        super().__init__(
            table_name="artwork",
            select_columns=columns,
            limit_lexical=HYBRID_SEARCH.artwork_lexical_limit,
            limit_vector=HYBRID_SEARCH.artwork_vector_limit,
        )

    def _build_payload(self, fields: Sequence,
                       semantic_score: float,
                       lexical_score: float,
                       final_score: float) -> dict:
        artwork_id, title, artist, image_url = fields
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
        )

    def _build_payload(self, fields: Sequence,
                       semantic_score: float,
                       lexical_score: float,
                       final_score: float) -> dict:
        essay_id, essay_title, chunk_text, chunk_index, source = fields
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
        
