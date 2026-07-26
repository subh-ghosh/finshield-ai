import { useState, useRef, useEffect } from 'react'
import { Activity, Send, Terminal, Database, Code2, CheckCircle2, AlertTriangle, Info, X } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

// Extract a customer ID from a free-text message
function extractCustomerId(message: string): string {
  // Match C_NNN, CUST-NNN patterns
  const match = message.match(/\b(C_\d+|CUST-\d+)\b/i)
  if (match) return match[1].toUpperCase()
  // Dataset-level queries Ã¢â‚¬â€ no customer ID
  return 'UNKNOWN'
}

function RecommendationBadge({ rec }: { rec: string }) {
  const styles: Record<string, string> = {
    FILE_SAR: 'bg-red-100 text-red-700 border border-red-300',
    ESCALATE: 'bg-orange-100 text-orange-700 border border-orange-300',
    MANUAL_REVIEW: 'bg-yellow-100 text-yellow-700 border border-yellow-300',
    CLEAR: 'bg-green-100 text-green-700 border border-green-300',
  }
  return (
    <span className={`text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded ${styles[rec] || 'bg-gray-100 text-gray-600'}`}>
      {rec}
    </span>
  )
}

export default function PlannerPlayground() {
  const [input, setInput] = useState('')
  const [history, setHistory] = useState<any[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [showToolRegistry, setShowToolRegistry] = useState(false)
  const [showViewState, setShowViewState] = useState(false)
  const [lastResult, setLastResult] = useState<any>(null)
  const endRef = useRef<HTMLDivElement>(null)

  const handleSend = async () => {
    if (!input.trim() || isProcessing) return
    const userMsg = input
    const customerId = extractCustomerId(userMsg)

    setHistory(prev => [...prev, { type: 'user', content: userMsg }])
    setInput('')
    setIsProcessing(true)

    // Add placeholder agent response
    setHistory(prev => [...prev, {
      type: 'agent',
      status: 'running',
      customerId,
      steps: [],
      result: null,
      error: null
    }])

    try {
      const response = await fetch('http://localhost:8000/api/v1/planner/investigate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_id: customerId, request: userMsg })
      })

      const data = await response.json()

      if (!response.ok) {
        setHistory(prev => {
          const n = [...prev]
          const last = n[n.length - 1]
          last.status = 'error'
          last.error = data.details || data.message || 'Investigation failed'
          return n
        })
        return
      }

      setHistory(prev => {
        const n = [...prev]
        const last = n[n.length - 1]
        last.status = 'done'
        last.steps = data.reasoning_steps || []
        last.result = data
        setLastResult(data)
        return n
      })
    } catch {
      setHistory(prev => {
        const n = [...prev]
        const last = n[n.length - 1]
        last.status = 'error'
        last.error = 'Cannot connect to FinShield backend at localhost:8000. Ensure the backend is running.'
        return n
      })
    } finally {
      setIsProcessing(false)
    }
  }

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [history, isProcessing])

  return (
    <div className="flex flex-col h-[calc(100vh-55px)]">
      {/* Toolbar */}
      <div className="h-11 bg-white border-b border-[#E4E7EC] flex items-center justify-between px-6 flex-shrink-0">
        <div className="flex items-center gap-2">
          <Terminal className="h-3.5 w-3.5 text-brand-red" />
          <span className="text-[12px] font-bold tracking-wider uppercase text-[#6B7280]">AI Investigation Console</span>
        </div>
        <div className="flex gap-2 items-center">
          <span className="text-[10px] font-mono text-brand-gray bg-[#F3F4F6] px-2 py-0.5 rounded border border-[#E4E7EC]">
            Engine: Deterministic v2.0 + LLM Report
          </span>
          <button
            onClick={() => setShowToolRegistry(true)}
            className="text-[11px] border border-[#E4E7EC] px-3 py-1 bg-white text-[#6B7280] hover:bg-[#F9FAFB] flex items-center gap-1.5 transition-colors shadow-sm"
          >
            <Database className="h-3 w-3" /> Tool Registry
          </button>
          <button
            onClick={() => setShowViewState(true)}
            className="text-[11px] border border-[#E4E7EC] px-3 py-1 bg-white text-[#6B7280] hover:bg-[#F9FAFB] flex items-center gap-1.5 transition-colors shadow-sm"
          >
            <Code2 className="h-3 w-3" /> View State
          </button>
        </div>
      </div>

      {/* Console */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 fs-page-bg font-mono text-[13px]">
        {history.length === 0 && (
          <div className="text-center mt-16">
            <div className="w-14 h-14 rounded-full bg-white border border-[#E4E7EC] flex items-center justify-center mx-auto mb-4 shadow-sm">
              <Terminal className="h-6 w-6 text-brand-gray" />
            </div>
            <div className="text-[13px] font-semibold text-[#6B7280] font-sans">System Ready</div>
            <div className="text-[12px] text-brand-gray font-sans mt-1">
              Ask about a customer, or query the full dataset
            </div>
            <div className="mt-4 flex flex-wrap gap-2 justify-center">
              {[
                'Analyse this dataset for suspicious activity',
                'Find structuring patterns across all customers',
                'Investigate C_1',
                'Run AML check on C_2',
                'Flag high-risk customers',
                'Analyze customer C_500',
              ].map(s => (
                <button
                  key={s}
                  onClick={() => setInput(s)}
                  className="text-[11px] font-sans border border-[#E4E7EC] px-3 py-1.5 bg-white text-[#6B7280] hover:bg-[#F9FAFB] hover:text-brand-black hover:border-brand-red/30 transition-all rounded-sm"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {history.map((msg, i) => (
          <div key={i} className={`flex flex-col ${msg.type === 'user' ? 'items-end' : 'items-start'}`}>
            {msg.type === 'user' ? (
              <div className="max-w-[85%] p-3 shadow-sm bg-[#161A22] text-[#22C55E]">
                <div><span className="text-brand-red font-bold">&gt;</span> {msg.content}</div>
              </div>
            ) : (
              <div className="max-w-[90%] w-full bg-white border border-[#E4E7EC] shadow-sm">
                {/* Header */}
                <div className="flex items-center justify-between px-4 py-2 border-b border-[#F3F4F6] bg-[#FAFBFC]">
                  <div className="flex items-center gap-2">
                    <Activity className={`h-3 w-3 ${msg.status === 'running' ? 'animate-spin text-brand-red' : msg.status === 'done' ? 'text-green-500' : 'text-red-400'}`} />
                    <span className="text-[11px] font-bold text-[#6B7280] uppercase tracking-widest font-sans">
                      {msg.status === 'running' ? 'Executing Investigation...' : msg.status === 'error' ? 'Investigation Failed' : 'Investigation Complete'}
                    </span>
                  </div>
                  {msg.customerId && (
                    <span className="text-[10px] font-mono bg-[#F3F4F6] px-2 py-0.5 text-[#6B7280] border border-[#E4E7EC]">
                      {msg.customerId}
                    </span>
                  )}
                </div>

                {/* Error state */}
                {msg.status === 'error' && (
                  <div className="p-4 flex items-start gap-2">
                    <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                    <p className="text-[12px] text-red-600 font-sans">{msg.error}</p>
                  </div>
                )}

                {/* Execution trace */}
                {(msg.steps?.length > 0 || msg.status === 'running') && (
                  <div className="px-4 py-3 border-b border-[#F3F4F6] space-y-1.5">
                    <div className="text-[10px] font-bold text-brand-red uppercase tracking-[0.15em] mb-2">++ Execution Trace ++</div>
                    {msg.status === 'running' && msg.steps?.length === 0 && (
                      <div className="text-[11px] text-brand-gray flex items-center gap-1.5">
                        <Activity className="h-3 w-3 animate-spin" /> Running pipeline stages...
                      </div>
                    )}
                    {msg.steps?.map((step: string, idx: number) => (
                      <div key={idx} className="text-[11px] text-[#6B7280] flex items-start gap-2">
                        <CheckCircle2 className="h-3 w-3 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>{step}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Result */}
                {msg.result &                  <div className="p-4 space-y-3 font-sans">
                    {/* Intent Parsing Summary â€” shows what the agent extracted */}
                    {(msg.result.filters_extracted && Object.keys(msg.result.filters_extracted).length > 0) && (
                      <div className="bg-blue-50 border border-blue-200 rounded p-3">
                        <div className="text-[10px] font-bold text-blue-700 uppercase tracking-widest mb-2 flex items-center gap-1.5">
                          <Code2 className="h-3 w-3" /> Query Intent Parsed
                        </div>
                        <div className="grid grid-cols-2 gap-1">
                          {Object.entries(msg.result.filters_extracted).map(([k, v]) => v && (
                            <div key={k} className="flex items-center gap-1 text-[11px]">
                              <span className="text-blue-500 font-mono">{k}:</span>
                              <span className="text-blue-800 font-semibold">{String(v)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Key metrics */}
                    <div className="grid grid-cols-3 gap-3">
                      <div className="text-center p-3 bg-[#FAFBFC] border border-[#E4E7EC]">
                        <div className="text-[10px] uppercase tracking-widest text-brand-gray mb-1">Recommendation</div>
                        <RecommendationBadge rec={msg.result.recommendation} />
                      </div>
                      <div className="text-center p-3 bg-[#FAFBFC] border border-[#E4E7EC]">
                        <div className="text-[10px] uppercase tracking-widest text-brand-gray mb-1">Confidence</div>
                        <div className="text-[16px] font-bold text-brand-black">{(parseFloat(msg.result.confidence) * 100).toFixed(0)}%</div>
                      </div>
                      <div className="text-center p-3 bg-[#FAFBFC] border border-[#E4E7EC]">
                        <div className="text-[10px] uppercase tracking-widest text-brand-gray mb-1">Exec Time</div>
                        <div className="text-[14px] font-bold text-brand-black">{msg.result.execution_time_ms?.toFixed(1)}ms</div>
                      </div>
                    </div>

                    {/* Report â€” rendered as Markdown */}
                    {msg.result.final_report && (
                      <div className="mt-2">
                        <div className="text-[10px] font-bold text-[#6B7280] uppercase tracking-widest mb-2 flex items-center gap-1.5">
                          <Info className="h-3 w-3" /> Investigation Report
                        </div>
                        <div className="bg-[#FAFBFC] border border-[#E4E7EC] p-3 max-h-64 overflow-y-auto">
                          <div className="prose prose-sm max-w-none
                            prose-headings:text-brand-black prose-headings:font-bold prose-headings:text-[13px]
                            prose-p:text-[12px] prose-p:text-[#374151] prose-p:leading-relaxed prose-p:my-1
                            prose-strong:text-brand-black prose-strong:font-bold
                            prose-ul:my-1 prose-li:text-[12px] prose-li:text-[#374151]
                            prose-table:text-[11px] prose-td:py-1 prose-th:py-1
                          ">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.result.final_report}</ReactMarkdown>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
    </div>
                )}
              </div>
            )}
          </div>
        ))}

        {isProcessing && history[history.length - 1]?.status === 'running' && (
          <div className="flex items-center gap-2 text-[12px] text-brand-gray bg-white border border-[#E4E7EC] p-3 w-fit font-sans shadow-sm">
            <Activity className="h-3.5 w-3.5 animate-spin text-brand-red" /> Deterministic engine processing...
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="p-4 bg-white border-t border-[#E4E7EC] flex-shrink-0">
        <div className="relative flex items-center max-w-4xl mx-auto">
          <span className="absolute left-4 font-mono text-brand-red font-bold text-[14px]">&gt;</span>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="e.g. Analyse dataset for suspicious activity  or  Investigate C_1"
            className="w-full bg-[#F9FAFB] border border-[#E4E7EC] pl-10 pr-24 py-3 text-[13px] font-mono focus:outline-none focus:border-brand-red/40 focus:shadow-[0_0_0_3px_rgba(225,0,15,0.06)] placeholder:text-brand-gray transition-all"
            disabled={isProcessing}
          />
          <button
            className="absolute right-2 bg-brand-red hover:bg-[#c5000d] text-white text-[11px] font-bold px-4 py-1.5 tracking-wider transition-colors disabled:opacity-30 shadow-sm"
            onClick={handleSend}
            disabled={isProcessing || !input.trim()}
          >
            EXEC <Send className="inline h-3 w-3 ml-1" />
          </button>
        </div>
      </div>

      {/* Tool Registry Modal */}
      {showToolRegistry && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/40" onClick={() => setShowToolRegistry(false)} />
          <div className="relative bg-white w-[560px] max-h-[80vh] overflow-y-auto shadow-2xl">
            <div className="flex items-center justify-between px-6 py-4 border-b border-[#E4E7EC] sticky top-0 bg-white">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-brand-red" />
                <h2 className="text-[13px] font-bold text-brand-black tracking-wide">FinShield Tool Registry</h2>
              </div>
              <button onClick={() => setShowToolRegistry(false)}><X className="h-4 w-4 text-brand-gray" /></button>
            </div>
            <div className="p-6 space-y-3">
              {[
                // === 5 Core Agent Tools (required by problem statement) ===
                {
                  name: 'eda_analysis',
                  badge: 'EDA Tool',
                  desc: 'Dataset-level EDA: fraud rate, tx type distribution, top risky customers, AML pattern prevalence. Use for broad queries like "Analyse this dataset" or "Flag high-risk customers".',
                  input: 'none (dataset-level)',
                  output: 'total_tx, fraud_rate_pct, top_10_risky_customers, risk_distribution',
                  endpoint: 'GET /api/v1/eda/summary'
                },
                {
                  name: 'feature_engineering',
                  badge: 'Feature Engineering',
                  desc: 'Computes AML feature vector per customer: transaction velocity, rolling 24h sums, structuring score, smurfing score, cash-out ratio, amount deviation, network risk.',
                  input: 'customer_id: str',
                  output: 'velocity_features, amount_features, pattern_features, network_features',
                  endpoint: 'GET /api/v1/features/{id}'
                },
                {
                  name: 'anomaly_detection',
                  badge: 'Anomaly Detection',
                  desc: 'Isolation Forest ML scoring for a customer. Returns anomaly_score (0-1, higher=more suspicious), prediction (-1=flagged), severity, confidence, and natural language interpretation.',
                  input: 'customer_id: str',
                  output: 'anomaly_score, prediction, severity, confidence, is_anomaly, interpretation',
                  endpoint: 'GET /api/v1/anomaly/{id}'
                },
                {
                  name: 'risk_classification',
                  badge: 'Risk Classification',
                  desc: 'Hybrid risk classification: combines rule engine (30%) + Isolation Forest (30%) + GNN (40%) into risk_score_pct (0-100), risk_category (LOW/MEDIUM/HIGH/CRITICAL), and escalation action.',
                  input: 'customer_id: str',
                  output: 'risk_score_pct, risk_category, recommendation, rule_contribution, ml_contribution',
                  endpoint: 'GET /api/v1/risk-classify/{id}'
                },
                {
                  name: 'get_explanation',
                  badge: 'Explanation',
                  desc: 'Returns detailed Gemini-generated explanation with evidence timeline, triggered rules, and natural language rationale for each flag â€” tied to the original query intent.',
                  input: 'customer_id: str',
                  output: 'ExplanationResponseV1 (evidence_items, timeline, rule_violations, narrative)',
                  endpoint: 'GET /api/v1/explanation/{id}'
                },
                // === Supporting Tools ===
                {
                  name: 'analyze_customer',
                  badge: 'Full Pipeline',
                  desc: 'End-to-end AML analysis for one customer: runs all 5 pipeline stages (load â†’ rules â†’ ML â†’ hybrid risk â†’ evidence). Best for "Is C_1 suspicious?" type queries.',
                  input: 'customer_id: str',
                  output: 'risk_score, recommendation, evidence_summary, triggered_rules',
                  endpoint: 'POST /api/v1/analyze/customer'
                },
                {
                  name: 'analyze_batch',
                  badge: 'Batch',
                  desc: 'Batch AML analysis for a list of customer IDs. Returns risk scores and recommendations for all.',
                  input: 'customer_ids: List[str]',
                  output: 'List[AnalysisResult]',
                  endpoint: 'POST /api/v1/analyze/batch'
                },
                {
                  name: 'get_customer_profile',
                  badge: 'Profile',
                  desc: 'Returns cached customer feature metrics, rule summary, and anomaly score summary. Lightweight alternative to full analysis.',
                  input: 'customer_id: str',
                  output: 'feature_metrics, rule_summary, anomaly_summary',
                  endpoint: 'GET /api/v1/customer/{id}'
                },
                {
                  name: 'health',
                  badge: 'Utility',
                  desc: 'Backend health check â€” verifies all services (pipeline, ML model, rules) are operational.',
                  input: 'none',
                  output: 'status: ok | degraded',
                  endpoint: 'GET /api/v1/health'
                },
                {
                  name: 'version',
                  badge: 'Utility',
                  desc: 'Returns backend API version, model versions, and pipeline configuration metadata.',
                  input: 'none',
                  output: 'api_version, model_versions',
                  endpoint: 'GET /api/v1/version'
                },
              ].map((tool, i) => (
                <div key={i} className="border border-[#E4E7EC] p-4 hover:border-brand-red/20 transition-colors">
                  <div className="flex items-start justify-between gap-2">
                    <code className="text-[12px] font-bold text-brand-red font-mono">{tool.name}</code>
                    <div className="flex gap-1 flex-shrink-0">
                      <span className="text-[9px] bg-blue-100 text-blue-700 px-1.5 py-0.5 font-bold">{tool.badge}</span>
                      <span className="text-[9px] bg-green-100 text-green-700 px-1.5 py-0.5 font-bold">ACTIVE</span>
                    </div>
                  </div>
                  <p className="text-[12px] text-[#374151] mt-1 leading-snug">{tool.desc}</p>
                  <div className="flex flex-col gap-0.5 mt-2">
                    <span className="text-[10px] text-brand-gray">IN: <code className="text-[#6B7280]">{tool.input}</code></span>
                    <span className="text-[10px] text-brand-gray">OUT: <code className="text-[#6B7280]">{tool.output}</code></span>
                    <span className="text-[10px] text-brand-gray font-mono">{tool.endpoint}</span>
                  </div>
                </div>
              ))}

            </div>
          </div>
        </div>
      )}

      {/* View State Modal */}
      {showViewState && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/40" onClick={() => setShowViewState(false)} />
          <div className="relative bg-[#161A22] w-[640px] max-h-[80vh] overflow-y-auto shadow-2xl">
            <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 sticky top-0 bg-[#161A22]">
              <div className="flex items-center gap-2">
                <Code2 className="h-4 w-4 text-[#22C55E]" />
                <h2 className="text-[13px] font-bold text-white tracking-wide font-mono">Pipeline State</h2>
              </div>
              <button onClick={() => setShowViewState(false)}><X className="h-4 w-4 text-white/40" /></button>
            </div>
            <div className="p-6">
              <pre className="text-[11px] text-[#22C55E] font-mono leading-relaxed whitespace-pre-wrap">
                {JSON.stringify(lastResult ? {
                  engine: 'FinShield Deterministic v2.0',
                  customer_id: lastResult.customer_id,
                  planner_status: lastResult.planner_status,
                  recommendation: lastResult.recommendation,
                  confidence: lastResult.confidence,
                  risk_score: lastResult.risk_score,
                  execution_time_ms: lastResult.execution_time_ms,
                  reasoning_steps: lastResult.reasoning_steps,
                  errors: lastResult.errors,
                } : { status: 'No investigation run yet. Execute a query to see pipeline state.' }, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}



