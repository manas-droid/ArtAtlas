
from sentence_transformers import SentenceTransformer
import torch
from .search_model import SearchResponse

from .vector_search_service import get_lexical_results, get_fallback_vector_search_result, get_re_ranked_results, get_vector_search_result


from db.db_pool import get_connection



device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = SentenceTransformer('all-MiniLM-L6-v2').to(device)


def find_top15_relevant_results(query:str)->SearchResponse:
    if not query or  len(query.replace(" ", "")) == 0:
            return {'message': 'InAppropriate Query', 'results': []}
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                
                lexical_score_map = get_lexical_results(cur, query)

                lexical_ids = list(lexical_score_map.keys())

                id_array_string = f"{{{', '.join(map(str, lexical_ids))}}}"

                query_vector_embedding  = model.encode(query).tolist()

                results = []
                
                if not lexical_ids:
                    results = get_fallback_vector_search_result(cur, query_vector_embedding)

                else:
                    results = get_vector_search_result(cur, query_vector_embedding,id_array_string)                     
                

                final_ranked_results = get_re_ranked_results(results, lexical_score_map)

                print(f"Reranking complete. Final count: {len(final_ranked_results)} results.")

                return {'message': 'Search Successful', 'results': final_ranked_results}

    except Exception as error:
        print(f"An error occurred: {error}")
        return {'message':'Search Failed', 'results':[]}