import { useParams, Link } from 'react-router-dom'
import { Building2, Globe, Calendar, Briefcase, ExternalLink } from 'lucide-react'
import { useCustomerDetails } from '../hooks'
import { StateView } from '../components/shared'

export default function Customer360() {
  const { id } = useParams()
  const { data: customer, isLoading, isError, error } = useCustomerDetails(id || '');

  return (
    <div className="p-6">
      <StateView isLoading={isLoading} isError={isError} error={error} isEmpty={!customer}>
        {customer && (
          <>
            {/* Header */}
            <div className="flex items-center justify-between mb-5">
              <div>
                <div className="flex items-center gap-3">
                  <h1 className="text-lg font-bold text-black">{customer.name}</h1>
                  <span className="text-[11px] font-bold bg-[#E1000F] text-white px-2 py-0.5">RISK: {customer.historical_risk?.toUpperCase()}</span>
                </div>
                <p className="text-[12px] text-gray-500 mt-1">Entity ID: {customer.id} • {customer.industry} • {customer.jurisdiction}</p>
              </div>
              <Link to={`/investigation/${id}`} className="text-[12px] font-semibold text-[#E1000F] hover:underline inline-flex items-center gap-1">
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
              </div>

              {/* Right side */}
              <div className="lg:col-span-2 space-y-4">
                {/* Connections */}
                <div className="bg-white border border-[#e3e3e3] p-5">
                  <h3 className="text-[11px] font-bold tracking-wider uppercase text-gray-500 mb-4 pb-2 border-b border-gray-200">Network Connections</h3>
                  <div className="space-y-2">
                    {customer.connections.map(conn => (
                      <div key={conn.id} className="flex items-center justify-between py-2.5 px-3 bg-[#f9f9f9] border border-gray-100">
                        <div>
                          <div className="text-[13px] font-medium text-black">{conn.name}</div>
                          <div className="text-[11px] text-gray-400">{conn.role} • {conn.id}</div>
                        </div>
                        <span className={`text-[11px] font-bold px-2 py-0.5 ${
                          conn.risk === 'High' ? 'bg-[#E1000F] text-white' : 'bg-gray-200 text-gray-600'
                        }`}>
                          {conn.risk.toUpperCase()}
                        </span>
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
                      </tr>
                    </thead>
                    <tbody>
                      {customer.recent_transactions.map((tx, idx) => (
                        <tr key={idx} className="border-b border-gray-50 hover:bg-[#fafafa]">
                          <td className="py-2.5 text-gray-600">{tx.date}</td>
                          <td className="py-2.5 text-black">{tx.type}</td>
                          <td className="py-2.5 text-black">{tx.party}</td>
                          <td className="py-2.5 text-right font-mono font-semibold text-black">{tx.amount}</td>
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
