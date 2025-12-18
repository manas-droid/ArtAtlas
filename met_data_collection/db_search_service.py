from sentence_transformers import SentenceTransformer
import torch

from db.db_pool import get_connection


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = SentenceTransformer('all-MiniLM-L6-v2').to(device)


def get_lexical_results_for_artwork(cur, query):
    query_lexical = """
    SELECT id, ts_rank(searchable_tsv, websearch_to_tsquery('english', %s)) AS lexical_score
    FROM artwork
    WHERE searchable_tsv @@ websearch_to_tsquery('english', %s)
    ORDER BY ts_rank(searchable_tsv, websearch_to_tsquery('english', %s)) DESC
    LIMIT 50;
    """
    cur.execute(query_lexical, (query, query ,query))

    lexical_response = cur.fetchall()

    lexical_score_map = {
        row[0]: row[1] for row in lexical_response
    }

    return lexical_score_map



def get_results_with_score(final_results, lexical_score_map):
    results_with_score = []
    LEXICAL_WEIGHT = 0.4
    SEMANTIC_WEIGHT = 0.6

    for row in final_results:
        artwork_id, title, artist, semantic_score, image_url = row
        lexical_score = lexical_score_map.get(artwork_id, 0.0)

        final_score = (
            LEXICAL_WEIGHT * lexical_score +
            SEMANTIC_WEIGHT * semantic_score
        )

        if lexical_score == 0:
            final_score *= 0.7
        
        results_with_score.append({
            "result_type": "artwork",
            "id": artwork_id,
            "title": title,
            "artist": artist,
            "image_url":image_url,
            "score" : {
            "lexical_score": lexical_score,
            "semantic_score": semantic_score,
            "final_score": final_score
            }
        })

    
    return results_with_score


"""
Expensive operation. Will have to find ways to reduce calls to the function
"""
def get_fallback_vector_search_result_for_artwork(cur, query_vector_embedding):
    print("No lexical results found for Artwork-  [Fallback] Searching vector embeddings")

    query_vector_search = """
        SELECT id, title, artist,
        1 - (embedding <=> %s::vector) AS semantic_score,
        image_url
        FROM artwork
        ORDER BY embedding <=> %s::vector
        LIMIT 3;
    """

    cur.execute(query_vector_search, (query_vector_embedding, query_vector_embedding))
    return cur.fetchall()




def get_vector_search_result_for_artwork(cur, query_vector_embedding, id_array_string):
    print("..... Found Lexical Results, Filtering By Vector Embeddings ......")


    query_semantic = """
        SELECT id, title, artist,
            1 - (embedding <=> %s::vector) AS semantic_score,
            image_url
        FROM artwork
        WHERE id = ANY(%s)
        ORDER BY embedding <=> %s::vector
        LIMIT 3;
    """

    cur.execute(query_semantic, (query_vector_embedding, id_array_string, query_vector_embedding))
    
    return cur.fetchall()




def get_search_results_for_artwork(query:str):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                
                lexical_score_map = get_lexical_results_for_artwork(cur, query)

                lexical_ids = list(lexical_score_map.keys())

                id_array_string = f"{{{', '.join(map(str, lexical_ids))}}}"

                query_vector_embedding  = model.encode(query).tolist()

                results = []
                
                if not lexical_ids:
                    results = get_fallback_vector_search_result_for_artwork(cur, query_vector_embedding)


                else:
                    results = get_vector_search_result_for_artwork(cur, query_vector_embedding,id_array_string)  
                

                results_with_score = get_results_with_score(results, lexical_score_map)


                return results_with_score

    except Exception as error:
        print(f"An error occurred: {error}")
        return []
    