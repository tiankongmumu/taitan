import type { Metadata } from "next";
import "./globals.css";
import { ClerkProvider, SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs'
import { CyberGridBackground } from '@/components/ui/CyberGridBackground'
import { Inter, Outfit } from 'next/font/google'
import { MobileMenu } from '@/components/ui/MobileMenu'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const outfit = Outfit({ subsets: ['latin'], variable: '--font-outfit' })

export const metadata: Metadata = {
  title: "ShipMicro — AI效率工具平台 | 证件照·关税查询·开发者工具",
  description: "AI证件照制作、HS关税秒查、15+开发者工具、小游戏、科技资讯。好用的效率工具合集。",
  openGraph: {
    title: "ShipMicro — AI效率工具平台",
    description: "证件照制作、关税查询、15+开发者工具。打开就能用，好用不贵。",
    siteName: "ShipMicro",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "ShipMicro — AI效率工具平台",
    description: "证件照制作、关税查询、15+开发者工具。打开就能用。",
  },
};

const NAV_LINKS = [
  { href: "/#products", label: "产品", emoji: "🔥" },
  { href: "/tools", label: "工具", emoji: "⚡" },
  { href: "/arcade", label: "游戏", emoji: "🎮" },
  { href: "/news", label: "资讯", emoji: "📰" },
  { href: "/ideas", label: "灵感", emoji: "💡" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="zh-CN" className={`${inter.variable} ${outfit.variable} dark`}>
        <head>
          <meta name='impact-site-verification' content='f0db7f0c-4f86-40c1-9dc4-425278280eb5' />
          <meta name='viewport' content='width=device-width, initial-scale=1.0, viewport-fit=cover' />
          <link rel="icon" href="/favicon.ico" />
        </head>
        <body className="bg-[#060918] text-white antialiased font-sans noise">
          <CyberGridBackground />

          {/* ═══ Premium Nav ═══ */}
          <nav className="sticky top-0 z-50 border-b border-white/[0.05]" style={{
            background: "linear-gradient(180deg, rgba(6,9,24,0.95) 0%, rgba(6,9,24,0.85) 100%)",
            backdropFilter: "blur(20px) saturate(180%)",
            WebkitBackdropFilter: "blur(20px) saturate(180%)",
          }}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 sm:h-16 flex items-center justify-between">
              {/* Logo */}
              <a href="/" className="flex items-center gap-2 sm:gap-2.5 shrink-0 group">
                <div className="relative">
                  <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center text-xs sm:text-sm font-black text-white shadow-lg shadow-violet-500/20 group-hover:shadow-violet-500/40 transition-shadow">
                    S
                  </div>
                  <div className="absolute -top-0.5 -right-0.5 w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full bg-emerald-400 border-2 border-[#060918] animate-pulse" />
                </div>
                <span className="text-base sm:text-lg font-bold font-[family-name:var(--font-outfit)]">
                  <span className="text-white">Ship</span>
                  <span className="text-gradient-main">Micro</span>
                </span>
              </a>

              {/* Desktop Nav Links */}
              <div className="hidden sm:flex items-center gap-1">
                {NAV_LINKS.map((link) => (
                  <a key={link.href} href={link.href}
                    className="px-3 py-1.5 rounded-lg text-sm font-medium text-gray-400 hover:text-white hover:bg-white/[0.06] transition-all duration-200 flex items-center gap-1.5">
                    <span className="text-xs">{link.emoji}</span>
                    {link.label}
                  </a>
                ))}
              </div>

              {/* Right Side */}
              <div className="flex items-center gap-2 sm:gap-3">
                <div className="border-l border-white/10 pl-2 sm:pl-3 flex items-center">
                  <SignedOut>
                    <SignInButton mode="modal">
                      <button className="px-3 sm:px-4 py-1.5 rounded-full text-[11px] sm:text-xs font-bold transition-all duration-300 bg-gradient-to-r from-violet-600 to-cyan-600 text-white hover:shadow-lg hover:shadow-violet-500/25 hover:scale-105">
                        登录
                      </button>
                    </SignInButton>
                  </SignedOut>
                  <SignedIn>
                    <UserButton afterSignOutUrl="/" />
                  </SignedIn>
                </div>

                {/* Mobile hamburger */}
                <MobileMenu />
              </div>
            </div>
          </nav>

          <main>{children}</main>

          {/* ═══ Chinese Footer ═══ */}
          <footer className="border-t border-white/[0.05] mt-12 sm:mt-20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 sm:gap-8 mb-6 sm:mb-8">
                <div>
                  <h4 className="text-sm font-bold text-white mb-3">产品</h4>
                  <div className="space-y-2">
                    <a href="/#products" className="block text-xs text-gray-500 hover:text-gray-300 transition-colors">AI证件照</a>
                    <a href="/#products" className="block text-xs text-gray-500 hover:text-gray-300 transition-colors">HS关税查询</a>
                    <a href="/tools" className="block text-xs text-gray-500 hover:text-gray-300 transition-colors">开发者工具</a>
                    <a href="/arcade" className="block text-xs text-gray-500 hover:text-gray-300 transition-colors">小游戏</a>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white mb-3">工具</h4>
                  <div className="space-y-2">
                    <a href="/tools/json-formatter" className="block text-xs text-gray-500 hover:text-gray-300 transition-colors">JSON 格式化</a>
                    <a href="/tools/regex-tester" className="block text-xs text-gray-500 hover:text-gray-300 transition-colors">正则测试</a>
                    <a href="/tools/password-gen" className="block text-xs text-gray-500 hover:text-gray-300 transition-colors">密码生成</a>
                    <a href="/tools/qr-generator" className="block text-xs text-gray-500 hover:text-gray-300 transition-colors">二维码生成</a>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white mb-3">社区</h4>
                  <div className="space-y-2">
                    <a href="https://www.xiaohongshu.com/" target="_blank" rel="noopener noreferrer" className="block text-xs text-gray-500 hover:text-gray-300 transition-colors">📕 关注小红书</a>
                    <a href="https://xiaobot.net/" target="_blank" rel="noopener noreferrer" className="block text-xs text-gray-500 hover:text-gray-300 transition-colors">📖 小报童专栏</a>
                    <a href="https://afdian.com/a/tiankongmumu" target="_blank" rel="noopener noreferrer" className="block text-xs text-gray-500 hover:text-gray-300 transition-colors">☕ 爱发电支持</a>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white mb-3">关于</h4>
                  <div className="space-y-2">
                    <span className="block text-xs text-gray-500">TITAN 引擎驱动</span>
                    <span className="block text-xs text-gray-500">基于 Next.js 构建</span>
                    <span className="block text-xs text-gray-500">© 2026 ShipMicro</span>
                  </div>
                </div>
              </div>
              <div className="border-t border-white/[0.05] pt-4 sm:pt-6 flex flex-col sm:flex-row items-center justify-between gap-3 sm:gap-4">
                <span className="text-[11px] sm:text-xs text-gray-600">© 2026 ShipMicro · 木木效率工坊 · 所有工具免费使用</span>
                <div className="flex items-center gap-2">
                  <span className="badge badge-purple text-[9px] sm:text-[10px]">TITAN v3.5</span>
                  <span className="badge badge-cyan text-[9px] sm:text-[10px]">17+ 工具</span>
                  <span className="badge badge-emerald text-[9px] sm:text-[10px]">永久免费</span>
                </div>
              </div>
            </div>
          </footer>
        </body>
      </html>
    </ClerkProvider>
  );
}
