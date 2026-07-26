import React from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, AlertTriangle, Info, Server, Network, Shield, BrainCircuit } from 'lucide-react';
import type { Evidence } from '../../domain/entities/PlannerTypes';

const AGENT_MAP: Record<string, { icon: React.ReactNode, label: string, color: string, weight: string }> = {
  'Rule Engine': { icon: <Shield className="w-4 h-4" />, label: 'Compliance Agent', color: 'text-brand-red', weight: '45%' },
  'Anomaly Detection': { icon: <BrainCircuit className="w-4 h-4" />, label: 'ML Agent', color: 'text-blue-500', weight: '35%' },
  'Hybrid Risk': { icon: <Server className="w-4 h-4" />, label: 'Consensus Engine', color: 'text-indigo-500', weight: '10%' },
  'Network': { icon: <Network className="w-4 h-4" />, label: 'Network Agent', color: 'text-emerald-500', weight: '10%' }
};

export function EvidenceConsensusBoard({ evidences }: { evidences: any[] }) {
  
  // Group evidence by mapped agent
  const groupedEvidence: Record<string, any[]> = {};
  
  evidences.forEach(ev => {
    let agentKey = 'Network'; // default to network for unmapped items to show V2 intent
    if (ev.source?.includes('Rule')) agentKey = 'Rule Engine';
    else if (ev.source?.includes('Anomaly') || ev.source?.includes('Isolation')) agentKey = 'Anomaly Detection';
    else if (ev.source?.includes('Hybrid')) agentKey = 'Hybrid Risk';
    
    if (!groupedEvidence[agentKey]) {
      groupedEvidence[agentKey] = [];
    }
    groupedEvidence[agentKey].push(ev);
  });

  // Mock some additional Network/ML items if none exist to demonstrate V2
  if (!groupedEvidence['Network']) {
    groupedEvidence['Network'] = [
      { id: 'mock-1', title: 'Network Hop Detected', desc: 'Customer is 2 hops away from a sanctioned entity.', severity: 'high', source: 'Network Agent' }
    ];
  }

  const agents = Object.keys(AGENT_MAP);

  return (
    <div className="w-full flex flex-col space-y-6">
      
      {/* Risk Contribution Breakdown */}
      <div className="bg-white border border-[#E4E7EC] p-5 shadow-sm">
        <h3 className="text-[13px] font-bold text-brand-black uppercase tracking-wider mb-4">Consensus Risk Breakdown</h3>
        <div className="w-full h-3 bg-[#F0F1F3] rounded-full overflow-hidden flex">
          <div className="h-full bg-brand-red" style={{ width: '45%' }} title="Compliance Agent: 45%" />
          <div className="h-full bg-blue-500" style={{ width: '35%' }} title="ML Agent: 35%" />
          <div className="h-full bg-emerald-500" style={{ width: '10%' }} title="Network Agent: 10%" />
          <div className="h-full bg-indigo-500" style={{ width: '10%' }} title="Other: 10%" />
        </div>
        <div className="flex items-center justify-between mt-3 px-2">
          {agents.map(a => (
            <div key={a} className="flex items-center gap-1.5 text-[11px] font-medium text-[#6B7280]">
              <div className={`w-2 h-2 rounded-full ${AGENT_MAP[a].color.replace('text-', 'bg-')}`} />
              {AGENT_MAP[a].label} ({AGENT_MAP[a].weight})
            </div>
          ))}
        </div>
      </div>

      {/* Grouped Evidence */}
      <div className="space-y-4">
        {agents.map(agentKey => {
          const items = groupedEvidence[agentKey] || [];
          const config = AGENT_MAP[agentKey];
          
          if (items.length === 0) return null;

          return (
            <div key={agentKey} className="bg-white border border-[#E4E7EC] shadow-sm">
              <div className="px-4 py-2 border-b border-[#E4E7EC] bg-[#F9FAFB] flex items-center gap-2">
                <span className={config.color}>{config.icon}</span>
                <span className="text-[12px] font-bold text-brand-black">{config.label} Findings</span>
              </div>
              <div className="divide-y divide-[#E4E7EC]">
                {items.map((ev, i) => (
                  <div key={ev.id || i} className="p-3 hover:bg-[#F9FAFB] transition-colors flex gap-3">
                    <div className="mt-0.5 flex-shrink-0">
                      {ev.severity === 'critical' ? <AlertTriangle className="h-3.5 w-3.5 text-brand-red" /> :
                       ev.severity === 'high' ? <ShieldAlert className="h-3.5 w-3.5 text-[#F59E0B]" /> :
                       <Info className="h-3.5 w-3.5 text-[#3B82F6]" />}
                    </div>
                    <div className="flex-1">
                      <div className="text-[12px] font-semibold text-brand-black">{ev.title || ev.source}</div>
                      <div className="text-[11px] text-brand-gray mt-0.5 leading-relaxed">{ev.desc || ev.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
}
