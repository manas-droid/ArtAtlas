"""Reusable helpers for hybrid lexical/vector retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from utils.config import HYBRID_SEARCH
from db.db_pool import get_connection
from utils.embeddings import encode_text


@dataclass
class SearchWeights:
    lexical_weight: float = HYBRID_SEARCH.lexical_weight
    semantic_weight: float = HYBRID_SEARCH.semantic_weight
    fallback_penalty: float = HYBRID_SEARCH.fallback_penalty


class HybridRetriever:
    """Encapsulates shared lexical/vector logic for different tables."""

    def __init__(self, table_name: str, select_columns: str, limit_lexical: int, limit_vector: int,
                 weights: SearchWeights | None = None) -> None:
        self.table = table_name
        self.columns = select_columns
        self.lexical_limit = limit_lexical
        self.vector_limit = limit_vector
        self.weights = weights or SearchWeights()

    def _lexical_sql(self) -> str:
        return f"""
            WITH search_results AS (
            SELECT 
                id, 
                searchable_tsv,
                ts_rank(searchable_tsv, query) AS lexical_score,
                query AS original_query
            FROM {self.table}, websearch_to_tsquery('english', %s) AS query
            WHERE searchable_tsv @@ query
            ORDER BY lexical_score DESC
            LIMIT {self.lexical_limit}
        )
        SELECT 
            id,
            lexical_score,
            ARRAY(
                SELECT DISTINCT lex
                FROM unnest(tsvector_to_array(searchable_tsv)) AS lex
                WHERE lex IN (
                    SELECT unnest(tsvector_to_array(to_tsvector('english', %s)))
                )
            ) AS matched_terms
        FROM search_results;
        """

    def _vector_sql(self, filtered: bool) -> str:
        filter_clause = "WHERE id = ANY(%s)" if filtered else ""
        return f"""
            SELECT {self.columns},
                   1 - (embedding <=> %s::vector) AS semantic_score
            FROM {self.table}
            {filter_clause}
            ORDER BY embedding <=> %s::vector
            LIMIT {self.vector_limit};
        """

    def _score(self, semantic_score: float, lexical_score: float) -> float:
        final_score = (
            self.weights.lexical_weight * lexical_score +
            self.weights.semantic_weight * semantic_score
        )
        if lexical_score == 0:
            final_score *= self.weights.fallback_penalty
        return final_score

    def _format_result(self, row: Sequence, lexical_score_map: dict[int, dict]) -> dict:
        *fields, semantic_score = row
        record_id = fields[0]
        lexical_info = lexical_score_map.get(record_id, {"score": 0.0, "matched_terms": []})
        lexical_score = lexical_info.get("score", 0.0)
        matched_terms = lexical_info.get("matched_terms", [])
        final_score = self._score(semantic_score, lexical_score)
        return self._build_payload(fields, semantic_score, lexical_score, final_score, matched_terms)

    def _build_payload(self, fields: Sequence,
                       semantic_score: float,
                       lexical_score: float,
                       final_score: float,
                       matched_terms: Sequence[str] | None = None) -> dict:
        raise NotImplementedError

    def search(self, query: str) -> list[dict]:
        query_vector = encode_text(query)
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(self._lexical_sql(), (query,query))
            lexical_rows = cur.fetchall()
            lexical_score_map = {
                row[0]: {"score": row[1], "matched_terms": row[2] or []}
                for row in lexical_rows
            }
            lexical_ids = list(lexical_score_map.keys())

            if lexical_ids:
                id_array = f"{{{', '.join(map(str, lexical_ids))}}}"
                cur.execute(self._vector_sql(filtered=True), (query_vector, id_array, query_vector))
            else:
                cur.execute(self._vector_sql(filtered=False), (query_vector, query_vector))

            vector_rows = cur.fetchall()

        return [self._format_result(row, lexical_score_map) for row in vector_rows]
