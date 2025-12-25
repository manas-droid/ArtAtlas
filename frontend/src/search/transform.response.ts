import type { Artwork, Concept, ExplanationBlock, SearchModel } from "./search.model";

export const transformResponseToUIModel = (apiResponse: any): SearchModel => {
    const requestedQuery = typeof apiResponse?.query === "string" ? apiResponse.query : "";

    const graph = apiResponse?.explanation_graph ?? {};
    const edges = ensureArray(graph.edges);
    const nodes = ensureArray(graph.nodes);
    const results = ensureArray(apiResponse.results);

    const explanationBlocks = buildExplanationBlocks(edges, nodes, results);

    return {
        explanationBlocks,
        metadata: {
            explanationComplete: Boolean(apiResponse?.meta?.explanation_complete ?? true),
            unexplainedResultsHidden: Boolean(apiResponse?.meta?.unexplained_results_hidden ?? true),
        },
        query: requestedQuery,
    };
};

const buildExplanationBlocks = (edges: any[], nodes: any[], results: any[]): ExplanationBlock[] => {
    const concepts: any[] = nodes.filter((node: any) => node?.node_type === "concept");
    const result: ExplanationBlock[] = [];
    const allArtworks: any[] = results.filter((res) => res?.result_type === "artwork");

    concepts.forEach((concept: any) => {
        const conceptEdge = edges.find(
            (edge: any) => edge?.edge_type === "query_supports_concept" && edge?.to_node === concept?.node_id
        );

        if (!conceptEdge) return;

        const conceptModel: Concept = {
            id: toNumber(concept?.node_id),
            label: concept?.label ?? "",
            confidenceValue: toNumber(conceptEdge.confidence),
            confidenceLabel: transformConfidenceToString(toNumber(conceptEdge.confidence)),
        };

        const evidenceEdge = edges.find(
            (edge: any) => edge?.edge_type === "concept_forms_bundle" && edge?.from_node === concept?.node_id
        );

        if (!evidenceEdge) return;

        const evidenceNode = nodes.find((node: any) => node?.node_id === evidenceEdge.to_node);
        if (!evidenceNode) return;

        const evidenceId: string = evidenceEdge.to_node;
        const evidenceConfidence: number = toNumber(evidenceNode.confidence);

        const supportArtWorksByEvidence: Artwork[] = edges
            .filter(
                (edge) => edge?.from_node === evidenceId && edge?.edge_type === "bundle_supported_by_artwork"
            )
            .map((edge) => {
                const artworkNode = nodes.find((node) => node?.node_id === edge?.to_node);
                if (!artworkNode) return null;

                const confidenceValue = toNumber(edge.confidence);
                const artworkRefId = toNumber(artworkNode.ref_id, NaN);
                if (!Number.isFinite(artworkRefId)) return null;

                const art = allArtworks.find((item) => toNumber(item?.id, NaN) === artworkRefId);
                if (!art) return null;

                const imageUrl = safeString(art.image_url);
                const title = safeString(art.title, "Untitled artwork");


                return {
                    artworkId: artworkRefId,
                    provenance: edge?.provenance ?? "",
                    supportStrengthValue: confidenceValue,
                    supportStrengthLabel: transformConfidenceToString(confidenceValue),
                    whyThisArtwork: explainWhyThisArtworks(edge?.provenance, concept?.label ?? ""),
                    imageUrl,
                    title,
                };
            })
            .filter(Boolean) as Artwork[];

        result.push({
            concept: conceptModel,
            evidence: {
                overallStrengthValue: evidenceConfidence,
                overallStrengthLabel: transformConfidenceToString(evidenceConfidence),
                artworks: supportArtWorksByEvidence,
            },
        });
    });

    return result;
};

function transformConfidenceToString(confidence: number): string {
    const value = Number.isFinite(confidence) ? confidence : 0;

    if (value >= 0.85) return "Very High";
    if (value >= 0.7) return "High";
    if (value >= 0.6) return "Moderate";
    return "Low";
}

function explainWhyThisArtworks(provenance: string, conceptName: string): string {
    if (provenance === "embedding_similarity") return `visual features closely match known ${conceptName} compositions`;

    return "";
}

function ensureArray<T>(value: T[] | unknown): T[] {
    return Array.isArray(value) ? value : [];
}

function toNumber(value: unknown, fallback = 0): number {
    const parsed = typeof value === "string" ? Number(value) : value;
    return Number.isFinite(parsed) ? (parsed as number) : fallback;
}

function safeString(value: unknown, fallback = ""): string {
    return typeof value === "string" && value.trim().length > 0 ? value : fallback;
}
