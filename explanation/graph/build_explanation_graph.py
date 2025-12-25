

from concept_data_pipeline.artwork_concept.prototypes import ConceptMatch
from explanation.evidence.evidence_model import EvidenceBundle

from .graph_model import LabeledGraphNode, GraphNode, BundleGraphNode, GraphEdge

def build_explanation_graph(query:str, detected_concepts:tuple[ConceptMatch], evidence_bundles:list[EvidenceBundle])->tuple:
    nodes:dict[str, any] = {}
    query_node_id:str = "q:0"

    nodes[query_node_id] = LabeledGraphNode(label=query, node_id=query_node_id, node_type="query", ref_id=None)
    concept_conf_map = {
        c.concept_id: (c.confidence_score, c.concept_name)
        for c in detected_concepts
    }

    edges:list[GraphEdge] = []

    for evidence_bundle in evidence_bundles:
        
        evidence_bundle_node_id = f"b:{evidence_bundle.evidence_id}"
        
        # creating evidence bundle graph node 
        nodes[evidence_bundle_node_id] = BundleGraphNode(node_id=evidence_bundle_node_id, node_type="bundle", ref_id=evidence_bundle.evidence_id, confidence=evidence_bundle.evidence_confidence)

        concept_node_id = f"c:{evidence_bundle.primary_concept}"

        
        concept_confidence, concept_name = concept_conf_map.get(evidence_bundle.primary_concept)
        nodes[concept_node_id] = LabeledGraphNode(node_id=concept_node_id, node_type="concept", ref_id=evidence_bundle.primary_concept, label=concept_name)


        # Query → Concept edge

        edges.append(GraphEdge(from_node=query_node_id, 
                               to_node=concept_node_id, 
                               edge_type="query_supports_concept", 
                               confidence=concept_confidence,
                               provenance="v2_detected_concepts"
                               ))


        # Concept → Bundle edge (structural)
        edges.append(GraphEdge(from_node=concept_node_id, to_node=evidence_bundle_node_id, confidence=1.0, edge_type="concept_forms_bundle", provenance="bundle_construction"))

        # creating artwork graph node 
        for artwork in evidence_bundle.bundled_artworks:
            artwork_node_id = f"a:{artwork.artwork_id}"
            if artwork_node_id not in nodes:
                nodes[artwork_node_id] = GraphNode(node_id=artwork_node_id, node_type="artwork", ref_id=artwork.artwork_id)

            # Bundle → Artwork edge (this is the justification)
            edges.append(GraphEdge(from_node=evidence_bundle_node_id, to_node=artwork_node_id, confidence=artwork.mapping_confidence, edge_type="bundle_supported_by_artwork", provenance=artwork.provenance))



    return nodes, edges
