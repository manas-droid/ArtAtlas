from collections import defaultdict
from typing import Any
from concept_data_pipeline.artwork_concept.prototypes import ConceptMatch, compute_artwork_concept_similarities
from explanation.evidence.evidence_model import ArtworkEvidence, EvidenceBundle, Justification
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

def get_bundled_artworks_per_concept(artworks:list[dict], concepts:tuple[ConceptMatch])->defaultdict[Any, list[ArtworkEvidence]]:
    artwork_ids : list[int] = [artwork["id"] for artwork in artworks]

    artwork_concept_similarities = compute_artwork_concept_similarities(artwork_ids=artwork_ids, concept_ids=[concept.concept_id for concept in concepts])
    
    concept_artwork_support = defaultdict(list[ArtworkEvidence])

    for artwork_concept_similarity in artwork_concept_similarities:
        concept_artwork_support[artwork_concept_similarity[1]].append(ArtworkEvidence(artwork_id=artwork_concept_similarity[0], mapping_confidence=artwork_concept_similarity[2],provenance="embedding_similarity"))

    return concept_artwork_support


def calculate_evidence_bundle_confidence(concept_artwork_support: list[ArtworkEvidence])->float:
    sum_of_artwork_mapping_conf:float = 0.0

    for artwork in concept_artwork_support:
        sum_of_artwork_mapping_conf+=artwork.mapping_confidence

    return sum_of_artwork_mapping_conf/len(concept_artwork_support)


def form_justification_edges(artwork_bundle_list:  list[ArtworkEvidence])->list[Justification]:
    justification_list:list[Justification] = []

    for artwork in artwork_bundle_list:
        justification_list.append(Justification(justification_type="artwork_supports_concept", confidence=artwork.mapping_confidence, source_id=artwork.artwork_id, provenance=artwork.provenance))

    return justification_list

def build_evidence_bundle(search_context: SearchContext)->list[EvidenceBundle]:

    artworks:list[dict] = search_context.artworks
    concepts: tuple[ConceptMatch] =  search_context.detected_concepts

    concept_artwork_support = get_bundled_artworks_per_concept(artworks, concepts)
    result:list[EvidenceBundle] = []


    for concept_id in concept_artwork_support:
        artwork_bundle_list:list[ArtworkEvidence] = concept_artwork_support[concept_id]
        evidence_bundle = EvidenceBundle(bundled_artworks=artwork_bundle_list, 
                                         evidence_id=f"bundle__concept__{concept_id}", 
                                         evidence_confidence=calculate_evidence_bundle_confidence(artwork_bundle_list),
                                         justification_edges= form_justification_edges(artwork_bundle_list),
                                         primary_concept=concept_id
                                        )    
        
        result.append(evidence_bundle)

    return result