import React, { useState } from 'react';
import { ShieldAlert, CheckCircle2, AlertTriangle, Info, Lock, Check } from 'lucide-react';
import type { EvidenceGapAssessment } from '../../domain/entities/EvidenceGap';

interface EvidenceGapWidgetProps {
  assessment: EvidenceGapAssessment;
}

export const EvidenceGapWidget: React.FC<EvidenceGapWidgetProps> = ({ assessment }) => {
  const [showDetails, setShowDetails] = useState(false);

  const getScoreColor = (score: number) => {
    if (score >= 75) return 'text-[#10B981] bg-[#ECFDF5] border-[#A7F3D0]';
    if (score >= 50) return 'text-[#F59E0B] bg-[#FEF3C7] border-[#FDE68A]';
    return 'text-brand-red bg-[#FEF2F2] border-[#FECACA]';
  };

  const getProgressBarColor = (score: number) => {
    if (score >= 75) return 'bg-[#10B981]';
    if (score >= 50) return 'bg-[#F59E0B]';
    return 'bg-brand-red';
  };

  return (
    <div className="bg-white border border-[#E4E7EC] rounded-sm p-4 shadow-sm space-y-4">
      {/* Header & Score Gauge */}
      <div className="flex items-center justify-between">
        <div>
          <div className="text-[11px] font-bold tracking-wider text-[#6B7280] uppercase flex items-center gap-1.5">
            <ShieldAlert className="h-3.5 w-3.5 text-brand-red" />
            Compliance Evidence Completeness
          </div>
          <div className="text-[12px] text-brand-gray mt-0.5">
            Evaluated across 8 mandatory FinCEN compliance pillars
          </div>
        </div>

        <div className={`px-2.5 py-1 border rounded-sm font-mono font-bold text-[14px] ${getScoreColor(assessment.completenessScore)}`}>
          {assessment.completenessScore}%
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-[#F3F4F6] rounded-full h-2 overflow-hidden">
        <div 
          className={`h-full transition-all duration-500 ease-out ${getProgressBarColor(assessment.completenessScore)}`}
          style={{ width: `${assessment.completenessScore}%` }}
        />
      </div>

      {/* Readiness Banner */}
      <div className={`p-2.5 rounded-sm border flex items-center justify-between text-[11px] font-medium ${
        assessment.sarFilingReady 
          ? 'bg-[#ECFDF5] border-[#A7F3D0] text-[#065F46]' 
          : 'bg-[#FEF2F2] border-[#FECACA] text-[#991B1B]'
      }`}>
        <div className="flex items-center gap-2">
          {assessment.sarFilingReady ? (
            <CheckCircle2 className="h-4 w-4 text-[#10B981] shrink-0" />
          ) : (
            <Lock className="h-4 w-4 text-brand-red shrink-0" />
          )}
          <span>
            {assessment.sarFilingReady
              ? 'Ready for SAR Filing (All mandatory compliance evidence present)'
              : `SAR Filing Blocked (${assessment.blockingCriticalGapsCount} mandatory compliance item(s) missing)`}
          </span>
        </div>

        <button 
          onClick={() => setShowDetails(!showDetails)}
          className="text-[10px] font-semibold underline uppercase tracking-wider hover:opacity-80 ml-2"
        >
          {showDetails ? 'Hide Details' : 'View Checklist'}
        </button>
      </div>

      {/* Compliance Pillars Checklist */}
      <div className="space-y-1.5 border-t border-[#F3F4F6] pt-3">
        {assessment.evaluations.map((item, idx) => {
          const isPresent = item.status === 'PRESENT';
          return (
            <div 
              key={idx} 
              className={`flex items-center justify-between p-2 rounded-sm text-[11px] transition-colors ${
                isPresent ? 'bg-[#F9FAFB]' : 'bg-[#FEF2F2] border border-[#FECACA]'
              }`}
            >
              <div className="flex items-center gap-2 min-w-0">
                {isPresent ? (
                  <div className="w-4 h-4 rounded-full bg-[#ECFDF5] text-[#10B981] flex items-center justify-center shrink-0">
                    <Check className="h-3 w-3" />
                  </div>
                ) : (
                  <div className="w-4 h-4 rounded-full bg-[#FEF2F2] text-brand-red flex items-center justify-center shrink-0">
                    <AlertTriangle className="h-3 w-3" />
                  </div>
                )}
                <span className={`truncate font-medium ${isPresent ? 'text-brand-black' : 'text-[#991B1B]'}`}>
                  {item.name}
                </span>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                {item.isRequiredForSar && (
                  <span className="text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 bg-[#E5E7EB] text-[#374151] rounded-xs">
                    Required
                  </span>
                )}
                <span className={`font-mono text-[10px] font-bold ${isPresent ? 'text-[#10B981]' : 'text-brand-red'}`}>
                  {isPresent ? 'PASS' : 'MISSING'}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Expanded Remediation Roadmap Details */}
      {showDetails && assessment.remediationRoadmap.length > 0 && (
        <div className="bg-[#FFFBEB] border border-[#FDE68A] p-3 rounded-sm space-y-2 mt-2">
          <div className="text-[11px] font-bold text-[#92400E] flex items-center gap-1.5 uppercase tracking-wider">
            <Info className="h-3.5 w-3.5 text-[#D97706]" /> Recommended Remediation Actions
          </div>
          <ul className="space-y-1 text-[11px] text-[#78350F] pl-4 list-disc">
            {assessment.remediationRoadmap.map((action, i) => (
              <li key={i}>{action}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
