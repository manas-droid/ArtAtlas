
from typing import List

from .load_data import ArtworkModel

import psycopg
from db.db_pool import get_connection

def db_batch_insert_artwork(list_of_artworks:List[ArtworkModel]):
    TABLE_NAME = "artwork"
    COLUMNS = [
        "met_object_id", 
        "image_url", 
        "artist", 
        "object_date", 
        "medium", 
        "culture", 
        "source_url", 
        "title", 
        "department", 
        "searchable_text", 
        "embedding"
    ]    


    INSERT_SQL = f"""
        INSERT INTO {TABLE_NAME} ({', '.join(COLUMNS)})
        VALUES ({', '.join(['%s'] * len(COLUMNS))})
        ON CONFLICT (met_object_id) DO NOTHING;
    """


    if not list_of_artworks:
        print("No artworks to insert.")
        return
    
    data_to_insert = []
    
    for artwork in list_of_artworks:
        # Create a tuple for each row, ensuring the order matches the COLUMNS list
        row_tuple = (
            artwork['objectID'],
            artwork.get('primaryImageSmall'), 
            artwork.get('artistDisplayName'),
            artwork.get('objectDate'),
            artwork.get('medium'),
            artwork.get('culture'),
            artwork.get('objectURL'),
            artwork.get('title'),
            artwork.get('department'),
            artwork['searchable_text'],
            artwork['embedding'] 
        )
        data_to_insert.append(row_tuple)

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(INSERT_SQL, data_to_insert)
                conn.commit()
                print(f"Successfully inserted/updated {cur.rowcount} artworks using executemany.")

    except psycopg.Error as e:
        conn.rollback()
        print(f"Database error during executemany batch insert: {e}")
        raise        



def check_object_exists(object_id: int) -> bool:
    sql = f"""
    SELECT EXISTS (
        SELECT 1 
        FROM artwork 
        WHERE met_object_id = %s
    ) AS object_exists;
    """

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (object_id,))
                
                result = cur.fetchone()
                
                if result:
                    return result[0]
                
                return False
            
    except psycopg.Error as e:
        print(f"Database error occurred: {e}")
        return False