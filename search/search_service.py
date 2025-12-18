from search.retrievers import ArtworkRetriever, EssayRetriever
from .search_model import SearchResponse


artwork_retriever = ArtworkRetriever()
essay_retriever = EssayRetriever()

def get_reranked_results(results_from_artwork:list, results_from_essay:list):
        results = []
        results.extend(results_from_essay)
        results.extend(results_from_artwork)
        results.sort( key=lambda x: x['score']["final_score"], reverse=True)

        return results

def find_top_relevant_results(query:str)->SearchResponse:
    if not query or  len(query.replace(" ", "")) == 0:
            return {'message': 'InAppropriate Query', 'results': []}

    results_from_artwork =  artwork_retriever.search(query)   
    results_from_essay   =  essay_retriever.search(query)

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
