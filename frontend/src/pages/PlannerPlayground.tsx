import { useState, useRef, useEffect } from 'react'
import { Activity, Send, Terminal, Database, Code2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function PlannerPlayground() {
  const [input, setInput] = useState('')
  const [history, setHistory] = useState<any[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)

  const handleSend = async () => {
    if (!input.trim()) return
    const userMsg = input
    setHistory(prev => [...prev, { type: 'user', content: userMsg }])
    setInput('')
    setIsProcessing(true)
    setHistory(prev => [...prev, { type: 'agent', content: '', steps: [] }])

    try {
      const response = await fetch('http://localhost:8000/api/v1/planner/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, customer_id: 'PLAYGROUND', thread_id: 'thread_1' })
      })
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let done = false
      while (reader && !done) {
        const { value, done: doneReading } = await reader.read()
        done = doneReading
        if (value) {
          const chunk = decoder.decode(value, { stream: true })
          const lines = chunk.split('\n')
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.slice(6)
              if (dataStr === '[DONE]') break
              try {
                const data = JSON.parse(dataStr)
                if (data.type === 'status') {
                  setHistory(prev => { const n = [...prev]; const l = n[n.length-1]; if (l.type === 'agent') l.steps = [...(l.steps||[]), {tool: data.content, result: 'Running...'}]; return n })
                } else if (data.type === 'final') {
                  setHistory(prev => { const n = [...prev]; const l = n[n.length-1]; if (l.type === 'agent') { l.content = data.response; l.steps = data.intermediate_steps; } return n })
                } else if (data.type === 'error') {
                  setHistory(prev => { const n = [...prev]; n[n.length-1].content = data.content; return n })
                }
              } catch {}
            }
          }
        }
      }
    } catch {
      setHistory(prev => { const n = [...prev]; n[n.length-1].content = "Error connecting to AI backend."; return n })
    } finally { setIsProcessing(false) }
  }

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [history, isProcessing])

  return (
    <div className="flex flex-col h-[calc(100vh-55px)]">
      {/* Toolbar */}
      <div className="h-11 bg-white border-b border-[#E4E7EC] flex items-center justify-between px-6 flex-shrink-0">
        <div className="flex items-center gap-2">
          <Terminal className="h-3.5 w-3.5 text-[#E1000F]" />
          <span className="text-[12px] font-bold tracking-wider uppercase text-[#6B7280]">Execution Console</span>
        </div>
        <div className="flex gap-2">
          <button className="text-[11px] border border-[#E4E7EC] px-3 py-1 bg-white text-[#6B7280] hover:bg-[#F9FAFB] flex items-center gap-1.5 transition-colors shadow-sm">
            <Database className="h-3 w-3" /> Tool Registry
          </button>
          <button className="text-[11px] border border-[#E4E7EC] px-3 py-1 bg-white text-[#6B7280] hover:bg-[#F9FAFB] flex items-center gap-1.5 transition-colors shadow-sm">
            <Code2 className="h-3 w-3" /> View State
          </button>
        </div>
      </div>

      {/* Console */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 sg-page-bg font-mono text-[13px]">
        {history.length === 0 && (
          <div className="text-center mt-16">
            <div className="w-14 h-14 rounded-full bg-white border border-[#E4E7EC] flex items-center justify-center mx-auto mb-4 shadow-sm">
              <Terminal className="h-6 w-6 text-[#9CA3AF]" />
            </div>
            <div className="text-[13px] font-semibold text-[#6B7280] font-sans">System Ready</div>
            <div className="text-[12px] text-[#9CA3AF] font-sans mt-1">Waiting for input query...</div>
          </div>
        )}

        {history.map((msg, i) => (
          <div key={i} className={`flex flex-col ${msg.type === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`max-w-[85%] p-3 shadow-sm ${
              msg.type === 'user' ? 'bg-[#161A22] text-[#22C55E]' : 'bg-white border border-[#E4E7EC] text-[#1E1E1E]'
            }`}>
              {msg.type === 'user' ? (
                <div><span className="text-[#E1000F] font-bold">&gt;</span> {msg.content}</div>
              ) : (
                <div className="space-y-3">
                  {msg.steps && msg.steps.length > 0 && (
                    <div className="space-y-1.5 border-l-2 border-[#E1000F] pl-3 py-1 bg-[#FAFBFC]">
                      <div className="text-[10px] font-bold text-[#E1000F] uppercase tracking-[0.15em]">++ Execution Trace ++</div>
                      {msg.steps.map((step: any, idx: number) => (
                        <div key={idx} className="text-[11px] text-[#6B7280]">
                          <span className="text-[#9CA3AF]">[{idx + 1}]</span>{' '}
                          {step.tool ? (<span>Tool: <span className="text-[#E1000F] font-bold">{step.tool}</span></span>) : (<span>Result: <span className="text-[#10B981] font-bold">"{step.result}"</span></span>)}
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="text-[#1E1E1E] whitespace-pre-wrap font-sans text-[13px]">{msg.content}</div>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isProcessing && (
          <div className="flex items-center gap-2 text-[12px] text-[#9CA3AF] bg-white border border-[#E4E7EC] p-3 w-fit font-sans shadow-sm">
            <Activity className="h-3.5 w-3.5 animate-spin text-[#E1000F]" /> Agent reasoning in progress...
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="p-4 bg-white border-t border-[#E4E7EC] flex-shrink-0">
        <div className="relative flex items-center max-w-4xl mx-auto">
          <span className="absolute left-4 font-mono text-[#E1000F] font-bold text-[14px]">&gt;</span>
          <input type="text" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleSend()} placeholder="e.g. Run a full investigation on CUST-8392" className="w-full bg-[#F9FAFB] border border-[#E4E7EC] pl-10 pr-24 py-3 text-[13px] font-mono focus:outline-none focus:border-[#E1000F]/40 focus:shadow-[0_0_0_3px_rgba(225,0,15,0.06)] placeholder:text-[#9CA3AF] transition-all" disabled={isProcessing} />
          <button className="absolute right-2 bg-[#E1000F] hover:bg-[#c5000d] text-white text-[11px] font-bold px-4 py-1.5 tracking-wider transition-colors disabled:opacity-30 shadow-sm" onClick={handleSend} disabled={isProcessing || !input.trim()}>
            EXEC <Send className="inline h-3 w-3 ml-1" />
          </button>
        </div>
      </div>
    </div>
  )
}
