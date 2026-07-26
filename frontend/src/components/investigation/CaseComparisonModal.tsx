import React from 'react';
import { X, Scale, CheckCircle2, AlertTriangle, ArrowRight, Shield, Activity, Clock, FileText } from 'lucide-react';
import { useCaseComparison } from '../../hooks/useSimilarCases';

interface CaseComparisonModalProps {
  currentId: string;
  historicalCaseId: string | null;
  onClose: () => void;
}

export const CaseComparisonModal: React.FC<CaseComparisonModalProps> = ({
  currentId,
  historicalCaseId,
  onClose,
}) => {
  const { data: comparison, isLoading } = useCaseComparison(currentId, historicalCaseId);

  if (!historicalCaseId) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white border border-[#CBD5E1] rounded-md shadow-2xl w-full max-w-5xl max-h-[90vh] flex flex-col overflow-hidden">
        {/* Modal Header */}
        <div className="bg-[#1E293B] text-white p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Scale className="h-5 w-5 text-[#38BDF8]" />
            <div>
              <h2 className="text-[14px] font-bold tracking-wide uppercase flex items-center gap-2">
                Enterprise Case Comparison Workspace
              </h2>
              <p className="text-[11px] text-[#94A3B8]">
                Side-by-Side Comparative Analysis: Active Case <span className="font-mono text-white">#{currentId}</span> vs Historical Case <span className="font-mono text-[#38BDF8]">#{historicalCaseId}</span>
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1 hover:bg-[#334155] rounded-full text-[#94A3B8] hover:text-white transition-colors cursor-pointer"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-5 overflow-y-auto space-y-4">
          {isLoading ? (
            <div className="py-16 text-center space-y-2">
              <Activity className="h-6 w-6 animate-spin mx-auto text-[#0284C7]" />
              <div className="text-[12px] font-medium text-[#64748B]">Computing multi-dimensional similarity comparison...</div>
            </div>
          ) : comparison ? (
            <>
              {/* Executive Summary Card */}
              <div className="bg-[#F0F9FF] border border-[#BAE6FD] p-3.5 rounded-sm space-y-1.5">
                <div className="flex items-center justify-between text-[11px] font-bold text-[#0369A1] uppercase tracking-wider">
                  <span className="flex items-center gap-1.5">
                    <FileText className="h-4 w-4 text-[#0284C7]" /> Executive Comparison Assessment
                  </span>
                  <span className="font-mono font-extrabold text-[12px] bg-[#E0F2FE] px-2 py-0.5 rounded-xs border border-[#7DD3FC]">
                    Match Score: {comparison.overallSimilarityPct.toFixed(0)}%
                  </span>
                </div>
                <div className="text-[11px] leading-relaxed text-[#0C4A6E]">
                  {comparison.executiveComparisonSummary}
                </div>
              </div>

              {/* Side by Side Metric Cards */}
              <div className="grid grid-cols-2 gap-4">
                {/* CURRENT CASE CARD */}
                <div className="border border-[#CBD5E1] rounded-sm p-4 bg-[#F8FAFC] space-y-3">
                  <div className="border-b border-[#E2E8F0] pb-2 flex justify-between items-center">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-[#475569]">Current Active Case</span>
                    <span className="font-mono text-[12px] font-bold text-brand-black">#{comparison.currentInvestigationId}</span>
                  </div>

                  <div className="space-y-2 text-[11px]">
                    <div className="flex justify-between items-center py-1 border-b border-[#F1F5F9]">
                      <span className="text-[#64748B]">Risk Score:</span>
                      <span className="font-mono font-bold text-brand-red">{comparison.riskScoreComparison.current}/100</span>
                    </div>

                    <div className="flex justify-between items-center py-1 border-b border-[#F1F5F9]">
                      <span className="text-[#64748B]">Decision Status:</span>
                      <span className="font-mono font-bold text-white bg-brand-red px-1.5 py-0.5 rounded-xs text-[10px]">
                        {comparison.decisionComparison.current}
                      </span>
                    </div>

                    <div className="flex justify-between items-center py-1 border-b border-[#F1F5F9]">
                      <span className="text-[#64748B]">AML Typology:</span>
                      <span className="font-mono font-bold text-brand-black bg-[#E2E8F0] px-1.5 py-0.5 rounded-xs text-[10px]">
                        {comparison.typologyComparison.current}
                      </span>
                    </div>

                    <div className="py-1">
                      <span className="text-[#64748B] block mb-1">Triggered Rules:</span>
                      <div className="flex flex-wrap gap-1">
                        {comparison.rulesComparison.current.map((r, i) => (
                          <span key={i} className="font-mono text-[9px] font-semibold bg-[#F1F5F9] text-[#334155] border border-[#CBD5E1] px-1.5 py-0.5 rounded-xs">
                            {r}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* HISTORICAL CASE CARD */}
                <div className="border border-[#38BDF8]/40 rounded-sm p-4 bg-[#F0F9FF] space-y-3">
                  <div className="border-b border-[#BAE6FD] pb-2 flex justify-between items-center">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-[#0369A1]">Historical Precedent</span>
                    <span className="font-mono text-[12px] font-bold text-[#0284C7]">#{comparison.historicalCaseId}</span>
                  </div>

                  <div className="space-y-2 text-[11px]">
                    <div className="flex justify-between items-center py-1 border-b border-[#E0F2FE]">
                      <span className="text-[#0369A1]">Risk Score:</span>
                      <span className="font-mono font-bold text-[#0284C7]">{comparison.riskScoreComparison.historical}/100</span>
                    </div>

                    <div className="flex justify-between items-center py-1 border-b border-[#E0F2FE]">
                      <span className="text-[#0369A1]">Historical Outcome:</span>
                      <span className="font-mono font-bold text-white bg-[#0369A1] px-1.5 py-0.5 rounded-xs text-[10px]">
                        {comparison.decisionComparison.historical}
                      </span>
                    </div>

                    <div className="flex justify-between items-center py-1 border-b border-[#E0F2FE]">
                      <span className="text-[#0369A1]">AML Typology:</span>
                      <span className="font-mono font-bold text-[#0C4A6E] bg-[#E0F2FE] border border-[#BAE6FD] px-1.5 py-0.5 rounded-xs text-[10px]">
                        {comparison.typologyComparison.historical}
                      </span>
                    </div>

                    <div className="py-1">
                      <span className="text-[#0369A1] block mb-1">Triggered Rules:</span>
                      <div className="flex flex-wrap gap-1">
                        {comparison.rulesComparison.historical.map((r, i) => (
                          <span key={i} className="font-mono text-[9px] font-semibold bg-[#E0F2FE] text-[#0369A1] border border-[#BAE6FD] px-1.5 py-0.5 rounded-xs">
                            {r}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Matching Indicators & Differences */}
              <div className="grid grid-cols-2 gap-4 pt-1">
                <div className="border border-[#86EFAC] bg-[#F0FDF4] p-3 rounded-sm space-y-1.5">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-[#166534] flex items-center gap-1">
                    <CheckCircle2 className="h-3.5 w-3.5 text-[#16A34A]" /> Key Matching Indicators
                  </div>
                  <div className="space-y-1 text-[11px] text-[#14532D]">
                    {comparison.matchingIndicators.map((item, idx) => (
                      <div key={idx} className="flex items-center gap-1.5 font-medium">
                        <span className="h-1.5 w-1.5 rounded-full bg-[#16A34A] shrink-0" />
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="border border-[#FED7AA] bg-[#FFF7ED] p-3 rounded-sm space-y-1.5">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-[#C2410C] flex items-center gap-1">
                    <AlertTriangle className="h-3.5 w-3.5 text-[#EA580C]" /> Key Variance Highlights
                  </div>
                  <div className="space-y-1 text-[11px] text-[#7C2D12]">
                    {comparison.differenceHighlights.map((item, idx) => (
                      <div key={idx} className="flex items-center gap-1.5 font-medium">
                        <span className="h-1.5 w-1.5 rounded-full bg-[#EA580C] shrink-0" />
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
};
