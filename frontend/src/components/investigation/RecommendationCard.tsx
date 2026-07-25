import type { PlannerResult } from '../../types/planner';
import { Target, AlertTriangle } from 'lucide-react';

export function RecommendationCard({ result }: { result: PlannerResult }) {
  const isHighRisk = result.recommendation.toUpperCase().includes('SAR') || result.recommendation.toUpperCase().includes('MANUAL REVIEW');

  return (
    <div className={`p-5 border ${isHighRisk ? 'border-[#FECACA] bg-[#FEF2F2]' : 'border-[#E4E7EC] bg-[#F9FAFB]'}`}>
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-[10px] font-bold tracking-[0.15em] uppercase text-[#6B7280]">AI Recommendation</span>
            <span className="sg-badge sg-badge-neutral">{result.confidence} Confidence</span>
          </div>
          <div className={`text-[20px] font-bold ${isHighRisk ? 'text-brand-red' : 'text-brand-black'}`}>
            {result.recommendation}
          </div>
        </div>
        <div className={`w-12 h-12 rounded-full flex items-center justify-center ${isHighRisk ? 'bg-brand-red/10' : 'bg-[#E4E7EC]'}`}>
          {isHighRisk ? <AlertTriangle className="h-6 w-6 text-brand-red" /> : <Target className="h-6 w-6 text-[#6B7280]" />}
        </div>
      </div>
    </div>
  );
}
