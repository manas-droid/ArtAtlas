from typing import List
import requests
import time

from .met_data_model import ObjectIdResponse, ObjectResponse




def get_object_ids_by_department(department_id: int)-> List[int]:

    response = requests.get('https://collectionapi.metmuseum.org/public/collection/v1/objects', params={"departmentIds" : department_id})

    object_ids:ObjectIdResponse = response.json()

    return object_ids['objectIDs']




def get_objects_by_object_id(object_id:int, retry_times:int = 0)-> ObjectResponse:

    url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"

    response = requests.get(url)

    if response.status_code == 200:
            
        result = response.json()

        object_response: ObjectResponse = dict(
            (k, result[k]) for k in ObjectResponse.__annotations__
        )

        return object_response 

    elif response.status_code == 403 and retry_times <= 4:
        time.sleep(30*(retry_times+1))
        print('RETRYING ....')
        get_objects_by_object_id(object_id, retry_times+1)

    print("Failed to process the request for " , object_id, " API responded with: ",response)
    return {}

