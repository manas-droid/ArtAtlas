
from typing import List

from .met_data_model import ArtworkModel, ObjectResponse

from .extract_data import get_object_ids_by_department, get_objects_by_object_id
from .met_data_service import check_object_exists, db_batch_insert_artwork

import time
from sentence_transformers import SentenceTransformer
import torch



 
DELAY_SECONDS = 0.5
BATCH_SIZE = 25



device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = SentenceTransformer('all-MiniLM-L6-v2').to(device)





def build_searchable_text(artwork:ArtworkModel):
    fields = [
        artwork['title'],
        artwork['artistDisplayName'],
        artwork['objectDate'],
        artwork['medium'],
        artwork['culture'],
        artwork['department']
    ]
    return " ".join([f for f in fields if f])



def validate_object_response(artwork_response:ArtworkModel)->bool:
    if not artwork_response['objectID'] or not artwork_response['primaryImageSmall'] or not artwork_response['searchable_text']:
        return False
    return True


def transform_object_to_artwork(object_response:ObjectResponse)->ArtworkModel:    
    artwork_model: ArtworkModel = object_response.copy()
    artwork_model['searchable_text'] = build_searchable_text(artwork_model)
    return artwork_model





"""
limit: Number of column in the database could differ in the db
"""
def save_batched_list_of_artworks(dept_id:int, limit:int = 3000):
    
    object_ids: List[int] = get_object_ids_by_department(department_id=dept_id)

    if(len(object_ids) == 0):
        print("No Object Ids found for", object_ids)


    list_of_artworks: List[ArtworkModel] = []
    dept_objects_in_db = 0

    for object_id in object_ids:

        if check_object_exists(object_id):
            continue
        
        time.sleep(DELAY_SECONDS)
        

        object_response:ObjectResponse = get_objects_by_object_id(object_id)
        if not object_response:
            db_batch_insert_artwork(list_of_artworks)
            print("Failed to complete collection, try again later")
            break


        artwork_response:ArtworkModel = transform_object_to_artwork(object_response)

        if validate_object_response(artwork_response):
            artwork_response['embedding'] = model.encode(artwork_response['searchable_text']).tolist()
            list_of_artworks.append(artwork_response) 
        
        
        if len(list_of_artworks) == BATCH_SIZE:

            print('STARTING WITH BATCH PROCESS...')
            db_batch_insert_artwork(list_of_artworks)
            dept_objects_in_db+=len(list_of_artworks)
            list_of_artworks:List[ArtworkModel] = [] 
        
        if dept_objects_in_db >= limit:
            break

    print("Data Collection from dept id", dept_id, " is completed!")