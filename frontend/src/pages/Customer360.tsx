import { useParams } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Building2, Globe, Calendar, Link as LinkIcon, Briefcase } from 'lucide-react'

export default function Customer360() {
  const { id } = useParams()

  // Static mock for the hackathon
  const customer = {
    id,
    name: "Acme Corp Ltd",
    industry: "Import/Export",
    jurisdiction: "Cayman Islands",
    onboarded: "2023-01-15",
    status: "Active",
    risk_tier: "High",
    connections: [
      { id: "CUST-1042", name: "Global Traders Inc", role: "Shared Director", risk: "High" },
      { id: "CUST-5512", name: "Offshore Holdings", role: "Parent Company", risk: "Medium" }
    ],
    recent_transactions: [
      { date: "2026-07-24", amount: "$9,900.00", type: "Wire Transfer", status: "Completed", party: "Unknown Entity A" },
      { date: "2026-07-24", amount: "$9,950.00", type: "Wire Transfer", status: "Completed", party: "Unknown Entity B" },
      { date: "2026-07-23", amount: "$500,000.00", type: "Incoming Wire", status: "Completed", party: "Offshore Holdings" },
    ]
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row justify-between md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-primary">Customer 360</h1>
          <p className="text-muted-foreground mt-1">Holistic view of {customer.name} and its network.</p>
        </div>
        <Badge variant="destructive" className="text-sm px-4 py-1">Risk Tier: {customer.risk_tier}</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="glass-panel col-span-1">
          <CardHeader>
            <CardTitle>Profile Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3">
              <Building2 className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Entity Name</p>
                <p className="font-medium">{customer.name}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Briefcase className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Industry</p>
                <p className="font-medium">{customer.industry}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Globe className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Jurisdiction</p>
                <p className="font-medium">{customer.jurisdiction}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Calendar className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Onboarded</p>
                <p className="font-medium">{customer.onboarded}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="col-span-1 md:col-span-2 space-y-6">
          <Card className="glass-panel">
            <CardHeader>
              <CardTitle>Network Connections</CardTitle>
              <CardDescription>Known related entities and their risk tiers</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {customer.connections.map(conn => (
                  <div key={conn.id} className="flex items-center justify-between p-3 rounded-lg border border-border/50 bg-secondary/20">
                    <div className="flex items-center gap-3">
                      <LinkIcon className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="font-medium text-sm">{conn.name}</p>
                        <p className="text-xs text-muted-foreground">{conn.role} ({conn.id})</p>
                      </div>
                    </div>
                    <Badge variant={conn.risk === 'High' ? 'destructive' : 'secondary'}>{conn.risk}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="glass-panel">
            <CardHeader>
              <CardTitle>Recent Transactions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="w-full overflow-auto">
                <table className="w-full text-sm">
                  <thead className="border-b border-border/50 text-muted-foreground">
                    <tr>
                      <th className="pb-3 text-left font-medium">Date</th>
                      <th className="pb-3 text-left font-medium">Type</th>
                      <th className="pb-3 text-left font-medium">Counterparty</th>
                      <th className="pb-3 text-right font-medium">Amount</th>
                    </tr>
                  </thead>
                  <tbody className="[&_tr:last-child]:border-0">
                    {customer.recent_transactions.map((tx, idx) => (
                      <tr key={idx} className="border-b border-border/30">
                        <td className="py-3">{tx.date}</td>
                        <td className="py-3">{tx.type}</td>
                        <td className="py-3">{tx.party}</td>
                        <td className="py-3 text-right font-mono font-medium">{tx.amount}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
