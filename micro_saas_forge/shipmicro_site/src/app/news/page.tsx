import { loadNews } from "@/lib/data";
import NewsClient from "./NewsClient";
import { Metadata } from "next";

export const metadata: Metadata = {
    title: "Tech News — AI-Curated Daily | ShipMicro",
    description: "AI-curated daily tech, startup, and developer news from HackerNews, GitHub Trending & more. Filter by category, search, and sort.",
};

export default async function NewsPage() {
    const news = loadNews();
    return <NewsClient articles={news} />;
}
