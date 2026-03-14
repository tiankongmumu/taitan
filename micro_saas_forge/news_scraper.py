"""
ShipMicro News Scraper - 自动抓取 AI/工具热点并用 LLM 改写为 SEO 资讯
数据源: HackerNews API, GitHub Trending
输出: Markdown 资讯文件（可被 Forge 部署管线消费）
"""
import os
import sys
import json
import time
import re
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from core_generators.llm_client import LLMClient
from logger import get_logger

log = get_logger("news")

# ============================================================
# 数据源抓取
# ============================================================

def fetch_hackernews_top(limit=10):
    """抓取 HackerNews 热门故事 (完全免费, 无需 API Key)"""
    log.info(f"📡 抓取 HackerNews Top {limit}...")
    try:
        top_ids = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=15
        ).json()[:limit * 2]  # 多抓一些，后面过滤

        stories = []
        for sid in top_ids:
            try:
                item = requests.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                    timeout=10
                ).json()
                if not item or item.get("type") != "story":
                    continue
                title = item.get("title", "")
                url = item.get("url", "")
                score = item.get("score", 0)
                # 过滤：只要 AI/工具/开发者相关 且 热度够高
                keywords = ["ai", "llm", "gpt", "tool", "saas", "dev", "api", "open source",
                            "startup", "launch", "ship", "build", "code", "deploy", "web",
                            "typescript", "react", "next", "python", "database", "cloud",
                            "automation", "agent", "model", "transformer", "generate",
                            "free", "alternative", "self-host"]
                title_lower = title.lower()
                if score >= 50 or any(kw in title_lower for kw in keywords):
                    stories.append({
                        "source": "HackerNews",
                        "title": title,
                        "url": url,
                        "score": score,
                        "comments": item.get("descendants", 0)
                    })
                if len(stories) >= limit:
                    break
            except Exception:
                continue
        log.info(f"  ✅ 获取 {len(stories)} 条 HackerNews 热点")
        return stories
    except Exception as e:
        log.warning(f"  ❌ HackerNews 抓取失败: {e}")
        return []


def fetch_github_trending(limit=10):
    """抓取 GitHub Trending 仓库 (通过搜索 API, 无需 Token)"""
    log.info(f"📡 抓取 GitHub Trending Top {limit}...")
    try:
        # 搜索最近一周创建的高星仓库
        from datetime import timedelta
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        resp = requests.get(
            "https://api.github.com/search/repositories",
            params={
                "q": f"created:>{week_ago} stars:>50",
                "sort": "stars",
                "order": "desc",
                "per_page": limit
            },
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=15
        )
        resp.raise_for_status()
        repos = resp.json().get("items", [])
        stories = []
        for repo in repos:
            stories.append({
                "source": "GitHub",
                "title": f"{repo['full_name']}: {repo.get('description', 'No description')}",
                "url": repo["html_url"],
                "score": repo["stargazers_count"],
                "comments": repo.get("open_issues_count", 0)
            })
        log.info(f"  ✅ 获取 {len(stories)} 条 GitHub 热门仓库")
        return stories
    except Exception as e:
        log.warning(f"  ❌ GitHub Trending 抓取失败: {e}")
        return []


# ============================================================
# LLM 内容改写
# ============================================================

def rewrite_story_to_article(story: dict, llm: LLMClient) -> dict:
    """将一条热点改写为 300-500 字的英文 SEO 资讯文章"""
    prompt = f"""You are a tech journalist writing for ShipMicro.com, a developer tools platform.

Rewrite the following trending topic into a concise, engaging English blog post (300-500 words).

TOPIC: {story['title']}
SOURCE: {story['source']} (Score: {story['score']})
URL: {story['url']}

REQUIREMENTS:
1. Write a catchy, SEO-optimized title (under 60 characters).
2. Write 3-5 paragraphs covering: what it is, why it matters, and who should care.
3. Include 3-5 relevant SEO keywords naturally in the text.
4. End with a "Related Tools on ShipMicro" section suggesting 1-2 tool ideas that could complement this topic (link format: shipmicro.com/tools/xxx).
5. Keep the tone professional but approachable, like a smart friend explaining tech.
6. Output format:
---
title: Your SEO Title Here
slug: your-seo-slug-here
keywords: [keyword1, keyword2, keyword3]
source_url: {story['url']}
source_name: {story['source']}
date: {datetime.now().strftime('%Y-%m-%d')}
---

[Your article content in Markdown here]
"""
    try:
        content = llm.generate(prompt)
        if not content:
            return None

        # 提取 frontmatter
        slug = re.sub(r'[^a-z0-9-]', '', story['title'].lower().replace(' ', '-'))[:60]
        return {
            "title": story["title"],
            "slug": slug,
            "source": story["source"],
            "content": content,
            "score": story["score"],
            "url": story["url"],
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        log.warning(f"  ⚠️ 改写失败: {story['title'][:40]}... => {e}")
        return None


# ============================================================
# 主流程
# ============================================================

def run_news_scraper(max_articles=6):
    """执行一次完整的新闻抓取 + 改写流程"""
    log.info("=" * 60)
    log.info("🗞️  SHIPMICRO NEWS SCRAPER 启动")
    log.info("=" * 60)
    start = time.time()

    # 1. 抓取数据源
    hn_stories = fetch_hackernews_top(limit=8)
    gh_stories = fetch_github_trending(limit=5)

    all_stories = hn_stories + gh_stories
    # 按热度排序，取前 N 条
    all_stories.sort(key=lambda x: x["score"], reverse=True)
    top_stories = all_stories[:max_articles]

    if not top_stories:
        log.warning("❌ 未抓取到任何热点，退出")
        return []

    log.info(f"📊 共抓取 {len(all_stories)} 条热点，取 Top {len(top_stories)} 进行改写")

    # 2. LLM 改写
    llm = LLMClient()
    articles = []
    output_dir = os.path.join(os.path.dirname(__file__), "news_articles")
    os.makedirs(output_dir, exist_ok=True)

    for i, story in enumerate(top_stories, 1):
        log.info(f"✍️ [{i}/{len(top_stories)}] 改写: {story['title'][:50]}...")
        article = rewrite_story_to_article(story, llm)
        if article:
            # 保存为 Markdown 文件
            filename = f"{datetime.now().strftime('%Y%m%d')}_{article['slug'][:40]}.md"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(article["content"])
            articles.append(article)
            log.info(f"  ✅ 已保存: {filename}")
        time.sleep(1)  # 控制 API 速率

    # 3. 生成索引文件
    index_path = os.path.join(output_dir, f"index_{datetime.now().strftime('%Y%m%d')}.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - start
    log.info("=" * 60)
    log.info(f"🎉 完成！共生成 {len(articles)} 篇资讯，耗时 {elapsed:.1f}s")
    log.info(f"📂 输出目录: {output_dir}")
    log.info("=" * 60)
    return articles


if __name__ == "__main__":
    articles = run_news_scraper(max_articles=6)
    if articles:
        print(f"\n📰 今日资讯摘要:")
        for a in articles:
            print(f"  [{a['source']}] {a['title'][:60]}  (🔥{a['score']})")
