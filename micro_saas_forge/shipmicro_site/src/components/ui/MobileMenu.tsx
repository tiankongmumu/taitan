"use client";

import { useState, useEffect } from "react";

const NAV_LINKS = [
    { href: "/#products", label: "产品", emoji: "🔥" },
    { href: "/tools", label: "工具", emoji: "⚡" },
    { href: "/arcade", label: "游戏", emoji: "🎮" },
    { href: "/news", label: "资讯", emoji: "📰" },
    { href: "/ideas", label: "灵感", emoji: "💡" },
];

export function MobileMenu() {
    const [isOpen, setIsOpen] = useState(false);

    // Close when route changes
    useEffect(() => {
        const handleClick = () => setIsOpen(false);
        window.addEventListener("popstate", handleClick);
        return () => window.removeEventListener("popstate", handleClick);
    }, []);

    // Lock scroll when open
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = "hidden";
        } else {
            document.body.style.overflow = "";
        }
        return () => { document.body.style.overflow = "" };
    }, [isOpen]);

    return (
        <>
            {/* Hamburger button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="sm:hidden flex flex-col items-center justify-center w-9 h-9 rounded-lg hover:bg-white/[0.06] transition-colors relative z-[60]"
                aria-label="菜单"
            >
                <span className={`block w-5 h-[2px] bg-white rounded-full transition-all duration-300 ${isOpen ? "rotate-45 translate-y-[3px]" : ""}`} />
                <span className={`block w-5 h-[2px] bg-white rounded-full transition-all duration-300 mt-[4px] ${isOpen ? "opacity-0" : ""}`} />
                <span className={`block w-5 h-[2px] bg-white rounded-full transition-all duration-300 mt-[4px] ${isOpen ? "-rotate-45 -translate-y-[7px]" : ""}`} />
            </button>

            {/* Overlay */}
            {isOpen && (
                <div
                    className="fixed inset-0 z-[90] bg-black/60 backdrop-blur-sm sm:hidden"
                    onClick={() => setIsOpen(false)}
                />
            )}

            {/* Drawer */}
            <div
                className={`fixed top-0 right-0 z-[95] h-screen w-[280px] sm:hidden
          bg-[#0a0d1e]/98 backdrop-blur-xl border-l border-white/[0.06]
          transform transition-transform duration-300 ease-out shadow-2xl shadow-black/50
          ${isOpen ? "translate-x-0" : "translate-x-full"}`
                }
            >
                <div className="pt-16 px-6 h-full flex flex-col">
                    {/* Nav links */}
                    <div className="space-y-1">
                        {NAV_LINKS.map((link, i) => (
                            <a
                                key={link.href}
                                href={link.href}
                                onClick={() => setIsOpen(false)}
                                className="flex items-center gap-3 px-4 py-3.5 rounded-xl text-base font-medium text-gray-300 hover:text-white hover:bg-white/[0.06] transition-all"
                                style={{ animationDelay: `${i * 50}ms` }}
                            >
                                <span className="text-lg w-7 text-center">{link.emoji}</span>
                                <span>{link.label}</span>
                            </a>
                        ))}
                    </div>

                    {/* Divider */}
                    <div className="mt-6 mb-4 border-t border-white/[0.06]" />

                    {/* Quick links */}
                    <div className="space-y-1">
                        <a href="https://xiaobot.net/" target="_blank" rel="noopener noreferrer"
                            onClick={() => setIsOpen(false)}
                            className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm text-gray-500 hover:text-gray-300 transition-colors">
                            <span className="w-7 text-center">📖</span>
                            <span>小报童专栏</span>
                        </a>
                    </div>

                    {/* Branding */}
                    <div className="mt-auto pb-8 text-center">
                        <div className="text-xs text-gray-600">Powered by TITAN Engine</div>
                    </div>
                </div>
            </div>
        </>
    );
}
