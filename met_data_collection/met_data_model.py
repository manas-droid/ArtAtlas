from typing import List, TypedDict

# Key Names should be similar to the API
class ObjectIdResponse(TypedDict):
    total: int
    objectIDs: List[int]

# Key Names should be similar to the API
class ObjectResponse(TypedDict):
    objectID: int
    primaryImageSmall: str 
    artistDisplayName : str
    objectDate:str
    medium:str
    culture:str
    objectURL:str
    title: str
    department: str



class ArtworkModel(ObjectResponse):
    searchable_text:str
    embedding:list

