import React, { useState } from 'react';
import { Sliders, Activity, TrendingUp, AlertTriangle, ArrowRight, RotateCcw, Zap } from 'lucide-react';
import type { CounterfactualSimulationResult } from '../../domain/entities/Counterfactual';

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
  const [isSimulating, setIsSimulating] = useState(false);

  // Compute live deterministic simulation
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
          className="text-[10px] font-semibold text-[#6B7280] hover:text-brand-black flex items-center gap-1 uppercase tracking-wider bg-[#F3F4F6] px-2 py-1 rounded-sm"
        >
          <RotateCcw className="h-3 w-3" /> Reset
        </button>
      </div>

      {/* Decision Boundary Comparison Banner */}
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

      {/* Interactive Risk Sliders */}
      <div className="space-y-3 pt-2">
        {/* Slider 1: Additional Cash Structuring Deposits */}
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

        {/* Slider 2: Cross-Border Transfer Volume Shift */}
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

      {/* Simulation Narrative Card */}
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
