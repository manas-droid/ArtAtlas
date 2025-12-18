from sentence_transformers import SentenceTransformer
import torch


from db.db_pool import get_connection



device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = SentenceTransformer('all-MiniLM-L6-v2').to(device)



def get_lexical_results_for_artwork(cur, query):
    query_lexical = """
    SELECT id, ts_rank(searchable_tsv, websearch_to_tsquery('english', %s)) AS lexical_score
    FROM essay
    WHERE searchable_tsv @@ websearch_to_tsquery('english', %s)
    ORDER BY ts_rank(searchable_tsv, websearch_to_tsquery('english', %s)) DESC
    LIMIT 20;
    """

    cur.execute(query_lexical, (query, query ,query))

    lexical_response = cur.fetchall()

    lexical_score_map = {
        row[0]: row[1] for row in lexical_response
    }

    return lexical_score_map


def get_fallback_vector_search_result_for_artwork(cur, query_vector_embedding):
    print("No lexical results found for Artwork-  [Fallback] Searching vector embeddings")

    query_vector_search = """
        SELECT id, essay_title, chunk_text, chunk_index,
        1 - (embedding <=> %s::vector) AS semantic_score,
        source
        FROM essay
        ORDER BY embedding <=> %s::vector
        LIMIT 2;
    """

    cur.execute(query_vector_search, (query_vector_embedding, query_vector_embedding))
    return cur.fetchall()




def get_vector_search_result_for_artwork(cur, query_vector_embedding, id_array_string):
    print("..... Found Lexical Results, Filtering By Vector Embeddings ......")


    query_semantic = """
        SELECT id, essay_title, chunk_text, chunk_index,
            1 - (embedding <=> %s::vector) AS semantic_score,
            source
        FROM essay
        WHERE id = ANY(%s)
        ORDER BY embedding <=> %s::vector
        LIMIT 2;
    """

    cur.execute(query_semantic, (query_vector_embedding, id_array_string, query_vector_embedding))
    
    return cur.fetchall()


def get_results_with_score(final_results, lexical_score_map):
    results_with_score = []
    LEXICAL_WEIGHT = 0.4
    SEMANTIC_WEIGHT = 0.6

    for row in final_results:
        essay_id, essay_title, chunk_text, chunk_index, semantic_score, source = row
        lexical_score = lexical_score_map.get(essay_id, 0.0)

        final_score = (
            LEXICAL_WEIGHT * lexical_score +
            SEMANTIC_WEIGHT * semantic_score
        )


        results_with_score.append({
            "result_type": "essay",
            "id": essay_id,
            "title": essay_title,
            "text": chunk_text,
            "chunk_index": chunk_index,
            "source":source,
            "score" : {
            "lexical_score": lexical_score,
            "semantic_score": semantic_score,
            "final_score": final_score
            }
        })

    
    return results_with_score




def get_search_results_for_essay(query:str):
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


                return  results_with_score

    except Exception as error:
        print(f"An error occurred: {error}")
        return []
