import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { LayoutDashboard, UserCircle, Briefcase, PlaySquare, LogOut, Settings, HelpCircle, Bell, Search, ChevronDown } from 'lucide-react'

export function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  
  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Investigation Queue', path: '/queue', icon: Briefcase },
    { name: 'Planner Playground', path: '/playground', icon: PlaySquare },
  ]

  const currentPage = navItems.find(n => location.pathname.startsWith(n.path))

  return (
    <div className="flex h-screen w-full overflow-hidden">
      {/* ── Sidebar ── */}
      <div className="w-[240px] bg-[#161A22] text-white flex flex-col flex-shrink-0 shadow-xl">
        {/* Logo */}
        <div className="px-6 pt-6 pb-5">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 relative flex-shrink-0">
              <div className="absolute top-0 left-0 w-[18px] h-[18px] bg-[#E1000F]"></div>
              <div className="absolute top-0 right-0 w-[18px] h-[18px] bg-white"></div>
              <div className="absolute bottom-0 left-0 w-[18px] h-[18px] bg-white"></div>
              <div className="absolute bottom-0 right-0 w-[18px] h-[18px] bg-[#161A22] border border-white/20"></div>
            </div>
            <div className="leading-none">
              <div className="text-[11px] font-bold tracking-[0.15em] text-white/95">SOCIETE</div>
              <div className="text-[11px] font-bold tracking-[0.15em] text-white/95">GENERALE</div>
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-white/10">
            <span className="text-[10px] tracking-[0.2em] uppercase text-white/40 font-semibold">FinShield AI Platform</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 space-y-0.5 overflow-y-auto">
          <div className="px-3 mb-2">
            <span className="text-[9px] tracking-[0.2em] uppercase text-white/30 font-bold">Navigation</span>
          </div>
          {navItems.map((item) => {
            const active = location.pathname.startsWith(item.path)
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-2.5 text-[13px] transition-all relative group ${
                  active 
                    ? 'bg-white/[0.08] text-white font-semibold' 
                    : 'text-white/50 hover:text-white/80 hover:bg-white/[0.04]'
                }`}
              >
                {active && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-[#E1000F]" />}
                <item.icon className="h-[16px] w-[16px] flex-shrink-0" />
                {item.name}
              </Link>
            )
          })}
        </nav>

        {/* Bottom */}
        <div className="border-t border-white/[0.08] px-3 py-2 space-y-0.5">
          <button className="flex items-center gap-3 px-4 py-2 text-[12px] text-white/40 hover:text-white/70 transition-colors w-full">
            <Settings className="h-4 w-4" /> Settings
          </button>
          <button className="flex items-center gap-3 px-4 py-2 text-[12px] text-white/40 hover:text-white/70 transition-colors w-full">
            <HelpCircle className="h-4 w-4" /> Support
          </button>
        </div>

        {/* User */}
        <div className="px-4 py-4 border-t border-white/[0.08] bg-[#12151C]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#E1000F] to-[#8B0000] flex items-center justify-center flex-shrink-0 text-[11px] font-bold text-white">
              A1
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-[12px] font-semibold text-white/90 truncate">Analyst 01</div>
              <div className="text-[10px] text-white/35">Admin · Paris</div>
            </div>
            <button onClick={() => navigate('/login')} className="text-white/25 hover:text-white/60 transition-colors">
              <LogOut className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* ── Main ── */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Red accent stripe */}
        <div className="h-[3px] bg-[#E1000F] flex-shrink-0" />
        
        {/* Header bar */}
        <div className="h-[52px] bg-white border-b border-[#E4E7EC] flex items-center justify-between px-7 flex-shrink-0">
          <div className="flex items-center gap-4">
            <h1 className="text-[14px] font-bold tracking-wide text-[#1E1E1E]">
              {currentPage?.name?.toUpperCase() || 'FINSHIELD AI'}
            </h1>
            <div className="h-4 w-px bg-[#E4E7EC]" />
            <span className="text-[11px] text-[#9CA3AF]">AML Investigation Platform</span>
          </div>
          <div className="flex items-center gap-5">
            <button className="relative text-[#9CA3AF] hover:text-[#1E1E1E] transition-colors">
              <Bell className="h-4 w-4" />
              <span className="absolute -top-1 -right-1 w-2 h-2 bg-[#E1000F] rounded-full" />
            </button>
            <div className="h-4 w-px bg-[#E4E7EC]" />
            <div className="flex items-center gap-2 text-[12px] text-[#6B7280]">
              <span>EN</span>
              <span className="text-[#E4E7EC]">|</span>
              <span className="font-semibold text-[#1E1E1E]">Societe Generale</span>
            </div>
          </div>
        </div>

        {/* Content */}
        <main className="flex-1 overflow-y-auto sg-page-bg">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
