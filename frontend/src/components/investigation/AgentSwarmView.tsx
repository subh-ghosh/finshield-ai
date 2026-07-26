import React from 'react';
import { motion } from 'framer-motion';
import { Activity, CheckCircle2, User, FileText, Globe, Search, ArrowRight, GitMerge, Loader2, ShieldCheck, FileSearch } from 'lucide-react';

const AGENT_CONFIG: Record<string, { icon: React.ReactNode, color: string, bg: string }> = {
  'Supervisor Agent': { icon: <Search className="w-5 h-5" />, color: 'text-[#E1000F]', bg: 'bg-[#FEF2F2]' },
  'Customer Agent': { icon: <User className="w-5 h-5" />, color: 'text-[#3B82F6]', bg: 'bg-[#EFF6FF]' },
  'Transaction Agent': { icon: <Activity className="w-5 h-5" />, color: 'text-[#8B5CF6]', bg: 'bg-[#F5F3FF]' },
  'Network Agent': { icon: <Globe className="w-5 h-5" />, color: 'text-[#10B981]', bg: 'bg-[#ECFDF5]' },
  'Rule Intelligence Agent': { icon: <FileSearch className="w-5 h-5" />, color: 'text-[#F59E0B]', bg: 'bg-[#FFFBEB]' },
  'ML Intelligence Agent': { icon: <Activity className="w-5 h-5" />, color: 'text-[#EC4899]', bg: 'bg-[#FDF2F8]' },
  'Compliance Agent': { icon: <ShieldCheck className="w-5 h-5" />, color: 'text-[#0EA5E9]', bg: 'bg-[#F0F9FF]' },
  'Evidence Aggregator': { icon: <GitMerge className="w-5 h-5" />, color: 'text-[#6366F1]', bg: 'bg-[#EEF2FF]' },
  'Report Generator Agent': { icon: <CheckCircle2 className="w-5 h-5" />, color: 'text-[#14B8A6]', bg: 'bg-[#ECFDF5]' },
  'Audit Agent': { icon: <FileText className="w-5 h-5" />, color: 'text-[#64748B]', bg: 'bg-[#F8FAFC]' },
};

export function AgentSwarmView({ timeline = [], events = [], isRunning = false }: { timeline?: any[], events?: any[], isRunning?: boolean }) {
  // If we have V2 timeline objects
  let completedAgents = timeline
    .filter(e => e.status === 'COMPLETED' && e.tool)
    .map(e => ({ name: e.tool, output: e.result, duration: e.duration, status: 'completed' }));
    
  // Fallback to legacy events if timeline is empty
  if (completedAgents.length === 0 && events.length > 0) {
    completedAgents = events
      .filter(e => e.type === 'tool_end' && e.step?.tool_name)
      .map(e => ({ name: e.step.tool_name, output: e.step.output, status: 'completed' }));
  }

  let activeAgent = null;
  if (isRunning) {
    const runningStep = timeline.find(e => e.status === 'RUNNING' || e.status === 'WAITING');
    if (runningStep) {
      activeAgent = runningStep.tool;
    } else {
      const runningEvent = events.find(e => e.type === 'tool_start' && e.step?.status === 'running');
      if (runningEvent) activeAgent = runningEvent.step.tool_name;
      else if (completedAgents.length === 0) activeAgent = 'Supervisor Agent';
      else activeAgent = 'Report Generator Agent';
    }
  }

  const agentsList = Object.keys(AGENT_CONFIG);

  return (
    <div className="w-full h-full flex flex-col p-6 space-y-6 bg-[#F9FAFB] overflow-y-auto">
      <div className="flex flex-col text-center items-center justify-center mb-4">
        <h2 className="text-[18px] font-bold text-brand-black">Agent Swarm Execution</h2>
        <p className="text-[12px] text-brand-gray mt-1">Multi-agent LangGraph orchestrating specialized analysts.</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {agentsList.map((agentName, idx) => {
          const config = AGENT_CONFIG[agentName];
          const completedInfo = completedAgents.find(a => a.name === agentName);
          const isCompleted = !!completedInfo;
          const isActive = isRunning && activeAgent && (activeAgent === agentName);
          
          return (
            <motion.div 
              key={agentName}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className={`p-4 border ${isActive ? 'border-[#E1000F] shadow-sm' : isCompleted ? 'border-[#E4E7EC] opacity-80' : 'border-[#F0F1F3] opacity-40'} bg-white flex flex-col relative overflow-hidden`}
            >
              {isActive && <div className="absolute top-0 left-0 w-full h-1 bg-[#E1000F] animate-pulse" />}
              
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 flex items-center justify-center rounded-full ${config.bg} ${config.color}`}>
                    {config.icon}
                  </div>
                  <div>
                    <h3 className="text-[13px] font-bold text-brand-black">{agentName}</h3>
                    <div className="text-[11px] text-brand-gray flex items-center gap-1 mt-0.5">
                      {isActive && <><Loader2 className="w-3 h-3 animate-spin text-brand-red" /> Executing...</>}
                      {isCompleted && <><CheckCircle2 className="w-3 h-3 text-[#10B981]" /> Completed {completedInfo.duration ? `(${completedInfo.duration}s)` : ''}</>}
                      {!isActive && !isCompleted && 'Waiting for dispatch...'}
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Show truncated output if completed */}
              {isCompleted && (
                <div className="mt-3 p-2 bg-[#F9FAFB] border border-[#E4E7EC] text-[10px] text-[#6B7280] font-mono truncate" title={completedInfo.output}>
                  {completedInfo.output || 'Output registered.'}
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
      
      {/* Visual flow arrows */}
      <div className="flex items-center justify-center py-4">
        <div className="w-full max-w-md bg-white border border-[#E4E7EC] p-4 text-center text-[11px] font-bold tracking-wider uppercase text-brand-black shadow-sm">
          {isRunning ? (
            <span className="flex items-center justify-center gap-2 text-brand-red"><Loader2 className="w-4 h-4 animate-spin" /> Investigation in Progress</span>
          ) : completedAgents.length > 0 ? (
            <span className="text-[#10B981]">Investigation Concluded</span>
          ) : (
            'Standby'
          )}
        </div>
      </div>
    </div>
  );
}
