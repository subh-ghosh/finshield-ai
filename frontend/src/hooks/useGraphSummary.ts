import { useQuery } from '@tanstack/react-query';
import { getNetworkSummary } from '../core/api/graph';
import type { NetworkSummaryDTO } from '../types/graph';

export const useGraphSummary = (nodeId: string, enabled: boolean = true) => {
    return useQuery<NetworkSummaryDTO, Error>({
        queryKey: ['graphSummary', nodeId],
        queryFn: () => getNetworkSummary(nodeId),
        enabled: Boolean(nodeId) && enabled,
        staleTime: 5 * 60 * 1000, // 5 minutes
    });
};
