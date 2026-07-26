import { useQuery } from '@tanstack/react-query';
import { getEgoGraph } from '../core/api/graph';
import type { GraphResponseDTO } from '../types/graph';

export const useKnowledgeGraph = (nodeId: string, radius: number = 1, entityTypes?: string, enabled: boolean = true) => {
    return useQuery<GraphResponseDTO, Error>({
        queryKey: ['knowledgeGraph', nodeId, radius, entityTypes],
        queryFn: () => getEgoGraph(nodeId, radius, entityTypes),
        enabled: Boolean(nodeId) && enabled,
        staleTime: 5 * 60 * 1000, // 5 minutes
    });

};
