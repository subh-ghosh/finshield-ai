import type { ExecutionStep } from "../../types";
import { CheckCircle2, Clock, XCircle, Loader2 } from 'lucide-react';

export function ExecutionStepItem({ step, index }: { step: ExecutionStep; index: number }) {
  
  const getIcon = () => {
    switch(step.status) {
      case 'completed': return <CheckCircle2 className="h-3 w-3 text-[#10B981]" />;
      case 'failed': return <XCircle className="h-3 w-3 text-[#E1000F]" />;
      case 'running': return <Loader2 className="h-3 w-3 text-[#3B82F6] animate-spin" />;
      default: return <Clock className="h-3 w-3 text-[#9CA3AF]" />;
    }
  };

  return (
    <div className="text-[11px] bg-white border border-[#F0F1F3] p-2.5 shadow-sm flex flex-col gap-1.5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 font-mono">
          <span className="text-[#E1000F] font-bold">[{index + 1}]</span>
          <span className="text-[#1E1E1E] font-semibold">{step.tool_name}</span>
        </div>
        <div className="flex items-center gap-2">
          {step.duration_ms && <span className="text-[#9CA3AF] font-mono">{step.duration_ms}ms</span>}
          {getIcon()}
        </div>
      </div>
      
      {step.output && (
        <div className="mt-1 pl-6 text-[#6B7280] font-mono border-l border-[#F0F1F3] ml-2">
          {step.output}
        </div>
      )}
      {step.error && (
        <div className="mt-1 pl-6 text-[#E1000F] font-mono border-l border-[#FECACA] ml-2 bg-[#FEF2F2] p-1">
          {step.error}
        </div>
      )}
    </div>
  );
}
