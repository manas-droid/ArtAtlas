
def get_lexical_results(cur, query):
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



def get_re_ranked_results(final_results, lexical_score_map):
    final_ranked_results = []
    LEXICAL_WEIGHT = 0.4
    SEMANTIC_WEIGHT = 0.6

    for row in final_results:
        artwork_id, title, artist, semantic_score = row
        lexical_score = lexical_score_map.get(artwork_id, 0.0)

        final_score = (
            LEXICAL_WEIGHT * lexical_score +
            SEMANTIC_WEIGHT * semantic_score
        )

        final_ranked_results.append({
            "id": artwork_id,
            "title": title,
            "artist": artist,
            "lexical_score": lexical_score,
            "semantic_score": semantic_score,
            "final_score": final_score
        })

    
        final_ranked_results.sort(
            key=lambda x: x["final_score"],
            reverse=True
        )
    return final_ranked_results


"""
Expensive operation. Will have to find ways to reduce calls to the function
"""
def get_fallback_vector_search_result(cur, query_vector_embedding):
    print("No lexical results found -  [Fallback] Searching vector embeddings")

    query_vector_search = """
        SELECT id, title, artist,
        1 - (embedding <=> %s::vector) AS semantic_score
        FROM artwork
        ORDER BY embedding <=> %s::vector
        LIMIT 15;
    """

    cur.execute(query_vector_search, (query_vector_embedding, query_vector_embedding))
    return cur.fetchall()




def get_vector_search_result(cur, query_vector_embedding, id_array_string):
    print("..... Found Lexical Results, Filtering By Vector Embeddings ......")


    query_semantic = """
        SELECT id, title, artist,
            1 - (embedding <=> %s::vector) AS semantic_score
        FROM artwork
        WHERE id = ANY(%s)
        ORDER BY embedding <=> %s::vector
        LIMIT 15;
    """

    cur.execute(query_semantic, (query_vector_embedding, id_array_string, query_vector_embedding))
    
    return cur.fetchall()
