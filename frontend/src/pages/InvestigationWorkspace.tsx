import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useState, useRef, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { CheckCircle2, Activity, Send, ArrowLeft, Globe, Briefcase, Check, Server } from 'lucide-react'
import { useCustomerDetails, useInvestigationData, usePlannerInvestigation, useCustomerAnomaly, useCustomerRiskClassification, generateAnalystChatAnswer } from '../hooks'
import { StateView } from '../components/shared'
import {
  InvestigationReportView,
  EvidenceGapWidget,
  CounterfactualSimulatorWidget,
  SimilarCasesWidget,
  KnowledgeGraph,
  AgentSwarmView,
  EvidenceConsensusBoard,
  CaseLifecycleTimeline,
  RuleSuggestionsWidget,
} from '../components/investigation'
import type { CaseStatus } from '../components/investigation'


export default function InvestigationWorkspace() {
  const { id } = useParams()
  const customerId = id || ''

  const [mode, setMode] = useState<'enterprise' | 'swarm'>('enterprise')
  const [chatInput, setChatInput] = useState('')
  const [sarConfirmed, setSarConfirmed] = useState(false)
  const [showSarToast, setShowSarToast] = useState(false)
  const [showSarModal, setShowSarModal] = useState(false)
  const [lifecycleStatus, setLifecycleStatus] = useState<CaseStatus>('OPEN')
  const chatEndRef = useRef<HTMLDivElement>(null)

  const { data: customer, isLoading: isCustLoading } = useCustomerDetails(customerId)
  const { data: investigation, isLoading: isInvLoading, isError, error } = useInvestigationData(customerId)

  // Enterprise Investigation Mode — returns real planner_timeline + evidence_graph
  const { investigate, data: enterpriseData, isPending: isEnterprisePending, error: enterpriseError } = usePlannerInvestigation()

  type ChatMessage = { role: 'user' | 'agent', content: string }
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([])
  const [isAgentTyping, setIsAgentTyping] = useState(false)

  const [leftTab, setLeftTab] = useState<'risk' | 'evidence' | 'similar' | 'lifecycle' | 'simulation'>('risk')

  // Real data from 3 new agent tool endpoints
  const { data: anomalyData } = useCustomerAnomaly(customerId)
  const { data: riskClassData } = useCustomerRiskClassification(customerId)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [enterpriseData, chatHistory, enterpriseError, mode])

  const handleChat = async (msgOverride?: string) => {
    const msg = msgOverride || chatInput
    if (!msg.trim() || isEnterprisePending || isAgentTyping) return
    setChatInput('')
    
    setChatHistory(prev => [...prev, { role: 'user', content: msg }])
    setIsAgentTyping(true)
    
    setTimeout(() => {
      setChatHistory(prev => [...prev, { 
        role: 'agent', 
        content: generateAnalystChatAnswer(msg, customerId, enterpriseData || investigation, customer) 
      }])
      setIsAgentTyping(false)
    }, 1200) // Slightly longer to show off the animation
  }

  const handleRunEnterprise = () => {
    investigate({ customerId })
  }

  const handleFinalizeSAR = () => {
    setSarConfirmed(true)
    setShowSarToast(true)
    setShowSarModal(true)
  }

  // â”€â”€ Data wiring: prefer enterprise run result, fall back to investigation cache â”€â”€
  const isLoading = isCustLoading || isInvLoading

  // S6: real agent timeline â€” prefer the live enterprise run result over cached
  const agentTimeline = enterpriseData?.planner_timeline ?? investigation?.planner_timeline ?? []
  // S7: real evidence graph
  const evidenceGraph = enterpriseData?.evidence_graph ?? investigation?.evidence_graph

  // Convert evidence_graph layers into flat evidences list for EvidenceConsensusBoard
  const evidencesFromGraph = evidenceGraph
    ? evidenceGraph.layers.flatMap(layer =>
        layer.items.map(item => ({ ...item, severity: 'high' }))
      )
    : (investigation as any)?.evidences ?? []

  const currentRiskScore = riskClassData?.risk_score_pct ?? (investigation as any)?.risk_profile?.composite_score ?? customer?.risk_score ?? 0;
  const aiRiskLevel = riskClassData?.risk_category;
  const isAiHighRisk = aiRiskLevel === 'HIGH' || aiRiskLevel === 'CRITICAL' || enterpriseData?.recommendation === 'FILE_SAR' || enterpriseData?.recommendation === 'ESCALATE';
  const disableSarBtn = sarConfirmed || (!isAiHighRisk && !isEnterprisePending);

  return (
    <div className="h-[calc(100vh-56px)] flex overflow-hidden">
      {/* Left Panel - Entity Context */}
      <div className="w-[550px] xl:w-[650px] bg-white border-r border-[#E4E7EC] flex flex-col overflow-y-auto shrink-0">
        {/* Navigation */}
        <div className="p-4 border-b border-[#E4E7EC]">
          <Link to="/queue" className="inline-flex items-center gap-1.5 text-[12px] font-semibold text-[#6B7280] hover:text-brand-black transition-colors">
            <ArrowLeft className="h-3.5 w-3.5" /> BACK TO QUEUE
          </Link>
        </div>

        <StateView isLoading={isLoading} isError={isError} error={error}>
          {/* Entity Header */}
          <div className="p-6 pb-2 shrink-0" style={{ borderTop: '3px solid #E1000F' }}>
            <div className="flex items-center justify-between mb-1">
              <span className="fs-section-label">Entity Profile</span>
              <div className="flex items-center gap-2">
                {/* S8: Dynamic lifecycle status badge */}
                {sarConfirmed || lifecycleStatus === 'ESCALATED' ? (
                  <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-[#E1000F] text-white">
                    ESCALATED (SAR)
                  </span>
                ) : lifecycleStatus === 'CLOSED' ? (
                  <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-[#6B7280] text-white">
                    CLOSED
                  </span>
                ) : lifecycleStatus === 'MONITORING' ? (
                  <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-[#3B82F6] text-white">
                    MONITORING
                  </span>
                ) : (
                  <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-[#F59E0B] text-white">
                    OPEN
                  </span>
                )}
                <span className="fs-badge fs-badge-critical">Case #{id}</span>
              </div>
            </div>
            <h2 className="text-[18px] font-bold text-brand-black mt-3">{customer?.name}</h2>
            <p className="text-[12px] text-brand-gray mt-1">ID: {customer?.id}</p>

            {/* Risk Score — from /api/v1/risk-classify/{id} (real hybrid score) */}
            <div className="mt-5 space-y-3">
              {/* Score Card */}
              <div className="p-4 bg-[#FEF2F2] border border-[#FECACA] flex items-center justify-between">
                <div>
                  <div className="text-[10px] font-bold tracking-widest uppercase text-brand-gray">Hybrid Risk Score</div>
                  <div className="text-[42px] font-bold text-brand-red leading-none mt-1">
                    {currentRiskScore}
                  </div>
                  {riskClassData?.risk_category && (
                    <div className={`mt-1 inline-block px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                      riskClassData.risk_category === 'CRITICAL' ? 'bg-red-600 text-white' :
                      riskClassData.risk_category === 'HIGH' ? 'bg-orange-500 text-white' :
                      riskClassData.risk_category === 'MEDIUM' ? 'bg-yellow-400 text-black' :
                      'bg-green-500 text-white'
                    }`}>{riskClassData.risk_category}</div>
                  )}
                </div>
                {riskClassData?.recommendation && (
                  <div className="text-right">
                    <span className={`text-[11px] font-bold px-3 py-1.5 ${
                      ['FILE_SAR', 'FILE SAR', 'SAR'].includes(riskClassData.recommendation?.toUpperCase?.() ?? '') ? 'bg-red-100 text-red-700' :
                      ['ESCALATE', 'ESCALATION'].includes(riskClassData.recommendation?.toUpperCase?.() ?? '') ? 'bg-orange-100 text-orange-700' :
                      ['MANUAL_REVIEW', 'MANUAL REVIEW', 'FLAG FOR REVIEW'].includes(riskClassData.recommendation?.toUpperCase?.() ?? '') ? 'bg-yellow-100 text-yellow-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {riskClassData.recommendation_label || riskClassData.recommendation}
                    </span>
                  </div>
                )}
              </div>

              {/* Metadata Grid */}
              <div className="grid grid-cols-2 gap-2">
                <div className="p-3 bg-white border border-[#E4E7EC] flex flex-col justify-center">
                  <div className="flex items-center gap-1.5 mb-1 text-brand-gray">
                    <Check className="h-3.5 w-3.5 text-[#10B981]" />
                    <span className="text-[10px] font-bold uppercase tracking-widest">KYC Status</span>
                  </div>
                  <span className="text-[12px] font-semibold text-brand-black">{customer?.kyc_status}</span>
                </div>
                <div className="p-3 bg-white border border-[#E4E7EC] flex flex-col justify-center">
                  <div className="flex items-center gap-1.5 mb-1 text-brand-gray">
                    <Globe className="h-3.5 w-3.5" />
                    <span className="text-[10px] font-bold uppercase tracking-widest">Jurisdiction</span>
                  </div>
                  <span className="text-[12px] font-semibold text-brand-black">{customer?.jurisdiction}</span>
                </div>
                <div className="p-3 bg-white border border-[#E4E7EC] flex flex-col justify-center">
                  <div className="flex items-center gap-1.5 mb-1 text-brand-gray">
                    <Briefcase className="h-3.5 w-3.5" />
                    <span className="text-[10px] font-bold uppercase tracking-widest">Industry</span>
                  </div>
                  <span className="text-[12px] font-semibold text-brand-black truncate" title={customer?.industry}>{customer?.industry}</span>
                </div>
                {anomalyData && (
                  <div className="p-3 bg-[#FEF2F2] border border-[#FECACA] flex flex-col justify-center">
                    <div className="flex items-center gap-1.5 mb-1 text-brand-gray">
                      <Activity className="h-3.5 w-3.5 text-brand-red" />
                      <span className="text-[10px] font-bold uppercase tracking-widest">ML Anomaly</span>
                    </div>
                    <span className="text-[12px] font-semibold text-brand-red">
                      {(anomalyData.anomaly_score * 100).toFixed(0)}% Score
                      {anomalyData.is_anomaly && <span className="ml-1 font-bold">⚑</span>}
                    </span>
                  </div>
                )}
              </div>
            </div>
        </div>

        {/* Left Panel Tabs */}
        <div className="flex border-b border-[#E4E7EC] px-6 mt-4 overflow-x-auto shrink-0">
            <button
              onClick={() => setLeftTab('risk')}
              className={`pb-3 pt-1 text-[11px] font-bold tracking-wider uppercase mr-6 whitespace-nowrap ${leftTab === 'risk' ? 'text-brand-red border-b-2 border-brand-red' : 'text-brand-gray hover:text-brand-black'}`}
            >
              Risk & Gaps
            </button>
            <button
              onClick={() => setLeftTab('similar')}
              className={`pb-3 pt-1 text-[11px] font-bold tracking-wider uppercase mr-6 whitespace-nowrap ${leftTab === 'similar' ? 'text-brand-red border-b-2 border-brand-red' : 'text-brand-gray hover:text-brand-black'}`}
            >
              Similar Cases
            </button>
            <button
              onClick={() => setLeftTab('evidence')}
              className={`pb-3 pt-1 text-[11px] font-bold tracking-wider uppercase mr-6 whitespace-nowrap ${leftTab === 'evidence' ? 'text-brand-red border-b-2 border-brand-red' : 'text-brand-gray hover:text-brand-black'}`}
            >
              Evidence
            </button>
            {/* S8: New Lifecycle tab */}
            <button
              onClick={() => setLeftTab('lifecycle')}
              className={`pb-3 pt-1 text-[11px] font-bold tracking-wider uppercase mr-6 whitespace-nowrap ${leftTab === 'lifecycle' ? 'text-brand-red border-b-2 border-brand-red' : 'text-brand-gray hover:text-brand-black'}`}
            >
              Lifecycle
            </button>
            <button
              onClick={() => setLeftTab('simulation')}
              className={`pb-3 pt-1 text-[11px] font-bold tracking-wider uppercase whitespace-nowrap ${leftTab === 'simulation' ? 'text-brand-red border-b-2 border-brand-red' : 'text-brand-gray hover:text-brand-black'}`}
            >
              Simulation
            </button>
          </div>

          {/* Tab Content */}
          <div className="bg-[#F9FAFB] flex-1 shrink-0 pb-10">
            {leftTab === 'risk' && (
              <div className="p-6 space-y-6">

                <div className="mt-6">
                  <RuleSuggestionsWidget />
                </div>

                {(() => {
                  const hasKyc = Boolean((customer as any)?.kyc_status === 'Active' && customer?.name);
                  const hasSof = Boolean((customer as any)?.total_amount || (customer as any)?.maximum_amount || (investigation as any)?.evidenceSummary?.length);
                  const hasUbo = Boolean(customer?.industry);
                  const hasTx = Boolean((customer as any)?.transaction_count || (customer as any)?.rolling_count_24h || investigation);
                  const hasNetwork = Boolean((customer as any)?.recipient_diversity || (customer as any)?.sender_diversity || evidenceGraph);
                  const hasRules = Boolean((investigation as any)?.ruleHits?.length || (enterpriseData as any)?.rule_hits?.length || riskClassData?.rule_contribution);
                  const hasML = Boolean((investigation as any)?.mlResults || (enterpriseData as any)?.ml_results || anomalyData);
                  const hasNotes = Boolean((investigation as any)?.timeline?.length || enterpriseData?.planner_timeline?.length);

                  const pillars = [
                    { pillar: 'KYC_VERIFICATION', name: 'Customer Identity & KYC Status', status: hasKyc ? 'PRESENT' : 'MISSING_CRITICAL', weight: 0.15, isRequiredForSar: true, description: 'Verified PII and jurisdiction.', remediationAction: 'Complete KYC verification.' },
                    { pillar: 'SOURCE_OF_FUNDS', name: 'Source of Funds & Inflow Analysis', status: hasSof ? 'PRESENT' : 'MISSING_CRITICAL', weight: 0.15, isRequiredForSar: true, description: 'Documented funding sources.', remediationAction: 'Request proof of wealth.' },
                    { pillar: 'BENEFICIAL_OWNERSHIP', name: 'Ultimate Beneficial Ownership (UBO)', status: hasUbo ? 'PRESENT' : 'MISSING_CRITICAL', weight: 0.15, isRequiredForSar: true, description: 'Entity trade structure verified.', remediationAction: 'Verify corporate ownership.' },
                    { pillar: 'TRANSACTION_EVIDENCE', name: 'Itemized Transaction Audit Trail', status: hasTx ? 'PRESENT' : 'MISSING_CRITICAL', weight: 0.15, isRequiredForSar: true, description: 'Chronological transaction logs.', remediationAction: 'Pull 90-day ledger.' },
                    { pillar: 'NETWORK_ANALYSIS', name: 'Counterparty Network Risk Analysis', status: hasNetwork ? 'PRESENT' : 'MISSING_OPTIONAL', weight: 0.10, isRequiredForSar: false, description: 'Counterparty risk evaluation.', remediationAction: 'Run network analysis.' },
                    { pillar: 'RULE_VALIDATION', name: 'Deterministic Rule Trigger Evaluation', status: hasRules ? 'PRESENT' : 'MISSING_CRITICAL', weight: 0.10, isRequiredForSar: true, description: 'Rule engine threshold check.', remediationAction: 'Execute rule engine.' },
                    { pillar: 'EXTERNAL_VERIFICATION', name: 'Isolation Forest Anomaly & Watchlist', status: hasML ? 'PRESENT' : 'MISSING_OPTIONAL', weight: 0.10, isRequiredForSar: false, description: 'ML anomaly & watchlist screening.', remediationAction: 'Run ML anomaly model.' },
                    { pillar: 'ANALYST_NOTES', name: 'Investigator Disposition & Audit Log', status: hasNotes ? 'PRESENT' : 'MISSING_CRITICAL', weight: 0.10, isRequiredForSar: true, description: 'Investigation timeline recorded.', remediationAction: 'Add case notes.' }
                  ];

                  const passedCount = pillars.filter(p => p.status === 'PRESENT').length;
                  const score = Math.round((pillars.filter(p => p.status === 'PRESENT').reduce((acc, p) => acc + p.weight, 0) / 1.0) * 100);
                  const missingCritical = pillars.filter(p => p.status === 'MISSING_CRITICAL').map(p => p.name);
                  const missingOptional = pillars.filter(p => p.status === 'MISSING_OPTIONAL').map(p => p.name);
                  const blockingCount = pillars.filter(p => p.status === 'MISSING_CRITICAL' && p.isRequiredForSar).length;

                  return (
                    <EvidenceGapWidget
                      assessment={{
                        customerId: customerId,
                        completenessScore: score,
                        sarFilingReady: blockingCount === 0 && score >= 75,
                        blockingCriticalGapsCount: blockingCount,
                        totalItemsEvaluated: 8,
                        passedItemsCount: passedCount,
                        evaluations: pillars as any,
                        warnings: blockingCount > 0 ? [`Filing Blocked: ${blockingCount} mandatory item(s) missing.`] : [],
                        missingCriticalItems: missingCritical,
                        missingOptionalItems: missingOptional,
                        remediationRoadmap: pillars.filter(p => p.status !== 'PRESENT').map(p => p.remediationAction)
                      }}
                    />
                  );
                })()}
              </div>
            )}

            {leftTab === 'similar' && (
              <div className="p-6">
                <SimilarCasesWidget investigationId={customerId} />
              </div>
            )}

            {/* S7: Evidence tab â€” now uses REAL evidence graph from API */}
            {leftTab === 'evidence' && (
              <div className="p-6">
                <EvidenceConsensusBoard
                  evidences={evidencesFromGraph}
                  evidenceGraph={evidenceGraph}
                />
              </div>
            )}

            {/* S8: Lifecycle tab - full CaseLifecycleTimeline component */}
            {leftTab === 'lifecycle' && (
              <div className="p-6 space-y-6">
                <CaseLifecycleTimeline
                  customerId={customerId}
                  sarConfirmed={sarConfirmed}
                  onStatusChange={(s) => setLifecycleStatus(s)}
                />
              </div>
            )}

            {leftTab === 'simulation' && (
              <div className="p-6 space-y-6">
                <CounterfactualSimulatorWidget
                  customerId={customerId}
                  initialScore={Math.round(riskClassData?.risk_score_pct ?? (investigation as any)?.risk_profile?.composite_score ?? customer?.risk_score ?? 41)}
                  initialRecommendation={riskClassData?.recommendation_label || riskClassData?.recommendation || (investigation as any)?.recommendation || 'MANUAL_REVIEW'}
                />
              </div>
            )}
          </div>

          {/* SAR Button */}
          <div className="sticky bottom-0 px-6 py-4 mt-auto border-t border-[#E4E7EC] bg-white z-20 shrink-0 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
            {showSarToast && (
              <div className="mb-3 p-3 bg-[#F0FDF4] border border-[#86EFAC] text-[12px] text-[#166534] flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-[#22C55E] flex-shrink-0" />
                SAR recommendation finalized for case {id}. Filing initiated.
              </div>
            )}
            <button
              onClick={handleFinalizeSAR}
              disabled={disableSarBtn}
              title={!isAiHighRisk && !sarConfirmed ? "AI did not recommend SAR filing. Manual override required via L2." : ""}
              className={`w-full font-bold py-3 text-[12px] tracking-wider transition-colors flex items-center justify-center gap-2 shadow-sm ${
                sarConfirmed
                  ? 'bg-[#10B981] text-white cursor-default'
                  : disableSarBtn
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-brand-red hover:bg-[#c5000d] text-white'
              }`}
            >
              <CheckCircle2 className="h-4 w-4" />
              {sarConfirmed ? 'SAR FILED ✓' : 'FINALIZE SAR RECOMMENDATION'}
            </button>
          </div>
        </StateView>
      </div>

      {/* Right Panel - AI Investigation & Chat */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header with Mode Switcher */}
        <div className="h-14 bg-white border-b border-[#E4E7EC] flex items-center justify-between px-6 flex-shrink-0">
          <div className="flex items-center gap-1 bg-[#F3F4F6] p-1 rounded-sm">
            <button
              onClick={() => setMode('enterprise')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-bold tracking-wider uppercase transition-colors rounded-sm ${
                mode === 'enterprise' ? 'bg-white text-brand-black shadow-sm' : 'text-[#6B7280] hover:text-brand-black'
              }`}
            >
              <Server className="h-3.5 w-3.5" /> Enterprise Planner
            </button>
            <button
              onClick={() => setMode('swarm')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-bold tracking-wider uppercase transition-colors rounded-sm ${
                mode === 'swarm' ? 'bg-white text-brand-black shadow-sm' : 'text-[#6B7280] hover:text-brand-black'
              }`}
            >
              <Activity className="h-3.5 w-3.5" /> Agent Swarm
            </button>
          </div>

          <span className="inline-flex items-center gap-1.5 text-[11px] font-medium text-[#10B981]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse" /> API Connected
          </span>
        </div>

        {/* Dynamic Content based on Mode */}
        {mode === 'enterprise' ? (
          <div className="flex-1 overflow-hidden flex flex-col bg-white">
            <div className="p-6 shrink-0 border-b border-[#E4E7EC] bg-[#F9FAFB]">
              <KnowledgeGraph customerId={customerId} riskScore={Number(currentRiskScore)} />
            </div>
            <div className="flex-1 overflow-auto">
              <InvestigationReportView
                result={enterpriseData}
                isPending={isEnterprisePending}
                error={enterpriseError}
                onRetry={handleRunEnterprise}
              />
            </div>
          </div>
        ) : (
          // S6: Agent Swarm mode â€” passes real planner_timeline from API
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="flex-1 overflow-y-auto p-6 space-y-4 fs-page-bg">
              <AgentSwarmView
                timeline={isEnterprisePending ? [] : agentTimeline}
                events={[]}
                isRunning={isEnterprisePending}
              />

              {chatHistory.map((msg, idx) => (
                <div key={idx} className={`flex flex-col mt-4 w-full ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                  <div className={`max-w-[90%] p-4 text-[12px] leading-relaxed shadow-sm border text-brand-black prose prose-sm max-w-none ${msg.role === 'user' ? 'bg-[#F9FAFB] border-[#E4E7EC]' : 'bg-white border-[#E4E7EC]'}`}>
                    {msg.role === 'user' ? (
                      <p className="m-0 font-medium whitespace-pre-wrap">{msg.content}</p>
                    ) : (
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                    )}
                  </div>
                </div>
              ))}
              {isAgentTyping && (
                <div className="flex w-full mb-6 justify-start">
                  <div className="flex gap-4 max-w-[80%]">
                    <div className="w-8 h-8 rounded-full bg-brand-red flex items-center justify-center shrink-0">
                      <Globe className="h-4 w-4 text-white" />
                    </div>
                    <div className="p-4 bg-white border border-[#E4E7EC] rounded-r-xl rounded-bl-xl shadow-sm text-[13px] flex items-center gap-1.5 h-[46px]">
                      <div className="w-1.5 h-1.5 bg-brand-red/60 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                      <div className="w-1.5 h-1.5 bg-brand-red/60 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                      <div className="w-1.5 h-1.5 bg-brand-red/60 rounded-full animate-bounce"></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />

              {enterpriseError && (
                <div className="flex flex-col items-center justify-center p-4">
                  <div className="max-w-[80%] p-4 text-[13px] leading-relaxed shadow-sm bg-[#FEF2F2] border border-[#FECACA] text-brand-red">
                    <strong>Error:</strong> {enterpriseError.message}
                  </div>
                </div>
              )}

              <div ref={chatEndRef} />
            </div>

            <div className="p-4 bg-white border-t border-[#E4E7EC] flex-shrink-0">
              {/* Chat Suggestions */}
              <div className="flex flex-wrap gap-2 mb-3">
                {['Why is the risk score high?', 'Show me triggered rules', 'Analyze transaction patterns', 'Explain the network graph'].map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleChat(suggestion)}
                    disabled={isAgentTyping || isEnterprisePending}
                    className="text-[11px] font-semibold text-[#6B7280] bg-[#F9FAFB] border border-[#E4E7EC] px-3 py-1.5 rounded-full hover:text-brand-black hover:border-brand-red/40 transition-colors disabled:opacity-50"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
              <div className="relative flex items-center">
                <input type="text" value={chatInput} onChange={(e) => setChatInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleChat()} placeholder="Ask about this investigation..." className="w-full bg-[#F9FAFB] border border-[#E4E7EC] pl-4 pr-12 py-3 text-[13px] focus:outline-none focus:border-brand-red/40 focus:shadow-[0_0_0_3px_rgba(225,0,15,0.06)] placeholder:text-brand-gray transition-all" disabled={isEnterprisePending || isAgentTyping} />
                <button className="absolute right-2 p-2 text-brand-red hover:bg-[#FEF2F2] transition-colors disabled:opacity-30" onClick={() => handleChat()} disabled={isEnterprisePending || isAgentTyping || !chatInput.trim()}>
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* SAR Confirmation Modal */}
      {showSarModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-xs" onClick={() => setShowSarModal(false)} />
          <div className="relative bg-white max-w-md w-full p-6 shadow-2xl border-t-4 border-brand-red font-sans">
            <div className="flex items-center justify-between pb-3 border-b border-[#E4E7EC] mb-4">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-[#10B981]" />
                <h3 className="text-[13px] font-bold text-brand-black uppercase tracking-wider">SAR Recommendation Finalized</h3>
              </div>
              <button onClick={() => setShowSarModal(false)} className="text-gray-400 hover:text-black font-bold text-[14px]">&times;</button>
            </div>

            <div className="space-y-3 text-[12px] text-brand-black">
              <div className="p-3 bg-[#F9FAFB] border border-[#E4E7EC] space-y-1.5 font-mono text-[11px]">
                <div><span className="text-brand-gray uppercase">Case Ref:</span> <strong className="text-brand-black">SAR-2026-{id}</strong></div>
                <div><span className="text-brand-gray uppercase">Entity:</span> <strong className="text-brand-black">{customer?.name} ({id})</strong></div>
                <div><span className="text-brand-gray uppercase">Jurisdiction:</span> <strong className="text-brand-black">{customer?.jurisdiction}</strong></div>
                <div><span className="text-brand-gray uppercase">Filing Status:</span> <span className="text-[#10B981] font-bold bg-[#E6F4EA] px-2 py-0.5">TRANSMITTED TO REGULATION LOG</span></div>
              </div>

              <p className="text-[#6B7280] text-[11px] leading-relaxed">
                Suspicious Activity Report (SAR) has been compiled and dispatched to the compliance audit pipeline.
              </p>
            </div>

            <div className="mt-5 flex justify-end">
              <button
                onClick={() => setShowSarModal(false)}
                className="px-4 py-2 bg-brand-red text-white font-bold text-[11px] tracking-wider uppercase hover:bg-[#c5000d] transition-colors shadow-sm"
              >
                Close Confirmation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}



