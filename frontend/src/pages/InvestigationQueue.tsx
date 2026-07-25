import { ArrowRight, Filter, Search, Download, RefreshCw } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useInvestigationQueue } from '../hooks'
import { StateView, TableSkeleton, RiskBadge, PriorityBadge, StatusBadge } from '../components/shared'

export default function InvestigationQueue() {
  const navigate = useNavigate()
  const { data: queue, isLoading, isError, error } = useInvestigationQueue();

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
              <th>Updated</th>
              <th style={{ textAlign: 'right' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            <StateView 
              isLoading={isLoading} 
              isError={isError} 
              error={error} 
              isEmpty={!queue?.length}
              loadingComponent={
                <tr>
                  <td colSpan={8} className="p-0"><TableSkeleton /></td>
                </tr>
              }
              emptyComponent={
                <tr>
                  <td colSpan={8} className="text-center py-12 text-[#9CA3AF] text-[13px]">No items in queue.</td>
                </tr>
              }
            >
              {queue?.map((row) => (
                <tr key={row.id}>
                  <td className="font-mono font-semibold text-[#1E1E1E]">{row.id}</td>
                  <td className="font-semibold text-[#1E1E1E]">{row.customer}</td>
                  <td><RiskBadge score={row.riskScore} /></td>
                  <td><PriorityBadge priority={row.priority} /></td>
                  <td><StatusBadge status={row.status} /></td>
                  <td className="text-[#6B7280]">{row.assignedTo}</td>
                  <td className="font-mono text-[#6B7280]">{row.lastUpdated}</td>
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
            </StateView>
          </tbody>
        </table>
      </div>
    </div>
  )
}
