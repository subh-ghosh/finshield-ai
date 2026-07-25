export const queryKeys = {
  dashboard: {
    metrics: ['dashboard', 'metrics'] as const,
  },
  customer: {
    profile: (id: string) => ['customer', 'profile', id] as const,
  },
  queue: {
    all: ['queue', 'all'] as const,
  },
  investigation: {
    detail: (id: string) => ['investigation', 'detail', id] as const,
  }
};
