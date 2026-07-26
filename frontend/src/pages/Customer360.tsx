import { useParams, Link, useNavigate } from 'react-router-dom'
import { Building2, Globe, Calendar, Briefcase, ExternalLink, ArrowLeft, Search } from 'lucide-react'
import { useState } from 'react'
import { useCustomerDetails } from '../hooks'
import { StateView } from '../components/shared'

// Quick-access sample customers
const SAMPLE_CUSTOMERS = [
  { id: 'C_1', name: 'Acme Corp Ltd' },
  { id: 'C_2', name: 'Global Traders Inc' },
  { id: 'C_3', name: 'TechVentures LLC' },
  { id: 'C_4', name: 'Nexus Dynamics' },
  { id: 'C_5', name: 'Pacific Holdings' },
]

export default function Customer360() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [searchInput, setSearchInput] = useState('')
  const { data: customer, isLoading, isError, error } = useCustomerDetails(id || '')

  // No ID — show customer selector landing
  if (!id) {
    return (
      <div className="p-7 max-w-2xl mx-auto">
        <h1 className="text-[18px] font-bold text-brand-black mb-1">Customer 360 View</h1>
        <p className="text-[12px] text-brand-gray mb-6">Search for a customer or select from recent investigations</p>

        {/* Search */}
        <div className="relative mb-6">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-brand-gray" />
          <input
            type="text"
            value={searchInput}
            onChange={e => setSearchInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && searchInput.trim()) navigate(`/customer/${searchInput.trim()}`) }}
            placeholder="Enter Customer ID (e.g. C_1) and press Enter..."
            className="w-full pl-11 pr-4 py-3 bg-white border border-[#E4E7EC] text-[13px] text-brand-black placeholder:text-brand-gray focus:outline-none focus:border-brand-red/40 focus:shadow-[0_0_0_3px_rgba(225,0,15,0.06)] transition-all"
          />
        </div>

        {/* Quick access */}
        <h3 className="text-[10px] font-bold text-brand-gray uppercase tracking-widest mb-3">Recent Investigations</h3>
        <div className="space-y-2">
          {SAMPLE_CUSTOMERS.map(c => (
            <button
              key={c.id}
              onClick={() => navigate(`/customer/${c.id}`)}
              className="w-full flex items-center justify-between p-4 bg-white border border-[#E4E7EC] hover:border-brand-red/30 hover:bg-[#FAFBFF] transition-all text-left group"
            >
              <div>
                <div className="text-[13px] font-semibold text-brand-black">{c.name}</div>
                <div className="text-[11px] font-mono text-brand-gray mt-0.5">{c.id}</div>
              </div>
              <ExternalLink className="h-4 w-4 text-brand-gray group-hover:text-brand-red transition-colors" />
            </button>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* Back link */}
      <div className="mb-4">
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-1.5 text-[12px] font-semibold text-[#6B7280] hover:text-brand-black transition-colors"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Back
        </button>
      </div>

      <StateView isLoading={isLoading} isError={isError} error={error} isEmpty={!customer}>
        {customer && (
          <>
            {/* Header */}
            <div className="flex items-center justify-between mb-5">
              <div>
                <div className="flex items-center gap-3">
                  <h1 className="text-lg font-bold text-black">{customer.name}</h1>
                  <span className="text-[11px] font-bold bg-brand-red text-white px-2 py-0.5">RISK: {customer.historical_risk?.toUpperCase()}</span>
                </div>
                <p className="text-[12px] text-gray-500 mt-1">Entity ID: {customer.id} • {customer.industry} • {customer.jurisdiction}</p>
              </div>
              <Link to={`/investigation/${id}`} className="text-[12px] font-semibold text-brand-red hover:underline inline-flex items-center gap-1">
                OPEN INVESTIGATION <ExternalLink className="h-3 w-3" />
              </Link>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {/* Profile Card */}
              <div className="bg-white border border-[#e3e3e3] p-5">
                <h3 className="text-[11px] font-bold tracking-wider uppercase text-gray-500 mb-4 pb-2 border-b border-gray-200">Profile Details</h3>
                <div className="space-y-4">
                  {[
                    { icon: Building2, label: 'Entity Name', val: customer.name },
                    { icon: Briefcase, label: 'Industry', val: customer.industry },
                    { icon: Globe, label: 'Jurisdiction', val: customer.jurisdiction },
                    { icon: Calendar, label: 'Onboarded', val: customer.onboarding_date },
                  ].map((item, i) => (
                    <div key={i} className="flex items-start gap-3">
                      <item.icon className="h-4 w-4 text-gray-400 mt-0.5 flex-shrink-0" />
                      <div>
                        <div className="text-[11px] text-gray-400 uppercase tracking-wide">{item.label}</div>
                        <div className="text-[13px] font-medium text-black">{item.val}</div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* KYC Status */}
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] text-gray-400 uppercase tracking-wide">KYC Status</span>
                    <span className={`text-[11px] font-bold px-2 py-0.5 ${
                      customer.kyc_status === 'Active' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                    }`}>{customer.kyc_status}</span>
                  </div>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-[11px] text-gray-400 uppercase tracking-wide">Risk Score</span>
                    <span className="text-[16px] font-bold text-brand-red">{customer.risk_score}</span>
                  </div>
                </div>
              </div>

              {/* Right side */}
              <div className="lg:col-span-2 space-y-4">
                {/* Connections */}
                <div className="bg-white border border-[#e3e3e3] p-5">
                  <h3 className="text-[11px] font-bold tracking-wider uppercase text-gray-500 mb-4 pb-2 border-b border-gray-200">Network Connections</h3>
                  <div className="space-y-2">
                    {customer.connections.map(conn => (
                      <div key={conn.id} className="flex items-center justify-between py-2.5 px-3 bg-[#f9f9f9] border border-gray-100 hover:border-brand-red/20 transition-colors group">
                        <div>
                          <div className="text-[13px] font-medium text-black">{conn.name}</div>
                          <div className="text-[11px] text-gray-400">{conn.role} • {conn.id}</div>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className={`text-[11px] font-bold px-2 py-0.5 ${
                            conn.risk === 'High' ? 'bg-brand-red text-white' : 'bg-gray-200 text-gray-600'
                          }`}>
                            {conn.risk.toUpperCase()}
                          </span>
                          <Link to={`/customer/${conn.id}`} className="text-brand-gray hover:text-brand-red transition-colors opacity-0 group-hover:opacity-100">
                            <ExternalLink className="h-3.5 w-3.5" />
                          </Link>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Transactions */}
                <div className="bg-white border border-[#e3e3e3] p-5">
                  <h3 className="text-[11px] font-bold tracking-wider uppercase text-gray-500 mb-4 pb-2 border-b border-gray-200">Recent Transactions</h3>
                  <table className="w-full text-[13px]">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left pb-2 text-[11px] font-bold tracking-wider uppercase text-gray-400">Date</th>
                        <th className="text-left pb-2 text-[11px] font-bold tracking-wider uppercase text-gray-400">Type</th>
                        <th className="text-left pb-2 text-[11px] font-bold tracking-wider uppercase text-gray-400">Counterparty</th>
                        <th className="text-right pb-2 text-[11px] font-bold tracking-wider uppercase text-gray-400">Amount</th>
                        <th className="text-right pb-2 text-[11px] font-bold tracking-wider uppercase text-gray-400">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {customer.recent_transactions.map((tx, idx) => (
                        <tr key={idx} className="border-b border-gray-50 hover:bg-[#fafafa]">
                          <td className="py-2.5 text-gray-600">{tx.date}</td>
                          <td className="py-2.5 text-black">{tx.type}</td>
                          <td className="py-2.5 text-black">{tx.party}</td>
                          <td className="py-2.5 text-right font-mono font-semibold text-black">{tx.amount}</td>
                          <td className="py-2.5 text-right">
                            <span className={`text-[10px] font-bold px-2 py-0.5 ${
                              tx.status === 'completed' ? 'bg-green-100 text-green-700' :
                              tx.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                              tx.status === 'flagged' ? 'bg-red-100 text-red-700' :
                              'bg-gray-100 text-gray-600'
                            }`}>{tx.status}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </>
        )}
      </StateView>
    </div>
  )
}
