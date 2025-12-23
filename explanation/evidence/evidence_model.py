
from dataclasses import dataclass
from typing import Literal




@dataclass(frozen=True)
class Justification:
    justification_type : Literal["artwork_supports_concept", "essay_supports_concept"]
    source_id: int 
    confidence:float
    provenance: str


@dataclass(frozen=True)
class EvidenceBundle:
    evidence_id: str
    primary_concept:str
    artworks:list[dict]
    essay_chunks: list[dict]
    justification_edges: Justification


