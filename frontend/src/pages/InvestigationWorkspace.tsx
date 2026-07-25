import { useState, useRef, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Send, ShieldAlert, Activity, FileText, CheckCircle2, Check, AlertTriangle, Globe, Briefcase } from 'lucide-react'
import { motion } from 'framer-motion'

export default function InvestigationWorkspace() {
  const { id } = useParams()
  const [chatInput, setChatInput] = useState('')
  const [messages, setMessages] = useState<any[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const chatEndRef = useRef<HTMLDivElement>(null)

  const { data: customer } = useQuery({
    queryKey: ['customer', id],
    queryFn: async () => {
      try {
        const res = await api.get(`/investigations/${id}`)
        return res.data
      } catch {
        return {
          id, name: "Acme Corp Ltd", kyc_status: "Verified", risk_score: 92,
          onboarding_date: "2023-01-15", industry: "Import/Export", jurisdiction: "Cayman Islands",
          connected_customers: [{ id: "CUST-1042", name: "Global Traders Inc", relation: "Shared Director" }]
        }
      }
    }
  })

  const evidences = [
    { id: 1, title: 'Velocity Score', desc: '145 transactions in 7 days, 400% above baseline.', severity: 'critical' },
    { id: 2, title: 'Structuring Pattern', desc: 'Multiple $9.9k transfers avoiding $10k reporting limit.', severity: 'critical' },
    { id: 3, title: 'High Risk Jurisdiction', desc: 'Funds flowing to/from Cayman Islands.', severity: 'high' },
    { id: 4, title: 'ML Anomaly Score', desc: 'Isolation Forest score: 0.89 (Top 1%).', severity: 'critical' }
  ]

  const handleChat = async () => {
    if (!chatInput.trim()) return
    const userMsg = chatInput
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setChatInput('')
    setIsTyping(true)
    try {
      const res = await api.post('/planner/chat', { message: userMsg, customer_id: id })
      const { response, intermediate_steps } = res.data
      setMessages(prev => [...prev, { role: 'assistant', content: response, steps: intermediate_steps }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: "Unable to connect to the LangGraph AI Planner. Operating in offline demonstration mode." }])
    } finally { setIsTyping(false) }
  }

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, isTyping])

  return (
    <div className="flex h-[calc(100vh-55px)]">
      {/* Left Panel */}
      <div className="w-[360px] border-r border-[#E4E7EC] bg-white overflow-y-auto flex-shrink-0">
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
              <div className="text-[42px] font-bold text-[#E1000F] leading-none mt-1">{customer?.risk_score}</div>
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
                className="flex gap-3 p-3 bg-[#FAFBFC] border border-[#F0F1F3] hover:border-[#E4E7EC] hover:shadow-sm transition-all cursor-default"
              >
                <div className="mt-0.5 flex-shrink-0">
                  {ev.severity === 'critical' 
                    ? <AlertTriangle className="h-3.5 w-3.5 text-[#E1000F]" /> 
                    : <ShieldAlert className="h-3.5 w-3.5 text-[#F59E0B]" />
                  }
                </div>
                <div>
                  <div className="text-[12px] font-semibold text-[#1E1E1E]">{ev.title}</div>
                  <div className="text-[11px] text-[#9CA3AF] mt-0.5 leading-relaxed">{ev.desc}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* SAR Button */}
        <div className="px-6 pb-6">
          <button className="w-full bg-[#E1000F] hover:bg-[#c5000d] text-white font-bold py-3 text-[12px] tracking-wider transition-colors flex items-center justify-center gap-2 shadow-sm">
            <CheckCircle2 className="h-4 w-4" /> FINALIZE SAR RECOMMENDATION
          </button>
        </div>
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
          {messages.length === 0 && (
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
          
          {messages.map((msg, i) => (
            <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div className={`max-w-[80%] p-4 text-[13px] leading-relaxed shadow-sm ${
                msg.role === 'user' ? 'bg-[#161A22] text-white' : 'bg-white border border-[#E4E7EC] text-[#1E1E1E]'
              }`}>
                {msg.content}
              </div>
              {msg.steps && msg.steps.length > 0 && (
                <div className="mt-2 space-y-1 border-l-2 border-[#E1000F] pl-3 max-w-[80%]">
                  <div className="text-[10px] font-bold text-[#9CA3AF] uppercase tracking-widest">Execution Trace</div>
                  {msg.steps.map((step: any, idx: number) => (
                    <div key={idx} className="text-[11px] bg-white border border-[#F0F1F3] p-2 font-mono shadow-sm">
                      <span className="text-[#E1000F] font-bold">[{idx + 1}]</span> {step.tool ? `${step.tool}` : step.result}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
          
          {isTyping && (
            <div className="flex items-center gap-2 text-[12px] text-[#9CA3AF] bg-white border border-[#E4E7EC] p-3 w-fit shadow-sm">
              <Activity className="h-3.5 w-3.5 animate-spin text-[#E1000F]" /> LangGraph reasoning...
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 bg-white border-t border-[#E4E7EC] flex-shrink-0">
          <div className="relative flex items-center">
            <input type="text" value={chatInput} onChange={(e) => setChatInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleChat()} placeholder="Ask the AI Planner to analyze transactions, explain risk, or generate a SAR..." className="w-full bg-[#F9FAFB] border border-[#E4E7EC] pl-4 pr-12 py-3 text-[13px] focus:outline-none focus:border-[#E1000F]/40 focus:shadow-[0_0_0_3px_rgba(225,0,15,0.06)] placeholder:text-[#9CA3AF] transition-all" disabled={isTyping} />
            <button className="absolute right-2 p-2 text-[#E1000F] hover:bg-[#FEF2F2] transition-colors disabled:opacity-30" onClick={handleChat} disabled={isTyping || !chatInput.trim()}>
              <Send className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
