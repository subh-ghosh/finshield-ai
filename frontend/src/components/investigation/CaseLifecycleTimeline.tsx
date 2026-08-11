import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FolderOpen, Eye, RefreshCw, AlertTriangle, XCircle, ChevronRight, Loader2, CheckCircle2
} from 'lucide-react';

// ── Types ───────────────────────────────────────────────────────────────────
export type CaseStatus = 'OPEN' | 'MONITORING' | 'UPDATE' | 'ESCALATED' | 'CLOSED';

interface LifecycleState {
  status: CaseStatus;
  label: string;
  icon: React.ReactNode;
  color: string;       // Tailwind text colour
  bg: string;          // Tailwind bg colour
  border: string;      // Tailwind border colour
  description: string;
}

interface TransitionRecord {
  from: CaseStatus;
  to: CaseStatus;
  timestamp: string;
  analyst: string;
  note: string;
}

// ── Config ──────────────────────────────────────────────────────────────────
const LIFECYCLE_STATES: LifecycleState[] = [
  {
    status: 'OPEN',
    label: 'Open',
    icon: <FolderOpen className="w-4 h-4" />,
    color: 'text-[#10B981]',
    bg: 'bg-[#ECFDF5]',
    border: 'border-[#10B981]',
    description: 'Case created and under initial review.',
  },
  {
    status: 'MONITORING',
    label: 'Monitoring',
    icon: <Eye className="w-4 h-4" />,
    color: 'text-[#3B82F6]',
    bg: 'bg-[#EFF6FF]',
    border: 'border-[#3B82F6]',
    description: 'No immediate action — continuous watch active.',
  },
  {
    status: 'UPDATE',
    label: 'Update',
    icon: <RefreshCw className="w-4 h-4" />,
    color: 'text-[#F59E0B]',
    bg: 'bg-[#FFFBEB]',
    border: 'border-[#F59E0B]',
    description: 'New evidence received. Case re-evaluated.',
  },
  {
    status: 'ESCALATED',
    label: 'Escalated',
    icon: <AlertTriangle className="w-4 h-4" />,
    color: 'text-[#E1000F]',
    bg: 'bg-[#FEF2F2]',
    border: 'border-[#E1000F]',
    description: 'Risk threshold breached. L2 review or SAR required.',
  },
  {
    status: 'CLOSED',
    label: 'Closed',
    icon: <XCircle className="w-4 h-4" />,
    color: 'text-[#6B7280]',
    bg: 'bg-[#F9FAFB]',
    border: 'border-[#9CA3AF]',
    description: 'Investigation concluded. Case archived.',
  },
];

// Allowed manual transitions per current state
const ALLOWED_TRANSITIONS: Record<CaseStatus, CaseStatus[]> = {
  OPEN: ['MONITORING', 'ESCALATED'],
  MONITORING: ['UPDATE', 'ESCALATED', 'CLOSED'],
  UPDATE: ['MONITORING', 'ESCALATED'],
  ESCALATED: ['CLOSED'],
  CLOSED: ['OPEN'], // Reopen
};

// ── Props ────────────────────────────────────────────────────────────────────
interface Props {
  customerId: string;
  sarConfirmed?: boolean;
  /** Called when the analyst transitions the case state */
  onStatusChange?: (newStatus: CaseStatus) => void;
}

