export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="flex min-h-screen bg-[#0F0B2B] text-gray-200">
            {/* Sidebar */}
            <aside className="w-64 border-r border-white/10 bg-white/[0.02] p-6 flex flex-col gap-6">
                <div className="text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-500 mb-8">
                    ShipMicro ⚡
                </div>

                <nav className="flex flex-col gap-2">
                    <p className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Personal</p>
                    <a href="/dashboard" className="px-4 py-2 rounded-lg bg-white/5 text-white hover:bg-white/10 transition-colors">Workspace</a>
                    <a href="#" className="px-4 py-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-colors">Favorites</a>
                    <a href="/pricing" className="px-4 py-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-colors">Billing</a>
                </nav>

                <nav className="flex flex-col gap-2 mt-8">
                    <p className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Admin</p>
                    <a href="/dashboard/ceo" className="px-4 py-2 rounded-lg text-cyan-400 hover:bg-cyan-500/10 transition-colors border border-transparent hover:border-cyan-500/30">CEO View 👑</a>
                </nav>

                <div className="mt-auto p-4 rounded-xl bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20">
                    <p className="text-sm font-bold text-white mb-1">Universal Pro</p>
                    <div className="w-full h-1.5 bg-black rounded-full overflow-hidden mb-2">
                        <div className="w-2/3 h-full bg-gradient-to-r from-cyan-400 to-purple-500" />
                    </div>
                    <p className="text-xs text-gray-400">66 credits remaining</p>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 p-10 overflow-auto">
                {children}
            </main>
        </div>
    );
}
