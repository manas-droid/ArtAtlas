from __future__ import annotations

from typing import Sequence

from utils.config import HYBRID_SEARCH
from search.hybrid_retriever import HybridRetriever


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
