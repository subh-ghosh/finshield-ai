import { Outlet, Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, UserCircle, Briefcase, Activity, PlaySquare } from 'lucide-react'

export function Layout() {
  const location = useLocation()
  
  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Queue', path: '/queue', icon: Briefcase },
    { name: 'Planner Playground', path: '/playground', icon: PlaySquare },
  ]

  return (
    <div className="flex h-screen w-full bg-background overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 border-r border-border/40 bg-card/40 flex flex-col backdrop-blur-md">
        <div className="p-6 flex items-center gap-3">
          <Activity className="h-6 w-6 text-primary animate-pulse-glow" />
          <span className="font-bold text-xl tracking-tight text-primary">FinShield AI</span>
        </div>
        <nav className="flex-1 px-4 space-y-2 mt-4">
          {navItems.map((item) => {
            const active = location.pathname.startsWith(item.path)
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  active 
                    ? 'bg-primary/10 text-primary border border-primary/20 shadow-sm' 
                    : 'text-muted-foreground hover:bg-secondary/50 hover:text-foreground'
                }`}
              >
                <item.icon className={`h-4 w-4 ${active ? 'text-primary' : 'text-muted-foreground'}`} />
                {item.name}
              </Link>
            )
          })}
        </nav>
        <div className="p-4 border-t border-border/40">
          <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-secondary/30 border border-border/50">
            <UserCircle className="h-8 w-8 text-muted-foreground" />
            <div className="flex flex-col">
              <span className="text-sm font-medium">Analyst 01</span>
              <span className="text-xs text-muted-foreground">Admin</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <main className="flex-1 relative overflow-y-auto">
        {/* Subtle background glow effect */}
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-primary/5 blur-[120px] pointer-events-none" />
        <div className="relative z-10 min-h-full">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
