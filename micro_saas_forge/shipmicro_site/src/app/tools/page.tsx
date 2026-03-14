import { loadTools } from "@/lib/data";
import { SearchableGrid } from "@/components/SearchableGrid";

const GAME_CATS = ["Tap", "Dodge", "Memory", "Pattern", "Math", "Typing", "Reaction", "Classic", "Game", "Arcade"];

export default async function ToolsPage() {
    const allTools = loadTools();
    const tools = allTools.filter(t => !GAME_CATS.includes(t.cat) && t.success);

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 sm:py-24 relative z-10 font-sans">
            <div className="mb-8 sm:mb-16">
                <div className="inline-block mb-3 sm:mb-4 px-3 py-1 rounded-full border border-cyan-500/20 bg-cyan-500/5 text-[10px] sm:text-xs font-bold text-cyan-400 uppercase tracking-widest shadow-[0_0_15px_rgba(6,182,212,0.1)]">
                    效率工具集
                </div>
                <h1 className="text-3xl sm:text-5xl md:text-6xl font-black tracking-tighter mb-3 sm:mb-6 font-[family-name:var(--font-outfit)]">
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 filter drop-shadow-[0_0_15px_rgba(6,182,212,0.3)]">免费开发者工具</span>
                </h1>
                <p className="text-gray-400 text-base sm:text-lg md:text-xl font-light max-w-2xl leading-relaxed">
                    100% 免费浏览器工具，无需注册，无需下载。数据保留在您的浏览器中，安全可靠。
                </p>
            </div>

            <SearchableGrid
                items={tools.map(t => ({
                    slug: t.slug,
                    title: t.nameCn || t.name,
                    description: t.descCn || t.desc,
                    icon: t.icon,
                    category: t.cat,
                    url: t.url || null,
                    isPremium: t.isPremium === true,
                }))}
                basePath="/tools"
                type="tool"
            />
        </div>
    );
}
