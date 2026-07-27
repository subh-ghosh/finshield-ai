import { useQuery } from '@tanstack/react-query';
import { api } from '../core/api';

export interface MetricsResponse {
  total_rows: number;
  clean_rows: number;
  engineered_customers: number;
  flagged_rules_count: number;
  flagged_anomalies_count: number;
  execution_time_seconds: number;
  timings: Record<string, number>;
}

export interface WatchlistItem {
  customer_id: string;
  added_at: string;
  reason: string;
  priority: string;
}

export function useSystemMetrics() {
  return useQuery<MetricsResponse>({
    queryKey: ['system-metrics'],
    queryFn: async () => {
      const response = await api.get<MetricsResponse>('/v1/metrics');
      return response.data;
    },
    staleTime: 30 * 1000, // 30 seconds
  });
}

export function useWatchlist() {
  return useQuery<Record<string, WatchlistItem>>({
    queryKey: ['system-watchlist'],
    queryFn: async () => {
      const response = await api.get<Record<string, WatchlistItem>>('/v1/monitoring/watchlist');
      return response.data;
    },
    staleTime: 30 * 1000,
  });
}
