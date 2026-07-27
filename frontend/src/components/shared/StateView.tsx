import type { ReactNode } from 'react';
import { AlertTriangle, Activity } from 'lucide-react';

interface StateViewProps {
  isLoading?: boolean;
  isError?: boolean;
  isEmpty?: boolean;
  error?: Error | null;
  loadingComponent?: ReactNode;
  emptyComponent?: ReactNode;
  errorComponent?: ReactNode;
  children: ReactNode;
}

export function StateView({
  isLoading,
  isError,
  isEmpty,
  error,
  loadingComponent,
  emptyComponent,
  errorComponent,
  children
}: StateViewProps) {
  if (isLoading) {
    return loadingComponent ? <>{loadingComponent}</> : (
      <div className="flex flex-col items-center justify-center p-12 text-brand-gray">
        <Activity className="h-6 w-6 animate-spin mb-3 text-brand-red" />
        <p className="text-[13px]">Loading data...</p>
      </div>
    );
  }

  if (isError) {
    return errorComponent ? <>{errorComponent}</> : (
      <div className="p-6 bg-[#FEF2F2] border border-[#FECACA] flex flex-col items-center justify-center text-center">
        <AlertTriangle className="h-8 w-8 text-brand-red mb-3" />
        <h3 className="text-[14px] font-bold text-brand-red">Failed to load data</h3>
        <p className="text-[12px] text-brand-gray mt-1">{error?.message || 'An unexpected error occurred'}</p>
        <button className="mt-4 text-[12px] font-semibold text-brand-black bg-white border border-[#E4E7EC] px-4 py-2 hover:bg-[#F9FAFB]" onClick={() => window.location.reload()}>
          Retry
        </button>
      </div>
    );
  }

  if (isEmpty) {
    return emptyComponent ? <>{emptyComponent}</> : (
      <div className="flex flex-col items-center justify-center p-12 text-brand-gray text-center">
        <p className="text-[13px]">No data available.</p>
      </div>
    );
  }

  return <>{children}</>;
}
