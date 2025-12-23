from dataclasses import dataclass
from typing import TypedDict

from concept_data_pipeline.artwork_concept.prototypes import ConceptMatch



class SearchResponse(TypedDict):
    message:str
    results:list

"""
Used as an input for Evidenvce Bundle and Explanation Graph logic
"""
@dataclass(frozen=True)
class SearchContext:
    artworks:list[dict]
    essays: list[dict]
    detected_concepts: tuple[ConceptMatch]
    scores: dict
