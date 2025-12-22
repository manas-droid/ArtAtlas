"""Helpers for combining results and applying concept-based rescoring."""

from __future__ import annotations

from typing import Sequence

from concept_data_pipeline.artwork_concept.prototypes import ConceptMatch
from search.retrievers import ArtworkRetriever, EssayRetriever

ConceptWeights = tuple[float, float, float]


def merge_results(
    essay_results: Sequence[dict],
    artwork_results: Sequence[dict],
) -> list[dict]:
    merged = list(essay_results) + list(artwork_results)
    merged.sort(key=lambda row: row["score"]["final_score"], reverse=True)
    return merged


def apply_concept_scores(
    *,
    results: list[dict],
    query_concepts: Sequence[ConceptMatch],
    artwork_retriever: ArtworkRetriever,
    essay_retriever: EssayRetriever,
    weights: ConceptWeights,
    essay_boost: float,
) -> None:
    if not query_concepts:
        return

    concept_ids = [concept.concept_id for concept in query_concepts]
    w1, w2, w3 = weights

    for result in results:
        concept_score = 0.0

        if result["result_type"] == "artwork":
            artwork_concepts = artwork_retriever.get_concept_score(
                result["id"], concept_ids
            )
            matches = [
                qc.confidence_score * ac.confidence_score
                for qc in query_concepts
                for ac in artwork_concepts
                if qc.concept_id == ac.concept_id
            ]

            if len(matches) >= 2:
                concept_score = max(matches)
            elif len(query_concepts) == 1 and len(matches) == 1:
                concept_score = matches[0]

        elif result["result_type"] == "essay" and essay_retriever.check_if_essay_concept_exists(
            result["id"], concept_ids
        ):
            concept_score = essay_boost

        result["score"]["final_score"] = (
            w1 * result["score"]["lexical_score"]
            + w2 * result["score"]["semantic_score"]
            + w3 * concept_score
        )
