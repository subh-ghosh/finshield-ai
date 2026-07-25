import { useState, useRef, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
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

    // Add a temporary agent message for streaming
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
                  setHistory(prev => {
                    const newHist = [...prev]
                    const lastMsg = newHist[newHist.length - 1]
                    if (lastMsg.type === 'agent') {
                      lastMsg.steps = [...(lastMsg.steps || []), { tool: data.content, result: 'Running...' }]
                    }
                    return newHist
                  })
                } else if (data.type === 'final') {
                  setHistory(prev => {
                    const newHist = [...prev]
                    const lastMsg = newHist[newHist.length - 1]
                    if (lastMsg.type === 'agent') {
                      lastMsg.content = data.response
                      lastMsg.steps = data.intermediate_steps
                    }
                    return newHist
                  })
                } else if (data.type === 'error') {
                  setHistory(prev => {
                    const newHist = [...prev]
                    newHist[newHist.length - 1].content = data.content
                    return newHist
                  })
                }
              } catch {
                // Ignore parse errors
              }
            }
          }
        }
      }
    } catch {
      setHistory(prev => {
        const newHist = [...prev]
        newHist[newHist.length - 1].content = "Error connecting to AI backend."
        return newHist
      })
    } finally {
      setIsProcessing(false)
    }
  }

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [history, isProcessing])

  return (
    <div className="p-8 max-w-5xl mx-auto h-[calc(100vh-4rem)] flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-primary">Planner Playground</h1>
          <p className="text-muted-foreground mt-1">Directly interact with the LangGraph orchestration engine.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline"><Database className="mr-2 h-4 w-4" /> Tool Registry</Button>
          <Button variant="outline"><Code2 className="mr-2 h-4 w-4" /> View State</Button>
        </div>
      </div>

      <Card className="glass-panel flex-1 flex flex-col min-h-0 border-primary/20 shadow-lg shadow-primary/5">
        <CardHeader className="bg-secondary/30 border-b border-border/50">
          <CardTitle className="flex items-center gap-2">
            <Terminal className="h-5 w-5 text-primary" />
            Execution Console
          </CardTitle>
          <CardDescription>Monitor how the agent reasons, selects tools, and synthesizes output.</CardDescription>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto p-6 space-y-6 bg-background/50 font-mono text-sm">
          {history.length === 0 && (
            <div className="text-center mt-10 text-muted-foreground">
              <Activity className="h-10 w-10 mx-auto mb-4 opacity-50" />
              <p>System Ready. Waiting for input query...</p>
            </div>
          )}

          {history.map((msg, i) => (
            <div key={i} className={`flex flex-col ${msg.type === 'user' ? 'items-end' : 'items-start'}`}>
              <div className={`max-w-[90%] p-4 rounded-md ${msg.type === 'user' ? 'bg-primary/20 text-primary-foreground border border-primary/30' : 'bg-card border border-border/80'}`}>
                {msg.type === 'user' ? (
                  <div>&gt; {msg.content}</div>
                ) : (
                  <div className="space-y-4">
                    {msg.steps && msg.steps.length > 0 && (
                      <div className="space-y-2 border-l-2 border-primary/50 pl-4 py-2 my-2 bg-secondary/20 rounded-r-md">
                        <div className="text-xs font-bold text-primary mb-2">++ PLANNER EXECUTION TRACE ++</div>
                        <AnimatePresence>
                          {msg.steps.map((step: any, idx: number) => (
                            <motion.div 
                              key={idx}
                              initial={{ opacity: 0, x: -10 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: idx * 0.15 }}
                              className="text-xs"
                            >
                              <span className="text-muted-foreground">[{idx + 1}]</span> 
                              {step.tool ? (
                                <span> Invoking Tool: <span className="text-yellow-400">{step.tool}</span>(args: {JSON.stringify(step.args)})</span>
                              ) : (
                                <span> Tool Result: <span className="text-green-400">"{step.result}"</span></span>
                              )}
                            </motion.div>
                          ))}
                        </AnimatePresence>
                      </div>
                    )}
                    <div className="text-foreground whitespace-pre-wrap">{msg.content}</div>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isProcessing && (
            <div className="flex items-center gap-3 text-muted-foreground bg-card p-4 rounded-md border border-border/50 max-w-xs">
              <Activity className="h-4 w-4 animate-spin text-primary" />
              <span>Agent reasoning in progress...</span>
            </div>
          )}
          <div ref={endRef} />
        </CardContent>
        <div className="p-4 bg-secondary/30 border-t border-border/50">
          <div className="relative flex items-center max-w-4xl mx-auto">
            <span className="absolute left-4 font-mono text-primary font-bold">&gt;</span>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="e.g. Run a full investigation on CUST-8392"
              className="w-full bg-background border border-border/80 rounded-md pl-10 pr-12 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary font-mono"
              disabled={isProcessing}
            />
            <Button 
              size="sm" 
              className="absolute right-2"
              onClick={handleSend}
              disabled={isProcessing || !input.trim()}
            >
              EXEC <Send className="ml-2 h-3 w-3" />
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}
