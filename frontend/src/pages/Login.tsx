import { useNavigate } from 'react-router-dom'

export default function Login() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen w-full flex bg-gradient-to-br from-[#dce6f0] via-[#e8eef4] to-[#f0f4f8]">
      {/* Left Branding Panel */}
      <div className="hidden lg:flex w-[45%] flex-col justify-between p-12 relative">
        {/* SG Logo */}
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 relative">
            <div className="absolute top-0 left-0 w-6 h-6 bg-brand-red"></div>
            <div className="absolute top-0 right-0 w-6 h-6 bg-black"></div>
            <div className="absolute bottom-0 left-0 w-6 h-6 bg-black"></div>
            <div className="absolute bottom-0 right-0 w-6 h-6 bg-white border border-gray-300"></div>
          </div>
          <div className="leading-tight">
            <div className="text-[15px] font-bold tracking-[0.08em] text-black">FINSHIELD</div>
            <div className="text-[15px] font-bold tracking-[0.08em] text-black">AI</div>
          </div>
        </div>

        {/* Branding text */}
        <div className="max-w-md">
          <h2 className="text-[42px] font-bold leading-[1.1] text-black tracking-tight">
            Discover more on<br/>FinShield AI
          </h2>
          <div className="mt-8">
            <button className="border border-gray-400 px-8 py-3 text-sm font-medium text-gray-700 hover:bg-white/50 transition-colors tracking-wide">
              Discover more
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="text-xs text-gray-500">
          Â© FINSHIELD AI Group {new Date().getFullYear()}
        </div>
      </div>

      {/* Right Login Panel */}
      <div className="w-full lg:w-[55%] flex items-center justify-center bg-white p-8 relative">
        {/* Top utility bar */}
        <div className="absolute top-6 right-8 flex items-center gap-4 text-sm text-gray-500">
          <span className="cursor-pointer hover:text-black">â“˜</span>
          <span className="cursor-pointer hover:text-black">âŠž</span>
          <span className="cursor-pointer hover:text-black">ðŸŒ EN â–¾</span>
        </div>

        <div className="w-full max-w-[440px]">
          {/* Mobile logo */}
          <div className="flex lg:hidden items-center gap-3 mb-10">
            <div className="w-10 h-10 relative">
              <div className="absolute top-0 left-0 w-5 h-5 bg-brand-red"></div>
              <div className="absolute top-0 right-0 w-5 h-5 bg-black"></div>
              <div className="absolute bottom-0 left-0 w-5 h-5 bg-black"></div>
              <div className="absolute bottom-0 right-0 w-5 h-5 bg-white border border-gray-300"></div>
            </div>
            <div className="leading-tight">
              <div className="text-xs font-bold tracking-[0.08em]">FINSHIELD</div>
              <div className="text-xs font-bold tracking-[0.08em]">AI</div>
            </div>
          </div>

          <h1 className="text-[32px] font-bold text-black mb-10">
            Sign in to FinShield AI
          </h1>

          <div className="space-y-4">
            <input 
              type="email" 
              placeholder="Email" 
              className="w-full bg-[#e8e8e8] px-4 py-3.5 text-sm text-black placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#E1000F]/30 border-none"
              defaultValue="analyst@FINSHIELDAI.com"
            />
            <input 
              type="password" 
              placeholder="Password" 
              className="w-full bg-[#e8e8e8] px-4 py-3.5 text-sm text-black placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#E1000F]/30 border-none"
              defaultValue="password"
            />
          </div>

          <div className="flex items-center justify-between mt-4 text-sm">
            <span className="text-gray-600 cursor-pointer hover:text-black">Forgot your password?</span>
            <label className="flex items-center gap-2 text-gray-600">
              <span>Remember my login email</span>
              <input type="checkbox" className="w-4 h-4 accent-[#E1000F]" />
            </label>
          </div>

          <button 
            onClick={() => navigate('/dashboard')}
            className="w-full mt-8 bg-brand-red hover:bg-[#c5000d] text-white font-semibold py-3.5 text-sm tracking-wide transition-colors shadow-sm"
          >
            Sign in
          </button>

          <div className="mt-6 space-y-1">
            <p className="text-sm text-gray-600 cursor-pointer hover:text-black hover:underline">Request access to FinShield AI</p>
            <p className="text-sm text-gray-600 cursor-pointer hover:text-black hover:underline">Notice to US persons</p>
          </div>
        </div>
      </div>
    </div>
  )
}

