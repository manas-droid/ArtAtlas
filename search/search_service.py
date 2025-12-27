from explanation.graph.graph_validation import validate_graph_objects
from search.retrievers import ArtworkRetriever, EssayRetriever
from search.ranking import ConceptWeights, apply_concept_scores, merge_results
from search.search_concept_service import (
    concept_has_artwork_mappings,
    detect_concept_from_query,
)
from .search_model import SearchContext, SearchResponse

from explanation.evidence.evidence_builder import build_evidence_bundle
from explanation.graph.build_explanation_graph import build_explanation_graph

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

    search_context = SearchContext(artworks=artwork_results, essays=essay_results, detected_concepts=query_concepts)
    list_of_evidence_bundles = build_evidence_bundle(search_context)

    nodes, edges = build_explanation_graph(query=query, detected_concepts=query_concepts, evidence_bundles=list_of_evidence_bundles)

    graph_nodes = list(nodes.values())
    validation_result = validate_graph_objects(nodes=graph_nodes, edges=edges)

    if validation_result.errors:
        print("Graph Errors: " , validation_result.errors)
        nodes = None 
        edges= None

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
        "explanation_graph": {
            "nodes": list(graph_nodes if nodes else {}),
            "edges": edges,
        }
    }
