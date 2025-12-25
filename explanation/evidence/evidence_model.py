
from dataclasses import dataclass
from typing import Literal




@dataclass(frozen=True)
class Justification:
    justification_type: Literal["artwork_supports_concept"]
    source_id: int 
    confidence:float
    provenance: str



@dataclass(frozen=True)
class ArtworkEvidence:
    artwork_id: int
    mapping_confidence:float
    provenance: str


@dataclass(frozen=True)
class EvidenceBundle:
    evidence_id: str
    primary_concept:int # concept_id
    bundled_artworks:list[ArtworkEvidence]
    justification_edges: list[Justification]
    evidence_confidence:float


