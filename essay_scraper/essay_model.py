
from enum import Enum
from typing import TypedDict


class EssayCategory(str, Enum):
    MOVEMENT = "movement"
    TECHNIQUE = "technique"
    GENRE = "genre"

class EssayResponse(TypedDict):
    chunks:list[str]
    essay_type:EssayCategory
    essay_title:str
    source:str
    source_url:str
