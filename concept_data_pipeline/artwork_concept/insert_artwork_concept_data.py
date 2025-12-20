"""Artwork-to-concept affinity insert template."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class ArtworkConceptRecord:
    """Captures an offline-computed concept confidence for an artwork."""
    artwork_id: int
    concept_id: int
    confidence_score: float
    provenance: str | None = None  # e.g., which batch job produced the score


def insert_artwork_concepts(
    affinities: Iterable[ArtworkConceptRecord], *, db_pool: Any
) -> None:
    """Template for inserting artwork concept affinities."""
    raise NotImplementedError(
        "Implement artwork_concept insertion once the affinity pipeline exists."
    )
