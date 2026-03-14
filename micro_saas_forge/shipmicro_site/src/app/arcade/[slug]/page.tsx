import { notFound, redirect } from "next/navigation";
import { Metadata } from "next";
import { currentUser } from "@clerk/nextjs/server";
import { loadTools } from "@/lib/data";

const GAME_CATS = ["Tap", "Dodge", "Memory", "Pattern", "Math", "Typing", "Reaction", "Classic", "Game", "Arcade"];

interface ArcadeGameProps {
    params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: ArcadeGameProps): Promise<Metadata> {
    const { slug } = await params;
    const allTools = loadTools();
    const game = allTools.find(t => t.slug === slug);
    if (!game) return { title: "Game Not Found | ShipMicro Arcade" };

    return {
        title: `${game.name} — Play Free | ShipMicro Arcade`,
        description: game.desc || `Play ${game.name} free online in the ShipMicro Arcade!`,
        openGraph: {
            title: `${game.name} | ShipMicro Arcade`,
            description: game.desc || `Play ${game.name} online now!`,
        }
    };
}

export default async function ArcadeGamePage({ params }: ArcadeGameProps) {
    const { slug } = await params;
    const allTools = loadTools();
    const game = allTools.find(t => t.slug === slug);

    if (!game || !GAME_CATS.includes(game.cat)) return notFound();

    const user = await currentUser();
    let isPro = false;
    if (user) {
        isPro = Boolean(user.publicMetadata?.isPro) || false;
    }

    const hasUrl = game.url && game.url !== "dry-run";

    return (
        <div className="min-h-screen flex flex-col bg-black">
            {/* Compact arcade bar */}
            <div className="bg-black/80 backdrop-blur border-b border-white/10 px-4 py-3 flex items-center justify-between z-20 relative">
                <div className="flex items-center gap-3">
                    <a href="/arcade" className="text-sm text-gray-400 hover:text-pink-400 transition-colors flex items-center gap-1">
                        ← 游戏厅
                    </a>
                    <span className="text-white/20">|</span>
                    <span className="text-sm font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-400 to-purple-400">
                        {game.icon} {game.nameCn || game.name}
                    </span>
                </div>
                <div className="flex items-center gap-4">
                    <span className="text-xs text-emerald-400 font-mono">免费</span>
                    <a href="/" className="text-xs text-gray-500 hover:text-white transition-colors">ShipMicro</a>
                </div>
            </div>

            {/* Full-screen game container or Paywall */}
            {hasUrl ? (
                <div className="relative flex-1 w-full" style={{ minHeight: "calc(100vh - 52px)" }}>
                    <iframe
                        src={game.url!}
                        className={`w-full h-full border-0 absolute inset-0`}
                        title={game.name}
                        sandbox="allow-scripts allow-same-origin allow-popups"
                        allow="fullscreen"
                    />
                </div>
            ) : (
                <div className="flex-1 flex items-center justify-center">
                    <div className="text-center">
                        <span className="text-6xl block mb-4 opacity-50">🕹️</span>
                        <h2 className="text-2xl font-bold text-gray-500 uppercase tracking-widest">即将上线</h2>
                        <p className="text-gray-600 mt-2">此游戏正在开发中。</p>
                        <a href="/arcade" className="mt-4 inline-block text-sm text-pink-400 hover:text-pink-300">← 返回游戏厅</a>
                    </div>
                </div>
            )}
        </div>
    );
}
