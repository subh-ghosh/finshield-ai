import { useState, useMemo } from 'react'
import { ArrowRight, Filter, Search, Download, RefreshCw, X, UserSquare2 } from 'lucide-react'
import { useNavigate, Link } from 'react-router-dom'
import { useInvestigationQueue } from '../hooks'
import { StateView, TableSkeleton, RiskBadge, PriorityBadge, StatusBadge } from '../components/shared'

export default function InvestigationQueue() {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [priorityFilter, setPriorityFilter] = useState<string>('All')
  const [showFilterMenu, setShowFilterMenu] = useState(false)
  const { data: queue, isLoading, isError, error, refetch } = useInvestigationQueue()

  const priorities = ['All', 'Critical', 'High', 'Medium', 'Low']

  const filteredQueue = useMemo(() => {
    if (!queue) return []
    return queue.filter(row => {
      const q = searchQuery.toLowerCase()
      const matchesSearch = !q || row.id.toLowerCase().includes(q) || row.customer.toLowerCase().includes(q)
      const matchesPriority = priorityFilter === 'All' || row.priority === priorityFilter
      return matchesSearch && matchesPriority
    })
  }, [queue, searchQuery, priorityFilter])

  const handleExport = () => {
    if (!filteredQueue.length) return
    const headers = ['ID', 'Customer', 'Risk Score', 'Priority', 'Status', 'Assigned To', 'Last Updated']
    const rows = filteredQueue.map(r => [r.id, r.customer, r.riskScore, r.priority, r.status, r.assignedTo, r.lastUpdated])
    const csv = [headers, ...rows].map(r => r.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'investigation_queue.csv'; a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="p-7 space-y-5">
      {/* Toolbar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-brand-gray" />
            <input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder="Search by entity name or ID..."
              className="pl-9 h-9 w-[280px] bg-white border border-[#E4E7EC] px-3 py-2 text-[13px] text-brand-black placeholder:text-brand-gray focus:outline-none focus:border-brand-red/40 focus:shadow-[0_0_0_3px_rgba(225,0,15,0.06)] transition-all"
            />
            {searchQuery && (
              <button onClick={() => setSearchQuery('')} className="absolute right-2 top-1/2 -translate-y-1/2 text-brand-gray hover:text-brand-black">
                <X className="h-3 w-3" />
              </button>
            )}
          </div>

          {/* Priority Filter */}
          <div className="relative">
            <button
              onClick={() => setShowFilterMenu(v => !v)}
              className={`h-9 px-4 bg-white border text-[12px] font-medium flex items-center gap-1.5 transition-colors ${
                priorityFilter !== 'All'
                  ? 'border-brand-red/40 text-brand-red bg-[#FEF2F2]'
                  : 'border-[#E4E7EC] text-[#6B7280] hover:bg-[#F9FAFB]'
              }`}
            >
              <Filter className="h-3.5 w-3.5" />
              {priorityFilter === 'All' ? 'Filters' : `Priority: ${priorityFilter}`}
            </button>
            {showFilterMenu && (
              <div className="absolute top-10 left-0 z-20 bg-white border border-[#E4E7EC] shadow-lg min-w-[150px]">
                {priorities.map(p => (
                  <button
                    key={p}
                    onClick={() => { setPriorityFilter(p); setShowFilterMenu(false) }}
                    className={`block w-full text-left px-4 py-2.5 text-[12px] hover:bg-[#F9FAFB] transition-colors ${
                      p === priorityFilter ? 'font-bold text-brand-red' : 'text-[#374151]'
                    }`}
                  >
                    {p}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Refresh */}
          <button
            onClick={() => refetch()}
            className="h-9 px-3 bg-white border border-[#E4E7EC] text-[#6B7280] hover:bg-[#F9FAFB] hover:text-brand-black transition-colors"
            title="Refresh queue"
          >
            <RefreshCw className="h-3.5 w-3.5" />
          </button>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-[11px] text-brand-gray font-medium">{filteredQueue.length} alerts</span>
          <button
            onClick={handleExport}
            disabled={filteredQueue.length === 0}
            className="h-9 px-4 bg-white border border-[#E4E7EC] text-[12px] font-medium text-[#6B7280] hover:bg-[#F9FAFB] flex items-center gap-1.5 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Download className="h-3.5 w-3.5" /> Export CSV
          </button>
        </div>
      </div>

      {/* Active Filters Badge */}
      {(searchQuery || priorityFilter !== 'All') && (
        <div className="flex items-center gap-2 text-[11px]">
          <span className="text-brand-gray">Active filters:</span>
          {searchQuery && (
            <span className="inline-flex items-center gap-1 bg-[#F3F4F6] border border-[#E4E7EC] px-2 py-0.5 text-[#374151]">
              Search: "{searchQuery}"
              <button onClick={() => setSearchQuery('')}><X className="h-2.5 w-2.5" /></button>
            </span>
          )}
          {priorityFilter !== 'All' && (
            <span className="inline-flex items-center gap-1 bg-[#FEF2F2] border border-[#FECACA] px-2 py-0.5 text-brand-red">
              Priority: {priorityFilter}
              <button onClick={() => setPriorityFilter('All')}><X className="h-2.5 w-2.5" /></button>
            </span>
          )}
          <button onClick={() => { setSearchQuery(''); setPriorityFilter('All') }} className="text-brand-gray hover:text-brand-red">
            Clear all
          </button>
        </div>
      )}

      {/* Table */}
      <div className="fs-panel overflow-hidden">
        <table className="fs-table">
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
              isEmpty={!filteredQueue.length}
              loadingComponent={
                <tr>
                  <td colSpan={8} className="p-0"><TableSkeleton /></td>
                </tr>
              }
              emptyComponent={
                <tr>
                  <td colSpan={8} className="text-center py-12 text-brand-gray text-[13px]">
                    {searchQuery || priorityFilter !== 'All' ? 'No results match your filters.' : 'No items in queue.'}
                  </td>
                </tr>
              }
              errorComponent={
                <tr>
                  <td colSpan={8} className="text-center py-12 text-brand-red text-[13px]">
                    Failed to load queue data.
                  </td>
                </tr>
              }
            >
              {filteredQueue.map((row) => (
                <tr key={row.id}>
                  <td className="font-mono font-semibold text-brand-black">{row.id}</td>
                  <td className="font-semibold text-brand-black">
                    <div>{row.customer}</div>
                    <Link to={`/customer/${row.id}`} className="text-[10px] text-brand-gray hover:text-brand-red inline-flex items-center gap-0.5 transition-colors mt-0.5">
                      <UserSquare2 className="h-2.5 w-2.5" /> View Profile
                    </Link>
                  </td>
                  <td><RiskBadge score={row.riskScore} /></td>
                  <td><PriorityBadge priority={row.priority} /></td>
                  <td><StatusBadge status={row.status} /></td>
                  <td className="text-[#6B7280]">{row.assignedTo}</td>
                  <td className="font-mono text-[#6B7280]">{row.lastUpdated}</td>
                  <td className="text-right">
                    <button
                      className="text-[11px] font-bold text-brand-red hover:text-[#b8000c] hover:underline inline-flex items-center gap-1 transition-colors tracking-wide"
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

