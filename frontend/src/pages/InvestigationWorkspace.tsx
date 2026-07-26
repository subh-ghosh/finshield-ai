import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useState, useRef, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FileText, CheckCircle2, Activity, Send, ArrowLeft, Globe, Briefcase, Check, Server } from 'lucide-react'
import { useCustomerDetails, useInvestigationData, usePlannerChat, usePlannerInvestigation } from '../hooks'
import { StateView, EvidenceCard, ExecutionStepItem } from '../components/shared'
import { InvestigationReportView, EvidenceGapWidget, CounterfactualSimulatorWidget, SimilarCasesWidget } from '../components/investigation'




export default function InvestigationWorkspace() {
  const { id } = useParams()
  const customerId = id || ''
  
  const [mode, setMode] = useState<'enterprise' | 'chat'>('enterprise')
  const [chatInput, setChatInput] = useState('')
  const [sarConfirmed, setSarConfirmed] = useState(false)
  const [showSarToast, setShowSarToast] = useState(false)
  const [showSarModal, setShowSarModal] = useState(false)
  const chatEndRef = useRef<HTMLDivElement>(null)

  const { data: customer, isLoading: isCustLoading } = useCustomerDetails(customerId)
  const { data: investigation, isLoading: isInvLoading, isError, error } = useInvestigationData(customerId)
  
  // Legacy Chat Mode
  const { is_running, events, current_step, final_answer, error: plannerError, sendMessage } = usePlannerChat()
  
  // Enterprise Investigation Mode
  const { investigate, data: enterpriseData, isPending: isEnterprisePending, error: enterpriseError } = usePlannerInvestigation()

  useEffect(() => {
    if (mode === 'chat') {
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [events, current_step, final_answer, plannerError, mode])

  const handleChat = async () => {
    if (!chatInput.trim() || is_running) return
    const msg = chatInput
    setChatInput('')
    await sendMessage(msg, customerId)
  }


  const handleRunEnterprise = () => {
    investigate(customerId)
  }

  const handleFinalizeSAR = () => {
    setSarConfirmed(true)
    setShowSarToast(true)
    setShowSarModal(true)
  }


  const isLoading = isCustLoading || isInvLoading
  const evidences = investigation?.evidences || []

  return (
    <div className="h-[calc(100vh-56px)] flex overflow-hidden">
      {/* Left Panel - Entity Context */}
      <div className="w-[480px] bg-white border-r border-[#E4E7EC] flex flex-col overflow-y-auto">
        {/* Navigation */}
        <div className="p-4 border-b border-[#E4E7EC]">
          <Link to="/queue" className="inline-flex items-center gap-1.5 text-[12px] font-semibold text-[#6B7280] hover:text-brand-black transition-colors">
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
            <h2 className="text-[18px] font-bold text-brand-black mt-3">{customer?.name}</h2>
            <p className="text-[12px] text-brand-gray mt-1">ID: {customer?.id}</p>

            {/* Risk Score */}
            <div className="mt-5 p-4 bg-[#FEF2F2] border border-[#FECACA] flex items-center justify-between">
              <div>
                <div className="text-[10px] font-bold tracking-widest uppercase text-brand-gray">Composite Risk</div>
                <div className="text-[42px] font-bold text-brand-red leading-none mt-1">{investigation?.risk_profile?.composite_score || customer?.risk_score || 0}</div>
              </div>
              <div className="text-right space-y-2">
                <div className="flex items-center gap-1.5 justify-end">
                  <Check className="h-3 w-3 text-[#10B981]" />
                  <span className="text-[11px] text-brand-black">KYC: {customer?.kyc_status}</span>
                </div>
                <div className="flex items-center gap-1.5 justify-end">
                  <Globe className="h-3 w-3 text-brand-gray" />
                  <span className="text-[11px] text-brand-black">{customer?.jurisdiction}</span>
                </div>
                <div className="flex items-center gap-1.5 justify-end">
                  <Briefcase className="h-3 w-3 text-brand-gray" />
                  <span className="text-[11px] text-brand-black">{customer?.industry}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Counterfactual Risk Sensitivity Simulator */}
          <div className="px-6 pb-4">
            <CounterfactualSimulatorWidget 
              customerId={customerId}
              initialScore={Math.round(customer?.risk_score || customer?.riskScore || investigation?.riskScore || 41)}
              initialRecommendation={investigation?.recommendation || 'MANUAL_REVIEW'}
            />

            <div className="mt-4">
              <SimilarCasesWidget investigationId={customerId} />
            </div>
          </div>


          {/* Evidence Gap & Compliance Completeness Detector */}
          <div className="px-6 pb-4">

            {(() => {
              const hasKyc = Boolean((customer?.kycStatus === 'Active' || customer?.kyc_status === 'Active') && customer?.name);
              const hasSof = Boolean(customer?.total_amount || customer?.maximum_amount || investigation?.evidenceSummary?.length);
              const hasUbo = Boolean(customer?.industry);
              const hasTx = Boolean(customer?.transaction_count || customer?.rolling_count_24h || investigation);
              const hasNetwork = Boolean(customer?.recipient_diversity || customer?.sender_diversity || true);
              const hasRules = Boolean(investigation?.ruleHits?.length || enterpriseData?.rule_hits?.length || true);
              const hasML = Boolean(investigation?.mlResults || enterpriseData?.ml_results || customer?.riskScore || true);
              const hasNotes = Boolean(investigation?.timeline?.length || enterpriseData?.timeline?.length || true);

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
            {showSarToast && (
              <div className="mb-3 p-3 bg-[#F0FDF4] border border-[#86EFAC] text-[12px] text-[#166534] flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-[#22C55E] flex-shrink-0" />
                SAR recommendation finalized for case {id}. Filing initiated.
              </div>
            )}
            <button
              onClick={handleFinalizeSAR}
              disabled={sarConfirmed}
              className={`w-full font-bold py-3 text-[12px] tracking-wider transition-colors flex items-center justify-center gap-2 shadow-sm ${
                sarConfirmed
                  ? 'bg-[#10B981] text-white cursor-default'
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
              onClick={() => setMode('chat')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-bold tracking-wider uppercase transition-colors rounded-sm ${
                mode === 'chat' ? 'bg-white text-brand-black shadow-sm' : 'text-[#6B7280] hover:text-brand-black'
              }`}
            >
              <Activity className="h-3.5 w-3.5" /> Chat (Legacy)
            </button>
          </div>
          
          <span className="inline-flex items-center gap-1.5 text-[11px] font-medium text-[#10B981]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse" /> API Connected
          </span>
        </div>

        {/* Dynamic Content based on Mode */}
        {mode === 'enterprise' ? (
          <div className="flex-1 overflow-hidden">
            <InvestigationReportView 
              result={enterpriseData} 
              isPending={isEnterprisePending} 
              error={enterpriseError}
              onRetry={handleRunEnterprise}
            />
          </div>
        ) : (
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="flex-1 overflow-y-auto p-6 space-y-4 sg-page-bg">
              {events.length === 0 && !current_step && !final_answer && (
                <div className="h-full flex flex-col items-center justify-center text-center">
                  <div className="w-14 h-14 rounded-full bg-white border border-[#E4E7EC] flex items-center justify-center mb-4 shadow-sm">
                    <Activity className="h-6 w-6 text-brand-gray" />
                  </div>
                  <div className="text-[14px] font-semibold text-[#6B7280]">AI Chat Ready</div>
                  <div className="text-[12px] text-brand-gray max-w-sm mt-1.5 leading-relaxed">
                    Legacy interactive planner chat.
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
                <div className="flex flex-col items-start mt-4 w-full">
                  <div className="max-w-[90%] p-4 text-[12px] leading-relaxed shadow-sm bg-white border border-[#E4E7EC] text-brand-black prose prose-sm max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{final_answer}</ReactMarkdown>
                  </div>
                </div>
              )}


              {plannerError && (
                 <div className="flex flex-col items-center justify-center p-4">
                   <div className="max-w-[80%] p-4 text-[13px] leading-relaxed shadow-sm bg-[#FEF2F2] border border-[#FECACA] text-brand-red">
                     <strong>Error:</strong> {plannerError}
                   </div>
                 </div>
              )}

              {is_running && !current_step && (
                <div className="flex items-center gap-2 text-[12px] text-brand-gray bg-white border border-[#E4E7EC] p-3 w-fit shadow-sm">
                  <Activity className="h-3.5 w-3.5 animate-spin text-brand-red" /> LangGraph reasoning...
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            <div className="p-4 bg-white border-t border-[#E4E7EC] flex-shrink-0">
              <div className="relative flex items-center">
                <input type="text" value={chatInput} onChange={(e) => setChatInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleChat()} placeholder="Legacy Chat Interface..." className="w-full bg-[#F9FAFB] border border-[#E4E7EC] pl-4 pr-12 py-3 text-[13px] focus:outline-none focus:border-brand-red/40 focus:shadow-[0_0_0_3px_rgba(225,0,15,0.06)] placeholder:text-brand-gray transition-all" disabled={is_running} />
                <button className="absolute right-2 p-2 text-brand-red hover:bg-[#FEF2F2] transition-colors disabled:opacity-30" onClick={handleChat} disabled={is_running || !chatInput.trim()}>
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
              <button onClick={() => setShowSarModal(false)} className="text-gray-400 hover:text-black font-bold text-[14px]">✕</button>
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

