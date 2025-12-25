
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class GraphNode:
    node_id:str
    node_type: Literal["query", "concept", "bundle", "artwork", "essay"]
    ref_id:int|str|None


@dataclass(frozen=True)
class LabeledGraphNode(GraphNode):
    label:str

@dataclass(frozen=True)
class BundleGraphNode(GraphNode):
    confidence:float




@dataclass(frozen=True)
class GraphEdge:
    from_node: str # node_id
    to_node: str # node_id
    edge_type: Literal["query_supports_concept", "concept_forms_bundle", "bundle_supported_by_artwork",  "bundle_supported_by_essay"] # explains the relationship between 2 nodes
    confidence:float
    provenance:str