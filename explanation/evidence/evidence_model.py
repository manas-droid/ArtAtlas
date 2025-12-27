
from dataclasses import dataclass
from typing import Literal



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
    evidence_confidence:float


