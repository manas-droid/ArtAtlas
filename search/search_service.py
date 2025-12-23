from search.retrievers import ArtworkRetriever, EssayRetriever
from search.ranking import ConceptWeights, apply_concept_scores, merge_results
from search.search_concept_service import (
    concept_has_artwork_mappings,
    detect_concept_from_query,
)
from .search_model import SearchContext, SearchResponse


artwork_retriever = ArtworkRetriever()
essay_retriever = EssayRetriever()

ESSAY_CONCEPT_BOOST = 0.3
CONCEPT_WEIGHTS: ConceptWeights = (0.20, 0.65, 0.15)

# Vanitas, Still life, Landscape, Genre Painting
PRIMARY_CONCEPT_IDS = {2, 3, 4, 5}


def _is_primary(concept_id: int) -> bool:
    return concept_id in PRIMARY_CONCEPT_IDS


def _expand_query_with_concepts(
    query: str, query_concepts
) -> str:
    expanded = query

    for concept in query_concepts:
        if _is_primary(concept.concept_id) and concept_has_artwork_mappings(
            concept.concept_id
        ):
            expanded += f" OR {concept.concept_name}"
            concept.used_for_expansion = True
    
    print("Expanded query for artwork: ", expanded)
    return expanded


def find_top_relevant_results(query: str) -> SearchResponse:
    if not query or len(query.replace(" ", "")) == 0:
        return {"message": "InAppropriate Query", "results": []}

    query_concepts = detect_concept_from_query(query)
    for concept in query_concepts:
        concept.concept_type = "primary" if _is_primary(concept.concept_id) else "secondary"
    essay_results = essay_retriever.search(query)

    if query_concepts:
        artwork_query = _expand_query_with_concepts(query, query_concepts)
    else:
        artwork_query = query
    artwork_results = artwork_retriever.search(artwork_query)

    combined_results = merge_results(essay_results, artwork_results)

    if query_concepts:
        apply_concept_scores(
            results=combined_results,
            query_concepts=query_concepts,
            artwork_retriever=artwork_retriever,
            essay_retriever=essay_retriever,
            weights=CONCEPT_WEIGHTS,
            essay_boost=ESSAY_CONCEPT_BOOST,
        )
    else:
        print("No concept relations were found while querying ", query)

    search_context = SearchContext(artworks=artwork_results, essays=essay_results, detected_concepts=query_concepts, score= combined_results['score'])

    
    combined_results.sort(key=lambda x: x["score"]["final_score"], reverse=True)

    return {
        "query": query,
        "message": "Search Successful",
        "metadata": {
            "path_taken": "lexical+vector",
            "artworks_results": len(artwork_results),
            "essay_results": len(essay_results),
        },
        "results": combined_results,
    }
