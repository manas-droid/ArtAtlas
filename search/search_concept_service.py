from utils.embeddings import encode_text
from concept_data_pipeline.artwork_concept.insert_artwork_concept_data import (
    ConceptMatch,
    get_concept_prototypes,
    score_concepts_for_vector,
)


from db.db_pool import get_connection


def detect_concept_from_query(query: str) -> tuple[ConceptMatch, ...]:
    encoded_query_text = encode_text(query)
    prototypes = get_concept_prototypes()
    concept_lookup = {proto.concept_id: proto.concept_name for proto in prototypes}
    concept_scores = score_concepts_for_vector(
        vector=encoded_query_text,
        prototypes=prototypes,
        max_concepts=2,
        concept_lookup=concept_lookup,
    )
    return concept_scores


def concept_has_artwork_mappings(concept_id: int) -> bool:
    result:bool = False

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS(
                        SELECT 1 
                        FROM artwork_concept 
                        WHERE concept_id = %s
                    );    
            """ , (concept_id, ))

            result = cur.fetchone()[0]
        


    return result