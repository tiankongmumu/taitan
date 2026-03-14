import { loadTools } from "@/lib/data";
import { FadeIn } from "@/components/ui/FadeIn";
import { Metadata } from "next";

export const metadata: Metadata = {
    title: "ShipMicro — 免费开发者工具合集 | 效率神器",
    description: "100%免费开发者工具：JSON格式化、正则测试、JWT解码、密码生成等15+工具。无需注册，即开即用。",
};

const TOOL_CATS = [
    { key: "Code", label: "代码工具", emoji: "⚡", gradient: "from-cyan-500 to-blue-500" },
    { key: "Security", label: "安全工具", emoji: "🔒", gradient: "from-emerald-500 to-teal-500" },
    { key: "Converter", label: "转换工具", emoji: "🔄", gradient: "from-orange-500 to-amber-500" },
    { key: "Editor", label: "编辑器", emoji: "📝", gradient: "from-purple-500 to-fuchsia-500" },
    { key: "Utility", label: "实用工具", emoji: "🛠️", gradient: "from-pink-500 to-rose-500" },
];

export default function ZhPage() {
    const allTools = loadTools();
    const tools = allTools.filter(t => t.cat !== "Game" && t.success);

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 relative z-10 font-sans">

            {/* ═══ Hero ═══ */}
            <section className="pt-24 sm:pt-36 pb-16 sm:pb-24 text-center relative flex flex-col items-center justify-center min-h-[50vh]">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] sm:w-[900px] h-[400px] bg-gradient-to-r from-cyan-600/15 via-fuchsia-600/15 to-amber-600/15 blur-[140px] rounded-full pointer-events-none -z-10" />

                <div className="inline-block mb-6 px-4 py-1.5 rounded-full border border-white/10 bg-white/5 backdrop-blur-md text-sm font-medium text-cyan-300 shadow-[0_0_15px_rgba(6,182,212,0.15)]">
                    <span className="animate-pulse mr-2">🟢</span> {tools.length} 款免费工具 · 持续更新中
                </div>

                <h1 className="text-4xl sm:text-6xl md:text-7xl font-black tracking-tighter mb-6 leading-[1.1] font-[family-name:var(--font-outfit)]">
                    <span className="text-white drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]">开发者效率工具</span><br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-fuchsia-500 to-amber-400 filter drop-shadow-[0_0_20px_rgba(236,72,153,0.4)]">免费 · 好用 · 无需注册</span>
                </h1>

                <p className="text-lg sm:text-xl text-gray-400 max-w-3xl mx-auto mb-8 px-4 font-light">
                    JSON格式化 · 正则测试 · JWT解码 · 颜色转换 · 二维码生成<br className="hidden sm:block" />
                    程序员必备的效率工具箱，打开浏览器就能用
                </p>

                <div className="flex gap-4 flex-wrap justify-center">
                    <a href="/tools" className="px-6 py-3 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold text-sm hover:scale-105 transition-transform shadow-[0_0_30px_rgba(6,182,212,0.3)]">
                        🛠️ 立即使用工具
                    </a>
                    <a href="/arcade" className="px-6 py-3 rounded-full border border-white/20 bg-white/5 text-white font-bold text-sm hover:bg-white/10 transition-all">
                        🎮 玩游戏放松
                    </a>
                </div>
            </section>

            {/* ═══ Tool Categories ═══ */}
            {TOOL_CATS.map((cat) => {
                const catTools = tools.filter(t => t.cat === cat.key);
                if (catTools.length === 0) return null;
                return (
                    <section key={cat.key} className="pb-12">
                        <div className="flex items-center gap-3 mb-6">
                            <span className="text-2xl">{cat.emoji}</span>
                            <h2 className="text-2xl font-black text-white">{cat.label}</h2>
                            <span className="text-sm text-gray-500">{catTools.length} 个工具</span>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                            {catTools.map((tool, i) => (
                                <FadeIn key={tool.slug} delay={i * 80}>
                                    <a href={`/tools/${tool.slug}`}
                                        className={`group block p-6 rounded-2xl border border-white/10 bg-white/[0.02] hover:bg-white/[0.05] hover:border-white/20 transition-all duration-300 hover:-translate-y-0.5`}>
                                        <div className="flex items-center gap-3 mb-3">
                                            <span className="text-3xl">{tool.icon}</span>
                                            <div>
                                                <h3 className="text-white font-bold text-base group-hover:text-cyan-300 transition-colors">
                                                    {tool.nameCn || tool.name}
                                                </h3>
                                                <p className="text-gray-500 text-xs">{tool.name}</p>
                                            </div>
                                        </div>
                                        <p className="text-gray-400 text-sm">{tool.descCn || tool.desc}</p>
                                        <div className="mt-4 inline-flex items-center gap-1 text-xs font-bold text-cyan-400">
                                            免费使用 <span className="group-hover:translate-x-1 transition-transform">→</span>
                                        </div>
                                    </a>
                                </FadeIn>
                            ))}
                        </div>
                    </section>
                );
            })}

            {/* ═══ CTA ═══ */}
            <section className="py-16 text-center">
                <div className="max-w-2xl mx-auto p-8 rounded-3xl border border-cyan-500/20 bg-gradient-to-b from-cyan-500/5 to-transparent">
                    <h2 className="text-2xl font-black text-white mb-3">💡 更多效率干货</h2>
                    <p className="text-gray-400 mb-6">关注小红书「木木效率工坊」获取最新工具测评和创业干货</p>
                    <div className="flex gap-4 justify-center flex-wrap">
                        <a href="/news" className="px-5 py-2 rounded-full bg-amber-500/20 text-amber-400 font-bold text-sm border border-amber-500/30 hover:bg-amber-500 hover:text-white transition-colors">
                            📰 科技资讯
                        </a>
                        <a href="/ideas" className="px-5 py-2 rounded-full bg-emerald-500/20 text-emerald-400 font-bold text-sm border border-emerald-500/30 hover:bg-emerald-500 hover:text-white transition-colors">
                            💰 赚钱点子
                        </a>
                    </div>
                </div>
            </section>

            {/* ═══ Footer ═══ */}
            <footer className="border-t border-white/10 py-8 text-center text-gray-600 text-sm">
                <p>© 2026 ShipMicro · Powered by TITAN Engine</p>
                <p className="mt-1 text-gray-700">免费工具 · 科技资讯 · 赚钱点子 · 小游戏</p>
            </footer>
        </div>
    );
}
