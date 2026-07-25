import type { PlannerResult } from '../../types/planner';
import { LoadingInvestigation } from './LoadingInvestigation';
import { InvestigationHeader } from './InvestigationHeader';
import { RecommendationCard } from './RecommendationCard';
import { ReasoningTimeline } from './ReasoningTimeline';
import { DeveloperSection } from './DeveloperSection';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Activity, ShieldAlert, AlertTriangle } from 'lucide-react';

interface Props {
  result?: PlannerResult;
  isPending: boolean;
  error?: Error | null;
  onRetry: () => void;
}

export function InvestigationReportView({ result, isPending, error, onRetry }: Props) {
  if (isPending) {
    return <LoadingInvestigation />;
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-8 h-full bg-[#FEF2F2]">
        <AlertTriangle className="h-10 w-10 text-brand-red mb-4" />
        <h3 className="text-[16px] font-bold text-brand-red mb-2">Investigation Failed</h3>
        <p className="text-[13px] text-brand-black mb-6 text-center max-w-md">
          {error.message || 'An unexpected error occurred while communicating with the Planner API.'}
        </p>
        <button 
          onClick={onRetry}
          className="bg-brand-red hover:bg-[#c5000d] text-white font-bold py-2 px-6 text-[12px] tracking-wider transition-colors shadow-sm"
        >
          RETRY INVESTIGATION
        </button>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center p-8">
        <div className="w-14 h-14 rounded-full bg-white border border-[#E4E7EC] flex items-center justify-center mb-4 shadow-sm">
          <Activity className="h-6 w-6 text-brand-gray" />
        </div>
        <div className="text-[14px] font-semibold text-[#6B7280]">Enterprise Planner Ready</div>
        <div className="text-[12px] text-brand-gray max-w-sm mt-1.5 leading-relaxed">
          Click the button below to trigger the LangGraph orchestration engine. The AI will autonomously investigate this entity.
        </div>
        <button 
          onClick={onRetry}
          className="mt-6 bg-brand-red hover:bg-[#c5000d] text-white font-bold py-2 px-6 text-[12px] tracking-wider transition-colors shadow-sm"
        >
          START INVESTIGATION
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-y-auto bg-white">
      <InvestigationHeader result={result} />
      
      <div className="p-6 space-y-6">
        {result.errors && result.errors.length > 0 && (
          <div className="bg-[#FEF2F2] border border-[#FECACA] p-4 flex gap-3">
            <ShieldAlert className="h-5 w-5 text-brand-red shrink-0" />
            <div>
              <h4 className="text-[13px] font-bold text-brand-red mb-1">Warnings Encountered</h4>
              <ul className="list-disc pl-4 text-[12px] text-brand-black space-y-1">
                {result.errors.map((err, i) => <li key={i}>{err}</li>)}
              </ul>
            </div>
          </div>
        )}

        <RecommendationCard result={result} />

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-2 space-y-6">
            <div className="border border-[#E4E7EC] p-5">
              <h3 className="sg-section-label mb-4 pb-2 border-b border-[#E4E7EC]">Final Investigation Report</h3>
              <div className="prose prose-sm max-w-none prose-headings:font-bold prose-headings:text-brand-black prose-p:text-brand-black prose-p:leading-relaxed text-[13px]">
                {result.final_report ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{result.final_report}</ReactMarkdown>
                ) : (
                  <span className="text-brand-gray italic">No report generated.</span>
                )}
              </div>
            </div>
          </div>
          
          <div className="xl:col-span-1 space-y-6">
            <ReasoningTimeline steps={result.reasoning_steps} />
            <DeveloperSection result={result} />
          </div>
        </div>
      </div>
    </div>
  );
}
