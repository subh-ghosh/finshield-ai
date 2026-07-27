import { StateView } from '../components/shared';
import { useSystemMetrics, useWatchlist } from '../hooks/useSystemAdmin';
import { Server, Activity, Clock, ShieldAlert, CheckCircle2 } from 'lucide-react';

export default function SystemAdmin() {
  const { data: metrics, isLoading: isMetricsLoading, error: metricsError } = useSystemMetrics();
  const { data: watchlist, isLoading: isWatchlistLoading, error: watchlistError } = useWatchlist();

  const isLoading = isMetricsLoading || isWatchlistLoading;
  const error = metricsError || watchlistError;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-brand-black">System Administration & Monitoring</h1>
          <p className="text-sm text-brand-gray mt-1">Backend pipeline performance metrics and active monitoring watchlist.</p>
        </div>
      </div>

      <StateView isLoading={isLoading} error={error ? new Error('Failed to load system data') : null}>
        {metrics && (
          <>
            {/* Top Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white p-5 border border-gray-200">
                <div className="flex items-center gap-3 mb-2">
                  <div className="bg-green-50 p-2 rounded-lg">
                    <Server className="h-5 w-5 text-green-600" />
                  </div>
                  <div className="text-sm font-medium text-gray-500">Pipeline Status</div>
                </div>
                <div className="text-xl font-bold text-gray-900 flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-500" /> Operational
                </div>
              </div>

              <div className="bg-white p-5 border border-gray-200">
                <div className="flex items-center gap-3 mb-2">
                  <div className="bg-blue-50 p-2 rounded-lg">
                    <Activity className="h-5 w-5 text-blue-600" />
                  </div>
                  <div className="text-sm font-medium text-gray-500">Total Processed Rows</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">{metrics.total_rows.toLocaleString()}</div>
                <div className="text-xs text-gray-500 mt-1">{metrics.clean_rows.toLocaleString()} clean rows</div>
              </div>

              <div className="bg-white p-5 border border-gray-200">
                <div className="flex items-center gap-3 mb-2">
                  <div className="bg-purple-50 p-2 rounded-lg">
                    <Clock className="h-5 w-5 text-purple-600" />
                  </div>
                  <div className="text-sm font-medium text-gray-500">Execution Time</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">{metrics.execution_time_seconds.toFixed(2)}s</div>
                <div className="text-xs text-gray-500 mt-1">Full pipeline run</div>
              </div>

              <div className="bg-white p-5 border border-gray-200">
                <div className="flex items-center gap-3 mb-2">
                  <div className="bg-red-50 p-2 rounded-lg">
                    <ShieldAlert className="h-5 w-5 text-red-600" />
                  </div>
                  <div className="text-sm font-medium text-gray-500">Flagged Rules</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">{metrics.flagged_rules_count.toLocaleString()}</div>
                <div className="text-xs text-gray-500 mt-1">Detections</div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* Pipeline Timings */}
              <div className="bg-white p-6 border border-gray-200">
                <h3 className="text-sm font-bold uppercase tracking-wider text-gray-500 mb-6">Pipeline Stage Profiling</h3>
                <div className="space-y-4">
                  {Object.entries(metrics.timings).map(([stage, timeSecs]) => {
                    const pct = (timeSecs / metrics.execution_time_seconds) * 100;
                    return (
                      <div key={stage}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="font-medium text-gray-700 capitalize">{stage.replace(/_/g, ' ')}</span>
                          <span className="text-gray-500 font-mono">{timeSecs.toFixed(3)}s</span>
                        </div>
                        <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-blue-500"
                            style={{ width: `${Math.max(pct, 1)}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Monitoring Watchlist */}
              <div className="bg-white p-6 border border-gray-200 flex flex-col">
                <h3 className="text-sm font-bold uppercase tracking-wider text-gray-500 mb-6">Active Monitoring Watchlist</h3>
                <div className="flex-1 overflow-auto">
                  {watchlist && Object.keys(watchlist).length > 0 ? (
                    <div className="space-y-3">
                      {Object.values(watchlist).map((item) => (
                        <div key={item.customer_id} className="p-3 border border-gray-100 bg-gray-50 rounded-sm">
                          <div className="flex justify-between items-start mb-1">
                            <span className="font-bold text-brand-black">{item.customer_id}</span>
                            <span className="text-[10px] uppercase font-bold bg-red-100 text-red-700 px-2 py-0.5 rounded-sm">
                              {item.priority}
                            </span>
                          </div>
                          <div className="text-xs text-gray-600 mb-2">{item.reason}</div>
                          <div className="text-[10px] text-gray-400">Added: {new Date(item.added_at).toLocaleString()}</div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="h-full flex items-center justify-center text-sm text-gray-500">
                      No customers currently on the watchlist.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </>
        )}
      </StateView>
    </div>
  );
}
