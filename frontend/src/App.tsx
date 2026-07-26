import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Layout } from '@/components/Layout'
import Dashboard from '@/pages/Dashboard'
import InvestigationQueue from '@/pages/InvestigationQueue'
import InvestigationWorkspace from '@/pages/InvestigationWorkspace'
import Customer360 from '@/pages/Customer360'
import PlannerPlayground from '@/pages/PlannerPlayground'
import Login from '@/pages/Login'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,      // Data stays fresh for 5 minutes
      gcTime: 30 * 60 * 1000,         // Cache stays alive for 30 minutes
      retry: 1,                        // Only retry once on failure
      refetchOnWindowFocus: false,     // Don't refetch when switching tabs
      refetchOnMount: false,           // Use cache if data exists
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="queue" element={<InvestigationQueue />} />
            <Route path="investigation/:id" element={<InvestigationWorkspace />} />
            <Route path="customer" element={<Customer360 />} />
            <Route path="customer/:id" element={<Customer360 />} />
            <Route path="playground" element={<PlannerPlayground />} />
          </Route>
        </Routes>
      </Router>
    </QueryClientProvider>
  )
}

export default App
