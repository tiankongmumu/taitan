import { loadTools } from "@/lib/data";

export const dynamic = "force-dynamic";

const GAME_CATS = ["Tap", "Dodge", "Memory", "Pattern", "Math", "Typing", "Reaction", "Classic", "Game", "Arcade"];

export default async function CEODashboard() {
    const allTools = loadTools();
    const tools = allTools.filter(t => !GAME_CATS.includes(t.cat) && t.success);
    const games = allTools.filter(t => GAME_CATS.includes(t.cat) && t.success);
    const successfulTools = allTools.filter(t => t.url && t.url !== "dry-run" && t.success);
    const blogs = 0; // Blog system pending migration
    const proUsers = 0; // Tracked via Clerk publicMetadata

    return (
        <div className="max-w-6xl mx-auto px-6 py-12">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-10 gap-4">
                <div>
                    <h1 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-orange-500 mb-2">
                        System Operations Terminal
                    </h1>
                    <p className="text-gray-400 font-mono text-sm">V18 Serverless Core / Live Metrics Monitor</p>
                </div>
                <div className="flex items-center gap-3 bg-red-500/10 border border-red-500/30 px-5 py-3 rounded-xl shadow-[0_0_15px_rgba(239,68,68,0.2)]">
                    <span className="w-3 h-3 rounded-full bg-red-500 animate-ping" />
                    <span className="text-sm font-bold text-red-500 tracking-widest uppercase">Frenzy Mode Active</span>
                </div>
            </div>

            {/* Quick KPIs */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.05] relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 blur-[50px] rounded-full pointer-events-none" />
                    <h3 className="text-gray-400 text-sm font-mono mb-2">MICRO-SAAS DEPLOYED</h3>
                    <p className="text-5xl font-black text-cyan-400">{tools.length}</p>
                </div>

                <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.05] relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-pink-500/10 blur-[50px] rounded-full pointer-events-none" />
                    <h3 className="text-gray-400 text-sm font-mono mb-2">ARCADE GAMES</h3>
                    <p className="text-5xl font-black text-pink-400">{games.length}</p>
                </div>

                <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.05] relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/10 blur-[50px] rounded-full pointer-events-none" />
                    <h3 className="text-gray-400 text-sm font-mono mb-2">SEO BLOGS MINED</h3>
                    <p className="text-5xl font-black text-amber-400">{blogs}</p>
                </div>

                <div className="p-6 rounded-2xl border border-emerald-500/30 bg-gradient-to-br from-emerald-500/10 to-transparent relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/20 blur-[50px] rounded-full pointer-events-none" />
                    <h3 className="text-emerald-400 text-sm font-mono mb-2">PAYPAL SUBSCRIBERS</h3>
                    <p className="text-5xl font-black text-white">{proUsers}</p>
                    <p className="text-xs text-emerald-400 mt-2 font-mono">Universal Pro: Active</p>
                </div>
            </div>

            {/* Production Log */}
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-white font-mono">Recent Production Log</h2>
                <div className="text-xs text-gray-400 font-mono">Total Successful Builds: <span className="text-emerald-400 font-bold">{successfulTools.length}</span></div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-[#0A0A0A] overflow-hidden shadow-2xl">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="border-b border-white/10 text-xs text-gray-500 uppercase tracking-widest bg-white/5 font-mono">
                            <th className="p-4 font-bold">Artifact Name</th>
                            <th className="p-4 font-bold">Type</th>
                            <th className="p-4 font-bold">Status</th>
                            <th className="p-4 font-bold">Live URL</th>
                        </tr>
                    </thead>
                    <tbody className="text-sm font-mono">
                        {allTools.filter(t => t.success).slice(0, 15).map(t => (
                            <tr key={t.slug} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                                <td className="p-4 font-semibold text-gray-200">
                                    <span className="mr-2 opacity-50">{t.icon}</span>{t.name}
                                </td>
                                <td className="p-4">
                                    <span className={`px-2 py-0.5 rounded text-xs border ${t.cat === 'Game' ? 'text-pink-400 border-pink-400/30 bg-pink-400/10' : 'text-cyan-400 border-cyan-400/30 bg-cyan-400/10'}`}>
                                        {t.cat.toUpperCase()}
                                    </span>
                                </td>
                                <td className="p-4">
                                    {t.url ? (
                                        <span className="flex items-center gap-2 text-emerald-400 text-xs font-bold">
                                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_5px_#34d399]"></span> ONLINE
                                        </span>
                                    ) : (
                                        <span className="flex items-center gap-2 text-red-400 text-xs font-bold">
                                            <span className="w-1.5 h-1.5 rounded-full bg-red-400 shadow-[0_0_5px_#f87171]"></span> FAILED
                                        </span>
                                    )}
                                </td>
                                <td className="p-4 text-gray-500 text-xs max-w-[200px] truncate">
                                    {t.url && t.url !== "dry-run" ? <a href={t.url} target="_blank" className="hover:text-blue-400 underline decoration-blue-400/30 underline-offset-4">{t.url.replace('https://', '')}</a> : "N/A"}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            <div className="mt-8 text-center text-xs text-gray-600 font-mono">
                System architecture V18 · ShipMicro AI Engine · Serverless Data via history.json
            </div>
        </div>
    );
}
