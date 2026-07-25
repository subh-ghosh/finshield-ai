import { useState, useRef, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Send, User, ShieldAlert, Activity, FileText, CheckCircle2, ChevronRight, Check } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

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
          id: id,
          name: "Acme Corp Ltd",
          kyc_status: "Verified",
          risk_score: 92,
          onboarding_date: "2023-01-15",
          industry: "Import/Export",
          jurisdiction: "Cayman Islands",
          historical_risk: "Medium",
          connected_customers: [
            { id: "CUST-1042", name: "Global Traders Inc", relation: "Shared Director" }
          ]
        }
      }
    }
  })

  // Mock Evidence
  const evidences = [
    { id: 1, title: 'Velocity Score', desc: '145 transactions in 7 days, 400% above baseline.', active: true },
    { id: 2, title: 'Structuring Pattern', desc: 'Multiple $9.9k transfers avoiding $10k reporting limit.', active: true },
    { id: 3, title: 'High Risk Jurisdiction', desc: 'Funds flowing to/from Cayman Islands.', active: true },
    { id: 4, title: 'ML Anomaly Score', desc: 'Isolation Forest score: 0.89 (Top 1%).', active: true }
  ]

  const handleChat = async () => {
    if (!chatInput.trim()) return
    const userMsg = chatInput
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setChatInput('')
    setIsTyping(true)

    try {
      const res = await api.post('/planner/chat', {
        message: userMsg,
        customer_id: id
      })
      
      const { response, intermediate_steps } = res.data
      
      setMessages(prev => [
        ...prev, 
        { 
          role: 'assistant', 
          content: response,
          steps: intermediate_steps
        }
      ])
    } catch {
      setMessages(prev => [
        ...prev, 
        { role: 'assistant', content: "I'm currently unable to connect to the LangGraph AI Planner. Operating in offline demonstration mode: The customer shows classic signs of layering." }
      ])
    } finally {
      setIsTyping(false)
    }
  }

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  return (
    <div className="p-8 max-w-[1600px] mx-auto h-[calc(100vh-4rem)] flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight text-primary">Investigation Workspace</h1>
            <Badge variant="outline" className="border-primary/50 text-primary bg-primary/10">Case #{id}</Badge>
          </div>
          <p className="text-muted-foreground mt-1">Comprehensive entity review and AI-assisted analysis.</p>
        </div>
        <Button className="gap-2">
          <CheckCircle2 className="h-4 w-4" /> Finalize SAR Recommendation
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0">
        
        {/* Left Column: Entity Context */}
        <div className="lg:col-span-4 flex flex-col gap-6 overflow-y-auto pr-2 custom-scrollbar">
          
          <Card className="glass-panel border-l-4 border-l-destructive">
            <CardHeader className="pb-3">
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-xl">{customer?.name}</CardTitle>
                  <CardDescription className="flex items-center gap-2 mt-1">
                    <User className="h-3 w-3" /> Entity ID: {customer?.id}
                  </CardDescription>
                </div>
                <div className="flex flex-col items-end">
                  <span className="text-3xl font-bold text-destructive">{customer?.risk_score}</span>
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Risk Score</span>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4 text-sm mt-2">
                <div>
                  <div className="text-muted-foreground mb-1 text-xs">KYC Status</div>
                  <div className="font-medium flex items-center gap-2">
                    <Check className="h-3 w-3 text-green-500" /> {customer?.kyc_status}
                  </div>
                </div>
                <div>
                  <div className="text-muted-foreground mb-1 text-xs">Jurisdiction</div>
                  <div className="font-medium">{customer?.jurisdiction}</div>
                </div>
                <div>
                  <div className="text-muted-foreground mb-1 text-xs">Industry</div>
                  <div className="font-medium">{customer?.industry}</div>
                </div>
                <div>
                  <div className="text-muted-foreground mb-1 text-xs">Onboarded</div>
                  <div className="font-medium">{customer?.onboarding_date}</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-panel flex-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-primary" />
                Evidence Board
              </CardTitle>
              <CardDescription>Aggregated signals from Rule Engine & Models</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {evidences.map((ev, i) => (
                <motion.div 
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  key={ev.id} 
                  className="p-3 rounded-lg border border-border/50 bg-secondary/20 flex gap-3"
                >
                  <div className="mt-0.5">
                    <ShieldAlert className="h-4 w-4 text-destructive" />
                  </div>
                  <div>
                    <div className="font-medium text-sm text-foreground">{ev.title}</div>
                    <div className="text-xs text-muted-foreground mt-1">{ev.desc}</div>
                  </div>
                </motion.div>
              ))}
            </CardContent>
          </Card>

        </div>

        {/* Right Column: AI Agent Interaction */}
        <div className="lg:col-span-8 flex flex-col gap-6 min-h-0">
          
          <Card className="glass-panel flex-1 flex flex-col min-h-0">
            <CardHeader className="border-b border-border/40 pb-4">
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Activity className="h-5 w-5 text-primary" />
                  FinShield AI Planner
                </div>
                <Badge variant="outline" className="bg-primary/5 text-primary border-primary/20">LangGraph Active</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col p-0 min-h-0">
              
              {/* Chat History & Traces */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {messages.length === 0 && (
                  <div className="h-full flex flex-col items-center justify-center text-center opacity-60">
                    <Activity className="h-12 w-12 text-primary mb-4 animate-pulse-glow" />
                    <h3 className="text-lg font-medium text-foreground">AI Planner Ready</h3>
                    <p className="text-sm text-muted-foreground max-w-sm mt-2">
                      Ask a question to trigger the LangGraph orchestration. The AI will autonomously decide which tools to use.
                    </p>
                    <div className="mt-6 flex flex-wrap gap-2 justify-center">
                      <Button variant="secondary" size="sm" onClick={() => setChatInput("Summarize the risk profile for this customer.")}>Summarize Risk</Button>
                      <Button variant="secondary" size="sm" onClick={() => setChatInput("Check for structuring patterns.")}>Check Structuring</Button>
                    </div>
                  </div>
                )}
                
                {messages.map((msg, i) => (
                  <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                    <div className={`max-w-[80%] rounded-xl p-4 ${msg.role === 'user' ? 'bg-primary/20 text-primary-foreground border border-primary/30' : 'bg-secondary/40 border border-border/50 text-foreground'}`}>
                      <div className="text-sm leading-relaxed">{msg.content}</div>
                    </div>
                    
                    {/* Tool Execution Trace */}
                    {msg.steps && msg.steps.length > 0 && (
                      <div className="mt-3 ml-2 space-y-2 border-l-2 border-primary/30 pl-4 w-full max-w-[80%]">
                        <div className="text-xs font-semibold text-muted-foreground mb-2 flex items-center gap-2">
                          <Activity className="h-3 w-3" /> Planner Execution Trace
                        </div>
                        <AnimatePresence>
                          {msg.steps.map((step: any, idx: number) => (
                            <motion.div 
                              key={idx}
                              initial={{ opacity: 0, height: 0 }}
                              animate={{ opacity: 1, height: 'auto' }}
                              className="text-xs bg-background/50 border border-border/50 rounded p-2 overflow-hidden text-muted-foreground"
                            >
                              <div className="font-mono text-primary flex items-center gap-2">
                                <ChevronRight className="h-3 w-3" /> 
                                {step.tool ? `Tool Executed: ${step.tool}` : 'Action'}
                              </div>
                              {step.args && <div className="mt-1 pl-5 opacity-70">Args: {JSON.stringify(step.args)}</div>}
                              {step.result && <div className="mt-1 pl-5 text-foreground/80 line-clamp-2">{step.result}</div>}
                            </motion.div>
                          ))}
                        </AnimatePresence>
                      </div>
                    )}
                  </div>
                ))}
                
                {isTyping && (
                  <div className="flex items-start">
                    <div className="bg-secondary/40 border border-border/50 rounded-xl p-4">
                      <div className="flex gap-1">
                        <motion.div animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 0.6 }} className="w-2 h-2 rounded-full bg-primary" />
                        <motion.div animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.2 }} className="w-2 h-2 rounded-full bg-primary" />
                        <motion.div animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.4 }} className="w-2 h-2 rounded-full bg-primary" />
                      </div>
                      <div className="text-xs text-muted-foreground mt-2 font-mono">LangGraph Reasoning...</div>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Chat Input */}
              <div className="p-4 border-t border-border/40 bg-card">
                <div className="relative flex items-center">
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleChat()}
                    placeholder="Ask the AI Planner to analyze transactions, explain risk, or generate a SAR..."
                    className="w-full bg-secondary/50 border border-border/50 rounded-lg pl-4 pr-12 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary placeholder:text-muted-foreground/70 transition-shadow"
                    disabled={isTyping}
                  />
                  <Button 
                    size="icon" 
                    variant="ghost" 
                    className="absolute right-2 text-primary hover:text-primary hover:bg-primary/20"
                    onClick={handleChat}
                    disabled={isTyping || !chatInput.trim()}
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  )
}
