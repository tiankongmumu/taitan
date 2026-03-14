import { FadeIn } from "@/components/ui/FadeIn";
import { Metadata } from "next";
import fs from "fs";
import path from "path";

export const metadata: Metadata = {
    title: "灯感创意 — 每日AI生成副业点子 | ShipMicro",
    description: "每天发现AI生成的副业点子，每个点子包含可行性评分、预估收入和所需技能。",
};

interface MoneyIdea {
    title: string;
    description: string;
    feasibility: number;  // 1-10
    estimated_monthly: string;
    required_skills: string[];
    category: string;
    generated_at: string;
}

function loadIdeas(): MoneyIdea[] {
    try {
        const ideasPath = path.join(process.cwd(), "..", "money_ideas.json");
        if (!fs.existsSync(ideasPath)) return getDefaultIdeas();
        return JSON.parse(fs.readFileSync(ideasPath, "utf-8"));
    } catch {
        return getDefaultIdeas();
    }
}

function getDefaultIdeas(): MoneyIdea[] {
    return [
        {
            title: "AI简历优化工具",
            description: "用AI帮用户优化简历，提供可操作建议。按次收费5元或月19元无限使用。",
            feasibility: 8,
            estimated_monthly: "￥500-2,000",
            required_skills: ["Python", "OpenAI API", "Web开发"],
            category: "SaaS",
            generated_at: new Date().toISOString(),
        },
        {
            title: "垂直领域付费内容专栏",
            description: "针对特定垂直领域（如AI工具、跟卖攻略）做周更专栏，通过付费订阅变现。",
            feasibility: 9,
            estimated_monthly: "￥200-1,000",
            required_skills: ["写作", "内容营销", "行业研究"],
            category: "内容",
            generated_at: new Date().toISOString(),
        },
        {
            title: "价格监控浏览器插件",
            description: "跟踪电商平台价格变动，用户下单时赚取佣金收益。",
            feasibility: 7,
            estimated_monthly: "￥300-3,000",
            required_skills: ["JavaScript", "浏览器插件开发", "联盟营销"],
            category: "工具",
            generated_at: new Date().toISOString(),
        },
        {
            title: "发票生成器 Micro-SaaS",
            description: "简洁美观的发票生成工具，免费版+9元/月去品牌水印和PDF导出。",
            feasibility: 8,
            estimated_monthly: "￥200-800",
            required_skills: ["React/Next.js", "PDF生成", "支付接入"],
            category: "SaaS",
            generated_at: new Date().toISOString(),
        },
        {
            title: "AI图片增强 API",
            description: "提供AI图片超分/增强接口，按次收费或卖点数，面向电商卖家产品图需求。",
            feasibility: 6,
            estimated_monthly: "￥500-5,000",
            required_skills: ["Python", "GPU服务器", "ML模型", "API设计"],
            category: "API",
            generated_at: new Date().toISOString(),
        },
    ];
}

function getFeasibilityColor(score: number): string {
    if (score >= 8) return "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
    if (score >= 6) return "text-amber-400 bg-amber-500/10 border-amber-500/30";
    return "text-red-400 bg-red-500/10 border-red-500/30";
}

function getCategoryColor(cat: string): string {
    const colors: Record<string, string> = {
        SaaS: "text-cyan-400 bg-cyan-500/10",
        Content: "text-purple-400 bg-purple-500/10",
        Tool: "text-blue-400 bg-blue-500/10",
        API: "text-emerald-400 bg-emerald-500/10",
        Affiliate: "text-pink-400 bg-pink-500/10",
    };
    return colors[cat] || "text-gray-400 bg-gray-500/10";
}

export default function IdeasPage() {
    const ideas = loadIdeas();

    return (
        <div className="max-w-5xl mx-auto px-4 sm:px-6 relative z-10 font-sans">
            {/* Hero */}
            <section className="pt-20 sm:pt-28 pb-12 text-center">
                <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[500px] h-[200px] bg-gradient-to-r from-emerald-600/15 to-teal-600/15 blur-[100px] rounded-full pointer-events-none -z-10" />

                <span className="text-5xl mb-4 block">💡</span>
                <h1 className="text-4xl sm:text-5xl font-black text-white mb-3 tracking-tight">
                    副业<span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-500">灵感</span>
                </h1>
                <p className="text-gray-400 text-lg">每日AI生成的副业点子，带可行性分析</p>
            </section>

            {/* Ideas Grid */}
            <section className="pb-20">
                <div className="space-y-4">
                    {ideas.map((idea: MoneyIdea, i: number) => (
                        <FadeIn key={i} delay={i * 80}>
                            <div className="group p-6 sm:p-8 rounded-2xl border border-white/10 bg-white/[0.02] hover:bg-white/[0.04] hover:border-emerald-500/30 transition-all">
                                {/* Top row: Category + Feasibility */}
                                <div className="flex items-center justify-between mb-4">
                                    <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${getCategoryColor(idea.category)}`}>
                                        {idea.category}
                                    </span>
                                    <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full border text-sm font-bold ${getFeasibilityColor(idea.feasibility)}`}>
                                        ⭐ {idea.feasibility}/10
                                    </div>
                                </div>

                                {/* Title */}
                                <h3 className="text-xl font-bold text-white mb-2 group-hover:text-emerald-300 transition-colors">
                                    {idea.title}
                                </h3>

                                {/* Description */}
                                <p className="text-gray-400 text-sm leading-relaxed mb-4">{idea.description}</p>

                                {/* Bottom row: Income + Skills */}
                                <div className="flex flex-wrap items-center gap-3">
                                    <div className="flex items-center gap-1.5 text-sm">
                                        <span className="text-emerald-400 font-bold">💰 {idea.estimated_monthly}</span>
                                        <span className="text-gray-600">/月</span>
                                    </div>
                                    <div className="text-gray-700">·</div>
                                    <div className="flex flex-wrap gap-1.5">
                                        {idea.required_skills.map((skill: string, j: number) => (
                                            <span key={j} className="text-xs px-2 py-0.5 rounded-md bg-white/5 text-gray-400 border border-white/10">
                                                {skill}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </FadeIn>
                    ))}
                </div>
            </section>

            <div className="text-center pb-12">
                <a href="/" className="text-sm text-gray-500 hover:text-white transition-colors">← 返回首页</a>
            </div>
        </div>
    );
}
