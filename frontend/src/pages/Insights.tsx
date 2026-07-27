import { StateView } from '../components/shared';
import { useEdaSummary } from '../hooks/useEdaSummary';
import { AlertTriangle, Users, Target, Activity } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Insights() {
  const { data: summary, isLoading, error } = useEdaSummary();

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-brand-black">Global Dataset Insights</h1>
          <p className="text-sm text-brand-gray mt-1">Exploratory Data Analysis across all processed transactions.</p>
        </div>
      </div>

      <StateView isLoading={isLoading} error={error ? new Error('Failed to load EDA summary') : null}>
        {summary && (
          <>
            {/* Top Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white p-5 border border-gray-200">
                <div className="flex items-center gap-3 mb-2">
                  <div className="bg-blue-50 p-2 rounded-lg">
                    <Activity className="h-5 w-5 text-blue-600" />
                  </div>
                  <div className="text-sm font-medium text-gray-500">Total Transactions</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">{summary.dataset_summary.total_transactions.toLocaleString()}</div>
              </div>

              <div className="bg-white p-5 border border-gray-200">
                <div className="flex items-center gap-3 mb-2">
                  <div className="bg-purple-50 p-2 rounded-lg">
                    <Users className="h-5 w-5 text-purple-600" />
                  </div>
                  <div className="text-sm font-medium text-gray-500">Total Customers</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">{summary.dataset_summary.total_customers.toLocaleString()}</div>
              </div>

              <div className="bg-white p-5 border border-gray-200">
                <div className="flex items-center gap-3 mb-2">
                  <div className="bg-red-50 p-2 rounded-lg">
                    <AlertTriangle className="h-5 w-5 text-red-600" />
                  </div>
                  <div className="text-sm font-medium text-gray-500">Fraud Rate</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">{summary.dataset_summary.fraud_rate_pct}%</div>
                <div className="text-xs text-gray-500 mt-1">{summary.dataset_summary.fraud_transactions.toLocaleString()} txs</div>
              </div>

              <div className="bg-white p-5 border border-gray-200">
                <div className="flex items-center gap-3 mb-2">
                  <div className="bg-orange-50 p-2 rounded-lg">
                    <Target className="h-5 w-5 text-orange-600" />
                  </div>
                  <div className="text-sm font-medium text-gray-500">Anomaly Flags</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">{summary.anomaly_detection.isolation_forest_flagged.toLocaleString()}</div>
                <div className="text-xs text-gray-500 mt-1">IForest Detections</div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* Risk Distribution */}
              <div className="bg-white p-6 border border-gray-200">
                <h3 className="text-sm font-bold uppercase tracking-wider text-gray-500 mb-6">Risk Distribution</h3>
                <div className="space-y-4">
                  {Object.entries(summary.risk_distribution).map(([label, count]) => {
                    const pct = (count / summary.dataset_summary.total_customers) * 100;
                    return (
                      <div key={label}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="font-medium text-gray-700">{label}</span>
                          <span className="text-gray-500">{count.toLocaleString()}</span>
                        </div>
                        <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                          <div 
                            className={`h-full ${label.includes('CRITICAL') ? 'bg-red-500' : label.includes('HIGH') ? 'bg-orange-400' : label.includes('MEDIUM') ? 'bg-yellow-400' : 'bg-green-500'}`}
                            style={{ width: `${Math.max(pct, 1)}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Amount Statistics */}
              <div className="bg-white p-6 border border-gray-200">
                <h3 className="text-sm font-bold uppercase tracking-wider text-gray-500 mb-6">Amount Statistics (USD)</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-gray-50 border border-gray-100">
                    <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Average</div>
                    <div className="text-xl font-mono text-gray-900">${summary.amount_statistics_usd.mean.toLocaleString(undefined, {maximumFractionDigits: 2})}</div>
                  </div>
                  <div className="p-4 bg-gray-50 border border-gray-100">
                    <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Median</div>
                    <div className="text-xl font-mono text-gray-900">${summary.amount_statistics_usd.median.toLocaleString(undefined, {maximumFractionDigits: 2})}</div>
                  </div>
                  <div className="p-4 bg-gray-50 border border-gray-100">
                    <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">95th Percentile</div>
                    <div className="text-xl font-mono text-gray-900">${summary.amount_statistics_usd.p95.toLocaleString(undefined, {maximumFractionDigits: 2})}</div>
                  </div>
                  <div className="p-4 bg-gray-50 border border-gray-100">
                    <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">99th Percentile</div>
                    <div className="text-xl font-mono text-red-600 font-bold">${summary.amount_statistics_usd.p99.toLocaleString(undefined, {maximumFractionDigits: 2})}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Top 10 Riskiest */}
            <div className="bg-white p-6 border border-gray-200">
              <h3 className="text-sm font-bold uppercase tracking-wider text-gray-500 mb-6">Top 10 High-Risk Customers</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs text-gray-500 uppercase bg-gray-50 border-y border-gray-200">
                    <tr>
                      <th className="px-4 py-3">Customer ID</th>
                      <th className="px-4 py-3">Severity</th>
                      <th className="px-4 py-3">Risk Score</th>
                      <th className="px-4 py-3">Recommendation</th>
                      <th className="px-4 py-3 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {summary.top_10_risky_customers.map((c) => (
                      <tr key={c.customer_id} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="px-4 py-3 font-medium text-gray-900">{c.customer_id}</td>
                        <td className="px-4 py-3">
                          <span className="px-2 py-1 text-[10px] font-bold uppercase bg-red-100 text-red-700">{c.severity}</span>
                        </td>
                        <td className="px-4 py-3 font-mono font-bold text-red-600">{c.risk_score}</td>
                        <td className="px-4 py-3 text-gray-600">{c.recommendation.replace(/_/g, ' ')}</td>
                        <td className="px-4 py-3 text-right">
                          <Link to={`/investigation/${c.customer_id}`} className="text-brand-red hover:underline font-medium text-xs">
                            INVESTIGATE
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </StateView>
    </div>
  );
}
