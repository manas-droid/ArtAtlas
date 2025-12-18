import psycopg
from sentence_transformers import SentenceTransformer
import torch
from db.db_pool import get_connection



device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = SentenceTransformer('all-MiniLM-L6-v2').to(device)



def save_essay_response_to_db(essay_response):
    TABLE_NAME = "essay"
    
    COLUMNS = [
        "essay_title", 
        "essay_type", 
        "source", 
        "source_url", 
        "chunk_text", 
        "chunk_index", 
        "embedding"
    ]    


    INSERT_SQL = f"""
        INSERT INTO {TABLE_NAME} ({', '.join(COLUMNS)})
        VALUES ({', '.join(['%s'] * len(COLUMNS))})
    """

    if not essay_response or len(essay_response['chunks']) == 0:
        print("No essays to insert.")
        return



    data_to_insert = []
    i = 0
    for chunk in essay_response['chunks']:
        chunk_embedding = model.encode(chunk).tolist()
        row_tuple = (
            essay_response['essay_title'],
            essay_response['essay_type'].name,
            essay_response['source'],
            essay_response['source_url'],
            chunk,
            i,
            chunk_embedding
        )
        i+=1
        
        data_to_insert.append(row_tuple)



    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(INSERT_SQL, data_to_insert)
                conn.commit()
                print(f"Successfully inserted/updated {cur.rowcount} essays using executemany.")
    except psycopg.Error as e:
        conn.rollback()
        print(f"Database error during executemany batch insert: {e}")
        raise        




"""
CREATE TABLE essay (
    id              SERIAL PRIMARY KEY,

    -- logical grouping
    essay_title     TEXT NOT NULL,     -- e.g. "Dutch Still Life Painting"
    essay_type      TEXT NOT NULL,     -- 'movement' | 'technique' | 'genre'
    
    -- chunk content
    chunk_index     INT NOT NULL,      -- order within essay
    chunk_text      TEXT NOT NULL,

    -- search
    searchable_tsv  TSVECTOR NOT NULL,
    embedding       VECTOR(384) NOT NULL,

    -- provenance
    source          TEXT,              -- e.g. 'Met Essay', 'ArtHistory.org'
    source_url      TEXT
);
"""