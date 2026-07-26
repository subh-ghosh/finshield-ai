import React, { useState, useEffect } from 'react';
import { api } from '../../core/api';
import { Loader2, AlertCircle, CheckCircle2, XCircle, Sparkles, ShieldCheck } from 'lucide-react';

interface RuleSuggestion {
  name: string;
  description: string;
  column: string;
  operator: string;
  threshold: number;
  confidence: number;
  status: string;
}

interface RuleSuggestionsWidgetProps {
  className?: string;
}

export const RuleSuggestionsWidget: React.FC<RuleSuggestionsWidgetProps> = ({ className }) => {
  const [suggestions, setSuggestions] = useState<RuleSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSuggestions = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/v1/rules/suggestions');
        setSuggestions(response.data.data || []);
        setError(null);
      } catch (err: any) {
        setError(err?.message || 'Failed to load rule suggestions');
      } finally {
        setIsLoading(false);
      }
    };
    fetchSuggestions();
  }, []);

  const handleApprove = async (ruleName: string) => {
    try {
      await api.post(`/v1/rules/approve/${ruleName}`);
      setSuggestions(prev =>
        prev.map(s => s.name === ruleName ? { ...s, status: 'APPROVED' } : s)
      );
    } catch (err) {
      console.error('Failed to approve rule:', err);
    }
  };

  const handleReject = async (ruleName: string) => {
    try {
      await api.post(`/v1/rules/reject/${ruleName}`);
      setSuggestions(prev =>
        prev.map(s => s.name === ruleName ? { ...s, status: 'REJECTED' } : s)
      );
    } catch (err) {
      console.error('Failed to reject rule:', err);
    }
  };

  if (isLoading) {
    return (
      <div className={`p-6 bg-white border border-[#E4E7EC] ${className || ''}`}>
        <div className="flex items-center gap-3">
          <Loader2 className="w-5 h-5 text-brand-red animate-spin" />
          <span className="text-[12px] text-brand-gray font-medium">Analyzing feature distributions...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`p-6 bg-white border border-[#E4E7EC] ${className || ''}`}>
        <div className="flex items-center gap-2 text-brand-red">
          <AlertCircle className="w-5 h-5" />
          <span className="text-[12px]">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white border border-[#E4E7EC] ${className || ''}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-[#E4E7EC] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-brand-red" />
          <h3 className="text-[12px] font-bold text-brand-black uppercase tracking-wider">
            AI-Suggested Rules
          </h3>
        </div>
        <span className="text-[11px] bg-[#F3F4F6] text-brand-gray px-2 py-0.5 font-mono">
          {suggestions.length} suggestions
        </span>
      </div>

      {/* Suggestions List */}
      {suggestions.length === 0 ? (
        <div className="p-6 text-center">
          <ShieldCheck className="w-8 h-8 text-[#10B981] mx-auto mb-2" />
          <p className="text-[12px] text-brand-gray">No rule suggestions at this time. Current rules provide adequate coverage.</p>
        </div>
      ) : (
        <div className="divide-y divide-[#E4E7EC]">
          {suggestions.map((rule) => (
            <div key={rule.name} className="px-6 py-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[12px] font-bold text-brand-black font-mono">
                      {rule.name}
                    </span>
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 uppercase tracking-wider ${
                      rule.status === 'APPROVED' 
                        ? 'bg-[#E6F4EA] text-[#166534]' 
                        : rule.status === 'REJECTED'
                        ? 'bg-[#FEF2F2] text-brand-red'
                        : 'bg-[#FFF7ED] text-[#9A3412]'
                    }`}>
                      {rule.status}
                    </span>
                  </div>
                  <p className="text-[11px] text-[#6B7280] leading-relaxed mb-2">
                    {rule.description}
                  </p>
                  <div className="flex items-center gap-4 text-[10px] text-brand-gray font-mono">
                    <span>Column: <strong className="text-brand-black">{rule.column}</strong></span>
                    <span>Operator: <strong className="text-brand-black">{rule.operator}</strong></span>
                    <span>Threshold: <strong className="text-brand-black">{rule.threshold.toFixed(2)}</strong></span>
                  </div>
                  {/* Confidence Bar */}
                  <div className="mt-2 flex items-center gap-2">
                    <div className="flex-1 bg-[#F3F4F6] h-1.5 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-brand-red rounded-full transition-all"
                        style={{ width: `${rule.confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-[10px] font-bold text-brand-black">
                      {(rule.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>

                {/* Action Buttons */}
                {rule.status === 'PENDING' && (
                  <div className="flex flex-col gap-1.5 flex-shrink-0">
                    <button
                      onClick={() => handleApprove(rule.name)}
                      className="flex items-center gap-1 px-3 py-1.5 bg-[#10B981] text-white text-[10px] font-bold uppercase tracking-wider hover:bg-[#059669] transition-colors"
                    >
                      <CheckCircle2 className="w-3 h-3" /> Approve
                    </button>
                    <button
                      onClick={() => handleReject(rule.name)}
                      className="flex items-center gap-1 px-3 py-1.5 bg-[#F3F4F6] text-[#6B7280] text-[10px] font-bold uppercase tracking-wider hover:bg-[#E5E7EB] transition-colors"
                    >
                      <XCircle className="w-3 h-3" /> Reject
                    </button>
                  </div>
                )}
                {rule.status === 'APPROVED' && (
                  <CheckCircle2 className="w-5 h-5 text-[#10B981] flex-shrink-0" />
                )}
                {rule.status === 'REJECTED' && (
                  <XCircle className="w-5 h-5 text-[#9CA3AF] flex-shrink-0" />
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
