import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ArrowRight, Filter, Search } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'

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
          {
            id: "CUST-8392",
            name: "Acme Corp Ltd",
            risk_score: 92,
            priority: "Critical",
            status: "Open",
            assigned_analyst: "Unassigned",
            recent_transactions: 145
          },
          {
            id: "CUST-1042",
            name: "Global Traders Inc",
            risk_score: 85,
            priority: "High",
            status: "In Progress",
            assigned_analyst: "Sarah Jenkins",
            recent_transactions: 89
          },
        ]
      }
    }
  })

  const getRiskBadge = (score: number) => {
    if (score >= 90) return <Badge variant="destructive">Critical ({score})</Badge>
    if (score >= 75) return <Badge variant="warning">High ({score})</Badge>
    if (score >= 50) return <Badge variant="secondary">Medium ({score})</Badge>
    return <Badge variant="success">Low ({score})</Badge>
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-primary">Investigation Queue</h1>
          <p className="text-muted-foreground">Prioritized list of alerts from the Rule Engine and Hybrid Risk Model.</p>
        </div>
        <div className="flex gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search entity..." 
              className="pl-9 h-10 w-[200px] rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
          </div>
          <Button variant="outline"><Filter className="h-4 w-4 mr-2" /> Filter</Button>
        </div>
      </div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Card className="glass-panel">
          <CardContent className="p-0">
            <div className="w-full overflow-auto">
              <table className="w-full caption-bottom text-sm">
                <thead className="[&_tr]:border-b border-border/50 bg-secondary/20">
                  <tr className="border-b transition-colors data-[state=selected]:bg-muted">
                    <th className="h-12 px-6 text-left align-middle font-medium text-muted-foreground">ID</th>
                    <th className="h-12 px-6 text-left align-middle font-medium text-muted-foreground">Entity Name</th>
                    <th className="h-12 px-6 text-left align-middle font-medium text-muted-foreground">Risk Score</th>
                    <th className="h-12 px-6 text-left align-middle font-medium text-muted-foreground">Status</th>
                    <th className="h-12 px-6 text-left align-middle font-medium text-muted-foreground">Analyst</th>
                    <th className="h-12 px-6 text-right align-middle font-medium text-muted-foreground">Action</th>
                  </tr>
                </thead>
                <tbody className="[&_tr:last-child]:border-0">
                  {isLoading ? (
                    <tr>
                      <td colSpan={6} className="p-8 text-center text-muted-foreground">Loading queue...</td>
                    </tr>
                  ) : queue?.map((row: any) => (
                    <tr key={row.id} className="border-b border-border/30 transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                      <td className="p-6 align-middle font-medium">{row.id}</td>
                      <td className="p-6 align-middle">{row.name}</td>
                      <td className="p-6 align-middle">{getRiskBadge(row.risk_score)}</td>
                      <td className="p-6 align-middle">
                        <Badge variant="outline">{row.status}</Badge>
                      </td>
                      <td className="p-6 align-middle text-muted-foreground">{row.assigned_analyst}</td>
                      <td className="p-6 align-middle text-right">
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => navigate(`/investigation/${row.id}`)}
                        >
                          Investigate <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
