import { notFound, redirect } from "next/navigation";
import { Metadata } from "next";
import { currentUser } from "@clerk/nextjs/server";
import { loadTools } from "@/lib/data";

const GAME_CATS = ["Tap", "Dodge", "Memory", "Pattern", "Math", "Typing", "Reaction", "Classic", "Game", "Arcade"];

interface ToolPageProps {
    params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: ToolPageProps): Promise<Metadata> {
    const { slug } = await params;
    const allTools = loadTools();
    const tool = allTools.find(t => t.slug === slug);
    if (!tool) return { title: "Tool Not Found | ShipMicro" };

    return {
        title: `${tool.name} — Free Online Tool | ShipMicro`,
        description: tool.desc || `Use ${tool.name} free online. No sign-up required.`,
        openGraph: {
            title: `${tool.name} | ShipMicro`,
            description: tool.desc || `Use ${tool.name} free, instantly in your browser.`,
        }
    };
}

export default async function ToolPage({ params }: ToolPageProps) {
    const { slug } = await params;
    const allTools = loadTools();
    const tool = allTools.find(t => t.slug === slug);

    if (!tool || GAME_CATS.includes(tool.cat)) return notFound();

    const user = await currentUser();
    let isPro = false;
    if (user) {
        isPro = Boolean(user.publicMetadata?.isPro) || false;
    }

    const hasUrl = tool.url && tool.url !== "dry-run";

    return (
        <div className="min-h-screen flex flex-col">
            {/* Compact top bar */}
            <div className="bg-black/40 backdrop-blur border-b border-white/10 px-4 py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <a href="/tools" className="text-sm text-gray-400 hover:text-white transition-colors flex items-center gap-1">
                        ← Tools
                    </a>
                    <span className="text-white/20">|</span>
                    <span className="text-sm font-semibold text-white">{tool.icon} {tool.name}</span>
                </div>
                <a href="/" className="text-xs text-gray-500 hover:text-white transition-colors">ShipMicro</a>
            </div>

            {/* Embedded tool or Paywall */}
            {hasUrl ? (
                <div className="relative flex-1 w-full" style={{ minHeight: "calc(100vh - 52px)" }}>
                    <iframe
                        src={tool.url!}
                        className={`w-full h-full border-0 absolute inset-0`}
                        title={tool.name}
                    />
                </div>
            ) : (
                <div className="flex-1 flex items-center justify-center">
                    <div className="text-center">
                        <span className="text-5xl block mb-4">🔧</span>
                        <h2 className="text-xl font-bold text-gray-400">Coming Soon</h2>
                        <p className="text-gray-600 mt-2">This tool is being built.</p>
                        <a href="/tools" className="mt-4 inline-block text-sm text-purple-400 hover:text-purple-300">← Browse other tools</a>
                    </div>
                </div>
            )}
        </div>
    );
}
