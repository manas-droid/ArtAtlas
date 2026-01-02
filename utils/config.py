"""Central configuration for ArtAtlas components."""

from __future__ import annotations

import os
from dataclasses import dataclass


EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

def _env_bool(name: str, default: str = "0") -> bool:
    value = os.getenv(name, default).strip().lower()
    return value in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class HybridSearchConfig:
    """Tunables for lexical/vector blending."""

    lexical_weight: float = float(os.getenv("LEXICAL_WEIGHT", "0.4"))
    semantic_weight: float = float(os.getenv("SEMANTIC_WEIGHT", "0.6"))
    fallback_penalty: float = float(os.getenv("FALLBACK_PENALTY", "0.7"))
    essay_lexical_limit: int = int(os.getenv("ESSAY_LEXICAL_LIMIT", "20"))
    essay_vector_limit: int = int(os.getenv("ESSAY_VECTOR_LIMIT", "3"))
    artwork_lexical_limit: int = int(os.getenv("ARTWORK_LEXICAL_LIMIT", "50"))
    artwork_vector_limit: int = int(os.getenv("ARTWORK_VECTOR_LIMIT", "5"))


@dataclass(frozen=True)
class IngestionConfig:
    """Batching settings for offline ingestion jobs."""

    artwork_batch_size: int = int(os.getenv("ARTWORK_BATCH_SIZE", "25"))
    artwork_delay_seconds: float = float(os.getenv("ARTWORK_DELAY_SECONDS", "0.5"))


HYBRID_SEARCH = HybridSearchConfig()
INGESTION = IngestionConfig()

# v3.3: field-aware lexical ordering (applies only to lexical score; semantic untouched).
FIELD_AWARE_LEXICAL = _env_bool("FIELD_AWARE_LEXICAL", default="1")

# Field weights are intentionally conservative. They should only improve ordering of already-retrieved results.
ARTWORK_LEXICAL_FIELD_WEIGHTS: dict[str, float] = {
    "artist": 1.4,
    "title": 1.3,
    "medium": 1.15,
    "culture": 1.0,
    "department": 0.85,
}

ESSAY_LEXICAL_FIELD_WEIGHTS: dict[str, float] = {
    "title": 1.1,
    "text": 1.0,
}
