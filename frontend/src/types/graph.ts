export interface GraphNodeDTO {
    id: string;
    label: string;
    type: string;
    metadata: Record<string, any>;
}

export interface GraphEdgeDTO {
    source: string;
    target: string;
    relationship: string;
    weight: number;
    timestamp?: string;
    metadata: Record<string, any>;
}

export interface GraphResponseDTO {
    nodes: GraphNodeDTO[];
    edges: GraphEdgeDTO[];
}

export interface CentralityMetricsDTO {
    degree: number;
    betweenness: number;
    pagerank: number;
}

export interface NetworkSummaryDTO {
    connected_customers: number;
    shared_devices: number;
    shared_ips: number;
    shared_phones: number;
    connected_companies: number;
    connected_directors: number;
    communities: number;
    high_risk_connections: number;
    centrality: CentralityMetricsDTO;
    insights: string[];
}

export interface ApiResponse<T> {
    success: boolean;
    version: number;
    generated_at: string;
    data: T;
    message?: string;
}
