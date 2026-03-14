"use client";

import { useState, useMemo } from "react";

/* ─── Types (duplicated from lib/data to avoid server import in client component) ─── */
interface NewsArticle {
    title: string;
    source: string;
    score: number;
    slug: string;
    url: string;
    category: string;
    generated_at: string;
}

const CATEGORIES = ["All", "AI", "Dev", "OpenSource", "Startup", "Cloud", "Web3"];

const CAT_COLORS: Record<string, string> = {
    AI: "text-purple-400 bg-purple-500/10 border-purple-500/20",
    Dev: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
    OpenSource: "text-green-400 bg-green-500/10 border-green-500/20",
    Startup: "text-amber-400 bg-amber-500/10 border-amber-500/20",
    Cloud: "text-blue-400 bg-blue-500/10 border-blue-500/20",
    Web3: "text-pink-400 bg-pink-500/10 border-pink-500/20",
};

const CAT_ICONS: Record<string, string> = {
    AI: "🤖", Dev: "💻", OpenSource: "🔓", Startup: "🚀", Cloud: "☁️", Web3: "⛓️",
};

function getSourceColor(source: string): string {
    const s = source.toLowerCase();
    if (s.includes("github")) return "text-purple-400 bg-purple-500/10 border-purple-500/20";
    if (s.includes("hacker") || s.includes("hn")) return "text-orange-400 bg-orange-500/10 border-orange-500/20";
    if (s.includes("reddit")) return "text-red-400 bg-red-500/10 border-red-500/20";
    if (s.includes("techcrunch")) return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
    if (s.includes("indie")) return "text-cyan-400 bg-cyan-500/10 border-cyan-500/20";
    return "text-amber-400 bg-amber-500/10 border-amber-500/20";
}

function getScoreBar(score: number): string {
    if (score >= 800) return "w-full bg-gradient-to-r from-emerald-500 to-cyan-500";
    if (score >= 500) return "w-3/4 bg-gradient-to-r from-amber-500 to-orange-500";
    if (score >= 200) return "w-1/2 bg-gradient-to-r from-blue-500 to-purple-500";
    return "w-1/4 bg-gray-600";
}

function timeAgo(dateStr: string): string {
    try {
        const diff = Date.now() - new Date(dateStr).getTime();
        const mins = Math.floor(diff / 60000);
        if (mins < 60) return `${mins}分钟前`;
        const hrs = Math.floor(mins / 60);
        if (hrs < 24) return `${hrs}小时前`;
        return `${Math.floor(hrs / 24)}天前`;
    } catch {
        return "今天";
    }
}

