export default function Loading() {
    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6">
            <div className="relative w-24 h-24 flex items-center justify-center">
                {/* Outer spin track */}
                <div className="absolute inset-0 rounded-full border border-purple-500/20 shadow-[0_0_20px_rgba(168,85,247,0.15)] animate-[spin_3s_linear_infinite]" />

                {/* Glowing segment */}
                <div className="absolute inset-0 rounded-full border-t-2 border-r-2 border-cyan-400 blur-[2px] animate-[spin_1s_ease-in-out_infinite]" />
                <div className="absolute inset-0 rounded-full border-t border-r border-cyan-400 animate-[spin_1s_ease-in-out_infinite]" />

                {/* Core entity */}
                <div className="w-4 h-4 rounded-full bg-white shadow-[0_0_15px_rgba(255,255,255,0.8)] animate-pulse" />
            </div>
            <p className="font-bold text-gray-500 tracking-widest uppercase text-sm animate-pulse">Initializing Interface...</p>
        </div>
    );
}
