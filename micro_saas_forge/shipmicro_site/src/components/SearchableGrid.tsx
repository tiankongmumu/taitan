"use client";
import { useState } from "react";

interface Item {
    slug: string;
    title: string;
    description: string | null;
    icon: string | null;
    category: string;
    url: string | null;
    isPremium?: boolean;
}

export function SearchableGrid({ items, basePath, type }: { items: Item[]; basePath: string; type: "game" | "tool" }) {
    const [search, setSearch] = useState("");
    const [activeCategory, setActiveCategory] = useState("All");

    // Extract unique categories
    const categories = ["All", ...Array.from(new Set(items.map(i => i.category)))];

    // Filter items
    const filtered = items.filter(item => {
        const matchesSearch = search === "" ||
            item.title.toLowerCase().includes(search.toLowerCase()) ||
            (item.description || "").toLowerCase().includes(search.toLowerCase());
        const matchesCategory = activeCategory === "All" || item.category === activeCategory;
        return matchesSearch && matchesCategory;
    });

    const isGame = type === "game";
    const accentColor = isGame ? "pink" : "blue";

    return (
        <div>
            {/* Search Bar */}
            <div className="relative mb-6">
                <input
                    type="text"
                    placeholder={`搜索 ${items.length} 个${isGame ? "游戏" : "工具"}...`}
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    className={`w-full px-5 py-4 pl-12 rounded-2xl bg-white/[0.04] backdrop-blur-md border border-white/10 text-white placeholder-gray-500 outline-none focus:border-${accentColor}-500/50 focus:bg-white/[0.06] transition-all shadow-[0_0_15px_rgba(0,0,0,0.5)]`}
                />
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 text-lg">🔍</span>
                {search && (
                    <button onClick={() => setSearch("")} className="absolute right-4 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-white/10 flex items-center justify-center text-gray-400 hover:text-white hover:bg-white/20 transition-all">✕</button>
                )}
            </div>

            {/* Category Tabs */}
            {categories.length > 2 && (
                <div className="flex flex-wrap gap-2 mb-8">
                    {categories.map(cat => (
                        <button
                            key={cat}
                            onClick={() => setActiveCategory(cat)}
                            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${activeCategory === cat
                                ? isGame
                                    ? "bg-pink-500/20 text-pink-400 border border-pink-500/40"
                                    : "bg-blue-500/20 text-blue-400 border border-blue-500/40"
                                : "bg-white/[0.03] text-gray-500 border border-white/[0.06] hover:text-gray-300"
                                }`}
                        >
                            {cat} ({items.filter(i => cat === "All" || i.category === cat).length})
                        </button>
                    ))}
                </div>
            )}

            {/* Results count */}
            <p className="text-sm text-gray-500 mb-4">找到 {filtered.length} 个{isGame ? "游戏" : "工具"}</p>

            {/* Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                {filtered.map(item => (
                    <a
                        key={item.slug}
                        href={`${basePath}/${item.slug}`}
                        className={`group relative block rounded-2xl p-4 sm:p-6 bg-[#0a0a0a]/80 backdrop-blur-md border hover:-translate-y-1 transition-all overflow-hidden h-full flex flex-col ${isGame
                            ? "border-white/5 hover:bg-[#111]"
                            : "border-white/5 hover:bg-[#111]"
                            }`}
                    >
                        {/* Hover Overlay Gradients */}
                        <div className={`absolute inset-0 bg-gradient-to-br from-${accentColor}-500/0 to-${accentColor}-500/0 group-hover:from-${accentColor}-500/5 group-hover:to-transparent transition-colors duration-500`}></div>
                        <div className={`absolute -inset-px bg-gradient-to-r ${isGame ? "from-fuchsia-500/50 to-pink-500/50" : "from-cyan-500/50 to-purple-500/50"} rounded-2xl opacity-0 group-hover:opacity-100 blur-sm transition-opacity duration-500 -z-10`}></div>

                        <div className="flex items-start justify-between mb-4 relative z-10">
                            <div className={`w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-2xl shadow-inner shadow-${accentColor}-500/10 group-hover:border-${accentColor}-500/30 transition-colors`}>
                                {item.icon || (isGame ? "🎮" : "🛠️")}
                            </div>
                            {item.isPremium ? (
                                <span className="text-[10px] uppercase tracking-widest flex items-center gap-1.5 px-2.5 py-1 rounded-full border bg-purple-500/20 text-purple-300 border-purple-500/40 shadow-[0_0_10px_rgba(168,85,247,0.3)]">
                                    <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse shadow-neon" />
                                    PRO
                                </span>
                            ) : (
                                <span className={`text-[10px] uppercase tracking-widest flex items-center gap-1.5 px-2.5 py-1 rounded-full border ${isGame
                                    ? "bg-pink-500/10 text-pink-400 border-pink-500/20"
                                    : "bg-cyan-500/10 text-cyan-400 border-cyan-500/20"
                                    }`}>
                                    <span className={`w-1.5 h-1.5 rounded-full ${isGame ? "bg-pink-400" : "bg-cyan-400"} opacity-70`} />
                                    免费
                                </span>
                            )}
                        </div>
                        <h3 className={`text-base sm:text-xl font-bold text-white mb-2 transition-colors relative z-10 ${isGame ? "group-hover:text-pink-400" : "group-hover:text-cyan-300"}`}>
                            {item.title}
                        </h3>
                        <p className="text-sm text-gray-400 leading-relaxed font-light mb-4 line-clamp-2 relative z-10 flex-grow">{item.description}</p>
                        <div className="flex items-center justify-between border-t border-white/5 pt-4 mt-auto relative z-10">
                            <span className={`text-[10px] uppercase tracking-widest px-2.5 py-1 rounded-full border ${isGame
                                ? "bg-fuchsia-500/10 text-fuchsia-400 border-fuchsia-500/20"
                                : "bg-blue-500/10 text-blue-400 border-blue-500/20"
                                }`}>{item.category}</span>
                            <span className={`text-xs font-bold uppercase tracking-widest transition-colors ${isGame ? "text-gray-500 group-hover:text-fuchsia-400" : "text-gray-500 group-hover:text-cyan-400"
                                }`}>{isGame ? "开始玩 →" : "立即使用 →"}</span>
                        </div>
                    </a>
                ))}
            </div>

            {/* Empty state */}
            {filtered.length === 0 && (
                <div className="text-center py-16 border border-dashed border-white/10 rounded-2xl">
                    <span className="text-4xl block mb-3">😕</span>
                    <p className="text-gray-400">没有找到 &quot;{search}&quot; 的结果</p>
                    <button onClick={() => { setSearch(""); setActiveCategory("All"); }} className="mt-3 text-sm text-purple-400 hover:text-purple-300">
                        清除筛选
                    </button>
                </div>
            )}
        </div>
    );
}
