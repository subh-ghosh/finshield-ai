import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { LayoutDashboard, Briefcase, PlaySquare, LogOut, Settings, HelpCircle, Bell, X, ChevronRight, UserSquare2 } from 'lucide-react'

export function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const [showSettings, setShowSettings] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  
  const notifications = [
    { id: 1, text: 'C_2 flagged as Critical risk', time: '2 min ago', unread: true },
    { id: 2, text: 'SAR filing deadline approaching for C_1', time: '15 min ago', unread: true },
    { id: 2, text: 'SAR filing deadline approaching for C_1', time: '15 min ago', unread: true },
    { id: 3, text: 'Pipeline reprocessed 9,999 customers', time: '1 hr ago', unread: false },
  ]
  const unreadCount = notifications.filter(n => n.unread).length
  
  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Investigation Queue', path: '/queue', icon: Briefcase },
    { name: 'Customer 360', path: '/customer', icon: UserSquare2 },
    { name: 'Planner Playground', path: '/playground', icon: PlaySquare },
  ]

  const currentPage = navItems.find(n => location.pathname.startsWith(n.path))

  return (
    <div className="flex h-screen w-full overflow-hidden">
      {/* â”€â”€ Sidebar â”€â”€ */}
      <div className="w-[240px] bg-[#161A22] text-white flex flex-col flex-shrink-0 shadow-xl">
        {/* Logo */}
        <div className="px-6 pt-6 pb-5">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 relative flex-shrink-0">
              <div className="absolute top-0 left-0 w-[18px] h-[18px] bg-brand-red"></div>
              <div className="absolute top-0 right-0 w-[18px] h-[18px] bg-white"></div>
              <div className="absolute bottom-0 left-0 w-[18px] h-[18px] bg-white"></div>
              <div className="absolute bottom-0 right-0 w-[18px] h-[18px] bg-[#161A22] border border-white/20"></div>
            </div>
            <div className="leading-none">
              <div className="text-[11px] font-bold tracking-[0.15em] text-white/95">FINSHIELD</div>
              <div className="text-[11px] font-bold tracking-[0.15em] text-white/95">AI</div>
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
                {active && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-brand-red" />}
                <item.icon className="h-[16px] w-[16px] flex-shrink-0" />
                {item.name}
              </Link>
            )
          })}
        </nav>

        {/* Bottom */}
        <div className="border-t border-white/[0.08] px-3 py-2 space-y-0.5">
          <button
            onClick={() => setShowSettings(true)}
            className="flex items-center gap-3 px-4 py-2 text-[12px] text-white/40 hover:text-white/70 transition-colors w-full"
          >
            <Settings className="h-4 w-4" /> Settings
          </button>
          <button
            onClick={() => alert('FinShield AI Support\n\nFor technical issues contact:\nfinshield-support@FINSHIELDAI.com\nPhone: +1 800 FINSHIELD')}
            className="flex items-center gap-3 px-4 py-2 text-[12px] text-white/40 hover:text-white/70 transition-colors w-full"
          >
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
              <div className="text-[10px] text-white/35">Admin &bull; Paris</div>
            </div>
            <button onClick={() => navigate('/login')} className="text-white/25 hover:text-white/60 transition-colors">
              <LogOut className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* â”€â”€ Main â”€â”€ */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Red accent stripe */}
        <div className="h-[3px] bg-brand-red flex-shrink-0" />
        
        {/* Header bar */}
        <div className="h-[52px] bg-white border-b border-[#E4E7EC] flex items-center justify-between px-7 flex-shrink-0">
          <div className="flex items-center gap-4">
            <h1 className="text-[14px] font-bold tracking-wide text-brand-black">
              {currentPage?.name?.toUpperCase() || 'FINSHIELD AI'}
            </h1>
            <div className="h-4 w-px bg-[#E4E7EC]" />
            <span className="text-[11px] text-brand-gray">AML Investigation Platform</span>
          </div>
          <div className="flex items-center gap-5">
            {/* Bell with dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowNotifications(v => !v)}
                className="relative text-brand-gray hover:text-brand-black transition-colors"
              >
                <Bell className="h-4 w-4" />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 bg-brand-red rounded-full text-[9px] text-white font-bold flex items-center justify-center">
                    {unreadCount}
                  </span>
                )}
              </button>
              {showNotifications && (
                <div className="absolute right-0 top-8 z-50 w-[320px] bg-white border border-[#E4E7EC] shadow-xl">
                  <div className="flex items-center justify-between px-4 py-3 border-b border-[#E4E7EC]">
                    <span className="text-[12px] font-bold text-brand-black">Notifications</span>
                    <button onClick={() => setShowNotifications(false)}><X className="h-3.5 w-3.5 text-brand-gray" /></button>
                  </div>
                  <div className="divide-y divide-[#F3F4F6]">
                    {notifications.map(n => (
                      <div key={n.id} className={`px-4 py-3 flex items-start gap-3 hover:bg-[#F9FAFB] cursor-pointer ${n.unread ? 'bg-[#FAFBFF]' : ''}`}>
                        <div className={`w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 ${n.unread ? 'bg-brand-red' : 'bg-[#E4E7EC]'}`} />
                        <div className="flex-1 min-w-0">
                          <p className="text-[12px] text-brand-black leading-snug">{n.text}</p>
                          <p className="text-[10px] text-brand-gray mt-1">{n.time}</p>
                        </div>
                        <ChevronRight className="h-3.5 w-3.5 text-brand-gray flex-shrink-0 mt-0.5" />
                      </div>
                    ))}
                  </div>
                  <div className="px-4 py-2 border-t border-[#E4E7EC]">
                    <button className="text-[11px] text-brand-red hover:underline font-medium">Mark all as read</button>
                  </div>
                </div>
              )}
            </div>
            <div className="h-4 w-px bg-[#E4E7EC]" />
            <div className="flex items-center gap-2 text-[12px] text-[#6B7280]">
              <span>EN</span>
              <span className="text-[#E4E7EC]">|</span>
              <span className="font-semibold text-brand-black">FINSHIELD AI</span>
            </div>
          </div>
        </div>

        {/* Content */}
        <main className="flex-1 overflow-y-auto fs-page-bg">
          <Outlet />
        </main>
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/40" onClick={() => setShowSettings(false)} />
          <div className="relative bg-white w-[480px] shadow-2xl">
            <div className="flex items-center justify-between px-6 py-4 border-b border-[#E4E7EC]">
              <h2 className="text-[14px] font-bold text-brand-black tracking-wide">Platform Settings</h2>
              <button onClick={() => setShowSettings(false)}><X className="h-4 w-4 text-brand-gray hover:text-brand-black" /></button>
            </div>
            <div className="p-6 space-y-5">
              <div>
                <h3 className="text-[10px] font-bold text-brand-gray uppercase tracking-widest mb-3">Appearance</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between py-2 border-b border-[#F3F4F6]">
                    <span className="text-[13px] text-[#374151]">Theme</span>
                    <span className="text-[12px] font-semibold text-brand-black bg-[#F3F4F6] px-3 py-1">Light (FinShield Corporate)</span>
                  </div>
                  <div className="flex items-center justify-between py-2 border-b border-[#F3F4F6]">
                    <span className="text-[13px] text-[#374151]">Language</span>
                    <span className="text-[12px] font-semibold text-brand-black bg-[#F3F4F6] px-3 py-1">English (EN)</span>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="text-[10px] font-bold text-brand-gray uppercase tracking-widest mb-3">Pipeline</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between py-2 border-b border-[#F3F4F6]">
                    <span className="text-[13px] text-[#374151]">Backend API</span>
                    <span className="text-[12px] font-mono text-[#10B981]">http://localhost:8000 âœ“</span>
                  </div>
                  <div className="flex items-center justify-between py-2 border-b border-[#F3F4F6]">
                    <span className="text-[13px] text-[#374151]">Investigation Engine</span>
                    <span className="text-[12px] font-semibold text-brand-black">Deterministic v2.0</span>
                  </div>
                  <div className="flex items-center justify-between py-2 border-b border-[#F3F4F6]">
                    <span className="text-[13px] text-[#374151]">Dataset</span>
                    <span className="text-[12px] font-semibold text-brand-black">IBM AMLSim (9,999 customers)</span>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="text-[10px] font-bold text-brand-gray uppercase tracking-widest mb-3">Session</h3>
                <div className="flex items-center justify-between py-2 border-b border-[#F3F4F6]">
                  <span className="text-[13px] text-[#374151]">Analyst</span>
                  <span className="text-[12px] font-semibold text-brand-black">analyst@FINSHIELDAI.com</span>
                </div>
              </div>
            </div>
            <div className="px-6 py-4 border-t border-[#E4E7EC] flex justify-end gap-3">
              <button onClick={() => setShowSettings(false)} className="px-5 py-2 text-[12px] font-medium text-[#6B7280] border border-[#E4E7EC] hover:bg-[#F9FAFB] transition-colors">
                Close
              </button>
              <button onClick={() => setShowSettings(false)} className="px-5 py-2 text-[12px] font-bold bg-brand-red hover:bg-[#c5000d] text-white transition-colors">
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}


