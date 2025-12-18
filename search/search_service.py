from .search_model import SearchResponse
from  met_data_collection.db_search_service import get_search_results_for_artwork
from essay_scraper.db_search_service import get_search_results_for_essay




def get_reranked_results(results_from_artwork:list, results_from_essay:list):
        results = []
        results.extend(results_from_essay)
        results.extend(results_from_artwork)
        results.sort( key=lambda x: x['score']["final_score"], reverse=True)

        return results

def find_top_relevant_results(query:str)->SearchResponse:
    if not query or  len(query.replace(" ", "")) == 0:
            return {'message': 'InAppropriate Query', 'results': []}

    results_from_artwork =  get_search_results_for_artwork(query)   
    results_from_essay   =  get_search_results_for_essay(query)

    reranked_results = get_reranked_results(results_from_artwork, results_from_essay)

    return {
                'query': query,
                'message':'Search Successful', 
                "metadata":{
                'path_taken': 'lexical+vector',
                'artworks_results': len(results_from_artwork),
                'essay_results' : len(results_from_essay) 
                },
                'results':reranked_results 
        }
