import { NextResponse } from "next/server";
import { loadTools, type ToolInfo } from "@/lib/data";

const GAME_CATS = ["Tap", "Dodge", "Memory", "Pattern", "Math", "Typing", "Reaction", "Classic", "Game", "Arcade"];

export async function GET() {
    try {
        const allTools: ToolInfo[] = loadTools();
        const tools = allTools.filter(t => !GAME_CATS.includes(t.cat) && t.success);
        const games = allTools.filter(t => GAME_CATS.includes(t.cat) && t.success);

        return NextResponse.json({
            status: "ok",
            version: "v18-serverless",
            timestamp: new Date().toISOString(),
            metrics: {
                totalItems: allTools.length,
                tools: tools.length,
                games: games.length,
                successRate: allTools.filter(t => t.success).length + "/" + allTools.length,
            },
        });
    } catch (error) {
        return NextResponse.json(
            {
                status: "error",
                timestamp: new Date().toISOString(),
                error: error instanceof Error ? error.message : "Unknown error",
            },
            { status: 500 }
        );
    }
}
