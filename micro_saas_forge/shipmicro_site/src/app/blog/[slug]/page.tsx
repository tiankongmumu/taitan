import { notFound } from "next/navigation";

interface BlogPostProps {
    params: Promise<{ slug: string }>;
}

export default async function BlogPostPage({ params }: BlogPostProps) {
    const { slug } = await params;
    // Blog system is pending migration — all slugs return 404
    void slug;
    return notFound();
}
