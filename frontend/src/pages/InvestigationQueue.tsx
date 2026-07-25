import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { ArrowRight, Filter, Search, Download, RefreshCw } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function InvestigationQueue() {
  const navigate = useNavigate()
  const { data: queue, isLoading } = useQuery({
    queryKey: ['queue'],
    queryFn: async () => {
      try {
        const res = await api.get('/investigations/queue')
        return res.data
      } catch {
        return [
          { id: "CUST-8392", name: "Acme Corp Ltd", risk_score: 92, priority: "Critical", status: "Open", assigned_analyst: "Unassigned", recent_transactions: 145 },
          { id: "CUST-1042", name: "Global Traders Inc", risk_score: 85, priority: "High", status: "In Progress", assigned_analyst: "Sarah Jenkins", recent_transactions: 89 },
          { id: "CUST-4491", name: "TechVentures LLC", risk_score: 78, priority: "High", status: "Open", assigned_analyst: "Unassigned", recent_transactions: 56 },
          { id: "CUST-9921", name: "Nexus Dynamics", risk_score: 65, priority: "Medium", status: "In Progress", assigned_analyst: "Michael Chen", recent_transactions: 34 },
          { id: "CUST-3371", name: "Pacific Holdings", risk_score: 91, priority: "Critical", status: "Open", assigned_analyst: "Unassigned", recent_transactions: 201 },
          { id: "CUST-7782", name: "Zenith Exports", risk_score: 72, priority: "High", status: "Pending Review", assigned_analyst: "Anna Müller", recent_transactions: 67 },
        ]
      }
    }
  })

  const getRiskBadge = (score: number) => {
    if (score >= 90) return <span className="sg-badge sg-badge-critical">CRITICAL ({score})</span>
    if (score >= 75) return <span className="sg-badge sg-badge-high">HIGH ({score})</span>
    if (score >= 50) return <span className="sg-badge sg-badge-medium">MEDIUM ({score})</span>
    return <span className="sg-badge sg-badge-low">LOW ({score})</span>
  }

  const getStatusStyle = (status: string) => {
    switch (status) {
      case 'Open': return 'bg-[#FEF2F2] text-[#E1000F] border-[#FECACA]'
      case 'In Progress': return 'bg-[#FEF9C3] text-[#92400E] border-[#FDE68A]'
      case 'Pending Review': return 'bg-[#F0FDF4] text-[#166534] border-[#BBF7D0]'
      default: return 'bg-[#F9FAFB] text-[#6B7280] border-[#E5E7EB]'
    }
  }

  return (
    <div className="p-7 space-y-5">
      {/* Toolbar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-[#9CA3AF]" />
            <input 
              type="text" 
              placeholder="Search by entity name or ID..." 
              className="pl-9 h-9 w-[280px] bg-white border border-[#E4E7EC] px-3 py-2 text-[13px] text-[#1E1E1E] placeholder:text-[#9CA3AF] focus:outline-none focus:border-[#E1000F]/40 focus:shadow-[0_0_0_3px_rgba(225,0,15,0.06)] transition-all"
            />
          </div>
          <button className="h-9 px-4 bg-white border border-[#E4E7EC] text-[12px] font-medium text-[#6B7280] hover:bg-[#F9FAFB] flex items-center gap-1.5 transition-colors">
            <Filter className="h-3.5 w-3.5" /> Filters
          </button>
          <button className="h-9 px-3 bg-white border border-[#E4E7EC] text-[#6B7280] hover:bg-[#F9FAFB] transition-colors">
            <RefreshCw className="h-3.5 w-3.5" />
          </button>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[11px] text-[#9CA3AF] font-medium">{queue?.length || 0} alerts</span>
          <button className="h-9 px-4 bg-white border border-[#E4E7EC] text-[12px] font-medium text-[#6B7280] hover:bg-[#F9FAFB] flex items-center gap-1.5 transition-colors">
            <Download className="h-3.5 w-3.5" /> Export
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="sg-panel overflow-hidden">
        <table className="sg-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Entity Name</th>
              <th>Risk Score</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Assigned Analyst</th>
              <th>Txns</th>
              <th style={{ textAlign: 'right' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={8} className="text-center py-12 text-[#9CA3AF]">Loading investigation queue...</td>
              </tr>
            ) : queue?.map((row: any) => (
              <tr key={row.id}>
                <td className="font-mono font-semibold text-[#1E1E1E]">{row.id}</td>
                <td className="font-semibold text-[#1E1E1E]">{row.name}</td>
                <td>{getRiskBadge(row.risk_score)}</td>
                <td>
                  <span className={`text-[10px] font-bold px-2 py-0.5 ${
                    row.priority === 'Critical' ? 'text-[#E1000F]' : row.priority === 'High' ? 'text-[#F59E0B]' : 'text-[#6B7280]'
                  }`}>
                    {row.priority}
                  </span>
                </td>
                <td>
                  <span className={`inline-flex items-center text-[10px] font-semibold px-2 py-0.5 border ${getStatusStyle(row.status)}`}>
                    {row.status}
                  </span>
                </td>
                <td className="text-[#6B7280]">{row.assigned_analyst}</td>
                <td className="font-mono text-[#6B7280]">{row.recent_transactions}</td>
                <td className="text-right">
                  <button 
                    className="text-[11px] font-bold text-[#E1000F] hover:text-[#b8000c] hover:underline inline-flex items-center gap-1 transition-colors tracking-wide"
                    onClick={() => navigate(`/investigation/${row.id}`)}
                  >
                    INVESTIGATE <ArrowRight className="h-3 w-3" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