// ── Component ────────────────────────────────────────────────────────────────
export function CaseLifecycleTimeline({ customerId, sarConfirmed = false, onStatusChange }: Props) {
  const [currentStatus, setCurrentStatus] = useState<CaseStatus>('OPEN');
  const [transitions, setTransitions] = useState<TransitionRecord[]>([]);
  const [noteInput, setNoteInput] = useState('');
  const [pendingTransition, setPendingTransition] = useState<CaseStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Auto-escalate if SAR is confirmed from parent
  useEffect(() => {
    if (sarConfirmed && currentStatus !== 'ESCALATED' && currentStatus !== 'CLOSED') {
      handleTransition('ESCALATED', 'Auto-escalated: SAR recommendation finalised by analyst.');
    }
  }, [sarConfirmed]);

  // Load from monitoring watchlist endpoint on mount
  useEffect(() => {
    const baseUrl = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? 'https://finshield-backend-131d.onrender.com/api' : 'http://localhost:8000/api');
    fetch(`${baseUrl}/v1/monitoring/watchlist`)
      .then(r => r.ok ? r.json() : null)
      .then((data: any[] | null) => {
        if (!data) return;
        const record = data.find(d => d.customer_id === customerId);
        if (record?.status) {
          const mapped: Record<string, CaseStatus> = {
            MONITORING: 'MONITORING',
            ESCALATED: 'ESCALATED',
          };
          if (mapped[record.status]) setCurrentStatus(mapped[record.status]);
        }
      })
      .catch(() => {}); // API may not be running locally — silent fail
  }, [customerId]);

  async function handleTransition(to: CaseStatus, autoNote?: string) {
    const note = autoNote || noteInput.trim() || `Analyst moved case to ${to}.`;
    setIsLoading(true);

    const record: TransitionRecord = {
      from: currentStatus,
      to,
      timestamp: new Date().toISOString(),
      analyst: 'Analyst (You)',
      note,
    };

    // Optimistic update
    setTransitions(prev => [record, ...prev]);
    setCurrentStatus(to);
    setNoteInput('');
    setPendingTransition(null);
    onStatusChange?.(to);

    // Call monitoring API in background
    const baseUrl = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? 'https://finshield-backend-131d.onrender.com/api' : 'http://localhost:8000/api');
    try {
      await fetch(`${baseUrl}/v1/monitoring/check/${customerId}?current_risk=${to === 'ESCALATED' ? 90 : 30}`, {
        method: 'POST',
      });
    } catch {
      // Silent — local-dev API may not be running
    } finally {
      setIsLoading(false);
    }
  }

  const currentStateConfig = LIFECYCLE_STATES.find(s => s.status === currentStatus)!;
  const allowedNext = ALLOWED_TRANSITIONS[currentStatus];

  return (
    <div className="bg-white border border-[#E4E7EC] shadow-sm">
      {/* Header */}
      <div className="px-5 py-3 border-b border-[#E4E7EC] bg-[#F9FAFB] flex items-center justify-between">
        <div>
          <span className="text-[11px] font-bold tracking-widest uppercase text-[#6B7280]">Case Lifecycle</span>
          <p className="text-[11px] text-[#9CA3AF] mt-0.5">Manual state transitions with audit log.</p>
        </div>
        {isLoading && <Loader2 className="w-4 h-4 animate-spin text-[#E1000F]" />}
      </div>

      {/* Horizontal timeline track */}
      <div className="px-5 pt-5 pb-3">
        <div className="flex items-center gap-0 w-full">
          {LIFECYCLE_STATES.map((state, idx) => {
            const isActive = state.status === currentStatus;
            const isPast = LIFECYCLE_STATES.findIndex(s => s.status === currentStatus) > idx;
            const isLast = idx === LIFECYCLE_STATES.length - 1;

            return (
              <React.Fragment key={state.status}>
                <div className="flex flex-col items-center flex-shrink-0">
                  <motion.div
                    animate={{
                      scale: isActive ? 1.15 : 1,
                      boxShadow: isActive ? '0 0 0 3px rgba(225,0,15,0.15)' : 'none',
                    }}
                    transition={{ duration: 0.3 }}
                    className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors
                      ${isActive ? `${state.bg} ${state.border} ${state.color}` :
                        isPast ? 'bg-[#F0FDF4] border-[#10B981] text-[#10B981]' :
                        'bg-[#F3F4F6] border-[#D1D5DB] text-[#9CA3AF]'}`}
                  >
                    {isPast ? <CheckCircle2 className="w-4 h-4" /> : state.icon}
                  </motion.div>
                  <span className={`text-[10px] font-bold mt-1.5 tracking-wide uppercase
                    ${isActive ? state.color : isPast ? 'text-[#10B981]' : 'text-[#9CA3AF]'}`}>
                    {state.label}
                  </span>
                </div>
                {!isLast && (
                  <div className={`flex-1 h-0.5 mx-1 mb-5 transition-colors
                    ${isPast || isActive ? 'bg-[#10B981]' : 'bg-[#E4E7EC]'}`} />
                )}
              </React.Fragment>
            );
          })}
        </div>

        {/* Current state description */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStatus}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            className={`mt-3 p-3 border ${currentStateConfig.border} ${currentStateConfig.bg} text-[11px] ${currentStateConfig.color} font-medium`}
          >
            <span className="font-bold">{currentStateConfig.label}:</span> {currentStateConfig.description}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Manual transition controls */}
      {allowedNext.length > 0 && (
        <div className="px-5 pb-4">
          <p className="text-[10px] font-bold tracking-widest uppercase text-[#6B7280] mb-2">Transition To</p>
          <div className="flex flex-wrap gap-2 mb-3">
            {allowedNext.map(nextStatus => {
              const cfg = LIFECYCLE_STATES.find(s => s.status === nextStatus)!;
              return (
                <button
                  key={nextStatus}
                  onClick={() => setPendingTransition(nextStatus)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 border text-[11px] font-bold transition-all
                    ${pendingTransition === nextStatus
                      ? `${cfg.bg} ${cfg.border} ${cfg.color} shadow-sm`
                      : 'border-[#E4E7EC] text-[#6B7280] hover:border-[#D1D5DB] hover:bg-[#F9FAFB]'}`}
                >
                  {cfg.icon} {cfg.label}
                </button>
              );
            })}
          </div>

          <AnimatePresence>
            {pendingTransition && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <textarea
                  value={noteInput}
                  onChange={e => setNoteInput(e.target.value)}
                  placeholder={`Note for transition to ${pendingTransition} (optional)...`}
                  rows={2}
                  className="w-full bg-[#F9FAFB] border border-[#E4E7EC] px-3 py-2 text-[12px] text-brand-black placeholder:text-[#9CA3AF] focus:outline-none focus:border-[#E1000F]/50 resize-none mb-2"
                />
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleTransition(pendingTransition!)}
                    disabled={isLoading}
                    className="flex items-center gap-1.5 px-4 py-2 bg-[#E1000F] hover:bg-[#c5000d] text-white text-[11px] font-bold tracking-wider uppercase transition-colors disabled:opacity-50"
                  >
                    <ChevronRight className="w-3.5 h-3.5" />
                    Confirm Transition
                  </button>
                  <button
                    onClick={() => { setPendingTransition(null); setNoteInput(''); }}
                    className="px-4 py-2 border border-[#E4E7EC] text-[11px] font-bold text-[#6B7280] hover:bg-[#F9FAFB] transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {/* Audit log */}
      {transitions.length > 0 && (
        <div className="border-t border-[#E4E7EC]">
          <div className="px-5 py-2 bg-[#F9FAFB]">
            <span className="text-[10px] font-bold tracking-widest uppercase text-[#6B7280]">
              Audit Log ({transitions.length})
            </span>
          </div>
          <div className="divide-y divide-[#F3F4F6] max-h-40 overflow-y-auto">
            {transitions.map((t, i) => (
              <div key={i} className="px-5 py-2 flex items-start gap-3">
                <span className={`mt-0.5 text-[10px] font-mono font-bold px-1.5 py-0.5
                  ${LIFECYCLE_STATES.find(s => s.status === t.to)?.color}
                  ${LIFECYCLE_STATES.find(s => s.status === t.to)?.bg}`}>
                  {t.from} → {t.to}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-[11px] text-brand-black truncate">{t.note}</p>
                  <p className="text-[10px] text-[#9CA3AF] mt-0.5">
                    {t.analyst} · {new Date(t.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
