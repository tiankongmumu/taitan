"""
TITAN Pipeline — Stage 5: SEO Content Generator
==================================================
Generates SEO-optimized articles from affiliate matches.
Each article targets a specific pain point + affiliate product.

Input:  demand_signals/affiliate_matches.json
Output: content_output/*.md + shipmicro_site/public/articles/*.html
"""
import os
import sys
import json
import re
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger
from core_generators.llm_client import LLMClient

log = get_logger("seo_content")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIGNALS_DIR = os.path.join(BASE_DIR, "demand_signals")
INPUT_FILE = os.path.join(SIGNALS_DIR, "affiliate_matches.json")
CONTENT_DIR = os.path.join(BASE_DIR, "content_output")
HTML_DIR = os.path.join(BASE_DIR, "shipmicro_site", "public", "articles")
os.makedirs(CONTENT_DIR, exist_ok=True)
os.makedirs(HTML_DIR, exist_ok=True)

ARTICLE_PROMPT_EN = """You are an expert SEO content writer for a SaaS-focused blog called ShipMicro.
Write a high-quality, 600-800 word article targeting this specific topic:

**Pain Point:** {pain}
**Recommended Solution:** {product} ({commission} commission)
**Affiliate Link:** {url}
**Target Audience:** Indie hackers, solopreneurs, SaaS founders

RULES:
1. Start with a compelling, SEO-friendly H1 title (include the main keyword)
2. Use 2-3 H2 subheadings to structure the content
3. Address the pain point in the first paragraph (hook the reader)
4. Naturally introduce the recommended tool in the second section
5. Include a clear CTA with the affiliate link (make it natural, not salesy)
6. End with a brief conclusion
7. Tone: Helpful indie hacker sharing real experience. NO corporate speak.
8. Include relevant keywords naturally for SEO

Output the article in Markdown format. Start with the H1 title."""

ARTICLE_PROMPT_CN = """你是一位顶级中文内容创作者，擅长写公众号/知乎/小红书风格的科技种草文。
请针对以下主题写一篇 800-1200 字的高质量中文文章：

**用户痛点：** {pain}
**推荐方案：** {product}（{commission}）
**推荐链接：** {url}
**目标平台：** {platform}
**目标受众：** 创业者、独立开发者、效率工具爱好者

要求：
1. 标题吸引眼球，适合{platform}传播（可加 emoji）
2. 开头用一个场景故事引入痛点（让读者产生共鸣）
3. 中间自然引出推荐工具，说清楚它怎么解决问题
4. 加入个人使用体验（即使是虚构的，也要写得真实）
5. 结尾放推荐链接，语气自然（"感兴趣的可以试试"而不是"快去买"）
6. 语气：像一个乐于分享的科技博主，不要官方腔
7. 如果是小红书风格，多用 emoji 和短句；如果是公众号风格，可以更深度

输出 Markdown 格式，以 # 标题 开头。"""


def _slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text)
    return text[:60].rstrip("-")


