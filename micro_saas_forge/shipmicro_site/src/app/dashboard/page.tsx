import { currentUser } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";

export default async function UserDashboard() {
    const user = await currentUser();
    if (!user) return redirect("/");

    const isPro = Boolean(user.publicMetadata?.isPro) || false;

    return (
        <div className="max-w-4xl">
            <h1 className="text-3xl font-bold text-white mb-2">Welcome back, {user.firstName || user.username || "Developer"}.</h1>
            <p className="text-gray-400 mb-10">Manage your Universal Pro subscription and favorite tools.</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
                    <h3 className="text-gray-400 text-sm mb-1">Total Tool Uses</h3>
                    <p className="text-4xl font-black text-white">124</p>
                </div>
                <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
                    <h3 className="text-gray-400 text-sm mb-1">Favorite Tools</h3>
                    <p className="text-4xl font-black text-white">3</p>
                </div>
                <div className="p-6 rounded-2xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30">
                    <h3 className="text-purple-300 text-sm mb-1">Plan Status</h3>
                    <p className="text-2xl font-black text-white">{isPro ? "Universal Pro 🚀" : "Free Explorer"}</p>
                    {isPro ? (
                        <p className="text-xs text-purple-300 mt-2">Active Subscription</p>
                    ) : (
                        <a href="/pricing" className="text-xs text-purple-300 mt-2 hover:underline inline-block">Upgrade to Pro →</a>
                    )}
                </div>
            </div>

            <h2 className="text-xl font-bold text-white mb-6">Recent Activity</h2>
            <div className="rounded-2xl border border-white/10 bg-white/[0.02] overflow-hidden">
                <div className="p-4 border-b border-white/5 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <span className="text-2xl">⚡</span>
                        <div>
                            <p className="text-sm font-bold text-white">JSON TypeScript Generator</p>
                            <p className="text-xs text-gray-500">2 minutes ago</p>
                        </div>
                    </div>
                    <span className="text-xs text-gray-400">-1 credit</span>
                </div>
                <div className="p-4 border-b border-white/5 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <span className="text-2xl">🎮</span>
                        <div>
                            <p className="text-sm font-bold text-white">Flappy Clone</p>
                            <p className="text-xs text-gray-500">2 hours ago</p>
                        </div>
                    </div>
                    <span className="text-xs text-gray-400">-3 credits</span>
                </div>
            </div>
        </div>
    );
}
