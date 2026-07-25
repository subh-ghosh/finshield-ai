import { Activity } from 'lucide-react';

export function LoadingInvestigation() {
  return (
    <div className="h-full flex flex-col items-center justify-center p-8 bg-white">
      <div className="w-16 h-16 relative flex items-center justify-center mb-6">
        <div className="absolute inset-0 rounded-full border-4 border-[#F0F1F3]"></div>
        <div className="absolute inset-0 rounded-full border-4 border-[#E1000F] border-t-transparent animate-spin"></div>
        <Activity className="h-6 w-6 text-[#E1000F] animate-pulse" />
      </div>
      
      <h3 className="text-[16px] font-bold text-[#1E1E1E] mb-2">LangGraph Investigation Running</h3>
      <p className="text-[13px] text-[#6B7280] mb-8 text-center max-w-md">
        The Enterprise Planner is orchestrating the investigation pipeline, evaluating risk, and gathering explanations...
      </p>

      <div className="w-full max-w-md space-y-4">
        {[
          { label: 'Planner Started', status: 'done' },
          { label: 'Backend Analysis & Risk Engine', status: 'running' },
          { label: 'Explainability Service', status: 'pending' },
          { label: 'AI Reasoning', status: 'pending' },
          { label: 'Report Generation', status: 'pending' },
        ].map((step, i) => (
          <div key={i} className="flex items-center gap-3">
            <div className={`w-4 h-4 rounded-full flex shrink-0 items-center justify-center ${
              step.status === 'done' ? 'bg-[#10B981]' : 
              step.status === 'running' ? 'bg-[#E1000F] animate-pulse' : 'bg-[#E4E7EC]'
            }`}>
              {step.status === 'done' && <div className="w-2 h-2 bg-white rounded-full"></div>}
            </div>
            <span className={`text-[12px] ${
              step.status === 'done' ? 'text-[#10B981] font-medium' :
              step.status === 'running' ? 'text-[#1E1E1E] font-bold' : 'text-[#9CA3AF]'
            }`}>{step.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
