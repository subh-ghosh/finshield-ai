/**
 * Hooks for the 3 new agent tool endpoints:
 * - GET /api/v1/features/{id}        -> useCustomerFeatures
 * - GET /api/v1/anomaly/{id}         -> useCustomerAnomaly
 * - GET /api/v1/risk-classify/{id}   -> useCustomerRiskClassification
 */
import { useQuery } from '@tanstack/react-query';
import { api } from '../core/api';

// ── Feature Engineering ──────────────────────────────────────────────────────
export function useCustomerFeatures(customerId: string) {
  return useQuery({
    queryKey: ['customer-features', customerId],
    queryFn: async () => {
      const res = await api.get<any>(`/v1/features/${customerId}`);
      return res.data;
    },
    enabled: Boolean(customerId),
    staleTime: 60_000,
    retry: 1,
  });
}

// ── Anomaly Detection ─────────────────────────────────────────────────────────
export function useCustomerAnomaly(customerId: string) {
  return useQuery({
    queryKey: ['customer-anomaly', customerId],
    queryFn: async () => {
      const res = await api.get<any>(`/v1/anomaly/${customerId}`);
      return res.data;
    },
    enabled: Boolean(customerId),
    staleTime: 60_000,
    retry: 1,
  });
}

// ── Risk Classification ───────────────────────────────────────────────────────
export function useCustomerRiskClassification(customerId: string) {
  return useQuery({
    queryKey: ['customer-risk-classification', customerId],
    queryFn: async () => {
      const res = await api.get<any>(`/v1/risk-classify/${customerId}`);
      return res.data;
    },
    enabled: Boolean(customerId),
    staleTime: 60_000,
    retry: 1,
  });
}

// ── Risk Distribution (dataset-level) ────────────────────────────────────────
export function useRiskDistribution() {
  return useQuery({
    queryKey: ['risk-distribution'],
    queryFn: async () => {
      const res = await api.get<any>('/v1/risk-classify/summary/distribution');
      return res.data;
    },
    staleTime: 120_000,
    retry: 1,
  });
}

// ── Top Anomalous Customers (dataset-level) ──────────────────────────────────
export function useTopAnomalousCustomers(topN = 10) {
  return useQuery({
    queryKey: ['top-anomalous', topN],
    queryFn: async () => {
      const res = await api.get<any>(`/v1/anomaly/summary/top?top_n=${topN}`);
      return res.data;
    },
    staleTime: 120_000,
    retry: 1,
  });
}
