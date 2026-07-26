import React from 'react';
import { useGraphSummary } from '../../hooks/useGraphSummary';
import { Loader2, AlertCircle, Share2, Users, MonitorSmartphone, Target } from 'lucide-react';

interface KnowledgeGraphSummaryProps {
  customerId: string;
}

export const KnowledgeGraphSummary: React.FC<KnowledgeGraphSummaryProps> = ({ customerId }) => {
  const { data, isLoading, isError, error } = useGraphSummary(customerId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-6 bg-slate-900 rounded-lg border border-slate-700/50">
        <Loader2 className="w-5 h-5 text-brand-blue animate-spin mr-3" />
        <span className="text-slate-300 text-sm">Analyzing network topography...</span>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex flex-col items-center justify-center p-6 bg-slate-900 rounded-lg border border-brand-red/20">
        <AlertCircle className="w-6 h-6 text-brand-red mb-2" />
        <span className="text-slate-300 text-sm">{error instanceof Error ? error.message : 'Failed to load network insights'}</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard icon={<Users className="w-4 h-4" />} label="Connected Customers" value={data.connected_customers} />
        <MetricCard icon={<MonitorSmartphone className="w-4 h-4" />} label="Shared Devices" value={data.shared_devices} />
        <MetricCard icon={<Share2 className="w-4 h-4" />} label="Communities" value={data.communities} />
        <MetricCard 
          icon={<Target className="w-4 h-4" />} 
          label="High Risk Links" 
          value={data.high_risk_connections} 
          highlight={data.high_risk_connections > 0} 
        />
      </div>

      {/* Deterministic Insights */}
      {data.insights && data.insights.length > 0 && (
        <div className="bg-slate-900 rounded-lg border border-slate-700/50 p-4">
          <h3 className="text-slate-200 text-sm font-semibold mb-3 flex items-center gap-2">
            <Share2 className="w-4 h-4 text-brand-blue" />
            Topological Insights
          </h3>
          <ul className="space-y-2">
            {data.insights.map((insight, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm">
                <span className="text-brand-blue mt-1">•</span>
                <span className={insight.includes('WARNING') ? 'text-brand-red font-medium' : 'text-slate-300'}>
                  {insight}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

function MetricCard({ icon, label, value, highlight = false }: { icon: React.ReactNode, label: string, value: number, highlight?: boolean }) {
  return (
    <div className={`p-4 rounded-lg border flex flex-col gap-1 ${highlight ? 'bg-brand-red/10 border-brand-red/30' : 'bg-slate-800 border-slate-700/50'}`}>
      <div className={`flex items-center gap-2 ${highlight ? 'text-brand-red' : 'text-slate-400'}`}>
        {icon}
        <span className="text-xs uppercase tracking-wider">{label}</span>
      </div>
      <span className={`text-2xl font-bold ${highlight ? 'text-brand-red' : 'text-slate-200'}`}>{value}</span>
    </div>
  );
}
