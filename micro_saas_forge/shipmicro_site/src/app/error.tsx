"use client";

export default function GlobalError({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    return (
        <div className="min-h-[60vh] flex flex-col items-center justify-center px-4 relative z-10">
            <div className="text-center max-w-md">
                <div className="text-6xl mb-6">⚠️</div>
                <h2 className="text-2xl font-black text-white mb-4 font-[family-name:var(--font-outfit)]">
                    Something went wrong
                </h2>
                <p className="text-gray-400 mb-2 text-sm">
                    An unexpected error occurred. Our autonomous systems have been notified.
                </p>
                {error.digest && (
                    <p className="text-gray-600 text-xs font-mono mb-6">
                        Error ID: {error.digest}
                    </p>
                )}
                <div className="flex gap-4 justify-center">
                    <button
                        onClick={() => reset()}
                        className="px-6 py-3 rounded-full bg-cyan-500/20 text-cyan-400 font-bold text-sm border border-cyan-500/30 hover:bg-cyan-500 hover:text-white transition-all"
                    >
                        Try Again
                    </button>
                    <a
                        href="/"
                        className="px-6 py-3 rounded-full bg-white/5 text-gray-300 font-bold text-sm border border-white/10 hover:bg-white/10 transition-all"
                    >
                        Back to Home
                    </a>
                </div>
            </div>
        </div>
    );
}