def _md_to_html(md_content: str, title: str) -> str:
    """Convert markdown to basic HTML page."""
    # Simple markdown → HTML conversion
    html_body = md_content
    # H1
    html_body = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html_body, flags=re.MULTILINE)
    # H2
    html_body = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html_body, flags=re.MULTILINE)
    # H3
    html_body = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html_body, flags=re.MULTILINE)
    # Bold
    html_body = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html_body)
    # Links
    html_body = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="nofollow sponsored">\1</a>', html_body)
    # Paragraphs
    paragraphs = html_body.split("\n\n")
    html_body = "\n".join(
        f"<p>{p.strip()}</p>" if not p.strip().startswith("<h") and not p.strip().startswith("<p") else p
        for p in paragraphs if p.strip()
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | ShipMicro Blog</title>
    <meta name="description" content="{title[:150]}">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:'Inter',sans-serif; background:#0f0f17; color:#e2e8f0; line-height:1.8; }}
        article {{ max-width:720px; margin:0 auto; padding:60px 20px; }}
        h1 {{ font-size:32px; font-weight:700; margin-bottom:24px; background:linear-gradient(135deg,#fff,#818cf8); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
        h2 {{ font-size:22px; font-weight:600; margin:32px 0 12px; color:#c7d2fe; }}
        p {{ margin-bottom:16px; color:#94a3b8; }}
        a {{ color:#818cf8; text-decoration:underline; }}
        a:hover {{ color:#a5b4fc; }}
        strong {{ color:#e2e8f0; }}
        .back {{ display:inline-block; margin-bottom:24px; color:#64748b; text-decoration:none; font-size:14px; }}
        .cta {{ display:inline-block; background:#6366f1; color:white; padding:12px 24px; border-radius:8px; text-decoration:none; font-weight:600; margin:16px 0; }}
        .cta:hover {{ background:#818cf8; }}
    </style>
</head>
<body>
    <article>
        <a href="https://shipmicro.com" class="back">← ShipMicro Home</a>
        {html_body}
        <p style="color:#475569;font-size:12px;margin-top:40px;border-top:1px solid #1e293b;padding-top:16px;">
            Published by <a href="https://shipmicro.com">ShipMicro</a> • AI-Curated SaaS Intelligence
        </p>
    </article>
</body>
</html>"""


def generate_articles(matches: List[Dict] = None) -> List[Dict]:
    """Generate SEO articles from affiliate matches."""
    log.info("=" * 50)
    log.info("📝 TITAN SEO Content Generator v5.0 — Starting")
    log.info("=" * 50)

    # Load matches
    if matches is None:
        if not os.path.exists(INPUT_FILE):
            log.error(f"Input not found: {INPUT_FILE}")
            return []
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            matches = json.load(f)

    log.info(f"📥 Input: {len(matches)} affiliate matches")
    llm = LLMClient()
    articles = []

    for i, match in enumerate(matches[:5], 1):  # Generate up to 5 articles
        keyword = match.get("pain_keyword", "unknown")
        platform = match.get("target_platform", "")
        is_cn = bool(platform) and any(p in platform for p in ["小红书", "知乎", "公众号", "闲鱼"])

        log.info(f"  ✍️ [{i}/{min(len(matches), 5)}] {'🇨🇳 CN' if is_cn else '🌍 EN'} article for: {keyword}")

        if is_cn:
            prompt = ARTICLE_PROMPT_CN.format(
                pain=match.get("pain_summary", match.get("pain_keyword", "")),
                product=match.get("product_name", ""),
                commission=match.get("commission", ""),
                url=match.get("affiliate_url", ""),
                platform=platform
            )
            system = "你是一位专业的中文科技内容创作者。"
        else:
            prompt = ARTICLE_PROMPT_EN.format(
                pain=match.get("pain_summary", match.get("pain_keyword", "")),
                product=match.get("product_name", ""),
                commission=match.get("commission", ""),
                url=match.get("affiliate_url", "")
            )
            system = "You are an expert SEO content writer."

        content = llm.generate(prompt=prompt, system_prompt=system)
        if not content:
            log.warning(f"    ⚠️ Skipped (empty response)")
            continue

        # Extract title from first line
        lines = content.strip().split("\n")
        title = lines[0].lstrip("# ").strip() if lines else keyword
        slug = _slugify(title)

        # Save Markdown
        md_path = os.path.join(CONTENT_DIR, f"{slug}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Save HTML
        html_content = _md_to_html(content, title)
        html_path = os.path.join(HTML_DIR, f"{slug}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        articles.append({
            "title": title,
            "slug": slug,
            "keyword": keyword,
            "product": match.get("product_name", ""),
            "affiliate_url": match.get("affiliate_url", ""),
            "md_path": md_path,
            "html_path": html_path,
            "word_count": len(content.split())
        })

        log.info(f"    ✅ {title[:50]} ({len(content.split())} words)")

    # Save article index
    index_path = os.path.join(CONTENT_DIR, "article_index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    log.info(f"✅ Generated {len(articles)} SEO articles → {CONTENT_DIR}")
    return articles


if __name__ == "__main__":
    arts = generate_articles()
    print(f"\n📝 Generated {len(arts)} articles:")
    for a in arts:
        print(f"  • {a['title'][:60]} ({a['word_count']} words)")
