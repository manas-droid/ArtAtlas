"""Validation helpers for explanation graphs built from our GraphNode/GraphEdge objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence
import math

from explanation.graph.graph_model import GraphEdge, GraphNode


@dataclass(frozen=True)
class ValidationResult:
    errors: List[str]
    warnings: List[str]

    @property
    def ok(self) -> bool:
        return not self.errors


ALLOWED_NODE_TYPES = {"query", "concept", "bundle", "artwork", "essay"}
ALLOWED_EDGE_TYPES = {
    "query_supports_concept",
    "concept_forms_bundle",
    "bundle_supported_by_artwork",
    "bundle_supported_by_essay",
}

# Edge type → (from_node_type, to_node_type)
EDGE_TYPE_CONSTRAINTS = {
    "query_supports_concept": ("query", "concept"),
    "concept_forms_bundle": ("concept", "bundle"),
    "bundle_supported_by_artwork": ("bundle", "artwork"),
    "bundle_supported_by_essay": ("bundle", "essay"),
}

ALLOWED_PROVENANCE = {
    "v2_detected_concepts",
    "bundle_construction",
    "embedding_similarity",
}


def _is_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and not math.isnan(float(x))


def _mean(xs: Sequence[float]) -> float | None:
    if not xs:
        return None
    return sum(xs) / len(xs)


def validate_graph_objects(
    nodes: Sequence[GraphNode],
    edges: Sequence[GraphEdge],
    *,
    strict_provenance: bool = True,
    require_no_orphans: bool = True,
    confidence_eps: float = 1e-6,
    bundle_confidence_eps: float = 1e-4,
) -> ValidationResult:
    """Validate a graph expressed as GraphNode/GraphEdge objects."""
    errors: List[str] = []
    warnings: List[str] = []

    # Index nodes
    nodes_by_id: Dict[str, GraphNode] = {}
    for node in nodes:
        if node.node_id in nodes_by_id:
            errors.append(f"Duplicate node_id: '{node.node_id}'.")
            continue
        if node.node_type not in ALLOWED_NODE_TYPES:
            errors.append(
                f"Node '{node.node_id}' has invalid node_type '{node.node_type}'. "
                f"Allowed: {sorted(ALLOWED_NODE_TYPES)}"
            )
        nodes_by_id[node.node_id] = node

    node_ids = set(nodes_by_id.keys())
    query_nodes = [nid for nid, n in nodes_by_id.items() if n.node_type == "query"]
    if len(query_nodes) != 1:
        errors.append(f"Graph must contain exactly 1 query node; found {len(query_nodes)}.")
    query_node_id = query_nodes[0] if len(query_nodes) == 1 else None

    involved_node_ids = set()
    incoming: Dict[str, List[GraphEdge]] = {nid: [] for nid in node_ids}
    outgoing: Dict[str, List[GraphEdge]] = {nid: [] for nid in node_ids}

    for i, edge in enumerate(edges):
        if edge.edge_type not in ALLOWED_EDGE_TYPES:
            errors.append(
                f"Edge[{i}] has invalid edge_type '{edge.edge_type}'. "
                f"Allowed: {sorted(ALLOWED_EDGE_TYPES)}"
            )
        if edge.from_node not in node_ids:
            errors.append(f"Edge[{i}] has invalid from_node '{edge.from_node}'.")
            continue
        if edge.to_node not in node_ids:
            errors.append(f"Edge[{i}] has invalid to_node '{edge.to_node}'.")
            continue

        involved_node_ids.update([edge.from_node, edge.to_node])
        incoming[edge.to_node].append(edge)
        outgoing[edge.from_node].append(edge)

        if edge.edge_type in EDGE_TYPE_CONSTRAINTS:
            expected_from, expected_to = EDGE_TYPE_CONSTRAINTS[edge.edge_type]
            actual_from = nodes_by_id[edge.from_node].node_type
            actual_to = nodes_by_id[edge.to_node].node_type
            if actual_from != expected_from or actual_to != expected_to:
                errors.append(
                    f"Edge[{i}] '{edge.edge_type}' must connect {expected_from}→{expected_to}, "
                    f"but connects {actual_from}→{actual_to} ({edge.from_node}→{edge.to_node})."
                )

        # Confidence checks
        conf = edge.confidence
        if conf is None:
            errors.append(f"Edge[{i}] '{edge.edge_type}' missing confidence.")
        elif not _is_number(conf) or not (-confidence_eps <= float(conf) <= 1.0 + confidence_eps):
            errors.append(f"Edge[{i}] '{edge.edge_type}' confidence out of range [0,1]: {conf}.")
        if edge.edge_type == "concept_forms_bundle" and conf is not None and abs(float(conf) - 1.0) > confidence_eps:
            errors.append(
                f"Edge[{i}] 'concept_forms_bundle' confidence must be 1.0; got {conf}."
            )

        prov = edge.provenance
        if prov is None or not isinstance(prov, str) or not prov:
            errors.append(f"Edge[{i}] '{edge.edge_type}' missing/invalid provenance.")
        elif strict_provenance and prov not in ALLOWED_PROVENANCE:
            errors.append(
                f"Edge[{i}] provenance '{prov}' not allowed. Allowed: {sorted(ALLOWED_PROVENANCE)}"
            )
        elif (not strict_provenance) and prov not in ALLOWED_PROVENANCE:
            warnings.append(
                f"Edge[{i}] provenance '{prov}' is non-standard."
            )

    if require_no_orphans:
        for nid, node in nodes_by_id.items():
            if node.node_type == "query":
                continue
            if nid not in involved_node_ids:
                errors.append(
                    f"Orphan node '{nid}' (node_type={node.node_type}) has no incident edges."
                )

    bundle_nodes = [nid for nid, n in nodes_by_id.items() if n.node_type == "bundle"]
    for b in bundle_nodes:
        inc_cf = [e for e in incoming[b] if e.edge_type == "concept_forms_bundle"]
        if len(inc_cf) != 1:
            errors.append(
                f"Bundle '{b}' must have exactly 1 incoming 'concept_forms_bundle' edge; found {len(inc_cf)}."
            )
        out_support = [
            e for e in outgoing[b]
            if e.edge_type in {"bundle_supported_by_artwork", "bundle_supported_by_essay"}
        ]
        if len(out_support) < 1:
            errors.append(
                f"Bundle '{b}' must have at least 1 outgoing support edge to artwork/essay."
            )
        bnode = nodes_by_id[b]
        bconf = getattr(bnode, "confidence", None)
        if bconf is None:
            errors.append(f"Bundle node '{b}' missing 'confidence'.")
        elif not _is_number(bconf):
            errors.append(f"Bundle node '{b}' has non-numeric confidence: {bconf!r}.")
        else:
            edge_confs = [float(e.confidence) for e in out_support if _is_number(e.confidence)]
            m = _mean(edge_confs)
            if m is not None and abs(float(bconf) - m) > bundle_confidence_eps:
                errors.append(
                    f"Bundle '{b}' confidence ({float(bconf):.6f}) must equal mean of its "
                    f"support edge confidences ({m:.6f})."
                )

    concept_nodes = [nid for nid, n in nodes_by_id.items() if n.node_type == "concept"]
    for c in concept_nodes:
        inc_qc = [e for e in incoming[c] if e.edge_type == "query_supports_concept"]
        out_cb = [e for e in outgoing[c] if e.edge_type == "concept_forms_bundle"]
        if len(inc_qc) != 1:
            errors.append(
                f"Concept '{c}' must have exactly 1 incoming 'query_supports_concept' edge; found {len(inc_qc)}."
            )
        if len(out_cb) != 1:
            errors.append(
                f"Concept '{c}' must have exactly 1 outgoing 'concept_forms_bundle' edge; found {len(out_cb)}."
            )

    evidence_nodes = [nid for nid, n in nodes_by_id.items() if n.node_type in {"artwork", "essay"}]
    for ev in evidence_nodes:
        inc_support = [
            e for e in incoming[ev]
            if e.edge_type in {"bundle_supported_by_artwork", "bundle_supported_by_essay"}
        ]
        if len(inc_support) < 1:
            errors.append(
                f"Evidence node '{ev}' must have at least 1 incoming support edge."
            )

    def _has_cycle() -> bool:
        adj: Dict[str, List[str]] = {nid: [] for nid in node_ids}
        for edge in edges:
            if edge.from_node in node_ids and edge.to_node in node_ids:
                adj[edge.from_node].append(edge.to_node)

        WHITE, GRAY, BLACK = 0, 1, 2
        color: Dict[str, int] = {nid: WHITE for nid in node_ids}

        def dfs(u: str) -> bool:
            color[u] = GRAY
            for v in adj[u]:
                if color[v] == GRAY:
                    return True
                if color[v] == WHITE and dfs(v):
                    return True
            color[u] = BLACK
            return False

        return any(color[nid] == WHITE and dfs(nid) for nid in node_ids)

    if _has_cycle():
        errors.append("Graph must be acyclic, but a cycle was detected.")

    if query_node_id is not None:
        out_qc = [
            e for e in outgoing[query_node_id]
            if e.edge_type == "query_supports_concept"
        ]
        if len(out_qc) < 1:
            warnings.append("Query node has no outgoing 'query_supports_concept' edges.")

    return ValidationResult(errors=errors, warnings=warnings)
