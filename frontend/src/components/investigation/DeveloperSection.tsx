import { useState } from 'react';
import type { PlannerResult } from '../../types/planner';
import { ChevronDown, ChevronRight, Terminal } from 'lucide-react';

export function DeveloperSection({ result }: { result: PlannerResult }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="border border-[#E4E7EC] bg-[#FAFBFC] rounded-sm overflow-hidden">
      <button 
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-3 flex items-center justify-between text-[11px] font-bold tracking-wider uppercase text-[#6B7280] hover:bg-[#F3F4F6] transition-colors"
      >
        <div className="flex items-center gap-2">
          <Terminal className="h-3.5 w-3.5" /> Developer Details
        </div>
        {isExpanded ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
      </button>

      {isExpanded && (
        <div className="p-4 border-t border-[#E4E7EC] space-y-4 font-mono text-[11px]">
          <div>
            <span className="text-[#9CA3AF] block mb-1">Correlation ID</span>
            <span className="text-[#1E1E1E] break-all bg-white px-2 py-1 border border-[#E4E7EC] rounded-sm">
              {result.correlation_id}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-[#9CA3AF] block mb-1">Planner Status</span>
              <span className="text-[#1E1E1E]">{result.planner_status}</span>
            </div>
            <div>
              <span className="text-[#9CA3AF] block mb-1">Execution Time</span>
              <span className="text-[#1E1E1E]">{result.execution_time_ms.toFixed(2)} ms</span>
            </div>
            <div>
              <span className="text-[#9CA3AF] block mb-1">API Calls</span>
              <span className="text-[#1E1E1E]">{result.api_calls}</span>
            </div>
          </div>

          <div>
            <span className="text-[#9CA3AF] block mb-2">Tool Calls</span>
            <div className="flex flex-wrap gap-2">
              {result.tool_calls.map((tool, i) => (
                <span key={i} className="px-2 py-1 bg-[#1E1E1E] text-white rounded-sm text-[10px]">
                  {tool}
                </span>
              ))}
              {result.tool_calls.length === 0 && <span className="text-[#9CA3AF]">None</span>}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
