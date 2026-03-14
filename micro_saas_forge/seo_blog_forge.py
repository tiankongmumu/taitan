"""
ShipMicro SEO Content Engine
==============================================
自动检索没有相关博客文章的工具或游戏，调用 DeepSeek 生成 1500 字以上的高质量、带关键词优化的技术/休闲软文。
写入 SQLite 数据库以供 Next.js 渲染。
"""
import os
import sys
import sqlite3
import datetime

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from logger import get_logger

log = get_logger("seo_blog")

DB_PATH = os.path.join(os.path.dirname(__file__), "shipmicro_site", "prisma", "dev.db")

def generate_blog_content(llm: LLMClient, tool_name: str, category: str, description: str) -> dict:
    prompt = f"""You are an elite, highly opinionated Silicon Valley Tech Evangelist writing for 'ShipMicro'—a cutting-edge platform for futuristic developer tools and browser games.
    
Write a comprehensive, culturally resonant, and highly immersive blog post about our latest application. DO NOT write generic, boring SEO copy. Write with SOUL, edge, and deep technical insight.
Name: {tool_name}
Category: {category}
Description: {description}

REQUIREMENTS:
1. Tone & Persona (The "Soul"): Write like a thought leader on Hacker News. Be slightly edgy, highly technical, and extremely passionate. Use tech analogies and culturally relevant memes/phrases if appropriate.
2. Length: Around 800 - 1200 words of pure substance and deep insights.
3. Content Structure (Use Markdown):
   - Catchy, click-worthy H1 Title (e.g., "Stop Using Boring Regex Testers. Meet the Cyberpunk Alternative.")
   - Engaging, punch-in-the-face introduction (hook the reader instantly).
   - The core problem this solves / The aesthetic soul of this tool (H2)
   - Deep Technical Dive: How it was built, the modern stack, or why it's flawlessly designed (H2)
   - Conclusion with a strong Call-To-Action to leap into the future and click the embedded tool.
4. Output format: Return pure Markdown. First line must be the Title starting with #.

Example:
# Why The Future of Developer Tools Looks Like a Cyberpunk Dashboard
(Body here...)
"""
    log.info(f"⏳ 正在为 {tool_name} 撰写博客文章...")
    content = llm.generate(prompt)
    
    # Extract title from the first line
    lines = content.strip().split("\n")
    title = tool_name + " Guide"
    if lines and lines[0].startswith("#"):
        title = lines[0].replace("#", "").strip()
        content = "\n".join(lines[1:]).strip()
        
    return {
        "title": title,
        "content_md": content
    }

def run_seo_blog_forge(limit=1):
    log.info("=" * 60)
    log.info("✍️ SHIPMICRO SEO CONTENT ENGINE 启动")
    log.info("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # 获取还没有博客的工具/游戏
    cur.execute("""
        SELECT c.slug, c.title, c.category, c.description 
        FROM ContentItem c
        LEFT JOIN Blog b ON c.slug = b.contentItemSlug
        WHERE b.id IS NULL
        ORDER BY c.createdAt DESC
        LIMIT ?
    """, (limit,))
    
    items = cur.fetchall()
    if not items:
        log.info("✅ 所有内容都已配备博客文章！")
        conn.close()
        return

    llm = LLMClient()
    success_count = 0
    
    for item in items:
        try:
            blog_data = generate_blog_content(llm, item["title"], item["category"], item["description"] or "")
            
            blog_slug = f"{item['slug']}-guide"
            
            import uuid
            blog_id = "c" + str(uuid.uuid4()).replace("-", "")[:24] # Fake cuid
            now = datetime.datetime.utcnow().isoformat() + "Z"
            
            cur.execute("""
                INSERT INTO Blog (id, slug, title, contentMd, contentItemSlug, createdAt, updatedAt)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (blog_id, blog_slug, blog_data["title"], blog_data["content_md"], item["slug"], now, now))
            
            conn.commit()
            log.info(f"✅ 生成成功: {blog_data['title']} (Slug: {blog_slug})")
            success_count += 1
            
        except Exception as e:
            log.error(f"❌ 为 {item['title']} 生成博客失败: {e}")
            
    conn.close()
    log.info(f"🏁 完成！成功生成 {success_count} 篇 SEO 博客。")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=3, help="批量生成几篇博客")
    args = parser.parse_args()
    run_seo_blog_forge(limit=args.limit)
