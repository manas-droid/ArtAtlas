from collections import defaultdict
from concept_data_pipeline.artwork_concept.prototypes import ConceptMatch, compute_artwork_concept_similarities
from search.search_model import SearchContext
from db.db_pool import get_connection

MAPPING_CONFIDENCE_THRESHOLD = 0.6


def get_db_artworks_mapped_to_concept(concept_id: int, artwork_ids: list[int])->list[int]:
    placeholders = ", ".join(["%s"] * len(artwork_ids))

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT artwork_id FROM artwork_concept WHERE concept_id = %s AND artwork_id IN({placeholders})", (concept_id , *artwork_ids))
            results = cur.fetchall()
            filtered_artwork_ids = [row[0] for row in results]

    return filtered_artwork_ids
    

"""
Did not choose to filter based on essay chunks because:
Evidence Bundles are allowed to be purely visual when textual evidence does not exist — but they must never be purely textual.
"""

def get_bundled_artworks_per_concept(artworks:list[dict], concepts:tuple[ConceptMatch])->dict:
    artwork_ids : list[int] = [artwork["id"] for artwork in artworks]

    artwork_concept_similarities = compute_artwork_concept_similarities(artwork_ids=artwork_ids, concept_ids=[concept.concept_id for concept in concepts])
    
    
    concept_artwork_support = defaultdict(list)

    for artwork_concept_similarity in artwork_concept_similarities:

        if artwork_concept_similarity[2] < MAPPING_CONFIDENCE_THRESHOLD: 
            continue

        concept_artwork_support[artwork_concept_similarity[1]].append({
            "artwork_id" : artwork_concept_similarity[0],
            "mapping_confidence": artwork_concept_similarity[2],
            "provenance" : "embedding_similarity"
        })


    return concept_artwork_support



def build_evidence_bundle(search_context: SearchContext):

    artworks:list[dict] = search_context.artworks
    concepts: tuple[ConceptMatch] =  search_context.detected_concepts
    