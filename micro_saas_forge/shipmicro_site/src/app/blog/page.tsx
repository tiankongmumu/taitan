export default function BlogPage() {
    return (
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12 sm:py-24 relative z-10 font-sans">
            <div className="mb-10 sm:mb-16">
                <div className="inline-block mb-4 px-3 py-1 rounded-full border border-amber-500/20 bg-amber-500/5 text-xs font-bold text-amber-400 uppercase tracking-widest">
                    Blog
                </div>
                <h1 className="text-4xl sm:text-6xl font-black tracking-tighter mb-4 sm:mb-6 font-[family-name:var(--font-outfit)]">
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-orange-500 to-red-500">Engineering Blog</span>
                </h1>
                <p className="text-gray-400 text-lg sm:text-xl font-light max-w-2xl leading-relaxed">
                    Deep dives into autonomous AI engineering, micro-SaaS architecture, and the ShipMicro generation pipeline.
                </p>
            </div>

            <div className="text-center py-20 border border-dashed border-white/10 rounded-2xl bg-white/[0.02]">
                <div className="text-5xl mb-4">🚧</div>
                <h2 className="text-2xl font-bold text-white mb-2">Coming Soon</h2>
                <p className="text-gray-400">Our AI agents are crafting the first batch of engineering articles. Stay tuned.</p>
            </div>
        </div>
    );
}
