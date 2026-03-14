"use client";

import { useUser } from "@clerk/nextjs";

export default function PricingPage() {
    const { isLoaded } = useUser();

    return (
        <div className="max-w-6xl mx-auto px-6 py-20 text-center">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-sm text-emerald-400 mb-8">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-neon" />
                100% Free Forever
            </div>

            <h1 className="text-5xl md:text-7xl font-black tracking-tight mb-6 text-white leading-tight">
                All Tools.<br />
                <span className="text-gradient from-emerald-400 to-cyan-500">Zero Cost.</span>
            </h1>

            <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-16">
                ShipMicro started as a premium tool platform. But we realized that developer tools and utility apps belong in the hands of everyone. Everything here is now completely free.
            </p>

            <div className="max-w-3xl mx-auto">
                {/* Always Free Tier */}
                <div className="p-10 rounded-3xl relative overflow-hidden bg-gradient-to-b from-[#0a1f18] to-[#0F0B2B] border border-emerald-500/30 shadow-[0_0_50px_rgba(16,185,129,0.15)] group transform hover:-translate-y-2 transition-transform duration-300 flex flex-col text-left">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/10 blur-[80px] rounded-full pointer-events-none" />

                    <h3 className="text-3xl font-black text-white mb-2">Universal Access</h3>
                    <p className="text-emerald-300/80 mb-6">Unlimited automated power without the paywalls.</p>
                    <div className="text-6xl font-black text-white mb-8">$0<span className="text-xl text-gray-500 font-normal">/forever</span></div>

                    <ul className="space-y-4 mb-8 relative z-10 flex-1">
                        <li className="flex items-center gap-3 text-gray-200 text-lg">
                            <span className="text-emerald-400 font-bold text-xl">✓</span> Unlimited tool executions (No daily caps)
                        </li>
                        <li className="flex items-center gap-3 text-gray-200 text-lg">
                            <span className="text-emerald-400 font-bold text-xl">✓</span> Ad-Free Arcade & Early Access Games
                        </li>
                        <li className="flex items-center gap-3 text-gray-200 text-lg">
                            <span className="text-emerald-400 font-bold text-xl">✓</span> Download High-Res output from AI Photo generators
                        </li>
                        <li className="flex items-center gap-3 text-gray-200 text-lg">
                            <span className="text-emerald-400 font-bold text-xl">✓</span> Export HS Tariff lookup results to CSV
                        </li>
                    </ul>

                    <div className="mt-8 relative z-20 min-h-[55px]">
                        {!isLoaded ? (
                            <button disabled className="w-full py-4 rounded-xl font-bold text-white bg-white/5 border border-white/10 opacity-50 cursor-not-allowed text-lg">Loading Status...</button>
                        ) : (
                            <a href="/tools" className="block text-center w-full py-4 rounded-xl font-black text-white bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 shadow-lg shadow-emerald-500/25 transition-all hover:scale-[1.02] text-lg">
                                Start Using Tools Now 🚀
                            </a>
                        )}
                    </div>
                    <p className="text-center text-sm text-gray-500 mt-5 relative z-10">No credit card required. No hidden fees. Open to everyone.</p>
                </div>
            </div>

            {/* Support CTA */}
            <div className="max-w-3xl mx-auto mt-20 p-8 rounded-3xl glass border border-amber-500/20 bg-gradient-to-tr from-amber-500/5 to-transparent flex flex-col md:flex-row items-center justify-between gap-8 text-left">
                <div>
                    <h3 className="text-2xl font-bold text-white mb-2 text-amber-50">Want to support the developer?</h3>
                    <p className="text-amber-100/60 font-sm">ShipMicro runs on server compute. If these tools saved you time, consider buying me a coffee.</p>
                </div>
                <a href="https://afdian.com/a/tiankongmumu" target="_blank" rel="noreferrer" className="shrink-0 px-8 py-4 rounded-full font-bold text-[#0F0B2B] bg-amber-400 hover:bg-amber-300 shadow-[0_0_20px_rgba(251,191,36,0.3)] transition-all hover:scale-105">
                    ☕ Buy me a Coffee
                </a>
            </div>
        </div>
    );
}
