import { loadTools } from "@/lib/data";
import { SearchableGrid } from "@/components/SearchableGrid";

const GAME_CATS = ["Tap", "Dodge", "Memory", "Pattern", "Math", "Typing", "Reaction", "Classic", "Game", "Arcade"];

export default async function ArcadePage() {
    const allTools = loadTools();
    const games = allTools.filter(t => GAME_CATS.includes(t.cat) && t.success);

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 sm:py-24 relative z-10 font-sans">
            <div className="mb-8 sm:mb-16">
                <div className="inline-block mb-3 sm:mb-4 px-3 py-1 rounded-full border border-fuchsia-500/20 bg-fuchsia-500/5 text-[10px] sm:text-xs font-bold text-fuchsia-400 uppercase tracking-widest shadow-[0_0_15px_rgba(236,72,153,0.1)]">
                    游戏中心
                </div>
                <h1 className="text-3xl sm:text-5xl md:text-6xl font-black tracking-tighter mb-3 sm:mb-6 font-[family-name:var(--font-outfit)]">
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-400 via-pink-500 to-rose-500 filter drop-shadow-[0_0_15px_rgba(236,72,153,0.3)]">免费在线小游戏</span>
                </h1>
                <p className="text-gray-400 text-base sm:text-lg md:text-xl font-light max-w-2xl leading-relaxed">
                    {games.length} 款免费 HTML5 小游戏，浏览器直接玩 — 无需下载，无需注册。
                </p>
            </div>

            <SearchableGrid
                items={games.map(g => ({
                    slug: g.slug,
                    title: g.nameCn || g.name,
                    description: g.descCn || g.desc,
                    icon: g.icon,
                    category: g.cat,
                    url: g.url || null,
                    isPremium: g.isPremium === true,
                }))}
                basePath="/arcade"
                type="game"
            />
        </div>
    );
}
