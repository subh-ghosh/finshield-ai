import type { PlannerResult } from '../../types/planner';
import { CheckCircle2, ShieldAlert } from 'lucide-react';

export function InvestigationHeader({ result }: { result: PlannerResult }) {
  return (
    <div className="h-14 bg-[#FAFBFC] border-b border-[#E4E7EC] flex items-center justify-between px-6 flex-shrink-0">
      <div className="flex items-center gap-3">
        <span className="text-[12px] font-bold tracking-wider uppercase text-[#6B7280]">
          Enterprise Investigation
        </span>
        <span className="px-2 py-0.5 bg-brand-black text-white text-[10px] font-bold tracking-widest rounded-sm">
          {result.customer_id}
        </span>
      </div>
      <div className="flex items-center gap-2">
        {result.investigation_complete ? (
          <span className="inline-flex items-center gap-1.5 text-[11px] font-medium text-[#10B981] bg-[#10B981]/10 px-2.5 py-1 rounded-full">
            <CheckCircle2 className="h-3.5 w-3.5" /> Complete
          </span>
        ) : (
          <span className="inline-flex items-center gap-1.5 text-[11px] font-medium text-[#F59E0B] bg-[#F59E0B]/10 px-2.5 py-1 rounded-full">
            <ShieldAlert className="h-3.5 w-3.5" /> Incomplete
          </span>
        )}
      </div>
    </div>
  );
}
