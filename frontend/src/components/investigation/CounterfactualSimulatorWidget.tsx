import React, { useState } from 'react';
import { Sliders, Activity, TrendingUp, AlertTriangle, ArrowRight, RotateCcw, Zap, Target, Shield, CheckCircle2 } from 'lucide-react';

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
  const [cashAmount, setCashAmount] = useState(9500);
  const [crossBorderChange, setCrossBorderChange] = useState(0);

  // Deterministic mathematical formulas
  const cashImpact = Math.min(38, (cashCount * cashAmount / 4500) * 7.5 * (cashAmount >= 8000 && cashAmount <= 9999 ? 1.35 : 1.0));
  const crossBorderImpact = (crossBorderChange / 100) * 18.0;
  const totalDelta = Math.round(cashImpact + crossBorderImpact);

  const simulatedScore = Math.max(5, Math.min(98, Math.round(initialScore + totalDelta)));

  const getRec = (score: number) => {
    if (score >= 85) return 'FILE_SAR';
    if (score >= 65) return 'ESCALATE';
    if (score >= 35) return 'MANUAL_REVIEW';
    return 'CLEAR';
  };

  const simulatedRec = getRec(simulatedScore);
  const isFlipped = simulatedRec !== initialRecommendation;

  // Feature 1: Risk Contribution Breakdown
  const structuringContrib = Math.round(cashImpact * 0.48);
  const velocityContrib = Math.round(cashImpact * 0.22);
  const cbContrib = Math.round(crossBorderImpact);
  const mlContrib = Math.round(cashImpact * 0.30);

  // Feature 2: Minimum Change Required calculation to reach next threshold
  const getNextTarget = (score: number) => {
    if (score < 35) return { target: 'MANUAL_REVIEW', targetScore: 35 };
    if (score < 65) return { target: 'ESCALATE', targetScore: 65 };
    if (score < 85) return { target: 'FILE_SAR', targetScore: 85 };
    return { target: 'FILE_SAR', targetScore: 85 };
  };

  const { target: nextTarget, targetScore } = getNextTarget(initialScore);
  const neededPts = Math.max(0, targetScore - initialScore);
  const reqCashDeposits = Math.ceil(neededPts / 21.37);
  const reqCbPct = Math.ceil((neededPts / 18.0) * 100);

  const handleReset = () => {
    setCashCount(0);
    setCrossBorderChange(0);
  };

  return (
    <div className="bg-white border border-[#E4E7EC] rounded-sm p-4 shadow-sm space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="text-[11px] font-bold tracking-wider text-[#6B7280] uppercase flex items-center gap-1.5">
            <Sliders className="h-3.5 w-3.5 text-brand-red" />
            Counterfactual Risk Sensitivity Simulator
          </div>
          <div className="text-[12px] text-brand-gray mt-0.5">
            Simulate parameter shifts & decision threshold boundaries
          </div>
        </div>

        <button 
          onClick={handleReset}
          className="text-[10px] font-semibold text-[#6B7280] hover:text-brand-black flex items-center gap-1 uppercase tracking-wider bg-[#F3F4F6] px-2 py-1 rounded-sm transition-colors"
        >
          <RotateCcw className="h-3 w-3" /> Reset
        </button>
      </div>

      {/* FEATURE 3: DECISION THRESHOLD INDICATOR BAR */}
      <div className="space-y-1.5 bg-[#F9FAFB] border border-[#E4E7EC] p-3 rounded-sm">
        <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider text-[#6B7280]">
          <span>Compliance Thresholds</span>
          <span className="font-mono text-brand-black font-bold">Baseline: {initialScore} | Sim: {simulatedScore}</span>
        </div>

        {/* Horizontal Bar with Pin/Triangle Cursors */}
        <div className="relative w-full h-6 bg-[#E5E7EB] rounded-xs flex font-mono text-[9px] font-bold text-white text-center leading-6 cursor-pointer shadow-inner">
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
            <div className="absolute top-0 bottom-0 left-[5px] w-[1px] bg-black/50" />
            <div className="absolute -bottom-3.5 left-0 text-[12px] font-bold text-black select-none">▲</div>
          </div>

          {/* Simulated Risk Pointer Pin Cursor (Upper ▼ & Lower ▲) */}
          <div 
            className="absolute top-0 bottom-0 -ml-[6px] z-20 transition-all duration-500 ease-out pointer-events-none animate-pulse"
            style={{ left: `${Math.min(99, Math.max(0, simulatedScore))}%` }}
            title={`Simulated Risk: ${simulatedScore}`}
          >
            <div className="absolute -top-4 left-0 text-[14px] font-extrabold text-[#D97706] drop-shadow-sm select-none">▼</div>
            <div className="absolute top-0 bottom-0 left-[6px] w-[1.5px] bg-[#D97706]" />
            <div className="absolute -bottom-4 left-0 text-[14px] font-extrabold text-[#D97706] drop-shadow-sm select-none">▲</div>
          </div>

        </div>

        <div className="flex justify-between text-[9px] font-mono text-[#6B7280] pt-1">
          <span className="flex items-center gap-1 font-bold text-black">
            <span className="inline-block w-2 h-2 bg-black rounded-full" /> Baseline Pin ({initialScore})
          </span>
          <span className="flex items-center gap-1 font-bold text-brand-red">
            <span className="inline-block w-2 h-2 bg-[#FACC15] border border-brand-red rounded-full" /> Simulated Pin ({simulatedScore})
          </span>
        </div>
      </div>


      {/* Baseline vs Simulated Cards */}
      <div className="grid grid-cols-2 gap-3 p-3 bg-[#F9FAFB] border border-[#E4E7EC] rounded-sm">
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

      {/* FEATURE 1: RISK CONTRIBUTION BREAKDOWN CARD */}
      {totalDelta !== 0 && (
        <div className="bg-[#F9FAFB] border border-[#E4E7EC] p-3 rounded-sm space-y-2">
          <div className="text-[10px] font-bold text-brand-black uppercase tracking-wider flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <TrendingUp className="h-3.5 w-3.5 text-brand-red" /> Risk Contribution Breakdown
            </span>
            <span className="font-mono text-brand-red">Total: {totalDelta >= 0 ? `+${totalDelta}` : totalDelta} pts</span>
          </div>

          <div className="space-y-1 font-mono text-[11px]">
            {structuringContrib > 0 && (
              <div className="flex justify-between text-[#991B1B]">
                <span>+ {structuringContrib} pts</span>
                <span className="font-sans font-medium text-brand-black">Structuring Pattern</span>
              </div>
            )}
            {velocityContrib > 0 && (
              <div className="flex justify-between text-[#991B1B]">
                <span>+ {velocityContrib} pts</span>
                <span className="font-sans font-medium text-brand-black">Transaction Velocity</span>
              </div>
            )}
            {cbContrib !== 0 && (
              <div className={`flex justify-between ${cbContrib > 0 ? 'text-[#991B1B]' : 'text-[#065F46]'}`}>
                <span>{cbContrib >= 0 ? `+ ${cbContrib}` : `- ${Math.abs(cbContrib)}`} pts</span>
                <span className="font-sans font-medium text-brand-black">Cross-Border Exposure</span>
              </div>
            )}
            {mlContrib > 0 && (
              <div className="flex justify-between text-[#991B1B]">
                <span>+ {mlContrib} pts</span>
                <span className="font-sans font-medium text-brand-black">Isolation Forest Anomaly</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* FEATURE 2: MINIMUM CHANGE REQUIRED PANEL */}
      <div className="bg-[#EFF6FF] border border-[#BFDBFE] p-3 rounded-sm space-y-2">
        <div className="text-[10px] font-bold text-[#1E40AF] uppercase tracking-wider flex items-center gap-1.5">
          <Target className="h-3.5 w-3.5 text-[#2563EB]" /> Minimum Change Required to reach <span className="font-mono underline">{nextTarget}</span> (Score {targetScore})
        </div>

        <div className="space-y-1.5 text-[11px] text-[#1E3A8A]">
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="h-3.5 w-3.5 text-[#2563EB] shrink-0" />
            <span><strong>+{reqCashDeposits}</strong> additional cash deposits of ₹9,500</span>
          </div>
          <div className="text-[10px] font-bold text-[#3B82F6] uppercase tracking-widest pl-5">OR</div>
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="h-3.5 w-3.5 text-[#2563EB] shrink-0" />
            <span><strong>+{reqCbPct}%</strong> cross-border transfer volume</span>
          </div>
          <div className="text-[10px] font-bold text-[#3B82F6] uppercase tracking-widest pl-5">OR</div>
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="h-3.5 w-3.5 text-[#2563EB] shrink-0" />
            <span>One additional transfer from a <strong>High Risk Jurisdiction</strong></span>
          </div>
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
          {cashCount === 0 && crossBorderChange === 0 ? (
            'Adjust sliders above to simulate how future cash structuring or cross-border velocity shifts will impact risk score thresholds.'
          ) : (
            `If ${cashCount > 0 ? `${cashCount} additional ₹${cashAmount.toLocaleString()} cash deposit(s) occur` : ''} ${
              cashCount > 0 && crossBorderChange !== 0 ? 'and ' : ''
            }${crossBorderChange !== 0 ? `cross-border volume ${crossBorderChange > 0 ? 'increases' : 'decreases'} by ${Math.abs(crossBorderChange)}%` : ''}, overall risk score ${
              totalDelta >= 0 ? 'increases' : 'decreases'
            } by ${Math.abs(totalDelta)} points from ${initialScore} to ${simulatedScore}.${
              isFlipped ? ` This flips compliance recommendation from ${initialRecommendation} to ${simulatedRec}.` : ''
            }`
          )}
        </div>
      </div>
    </div>
  );
};
