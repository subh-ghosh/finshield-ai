import { useState, useEffect } from 'react'
import { Activity, AlertTriangle, Users, FileCheck, TrendingUp, TrendingDown, ArrowUpRight, Clock, RefreshCw } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell, Area, AreaChart } from 'recharts'
import { useDashboardData } from '../hooks'
import { StateView, CardSkeleton } from '../components/shared'

export default function Dashboard() {
  const { data, isLoading, isError, error, refetch, isFetching } = useDashboardData();
  const [lastUpdated, setLastUpdated] = useState(new Date())

  useEffect(() => {
    setLastUpdated(new Date())
  }, [data])
  
  const stats = data?.metrics;
  const riskDistribution = data?.riskDistribution;
  const anomalyTrend = data?.anomalyTrend;

  const statCards = [
    { label: 'Active Investigations', value: stats?.activeInvestigations || 0, change: '+12%', trend: 'up', icon: Activity, color: '#E1000F' },
    { label: 'High Risk Entities', value: stats?.highRiskEntities || 0, change: '+4 today', trend: 'up', icon: AlertTriangle, color: '#EF4444' },
    { label: 'New Alerts', value: stats?.newAlerts || 0, change: 'Immediate triage', trend: 'neutral', icon: Users, color: '#F59E0B' },
    { label: 'Pending Reviews', value: stats?.pendingReviews || 0, change: '-5 from yesterday', trend: 'down', icon: FileCheck, color: '#10B981' },
  ];

  return (
    <div className="p-7 space-y-6">
      {/* Status bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Clock className="h-3.5 w-3.5 text-[#9CA3AF]" />
          <span className="text-[11px] text-[#9CA3AF]">
            Last updated: {lastUpdated.toLocaleTimeString()} · Auto-refresh: 30s
          </span>
          {isFetching && (
            <span className="text-[10px] font-bold text-[#E1000F] animate-pulse">REFRESHING...</span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="h-7 px-3 text-[11px] font-medium text-[#6B7280] border border-[#E4E7EC] bg-white hover:bg-[#F9FAFB] disabled:opacity-40 transition-colors flex items-center gap-1.5"
          >
            <RefreshCw className={`h-3 w-3 ${isFetching ? 'animate-spin' : ''}`} /> Refresh
          </button>
          <span className="inline-flex items-center gap-1.5 text-[11px] font-medium text-[#10B981]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse" />
            All Systems Operational
          </span>
        </div>
      </div>

      <StateView 
        isLoading={isLoading} 
        isError={isError} 
        error={error}
        loadingComponent={
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">
            {[1,2,3,4].map(i => <CardSkeleton key={i} />)}
          </div>
        }
      >
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">
          {statCards.map((stat, i) => (
            <div key={i} className="sg-stat-card group cursor-default">
              <div className="flex items-center justify-between mb-4">
                <span className="sg-section-label">{stat.label}</span>
                <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ background: `${stat.color}10` }}>
                  <stat.icon className="h-4 w-4" style={{ color: stat.color }} />
                </div>
              </div>
              <div className="text-[36px] font-bold text-[#1E1E1E] leading-none tracking-tight">{stat.value}</div>
              <div className="flex items-center gap-1.5 mt-3 pt-3 border-t border-[#F0F1F3]">
                {stat.trend === 'up' && <TrendingUp className="h-3 w-3 text-[#E1000F]" />}
                {stat.trend === 'down' && <TrendingDown className="h-3 w-3 text-[#10B981]" />}
                {stat.trend === 'neutral' && <ArrowUpRight className="h-3 w-3 text-[#F59E0B]" />}
                <span className="text-[11px] text-[#9CA3AF]">{stat.change}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-5 mt-6">
          {/* Risk Distribution */}
          <div className="sg-panel p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-[13px] font-bold text-[#1E1E1E]">Risk Distribution</h3>
                <p className="text-[11px] text-[#9CA3AF] mt-0.5">Entity risk breakdown – current period</p>
              </div>
              <span className="sg-section-label">Current Period</span>
            </div>
            <div className="h-[260px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={riskDistribution} barCategoryGap="30%">
                  <CartesianGrid strokeDasharray="3 3" stroke="#F0F1F3" vertical={false} />
                  <XAxis dataKey="name" stroke="#9CA3AF" fontSize={11} tickLine={false} axisLine={{ stroke: '#E4E7EC' }} />
                  <YAxis stroke="#9CA3AF" fontSize={11} tickLine={false} axisLine={false} />
                  <Tooltip 
                    cursor={{fill: 'rgba(0,0,0,0.02)'}} 
                    contentStyle={{ background: '#fff', border: '1px solid #E4E7EC', borderRadius: 0, fontSize: 12, boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }} 
                  />
                  <Bar dataKey="value" radius={[2, 2, 0, 0]}>
                    {riskDistribution?.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Anomaly Trend */}
          <div className="sg-panel p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-[13px] font-bold text-[#1E1E1E]">Isolation Forest Anomaly Trend</h3>
                <p className="text-[11px] text-[#9CA3AF] mt-0.5">24-hour anomaly detection feed</p>
              </div>
              <span className="inline-flex items-center gap-1.5 text-[11px] font-medium text-[#E1000F]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#E1000F] animate-pulse" />
                Live Feed
              </span>
            </div>
            <div className="h-[260px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={anomalyTrend}>
                  <defs>
                    <linearGradient id="anomalyGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#E1000F" stopOpacity={0.1}/>
                      <stop offset="95%" stopColor="#E1000F" stopOpacity={0.01}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F0F1F3" vertical={false} />
                  <XAxis dataKey="time" stroke="#9CA3AF" fontSize={11} tickLine={false} axisLine={{ stroke: '#E4E7EC' }} />
                  <YAxis stroke="#9CA3AF" fontSize={11} tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={{ background: '#fff', border: '1px solid #E4E7EC', borderRadius: 0, fontSize: 12, boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }} />
                  <Area type="monotone" dataKey="score" stroke="#E1000F" strokeWidth={2} fill="url(#anomalyGradient)" dot={{ r: 3, fill: "#E1000F", strokeWidth: 0 }} activeDot={{ r: 5, fill: "#E1000F", stroke: "#fff", strokeWidth: 2 }} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </StateView>
    </div>
  )
}
