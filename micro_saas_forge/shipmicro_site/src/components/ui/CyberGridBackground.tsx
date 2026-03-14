'use client'

import { useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'

export function CyberGridBackground() {
    const [mounted, setMounted] = useState(false)
    const pathname = usePathname()

    useEffect(() => {
        setMounted(true)
    }, [])

    if (!mounted) return null

    // Optional: Different vibe on arcade vs tools
    const isArcade = pathname?.startsWith('/arcade')
    const glowColor = isArcade ? 'rgba(236, 72, 153, 0.15)' : 'rgba(6, 182, 212, 0.15)'
    const glowPulse = isArcade ? 'rgba(168, 85, 247, 0.15)' : 'rgba(56, 189, 248, 0.15)'

    return (
        <div className="fixed inset-0 z-[-10] w-full h-full bg-[#050505] overflow-hidden pointer-events-none">
            {/* Dynamic Grid */}
            <div
                className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:40px_40px]"
                style={{
                    maskImage: 'radial-gradient(ellipse 60% 60% at 50% 50%, #000 70%, transparent 100%)',
                    WebkitMaskImage: 'radial-gradient(ellipse 60% 60% at 50% 50%, #000 70%, transparent 100%)'
                }}
            />

            {/* Cyber Glowing Orbs */}
            <div
                className="absolute top-0 left-1/4 w-[500px] h-[500px] rounded-full mix-blend-screen filter blur-[100px] opacity-40 animate-blob"
                style={{ backgroundColor: glowColor }}
            />
            <div
                className="absolute top-1/4 right-1/4 w-[600px] h-[600px] rounded-full mix-blend-screen filter blur-[120px] opacity-30 animate-blob animation-delay-2000"
                style={{ backgroundColor: glowPulse }}
            />
            <div
                className="absolute -bottom-32 left-1/2 w-[700px] h-[700px] rounded-full mix-blend-screen filter blur-[150px] opacity-20 animate-blob animation-delay-4000"
                style={{ backgroundColor: isArcade ? 'rgba(234, 179, 8, 0.1)' : 'rgba(16, 185, 129, 0.1)' }}
            />

            {/* Scanline Overlay */}
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] mix-blend-overlay"></div>
        </div>
    )
}
