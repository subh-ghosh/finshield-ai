import React, { useState } from 'react';
import { Sliders, TrendingUp, RotateCcw, Zap, Target, CheckCircle2, ChevronDown, ChevronUp, Info, Play } from 'lucide-react';
import { useSimulation } from '../../hooks/useSimulation';

interface CounterfactualSimulatorWidgetProps {
  customerId: string;
  initialScore?: number;
  initialRecommendation?: string;
}

export const CounterfactualSimulatorWidget: React.FC<CounterfactualSimulatorWidgetProps> = ({
  customerId,
  initialScore = 41,
  initialRecommendation = 'MANUAL_REVIEW'
}) => {
  const [cashCount, setCashCount] = useState(0);
  const [cashAmount] = useState(9500);
  const [crossBorderChange, setCrossBorderChange] = useState(0);
  const [expandedItemId, setExpandedItemId] = useState<string | null>(null);

  const { mutate: runSimulation, data: simResult, isPending, reset: resetSimulation } = useSimulation();

  const handleRunSimulation = () => {
    runSimulation({
      customer_id: customerId,
      additional_cash_deposits_count: cashCount,
      additional_cash_deposit_amount: cashAmount,
      cross_border_transfer_change_pct: crossBorderChange,
      velocity_multiplier: 1.0
    });
  };

  const handleReset = () => {
    setCashCount(0);
    setCrossBorderChange(0);
    setExpandedItemId(null);
    resetSimulation();
  };

  const toggleExpand = (id: string) => {
    setExpandedItemId(prev => prev === id ? null : id);
  };

  const simulatedScore = simResult?.simulated_risk_score ?? initialScore;
  const simulatedRec = simResult?.simulated_recommendation ?? initialRecommendation;
  const totalDelta = simResult?.score_delta ?? 0;
  const isFlipped = simResult?.recommendation_flipped ?? false;
  const contributionItems = (simResult?.risk_contributions ? Object.values(simResult.risk_contributions) : []) as Array<{
    id: string;
    category: string;
    points: number;
    subsystem: string;
    confidence: number;
    reason: string;
  }>;
  
  const nextTarget = simResult?.next_threshold_target ?? 'ESCALATE';
  const targetScore = simResult?.next_threshold_score ?? 65;
  const minimumChanges = simResult?.minimum_changes_required ?? [];

  return (
    <div className="bg-white border border-[#E4E7EC] rounded-sm p-4 shadow-sm space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="text-[11px] font-bold tracking-wider text-[#6B7280] uppercase flex items-center gap-1.5">
            <Sliders className="h-3.5 w-3.5 text-brand-red" />
            Counterfactual Risk Simulator (API Powered)
          </div>
          <div className="text-[12px] text-brand-gray mt-0.5">
            Simulate parameter shifts & decision threshold boundaries
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button 
            onClick={handleReset}
            className="text-[10px] font-semibold text-[#6B7280] hover:text-brand-black flex items-center gap-1 uppercase tracking-wider bg-[#F3F4F6] px-2 py-1 rounded-sm transition-colors cursor-pointer"
          >
            <RotateCcw className="h-3 w-3" /> Reset
          </button>
          <button 
            onClick={handleRunSimulation}
            disabled={isPending}
            className="text-[10px] font-semibold text-white bg-brand-red hover:bg-red-700 flex items-center gap-1 uppercase tracking-wider px-3 py-1 rounded-sm transition-colors cursor-pointer disabled:opacity-50"
          >
            <Play className="h-3 w-3" /> {isPending ? 'Simulating...' : 'Run Simulation'}
          </button>
        </div>
      </div>

      {/* FEATURE 3: DECISION THRESHOLD INDICATOR BAR */}
      <div className="space-y-1.5 bg-[#F9FAFB] border border-[#E4E7EC] p-3 rounded-sm">
        <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider text-[#6B7280]">
          <span>Compliance Thresholds</span>
          <span className="font-mono text-brand-black font-bold">Baseline: {initialScore} | Sim: {simulatedScore}</span>
        </div>

        {/* Horizontal Bar with Pure Triangle Pointer Cursors */}
        <div className="relative w-full h-6 bg-[#E5E7EB] rounded-xs flex font-mono text-[9px] font-bold text-white text-center leading-6 shadow-inner">
          <div className="w-[35%] bg-[#10B981] border-r border-white/40">CLEAR (0-34)</div>
          <div className="w-[30%] bg-[#F59E0B] border-r border-white/40">REVIEW (35-64)</div>
          <div className="w-[20%] bg-[#EF4444] border-r border-white/40">ESCALATE (65-84)</div>
          <div className="w-[15%] bg-[#991B1B]">SAR (85+)</div>

          {/* Baseline Risk Pointer Pin Cursor (Upper ▼ & Lower ▲) */}
          <div 
            className="absolute top-0 bottom-0 -ml-[5px] z-10 transition-all duration-300 pointer-events-none"
            style={{ left: `${Math.min(99, Math.max(0, initialScore))}%` }}
            title={`Baseline Risk: ${initialScore}`}
          >
            <div className="absolute -top-3.5 left-0 text-[12px] font-bold text-black select-none">▼</div>
            <div className="absolute -bottom-3.5 left-0 text-[12px] font-bold text-black select-none">▲</div>
          </div>

          {/* Simulated Risk Pointer Pin Cursor (Upper ▼ & Lower ▲) */}
          <div 
            className="absolute top-0 bottom-0 -ml-[6px] z-20 transition-all duration-500 ease-out pointer-events-none animate-pulse"
            style={{ left: `${Math.min(99, Math.max(0, simulatedScore))}%` }}
            title={`Simulated Risk: ${simulatedScore}`}
          >
            <div className="absolute -top-4 left-0 text-[14px] font-extrabold text-[#D97706] drop-shadow-sm select-none">▼</div>
            <div className="absolute -bottom-4 left-0 text-[14px] font-extrabold text-[#D97706] drop-shadow-sm select-none">▲</div>
          </div>
        </div>

        <div className="flex justify-between text-[9px] font-mono text-[#6B7280] pt-1">
          <span className="flex items-center gap-1 font-bold text-black">
            ▼ Baseline Pin ({initialScore})
          </span>
          <span className="flex items-center gap-1 font-bold text-brand-red">
            ▼ Simulated Pin ({simulatedScore})
          </span>
        </div>
      </div>

      {/* Baseline vs Simulated Cards */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-3 p-3 bg-[#F9FAFB] border border-[#E4E7EC] rounded-sm">
        <div>
          <div className="text-[10px] uppercase font-bold text-[#6B7280]">Baseline Risk</div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="font-mono text-[16px] font-bold text-brand-black">{initialScore}/100</span>
            <span className="text-[10px] font-bold px-1.5 py-0.5 bg-[#E5E7EB] text-[#374151] rounded-xs font-mono">
              {initialRecommendation}
            </span>
          </div>
        </div>

        <div>
          <div className="text-[10px] uppercase font-bold text-[#6B7280]">Simulated Risk</div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className={`font-mono text-[16px] font-bold ${
              totalDelta > 0 ? 'text-brand-red' : totalDelta < 0 ? 'text-[#10B981]' : 'text-brand-black'
            }`}>
              {simulatedScore}/100 ({totalDelta >= 0 ? `+${totalDelta}` : totalDelta})
            </span>
            <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-xs font-mono ${
              isFlipped ? 'bg-brand-red text-white animate-pulse' : 'bg-[#E5E7EB] text-[#374151]'
            }`}>
              {simulatedRec}
            </span>
          </div>
        </div>
      </div>

      {/* Sliders */}
      <div className="space-y-3 pt-1">
        <div>
          <div className="flex items-center justify-between text-[11px] font-medium text-brand-black mb-1">
            <span>Additional Sub-Threshold Cash Deposits (₹9,500 ea)</span>
            <span className="font-mono font-bold text-brand-red">+{cashCount} deposits (+₹{(cashCount * cashAmount).toLocaleString()})</span>
          </div>
          <input 
            type="range" 
            min="0" 
            max="10" 
            value={cashCount}
            onChange={(e) => setCashCount(parseInt(e.target.value))}
            className="w-full h-1.5 bg-[#E5E7EB] rounded-lg appearance-none cursor-pointer accent-brand-red"
          />
        </div>

        <div>
          <div className="flex items-center justify-between text-[11px] font-medium text-brand-black mb-1">
            <span>Cross-Border Transfer Volume Shift</span>
            <span className="font-mono font-bold text-brand-red">{crossBorderChange >= 0 ? `+${crossBorderChange}%` : `${crossBorderChange}%`}</span>
          </div>
          <input 
            type="range" 
            min="-100" 
            max="200" 
            step="10"
            value={crossBorderChange}
            onChange={(e) => setCrossBorderChange(parseInt(e.target.value))}
            className="w-full h-1.5 bg-[#E5E7EB] rounded-lg appearance-none cursor-pointer accent-brand-red"
          />
        </div>
      </div>

      {/* ENTERPRISE RISK CONTRIBUTION BREAKDOWN CARD */}
      {totalDelta !== 0 && (
        <div className="bg-[#F9FAFB] border border-[#E4E7EC] p-3 rounded-sm space-y-2.5">
          <div className="text-[10px] font-bold text-brand-black uppercase tracking-wider flex items-center justify-between border-b border-[#E4E7EC] pb-2">
            <span className="flex items-center gap-1.5">
              <TrendingUp className="h-3.5 w-3.5 text-brand-red" /> Enterprise Risk Contribution Breakdown
            </span>
            <div className="flex items-center gap-1 font-mono text-[10px]">
              <span className="text-[#6B7280]">{initialScore} → {simulatedScore}</span>
              <span className="font-bold text-brand-red px-1.5 py-0.5 bg-[#FEF2F2] border border-[#FECACA] rounded-xs">
                TOTAL: {totalDelta >= 0 ? `+${totalDelta}` : totalDelta} PTS
              </span>
            </div>
          </div>

          <div className="space-y-2">
            {contributionItems.map((item) => {
              const isExpanded = expandedItemId === item.id;
              return (
                <div 
                  key={item.id}
                  className="bg-white border border-[#E4E7EC] rounded-sm p-2 transition-all hover:border-[#CBD5E1]"
                >
                  <div 
                    onClick={() => toggleExpand(item.id)}
                    className="flex items-center justify-between cursor-pointer select-none"
                  >
                    <div className="flex items-center gap-2">
                      <span className={`font-mono text-[11px] font-bold px-1.5 py-0.5 rounded-xs ${
                        item.points > 0 ? 'bg-[#FEF2F2] text-[#991B1B]' : 'bg-[#ECFDF5] text-[#065F46]'
                      }`}>
                        {item.points >= 0 ? `+${item.points}` : item.points} pts
                      </span>
                      <span className="text-[11px] font-semibold text-brand-black">{item.category}</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-[9px] font-mono text-[#6B7280] bg-[#F3F4F6] px-1.5 py-0.5 rounded-xs">
                        {item.subsystem} ({Math.round(item.confidence * 100)}%)
                      </span>
                      {isExpanded ? <ChevronUp className="h-3.5 w-3.5 text-[#6B7280]" /> : <ChevronDown className="h-3.5 w-3.5 text-[#6B7280]" />}
                    </div>
                  </div>

                  {/* Expandable Analyst-Friendly Explanation */}
                  {isExpanded && (
                    <div className="mt-2 pt-2 border-t border-[#F1F5F9] text-[10px] text-brand-gray space-y-1 bg-[#F8FAFC] p-2 rounded-xs">
                      <div className="font-semibold text-brand-black flex items-center gap-1">
                        <Info className="h-3 w-3 text-[#3B82F6]" /> Subsystem Deterministic Reason:
                      </div>
                      <div className="leading-relaxed text-[#334155]">
                        "{item.reason}"
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* FEATURE 2: MINIMUM CHANGE REQUIRED PANEL */}
      <div className="bg-[#EFF6FF] border border-[#BFDBFE] p-3 rounded-sm space-y-2">
        <div className="text-[10px] font-bold text-[#1E40AF] uppercase tracking-wider flex items-center gap-1.5">
          <Target className="h-3.5 w-3.5 text-[#2563EB]" /> Minimum Change Required to reach <span className="font-mono underline">{nextTarget}</span> (Score {targetScore})
        </div>

        <div className="space-y-1.5 text-[11px] text-[#1E3A8A]">
          {minimumChanges.length > 0 ? minimumChanges.map((change, idx) => (
            <React.Fragment key={idx}>
              {idx > 0 && <div className="text-[10px] font-bold text-[#3B82F6] uppercase tracking-widest pl-5">OR</div>}
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="h-3.5 w-3.5 text-[#2563EB] shrink-0" />
                <span>{change}</span>
              </div>
            </React.Fragment>
          )) : (
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-[#2563EB] shrink-0" />
              <span>Use the sliders to simulate thresholds.</span>
            </div>
          )}
        </div>
      </div>

      {/* Narrative Card */}
      <div className={`p-3 rounded-sm border text-[11px] leading-relaxed ${
        isFlipped ? 'bg-[#FEF2F2] border-[#FECACA] text-[#991B1B]' : 'bg-[#F0FDF4] border-[#86EFAC] text-[#166534]'
      }`}>
        <div className="font-bold flex items-center gap-1.5 mb-1 uppercase tracking-wider text-[10px]">
          <Zap className="h-3.5 w-3.5" />
          {isFlipped ? 'Decision Threshold Boundary Crossed' : 'Sensitivity Impact Narrative'}
        </div>
        <div>
          {simResult?.counterfactual_narrative || 'Adjust sliders above and click Run Simulation to see how future cash structuring or cross-border velocity shifts will impact risk score thresholds.'}
        </div>
      </div>
    </div>
  );
};
