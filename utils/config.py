"""Central configuration for ArtAtlas components."""

from __future__ import annotations

import os
from dataclasses import dataclass


EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


@dataclass(frozen=True)
class HybridSearchConfig:
    """Tunables for lexical/vector blending."""

    lexical_weight: float = float(os.getenv("LEXICAL_WEIGHT", "0.4"))
    semantic_weight: float = float(os.getenv("SEMANTIC_WEIGHT", "0.6"))
    fallback_penalty: float = float(os.getenv("FALLBACK_PENALTY", "0.7"))
    essay_lexical_limit: int = int(os.getenv("ESSAY_LEXICAL_LIMIT", "20"))
    essay_vector_limit: int = int(os.getenv("ESSAY_VECTOR_LIMIT", "2"))
    artwork_lexical_limit: int = int(os.getenv("ARTWORK_LEXICAL_LIMIT", "50"))
    artwork_vector_limit: int = int(os.getenv("ARTWORK_VECTOR_LIMIT", "3"))


@dataclass(frozen=True)
class IngestionConfig:
    """Batching settings for offline ingestion jobs."""

    artwork_batch_size: int = int(os.getenv("ARTWORK_BATCH_SIZE", "25"))
    artwork_delay_seconds: float = float(os.getenv("ARTWORK_DELAY_SECONDS", "0.5"))


HYBRID_SEARCH = HybridSearchConfig()
INGESTION = IngestionConfig()
