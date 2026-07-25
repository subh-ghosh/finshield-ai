import type { Evidence } from "../../domain/entities/PlannerTypes";
import { ShieldAlert, AlertTriangle, Info } from 'lucide-react';

export function EvidenceCard({ evidence }: { evidence: Evidence }) {
  return (
    <div className="flex gap-3 p-3 bg-[#FAFBFC] border border-[#F0F1F3] hover:border-[#E4E7EC] hover:shadow-sm transition-all cursor-default">
      <div className="mt-0.5 flex-shrink-0">
        {evidence.severity === 'critical' && <AlertTriangle className="h-3.5 w-3.5 text-brand-red" />}
        {evidence.severity === 'high' && <ShieldAlert className="h-3.5 w-3.5 text-[#F59E0B]" />}
        {(evidence.severity === 'medium' || evidence.severity === 'low') && <Info className="h-3.5 w-3.5 text-[#3B82F6]" />}
      </div>
      <div className="flex-1">
        <div className="flex items-start justify-between gap-4">
          <div className="text-[12px] font-semibold text-brand-black">{evidence.title}</div>
          {evidence.confidence && (
            <span className="text-[10px] text-brand-gray whitespace-nowrap">
              Conf: {(evidence.confidence * 100).toFixed(0)}%
            </span>
          )}
        </div>
        <div className="text-[11px] text-brand-gray mt-0.5 leading-relaxed">{evidence.desc}</div>
        
        {(evidence.source || evidence.timestamp) && (
          <div className="flex items-center gap-3 mt-2 text-[10px] text-brand-gray font-medium uppercase tracking-wider">
            {evidence.source && <span>{evidence.source}</span>}
            {evidence.timestamp && <span>{evidence.timestamp}</span>}
          </div>
        )}
      </div>
    </div>
  );
}
