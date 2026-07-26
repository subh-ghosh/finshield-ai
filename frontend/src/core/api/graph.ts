import { api } from '../api';
import type { GraphResponseDTO, NetworkSummaryDTO, ApiResponse } from '../../types/graph';

export const getEgoGraph = async (nodeId: string, radius: number = 1, entityTypes?: string): Promise<GraphResponseDTO> => {
    let url = `/v1/graph/ego/${nodeId}?radius=${radius}`;
    if (entityTypes) url += `&entity_types=${entityTypes}`;
    const response = await api.get<ApiResponse<GraphResponseDTO>>(url);
    return response.data.data;
};

export const getNetworkSummary = async (nodeId: string): Promise<NetworkSummaryDTO> => {
    const response = await api.get<ApiResponse<NetworkSummaryDTO>>(`/v1/graph/summary/${nodeId}`);
    return response.data.data;
};
