import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Layout } from '@/components/Layout'
import Dashboard from '@/pages/Dashboard'
import InvestigationQueue from '@/pages/InvestigationQueue'
import InvestigationWorkspace from '@/pages/InvestigationWorkspace'
import Customer360 from '@/pages/Customer360'
import PlannerPlayground from '@/pages/PlannerPlayground'
import Login from '@/pages/Login'

const queryClient = new QueryClient()

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
            <Route path="customer/:id" element={<Customer360 />} />
            <Route path="playground" element={<PlannerPlayground />} />
          </Route>
        </Routes>
      </Router>
    </QueryClientProvider>
  )
}

export default App
