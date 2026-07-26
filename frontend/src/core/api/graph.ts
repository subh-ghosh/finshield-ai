import { api } from '../api';
import type { GraphResponseDTO, NetworkSummaryDTO, ApiResponse } from '../../types/graph';

export const getEgoGraph = async (nodeId: string, radius: number = 1): Promise<GraphResponseDTO> => {
    const response = await api.get<ApiResponse<GraphResponseDTO>>(`/v1/graph/ego/${nodeId}?radius=${radius}`);
    return response.data.data;
};

export const getNetworkSummary = async (nodeId: string): Promise<NetworkSummaryDTO> => {
    const response = await api.get<ApiResponse<NetworkSummaryDTO>>(`/v1/graph/summary/${nodeId}`);
    return response.data.data;
};
