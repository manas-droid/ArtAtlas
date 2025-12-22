from search.retrievers import ArtworkRetriever, EssayRetriever
from search.search_concept_service import detect_concept_from_query, concept_has_artwork_mappings
from .search_model import SearchResponse


artwork_retriever = ArtworkRetriever()
essay_retriever = EssayRetriever()

ESSAY_CONCEPT_BOOST = 0.3
w1 = 0.20
w2 = 0.65
w3 = 0.15


"""
    "Vanitas",
    "Still life",
    "Landscape",
    "Genre Painting",
"""
PRIMARY_CONCEPT_IDS = {2, 3, 4, 5}

def is_primary(concept_id)->bool:
        if concept_id in PRIMARY_CONCEPT_IDS:
                return True
        return False


def find_top_relevant_results(query:str)->SearchResponse:
        if not query or  len(query.replace(" ", "")) == 0:
                return {'message': 'InAppropriate Query', 'results': []}


        query_concepts = detect_concept_from_query(query)

        combined_results = []

        if query_concepts and len(query_concepts)  > 0:
        
                concept_ids:list[int] = [concept_score.concept_id for concept_score in query_concepts]

                
                query_with_related_concepts = query

                results_from_essay   =  essay_retriever.search(query)

                for concept in query_concepts:
                        if is_primary(concept.concept_id) and concept_has_artwork_mappings(concept.concept_id):
                                query_with_related_concepts += f' OR {concept.concept_name}'


                results_from_artwork =  artwork_retriever.search(query_with_related_concepts)   

                combined_results.extend(results_from_essay)
                combined_results.extend(results_from_artwork)

                
                for result in combined_results:
                        concept_score = 0

                        if result['result_type'] == 'artwork':
                                artwork_concepts = artwork_retriever.get_concept_score(result['id'], concept_ids)
                                matches = [
                                        qc.confidence_score * ac.confidence_score
                                        for qc in query_concepts
                                        for ac in artwork_concepts
                                        if qc.concept_id == ac.concept_id
                                        ]

                                if len(matches) >=2 :
                                        concept_score = max(matches)
                                elif len(query_concepts) == 1 and len(matches) == 1:
                                        concept_score = matches[0]
                                else:
                                        concept_score = 0

                        elif result['result_type'] == 'essay' and essay_retriever.check_if_essay_concept_exists(result['id'], concept_ids):
                                concept_score = ESSAY_CONCEPT_BOOST

                        result['score']['final_score'] = w1*result['score']['lexical_score'] + w2*result['score']['semantic_score'] + w3*concept_score

        else:
                results_from_artwork =  artwork_retriever.search(query)   
                results_from_essay   =  essay_retriever.search(query)
                combined_results.extend(results_from_essay)
                combined_results.extend(results_from_artwork)


                print("No concept relations were found while querying ", query)
        
        combined_results.sort( key=lambda x: x['score']["final_score"], reverse=True)

                
        return {
                'query': query,
                'message':'Search Successful', 
                "metadata":{
                'path_taken': 'lexical+vector',
                'artworks_results': len(results_from_artwork),
                'essay_results' : len(results_from_essay) 
                },
                'results':combined_results 
        }
