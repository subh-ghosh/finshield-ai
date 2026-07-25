import { useState, useRef, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FileText, CheckCircle2, Activity, Send, ArrowLeft, Globe, Briefcase, Check } from 'lucide-react'
import { useCustomerDetails, useInvestigationData, usePlannerChat } from '../hooks'
import { StateView, EvidenceCard, ExecutionStepItem } from '../components/shared'

export default function InvestigationWorkspace() {
  const { id } = useParams()
  const [chatInput, setChatInput] = useState('')
  const chatEndRef = useRef<HTMLDivElement>(null)

  const { data: customer, isLoading: isCustLoading } = useCustomerDetails(id || '');
  const { data: investigation, isLoading: isInvLoading, isError, error } = useInvestigationData(id || '');
  const { is_running, events, current_step, final_answer, error: plannerError, sendMessage } = usePlannerChat();

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [events, current_step, final_answer, plannerError])

  const handleChat = async () => {
    if (!chatInput.trim() || is_running) return;
    const msg = chatInput;
    setChatInput('');
    await sendMessage(msg);
  }

  const isLoading = isCustLoading || isInvLoading;
  const evidences = investigation?.evidences || [];

  return (
    <div className="h-[calc(100vh-56px)] flex overflow-hidden">
      {/* Left Panel - Entity Context */}
      <div className="w-[480px] bg-white border-r border-[#E4E7EC] flex flex-col overflow-y-auto">
        {/* Navigation */}
        <div className="p-4 border-b border-[#E4E7EC]">
          <Link to="/queue" className="inline-flex items-center gap-1.5 text-[12px] font-semibold text-[#6B7280] hover:text-[#1E1E1E] transition-colors">
            <ArrowLeft className="h-3.5 w-3.5" /> BACK TO QUEUE
          </Link>
        </div>

        <StateView isLoading={isLoading} isError={isError} error={error}>
          {/* Entity Header */}
          <div className="p-6" style={{ borderTop: '3px solid #E1000F' }}>
            <div className="flex items-center justify-between mb-1">
              <span className="sg-section-label">Entity Profile</span>
              <span className="sg-badge sg-badge-critical">Case #{id}</span>
            </div>
            <h2 className="text-[18px] font-bold text-[#1E1E1E] mt-3">{customer?.name}</h2>
            <p className="text-[12px] text-[#9CA3AF] mt-1">ID: {customer?.id}</p>

            {/* Risk Score */}
            <div className="mt-5 p-4 bg-[#FEF2F2] border border-[#FECACA] flex items-center justify-between">
              <div>
                <div className="text-[10px] font-bold tracking-widest uppercase text-[#9CA3AF]">Composite Risk</div>
                <div className="text-[42px] font-bold text-[#E1000F] leading-none mt-1">{investigation?.risk_profile.composite_score || customer?.risk_score}</div>
              </div>
              <div className="text-right space-y-2">
                <div className="flex items-center gap-1.5 justify-end">
                  <Check className="h-3 w-3 text-[#10B981]" />
                  <span className="text-[11px] text-[#1E1E1E]">KYC: {customer?.kyc_status}</span>
                </div>
                <div className="flex items-center gap-1.5 justify-end">
                  <Globe className="h-3 w-3 text-[#9CA3AF]" />
                  <span className="text-[11px] text-[#1E1E1E]">{customer?.jurisdiction}</span>
                </div>
                <div className="flex items-center gap-1.5 justify-end">
                  <Briefcase className="h-3 w-3 text-[#9CA3AF]" />
                  <span className="text-[11px] text-[#1E1E1E]">{customer?.industry}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Evidence */}
          <div className="px-6 pb-6">
            <h3 className="sg-section-label mb-3 pb-2 border-b border-[#E4E7EC] flex items-center gap-2">
              <FileText className="h-3.5 w-3.5" /> Evidence Board
            </h3>
            <div className="space-y-2">
              {evidences.map((ev, i) => (
                <motion.div
                  key={ev.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.08 }}
                >
                  <EvidenceCard evidence={ev} />
                </motion.div>
              ))}
            </div>
          </div>

          {/* SAR Button */}
          <div className="px-6 pb-6 mt-auto">
            <button className="w-full bg-[#E1000F] hover:bg-[#c5000d] text-white font-bold py-3 text-[12px] tracking-wider transition-colors flex items-center justify-center gap-2 shadow-sm">
              <CheckCircle2 className="h-4 w-4" /> FINALIZE SAR RECOMMENDATION
            </button>
          </div>
        </StateView>
      </div>

      {/* Right Panel - AI Chat */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Chat Header */}
        <div className="h-11 bg-white border-b border-[#E4E7EC] flex items-center justify-between px-6 flex-shrink-0">
          <div className="flex items-center gap-2">
            <Activity className="h-3.5 w-3.5 text-[#E1000F]" />
            <span className="text-[12px] font-bold tracking-wider uppercase text-[#6B7280]">FinShield AI Planner</span>
          </div>
          <span className="inline-flex items-center gap-1.5 text-[11px] font-medium text-[#10B981]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse" /> LangGraph Active
          </span>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 sg-page-bg">
          {events.length === 0 && !current_step && !final_answer && (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <div className="w-14 h-14 rounded-full bg-white border border-[#E4E7EC] flex items-center justify-center mb-4 shadow-sm">
                <Activity className="h-6 w-6 text-[#9CA3AF]" />
              </div>
              <div className="text-[14px] font-semibold text-[#6B7280]">AI Planner Ready</div>
              <div className="text-[12px] text-[#9CA3AF] max-w-sm mt-1.5 leading-relaxed">
                Ask a question to trigger the LangGraph orchestration engine. The AI will autonomously select tools.
              </div>
              <div className="mt-5 flex gap-2">
                {['Summarize Risk', 'Check Structuring', 'Generate SAR Draft'].map(label => (
                  <button key={label} className="text-[11px] border border-[#E4E7EC] px-3 py-1.5 bg-white text-[#6B7280] hover:bg-[#F9FAFB] hover:border-[#D1D5DB] transition-all shadow-sm" onClick={() => setChatInput(label === 'Summarize Risk' ? "Summarize the risk profile for this customer." : label === 'Check Structuring' ? "Check for structuring patterns." : "Generate a draft SAR narrative.")}>
                    {label}
                  </button>
                ))}
              </div>
            </div>
          )}
          
          {events.map((evt, i) => {
            if (evt.type === 'tool_end' && evt.step) {
              return <ExecutionStepItem key={i} step={evt.step} index={i} />;
            }
            if (evt.type === 'thought') {
              return (
                <div key={i} className="text-[12px] text-[#6B7280] italic ml-2 border-l-2 border-[#E4E7EC] pl-3 py-1">
                  {evt.content}
                </div>
              )
            }
            return null;
          })}

          {current_step && current_step.status === 'running' && (
            <ExecutionStepItem step={current_step} index={events.length} />
          )}
          
          {final_answer && (
            <div className="flex flex-col items-start mt-4">
              <div className="max-w-[80%] p-4 text-[13px] leading-relaxed shadow-sm bg-white border border-[#E4E7EC] text-[#1E1E1E]">
                {final_answer}
              </div>
            </div>
          )}

          {plannerError && (
             <div className="flex flex-col items-center justify-center p-4">
               <div className="max-w-[80%] p-4 text-[13px] leading-relaxed shadow-sm bg-[#FEF2F2] border border-[#FECACA] text-[#E1000F]">
                 <strong>Error:</strong> {plannerError}
               </div>
             </div>
          )}

          {is_running && !current_step && (
            <div className="flex items-center gap-2 text-[12px] text-[#9CA3AF] bg-white border border-[#E4E7EC] p-3 w-fit shadow-sm">
              <Activity className="h-3.5 w-3.5 animate-spin text-[#E1000F]" /> LangGraph reasoning...
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 bg-white border-t border-[#E4E7EC] flex-shrink-0">
          <div className="relative flex items-center">
            <input type="text" value={chatInput} onChange={(e) => setChatInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleChat()} placeholder="Ask the AI Planner to analyze transactions, explain risk, or generate a SAR..." className="w-full bg-[#F9FAFB] border border-[#E4E7EC] pl-4 pr-12 py-3 text-[13px] focus:outline-none focus:border-[#E1000F]/40 focus:shadow-[0_0_0_3px_rgba(225,0,15,0.06)] placeholder:text-[#9CA3AF] transition-all" disabled={is_running} />
            <button className="absolute right-2 p-2 text-[#E1000F] hover:bg-[#FEF2F2] transition-colors disabled:opacity-30" onClick={handleChat} disabled={is_running || !chatInput.trim()}>
              <Send className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