export default function NewsClient({ articles }: { articles: NewsArticle[] }) {
    const [activeCategory, setActiveCategory] = useState("All");
    const [searchQuery, setSearchQuery] = useState("");
    const [sortBy, setSortBy] = useState<"score" | "date">("score");

    const filtered = useMemo(() => {
        let result = articles;
        if (activeCategory !== "All") {
            result = result.filter(a => a.category === activeCategory);
        }
        if (searchQuery.trim()) {
            const q = searchQuery.toLowerCase();
            result = result.filter(a => a.title.toLowerCase().includes(q) || a.source.toLowerCase().includes(q));
        }
        if (sortBy === "score") result = [...result].sort((a, b) => b.score - a.score);
        else result = [...result].sort((a, b) => new Date(b.generated_at).getTime() - new Date(a.generated_at).getTime());
        return result;
    }, [articles, activeCategory, searchQuery, sortBy]);

    return (
        <div className="max-w-5xl mx-auto px-4 sm:px-6 relative z-10 font-sans">
            {/* Hero */}
            <section className="pt-20 sm:pt-28 pb-8 text-center">
                <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[500px] h-[200px] bg-gradient-to-r from-amber-600/15 to-orange-600/15 blur-[100px] rounded-full pointer-events-none -z-10" />
                <span className="text-5xl mb-4 block">📰</span>
                <h1 className="text-4xl sm:text-5xl font-black text-white mb-3 tracking-tight">
                    科技<span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-orange-500">资讯</span>
                </h1>
                <p className="text-gray-400 text-lg">AI 精选科技、创业与开发者新闻</p>
            </section>

            {/* Search Bar */}
            <section className="pb-4">
                <div className="relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">🔍</span>
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={e => setSearchQuery(e.target.value)}
                        placeholder="搜索资讯..."
                        className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/[0.03] border border-white/10 text-white placeholder-gray-600 outline-none focus:border-amber-500/40 transition-colors text-sm"
                    />
                    {searchQuery && (
                        <button onClick={() => setSearchQuery("")} className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white">✕</button>
                    )}
                </div>
            </section>

            {/* Category Filter + Sort */}
            <section className="flex items-center gap-3 pb-6 flex-wrap">
                <div className="flex gap-2 flex-wrap flex-1">
                    {CATEGORIES.map(cat => (
                        <button
                            key={cat}
                            onClick={() => setActiveCategory(cat)}
                            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${activeCategory === cat
                                ? "bg-amber-500/15 border border-amber-500/30 text-amber-400"
                                : "bg-white/[0.02] border border-white/10 text-gray-500 hover:text-white hover:border-white/20"
                                }`}
                        >
                            {cat !== "All" && <span className="mr-1">{CAT_ICONS[cat] || ""}</span>}
                            {cat}
                        </button>
                    ))}
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => setSortBy("score")}
                        className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${sortBy === "score" ? "bg-white/10 text-white" : "text-gray-600 hover:text-gray-400"}`}
                    >🔥 热门</button>
                    <button
                        onClick={() => setSortBy("date")}
                        className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${sortBy === "date" ? "bg-white/10 text-white" : "text-gray-600 hover:text-gray-400"}`}
                    >🕒 最新</button>
                </div>
            </section>

            {/* Results Count */}
            <div className="text-xs text-gray-600 mb-4">
                {filtered.length} 篇资讯
                {activeCategory !== "All" && ` · ${activeCategory} 分类`}
                {searchQuery && ` · 匹配 “${searchQuery}”`}
            </div>

            {/* News List */}
            <section className="pb-20">
                <div className="space-y-3">
                    {filtered.map((article, i) => (
                        <a
                            key={i}
                            href={article.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="group flex items-start gap-4 p-5 rounded-2xl border border-white/10 bg-white/[0.02] hover:bg-white/[0.05] hover:border-amber-500/30 transition-all"
                        >
                            {/* Score */}
                            <div className="flex-shrink-0 w-16 text-center">
                                <div className="text-2xl font-black text-amber-400">{article.score}</div>
                                <div className="text-xs text-gray-600 uppercase tracking-wider">热度</div>
                                <div className="mt-2 h-1 rounded-full overflow-hidden bg-white/5">
                                    <div className={`h-full rounded-full ${getScoreBar(article.score)}`} />
                                </div>
                            </div>

                            {/* Content */}
                            <div className="flex-1 min-w-0">
                                <h3 className="text-white font-semibold text-base leading-snug group-hover:text-amber-300 transition-colors mb-2">
                                    {article.title}
                                </h3>
                                <div className="flex items-center gap-2 flex-wrap">
                                    <span className={`text-xs px-2 py-0.5 rounded-full border ${getSourceColor(article.source)}`}>
                                        {article.source}
                                    </span>
                                    <span className={`text-xs px-2 py-0.5 rounded-full border ${CAT_COLORS[article.category] || "text-gray-400 bg-gray-500/10 border-gray-500/20"}`}>
                                        {CAT_ICONS[article.category] || "📝"} {article.category}
                                    </span>
                                    <span className="text-xs text-gray-600">{timeAgo(article.generated_at)}</span>
                                </div>
                            </div>

                            {/* Arrow */}
                            <div className="flex-shrink-0 text-gray-600 group-hover:text-amber-400 transition-colors self-center text-lg">↗</div>
                        </a>
                    ))}
                </div>

                {filtered.length === 0 && (
                    <div className="text-center py-20">
                        <span className="text-5xl block mb-4">{searchQuery ? "🔍" : "📡"}</span>
                        <h2 className="text-xl font-bold text-gray-400">
                            {searchQuery ? "未找到匹配结果" : "该分类暂无资讯"}
                        </h2>
                        <p className="text-gray-600 mt-2">
                            {searchQuery ? "请尝试其他搜索词" : "请稍后再来或换个分类"}
                        </p>
                    </div>
                )}
            </section>

            <div className="text-center pb-12">
                <a href="/" className="text-sm text-gray-500 hover:text-white transition-colors">← 返回首页</a>
            </div>
        </div>
    );
}
