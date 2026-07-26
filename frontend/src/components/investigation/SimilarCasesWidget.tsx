import React, { useState } from 'react';
import { History, Shield, Scale, ChevronDown, ChevronUp, Clock, CheckCircle2, AlertTriangle, ArrowRight, Zap, Info } from 'lucide-react';
import { useSimilarCases } from '../../hooks/useSimilarCases';
import { CaseComparisonModal } from './CaseComparisonModal';

interface SimilarCasesWidgetProps {
  investigationId: string;
}

export const SimilarCasesWidget: React.FC<SimilarCasesWidgetProps> = ({ investigationId }) => {
  const { data: response, isLoading } = useSimilarCases(investigationId);
  const [expandedCaseId, setExpandedCaseId] = useState<string | null>(null);
  const [comparisonHistoricalId, setComparisonHistoricalId] = useState<string | null>(null);

  const toggleExpand = (caseId: string) => {
    setExpandedCaseId(prev => prev === caseId ? null : caseId);
  };

  if (isLoading) {
    return (
      <div className="bg-white border border-[#E4E7EC] rounded-sm p-4 text-center space-y-2 shadow-sm">
        <History className="h-5 w-5 animate-spin mx-auto text-brand-red" />
        <div className="text-[11px] font-medium text-[#6B7280]">Searching Enterprise Memory Store for similar precedent cases...</div>
      </div>
    );
  }

  if (!response || response.similarCases.length === 0) {
    return (
      <div className="bg-white border border-[#E4E7EC] rounded-sm p-4 text-center text-[11px] text-brand-gray shadow-sm">
        No similar historical case precedent records found in memory.
      </div>
    );
  }

  return (
    <div className="bg-white border border-[#E4E7EC] rounded-sm p-4 shadow-sm space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#E4E7EC] pb-3">
        <div>
          <div className="text-[11px] font-bold tracking-wider text-[#6B7280] uppercase flex items-center gap-1.5">
            <History className="h-3.5 w-3.5 text-brand-red" />
            Enterprise Similar Historical Case Retrieval
          </div>
          <div className="text-[12px] text-brand-gray mt-0.5">
            Institutional Memory Precedent & Multi-Dimensional Similarity Matching
          </div>
        </div>

        <span className="font-mono text-[10px] font-bold bg-[#EFF6FF] text-[#1E40AF] px-2 py-0.5 rounded-xs border border-[#BFDBFE]">
          Avg Similarity: {response.averageSimilarityPct.toFixed(0)}%
        </span>
      </div>

      {/* Executive Summary Card */}
      <div className="bg-[#F8FAFC] border border-[#E2E8F0] p-3 rounded-sm space-y-1">
        <div className="text-[10px] font-bold text-brand-black uppercase tracking-wider flex items-center gap-1.5">
          <Zap className="h-3.5 w-3.5 text-[#0284C7]" /> Executive Precedent Summary
        </div>
        <div className="text-[11px] leading-relaxed text-[#334155]">
          {response.executiveSimilaritySummary}
        </div>
      </div>

      {/* Itemized Similar Case Cards */}
      <div className="space-y-3">
        {response.similarCases.map((item) => {
          const isExpanded = expandedCaseId === item.caseId;
          const simPct = item.similarityBreakdown.overallSimilarityScore;

          return (
            <div 
              key={item.caseId}
              className="border border-[#E4E7EC] rounded-sm p-3 bg-white hover:border-[#CBD5E1] transition-all space-y-2"
            >
              {/* Card Header Row */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={`font-mono text-[11px] font-extrabold px-2 py-0.5 rounded-xs border ${
                    simPct >= 90 ? 'bg-[#ECFDF5] text-[#065F46] border-[#A7F3D0]' : 'bg-[#EFF6FF] text-[#1E40AF] border-[#BFDBFE]'
                  }`}>
                    {simPct.toFixed(0)}% MATCH
                  </span>

                  <span className="font-mono font-bold text-[12px] text-brand-black">#{item.caseId}</span>

                  <span className="text-[9px] font-mono font-bold uppercase bg-[#F3F4F6] text-[#374151] px-1.5 py-0.5 rounded-xs">
                    {item.caseTypology}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-[#6B7280] font-mono flex items-center gap-1">
                    <Clock className="h-3 w-3" /> Saved ~{item.estimatedAnalystTimeSavedMin} mins
                  </span>

                  <button 
                    onClick={() => toggleExpand(item.caseId)}
                    className="p-1 text-[#6B7280] hover:text-brand-black transition-colors cursor-pointer"
                  >
                    {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              {/* Sub-header details */}
              <div className="flex items-center justify-between text-[11px] font-mono pt-1">
                <div className="flex items-center gap-2">
                  <span className="text-brand-gray">Decision:</span>
                  <span className="font-bold text-brand-black bg-[#E5E7EB] px-1.5 py-0.5 rounded-xs">
                    {item.finalDecision}
                  </span>
                  <span className="text-brand-gray">Risk Score:</span>
                  <span className="font-bold text-brand-red">{item.riskScore}/100</span>
                </div>

                <div className="text-[10px] text-[#6B7280]">
                  Date: {item.investigationDate}
                </div>
              </div>

              {/* Primary Rules */}
              <div className="flex items-center gap-1 pt-0.5">
                <span className="text-[10px] font-bold text-brand-gray uppercase mr-1">Rules:</span>
                {item.primaryRules.map((rule, idx) => (
                  <span key={idx} className="font-mono text-[9px] bg-[#F1F5F9] text-[#334155] border border-[#E2E8F0] px-1.5 py-0.5 rounded-xs">
                    {rule}
                  </span>
                ))}
              </div>

              {/* EXPANDED VIEW DETAILED BREAKDOWN */}
              {isExpanded && (
                <div className="mt-3 pt-3 border-t border-[#F1F5F9] space-y-3 bg-[#F8FAFC] p-3 rounded-xs">
                  {/* Similarity Dimension Bars */}
                  <div>
                    <div className="text-[10px] font-bold text-brand-black uppercase tracking-wider mb-2">
                      Multi-Dimensional Similarity Breakdown
                    </div>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-[10px] font-mono">
                      <div className="flex justify-between items-center">
                        <span className="text-[#64748B]">Feature Vector:</span>
                        <span className="font-bold text-[#0284C7]">{item.similarityBreakdown.featureVectorSimilarity.toFixed(0)}%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-[#64748B]">Narrative Embedding:</span>
                        <span className="font-bold text-[#0284C7]">{item.similarityBreakdown.narrativeSimilarity.toFixed(0)}%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-[#64748B]">Rule Overlap:</span>
                        <span className="font-bold text-[#0284C7]">{item.similarityBreakdown.ruleOverlapScore.toFixed(0)}%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-[#64748B]">Typology Match:</span>
                        <span className="font-bold text-[#0284C7]">{item.similarityBreakdown.typologyMatchScore.toFixed(0)}%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-[#64748B]">Customer Profile:</span>
                        <span className="font-bold text-[#0284C7]">{item.similarityBreakdown.customerProfileSimilarity.toFixed(0)}%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-[#64748B]">Jurisdiction:</span>
                        <span className="font-bold text-[#0284C7]">{item.similarityBreakdown.jurisdictionSimilarity.toFixed(0)}%</span>
                      </div>
                    </div>
                  </div>

                  {/* Deterministic Analyst Reasons */}
                  <div className="space-y-1">
                    <div className="text-[10px] font-bold text-brand-black uppercase tracking-wider flex items-center gap-1">
                      <Info className="h-3 w-3 text-[#0284C7]" /> Deterministic Precedent Reasons
                    </div>
                    <div className="space-y-1 text-[10px] text-[#334155]">
                      {item.deterministicReasons.map((reason, idx) => (
                        <div key={idx} className="flex items-center gap-1.5">
                          <span className="h-1 w-1 rounded-full bg-[#0284C7]" />
                          <span>{reason}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Compare Side-by-Side Action Button */}
                  <div className="pt-1">
                    <button 
                      onClick={() => setComparisonHistoricalId(item.caseId)}
                      className="w-full bg-[#1E293B] hover:bg-[#0F172A] text-white text-[11px] font-bold uppercase tracking-wider py-1.5 px-3 rounded-xs flex items-center justify-center gap-1.5 transition-colors cursor-pointer"
                    >
                      <Scale className="h-3.5 w-3.5 text-[#38BDF8]" /> Compare Side-by-Side in Workspace
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Side by Side Comparison Workspace Modal */}
      {comparisonHistoricalId && (
        <CaseComparisonModal 
          currentId={investigationId}
          historicalCaseId={comparisonHistoricalId}
          onClose={() => setComparisonHistoricalId(null)}
        />
      )}
    </div>
  );
};
